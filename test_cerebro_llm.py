"""Tests de cerebro_llm: cadena de fallback, mapeo de modelos y parseo de tool_calls. SIN red ni
tokens (monkeypatch de _post). Correr: py -3 test_cerebro_llm.py"""
import os
import io
import sys
import json
import tempfile
import traceback
import urllib.error

import cerebro_llm as llm


def _http_error(url, code, body):
    return urllib.error.HTTPError(url, code, "err", {}, io.BytesIO(body if isinstance(body, bytes) else body.encode()))


def _ok(name):
    print(f"  ok  {name}")


def _limpiar_env():
    for k in ("GROQ_API_KEY", "CEREBRAS_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY",
              "CEREBRO_LLM_PROVIDERS", "CEREBRO_LLM_MODEL", "CEREBRO_LLM_BASE_URL", "CEREBRO_LLM_API_KEY"):
        os.environ.pop(k, None)
    llm._BREAKER.clear()   # D2: el circuit-breaker es estado de proceso -> resetear entre casos


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


# ---- 9: D2 — un 429 abre el circuit-breaker y el proveedor se salta en la siguiente cadena ----
def test_breaker_abre_y_salta():
    _limpiar_env()
    os.environ["GROQ_API_KEY"] = "k"
    os.environ["OPENROUTER_API_KEY"] = "k"

    def fake_post(base_url, api_key, payload, timeout=60):
        if "groq" in base_url:
            raise _http_error(base_url, 429, '{"error":"credits depleted"}')
        return _resp("ok via openrouter")

    llm._post = fake_post
    r = llm.chat([{"role": "user", "content": "hi"}], tier="haiku")
    assert r["provider"] == "openrouter", r
    assert "groq" not in llm.proveedores_listos(), "groq debe quedar fuera tras el 429 (breaker)"
    assert "openrouter" in llm.proveedores_listos()
    err = r["intentos"][0]["error"].lower()
    assert "credito" in err or "saldo" in err, err   # D4: causa legible
    _ok("D2/D4: un 429 abre el breaker -> el proveedor se salta despues; el intento da causa legible")


# ---- 10: D2 — con la única clave en cooldown, chat da LLMError 'cooldown' (no el engañoso 'sin clave') ----
def test_breaker_todos_rotos_mensaje():
    _limpiar_env()
    os.environ["GROQ_API_KEY"] = "k"
    llm._post = lambda *a, **k: (_ for _ in ()).throw(_http_error("http://x", 429, "quota"))
    try:
        llm.chat([{"role": "user", "content": "hi"}])   # 1ª: trip breaker -> LLMError 'fallaron'
    except llm.LLMError:
        pass
    assert llm._con_clave() == ["groq"] and llm.proveedores_listos() == []   # clave presente pero rota
    try:
        llm.chat([{"role": "user", "content": "hi"}])   # 2ª: cadena vacía por breaker
        assert False, "deberia lanzar LLMError"
    except llm.LLMError as e:
        assert "cooldown" in str(e).lower(), str(e)
    except llm.LLMSinClave:
        assert False, "no debe decir 'sin clave' si hay clave pero en cooldown"
    _ok("D2: con la unica clave en cooldown -> LLMError 'cooldown' (no el enganoso 'sin clave')")


# ---- 11: D4 — _causa traduce los códigos crudos a texto accionable ----
def test_causa_traduce():
    assert "cloudflare" in llm._causa(403, "error 1010 cloudflare").lower()
    c429 = llm._causa(429, "credits depleted").lower()
    assert "credito" in c429 or "saldo" in c429
    assert "cuota" in llm._causa(429, "quota exceeded").lower()
    assert "clave" in llm._causa(401, "").lower()
    _ok("D4: _causa traduce 401 / 403-cloudflare / 429-creditos / 429-cuota a texto legible")


