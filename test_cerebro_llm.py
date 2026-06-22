"""Tests de cerebro_llm: cadena de fallback, mapeo de modelos y parseo de tool_calls. SIN red ni
tokens (monkeypatch de _post). Correr: py -3 test_cerebro_llm.py"""
import os
import sys
import json
import traceback

import cerebro_llm as llm


def _ok(name):
    print(f"  ok  {name}")


def _limpiar_env():
    for k in ("GROQ_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY",
              "CEREBRO_LLM_PROVIDERS", "CEREBRO_LLM_MODEL", "CEREBRO_LLM_BASE_URL", "CEREBRO_LLM_API_KEY"):
        os.environ.pop(k, None)


def _resp(text="hola", tool_calls=None):
    """Construye una respuesta estilo OpenAI."""
    msg = {"role": "assistant", "content": text}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return {"choices": [{"message": msg, "finish_reason": "tool_calls" if tool_calls else "stop"}]}


# ---- 1: sin ninguna clave -> LLMSinClave ----
def test_sin_clave_lanza():
    _limpiar_env()
    try:
        llm.chat([{"role": "user", "content": "hi"}])
        assert False, "deberia lanzar LLMSinClave"
    except llm.LLMSinClave:
        pass
    _ok("sin clave: chat lanza LLMSinClave con mensaje guia")


# ---- 2: cadena solo incluye proveedores con clave, en orden ----
def test_cadena_solo_con_clave():
    _limpiar_env()
    os.environ["OPENROUTER_API_KEY"] = "k1"
    os.environ["GROQ_API_KEY"] = "k2"
    nombres = llm.proveedores_listos()
    assert nombres == ["groq", "openrouter"], nombres   # orden DEFAULT, sin gemini (sin clave)
    _ok("cadena: incluye solo proveedores con clave y respeta el orden por defecto")


# ---- 3: CEREBRO_LLM_PROVIDERS cambia el orden ----
def test_orden_configurable():
    _limpiar_env()
    os.environ["GROQ_API_KEY"] = "k"
    os.environ["OPENROUTER_API_KEY"] = "k"
    os.environ["CEREBRO_LLM_PROVIDERS"] = "openrouter,groq"
    assert llm.proveedores_listos() == ["openrouter", "groq"]
    _ok("orden: CEREBRO_LLM_PROVIDERS reordena la cadena de respaldo")


# ---- 4: proveedor custom por CEREBRO_LLM_BASE_URL va primero ----
def test_custom_primero():
    _limpiar_env()
    os.environ["GROQ_API_KEY"] = "k"
    os.environ["CEREBRO_LLM_BASE_URL"] = "http://localhost:<PUERTO_LLM>/v1"
    os.environ["CEREBRO_LLM_API_KEY"] = "x"
    ch = llm.cadena()
    assert ch[0]["name"] == "custom" and ch[0]["base_url"] == "http://localhost:<PUERTO_LLM>/v1"
    _ok("custom: CEREBRO_LLM_BASE_URL agrega un proveedor OpenAI-compatible al frente")


# ---- 5: modelo_para respeta override global y mapeo por tier ----
def test_modelo_para():
    _limpiar_env()
    prov = {"models": {"haiku": "m-haiku", "sonnet": "m-sonnet"}}
    assert llm.modelo_para(prov, "haiku") == "m-haiku"
    assert llm.modelo_para(prov, "desconocido") == "m-sonnet"   # cae a sonnet
    os.environ["CEREBRO_LLM_MODEL"] = "forzado-x"
    assert llm.modelo_para(prov, "haiku") == "forzado-x"        # override global gana
    _ok("modelo_para: override global > mapeo por tier > sonnet de respaldo")


# ---- 6: chat cae al siguiente proveedor cuando el primero falla ----
def test_fallback_al_segundo():
    _limpiar_env()
    os.environ["GROQ_API_KEY"] = "k"
    os.environ["OPENROUTER_API_KEY"] = "k"
    llamados = []

    def fake_post(base_url, api_key, payload, timeout=60):
        llamados.append(base_url)
        if "groq" in base_url:
            raise RuntimeError("groq caido")
        return _resp("respuesta de respaldo")

    llm._post = fake_post
    r = llm.chat([{"role": "user", "content": "hi"}], tier="haiku")
    assert r["ok"] and r["provider"] == "openrouter" and r["text"] == "respuesta de respaldo"
    assert len(r["intentos"]) == 1 and r["intentos"][0]["provider"] == "groq"
    assert len(llamados) == 2   # intento groq (falla) + openrouter (ok)
    _ok("fallback: si el 1er proveedor falla, chat cae al siguiente y reporta el intento fallido")


# ---- 7: si TODOS fallan -> LLMError ----
def test_todos_fallan():
    _limpiar_env()
    os.environ["GROQ_API_KEY"] = "k"

    def fake_post(*a, **k):
        raise RuntimeError("caido")

    llm._post = fake_post
    try:
        llm.chat([{"role": "user", "content": "hi"}])
        assert False, "deberia lanzar LLMError"
    except llm.LLMError:
        pass
    _ok("todos fallan: chat lanza LLMError con el detalle de los intentos")


# ---- 8: parseo de tool_calls (arguments como string JSON) ----
def test_parseo_tool_calls():
    _limpiar_env()
    os.environ["GROQ_API_KEY"] = "k"
    tcs = [{"id": "c1", "function": {"name": "leer_archivo",
                                     "arguments": json.dumps({"ruta": "x.py"})}}]

    llm._post = lambda *a, **k: _resp(text="", tool_calls=tcs)
    r = llm.chat([{"role": "user", "content": "hi"}], tools=[{"type": "function"}])
    assert r["tool_calls"][0]["name"] == "leer_archivo"
    assert r["tool_calls"][0]["args"] == {"ruta": "x.py"}      # string JSON -> dict
    assert r["finish_reason"] == "tool_calls"
    _ok("tool_calls: extrae nombre y argumentos (string JSON -> dict) de la respuesta")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_llm ({len(fns)} casos) ==")
    _post_orig = llm._post
    for fn in fns:
        try:
            fn(); ok += 1
        except Exception:
            print("FAIL", fn.__name__); traceback.print_exc()
        finally:
            llm._post = _post_orig        # restaura el _post real entre casos
            _limpiar_env()
    print(f"\n{ok}/{len(fns)} verde")
    sys.exit(0 if ok == len(fns) else 1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _run()