# ---- 12: P0 — Cerebras esta en la cadena cuando tiene clave; orden default lo pone tras groq ----
def test_cerebras_en_cadena():
    _limpiar_env()
    os.environ["GROQ_API_KEY"] = "k"
    os.environ["CEREBRAS_API_KEY"] = "k"
    nombres = llm.proveedores_listos()
    assert nombres == ["groq", "cerebras"], nombres
    prov = [p for p in llm.cadena() if p["name"] == "cerebras"][0]
    assert prov["base_url"] == "https://api.cerebras.ai/v1"
    assert llm.modelo_para(prov, "haiku") == "gpt-oss-120b"   # modelos reales del free de Cerebras (jun-2026)
    _ok("P0: Cerebras entra a la cadena con CEREBRAS_API_KEY (tras groq en el orden default)")


# ---- 13: P0 — el orden default pone gemini AL FINAL (free-tier poco fiable) ----
def test_orden_default_gemini_ultimo():
    _limpiar_env()
    for k in ("GROQ_API_KEY", "CEREBRAS_API_KEY", "OPENROUTER_API_KEY", "GEMINI_API_KEY"):
        os.environ[k] = "k"
    nombres = llm.proveedores_listos()
    assert nombres == ["groq", "cerebras", "openrouter", "gemini"], nombres
    assert nombres[-1] == "gemini", "gemini debe ir al final del orden por defecto"
    _ok("P0: orden default = groq,cerebras,openrouter,gemini (gemini al final)")


# ---- 14: P0 — un 429 'prepayment' (bug billing) usa cooldown CORTO, no los 5 min normales ----
def test_429_prepayment_cooldown_corto():
    _limpiar_env()
    os.environ["GEMINI_API_KEY"] = "k"
    llm._post = lambda *a, **k: (_ for _ in ()).throw(
        _http_error("http://x", 429, '{"error":"prepayment credits depleted"}'))
    try:
        llm.chat([{"role": "user", "content": "hi"}])
    except llm.LLMError:
        pass
    restante = llm._BREAKER.get("gemini", 0) - __import__("time").time()
    assert 0 < restante <= llm.BREAKER_COOLDOWN_ESPURIO_S + 1, restante   # corto, no 300s
    assert restante < llm.BREAKER_COOLDOWN_S, "el 429 espurio NO debe usar el cooldown largo"
    assert llm._es_espurio(429, "X prepayment Y") and not llm._es_espurio(429, "quota")
    assert "espurio" in llm._causa(429, "prepayment credits depleted").lower()
    _ok("P0: 429 'prepayment' (bug billing free-tier) -> cooldown corto + causa legible")


# ---- 15: P0 — _cargar_dotenv carga una clave del .env cuando falta en el entorno ----
def test_dotenv_carga_si_falta():
    _limpiar_env()
    with tempfile.TemporaryDirectory() as d:
        env = os.path.join(d, ".env")
        with open(env, "w", encoding="utf-8") as fh:
            fh.write("# comentario\nexport GROQ_API_KEY = abc123\nOPENROUTER_API_KEY=\"or-key\"\n")
        cargadas = llm._cargar_dotenv(env, forzar=True)
        assert "GROQ_API_KEY" in cargadas and "OPENROUTER_API_KEY" in cargadas, cargadas
        assert os.environ["GROQ_API_KEY"] == "abc123"          # 'export ' y espacios limpiados
        assert os.environ["OPENROUTER_API_KEY"] == "or-key"    # comillas quitadas
        assert llm.proveedores_listos() == ["groq", "openrouter"]   # la cadena ya las ve
    _ok("P0: _cargar_dotenv carga claves del .env (export/espacios/comillas) cuando faltan")


# ---- 16: P0 — el .env NUNCA pisa una variable real ya definida en el entorno ----
def test_dotenv_no_pisa_entorno_real():
    _limpiar_env()
    os.environ["GROQ_API_KEY"] = "real-de-entorno"
    with tempfile.TemporaryDirectory() as d:
        env = os.path.join(d, ".env")
        with open(env, "w", encoding="utf-8") as fh:
            fh.write("GROQ_API_KEY=del-archivo\n")
        cargadas = llm._cargar_dotenv(env, forzar=True)
        assert "GROQ_API_KEY" not in cargadas                  # no la toca
        assert os.environ["GROQ_API_KEY"] == "real-de-entorno"  # el entorno real manda
    _ok("P0: el .env no pisa una variable ya definida en el entorno (el entorno real manda)")


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
