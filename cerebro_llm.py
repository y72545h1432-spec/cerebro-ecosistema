"""cerebro_llm.py — cliente LLM OpenAI-compatible MULTI-PROVEEDOR con FALLBACK. Stdlib pura (urllib).

POR QUE EXISTE (2026-06-21): el Agent Team puede correr workers a COSTO $0 usando los tiers GRATUITOS
de proveedores que hablan el protocolo OpenAI (`POST /chat/completions`): Groq, Google Gemini y
OpenRouter. Un solo cliente sirve para los tres porque el protocolo es el mismo; si uno falla o agota
su cuota del dia, se cae al siguiente automaticamente. Sin dependencias (urllib) -> fiel al ecosistema.

APTO PARA REPO PUBLICO: NINGUNA clave vive en el codigo. Todo se configura por variables de entorno,
asi cualquiera clona el repo, pega su(s) clave(s) gratis (sin tarjeta) y funciona.

CONFIG (variables de entorno):
  GROQ_API_KEY            clave gratis de https://console.groq.com   (sin tarjeta)
  GEMINI_API_KEY          clave gratis de https://aistudio.google.com (o GOOGLE_API_KEY)
  OPENROUTER_API_KEY      clave gratis de https://openrouter.ai/keys
  CEREBRO_LLM_PROVIDERS   orden de respaldo, ej "groq,gemini,openrouter" (default ese)
  CEREBRO_LLM_MODEL       fuerza un modelo concreto (ignora el mapeo por tier)
  CEREBRO_LLM_BASE_URL    + CEREBRO_LLM_API_KEY (+ CEREBRO_LLM_MODEL) -> proveedor CUSTOM (cualquiera
                          OpenAI-compatible: otro servicio, un gateway propio, etc.)

USO:
  import cerebro_llm
  r = cerebro_llm.chat([{"role": "user", "content": "hola"}], tier="haiku")
  print(r["text"], "via", r["provider"])      # r: {ok, text, tool_calls, provider, model, cost, ...}

TESTEABLE SIN RED NI TOKENS: monkeypatch `cerebro_llm._post` con un fake -> la cadena, el mapeo de
modelos y el parseo de tool_calls se prueban sin tocar internet (ver test_cerebro_llm.py).
"""
from __future__ import annotations
import os
import json
import urllib.request
import urllib.error

# --------------------------------------------------------------------------- presets de proveedores
# Cada proveedor: base_url OpenAI-compatible, las env vars donde buscar su clave, y el modelo GRATIS
# por defecto para cada tier. Los slugs de modelo cambian con el tiempo: se pueden sobreescribir por
# entorno (CEREBRO_LLM_MODEL) o por el toml ([api.models]). Aqui van defaults razonables (jun-2026).
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "env_keys": ["GROQ_API_KEY"],
        "consigue": "https://console.groq.com  (gratis, sin tarjeta)",
        "models": {"haiku": "llama-3.1-8b-instant",
                   "sonnet": "llama-3.3-70b-versatile",
                   "opus": "llama-3.3-70b-versatile"},
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "env_keys": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "consigue": "https://aistudio.google.com/apikey  (gratis, sin tarjeta)",
        "models": {"haiku": "gemini-2.5-flash-lite",
                   "sonnet": "gemini-2.5-flash",
                   "opus": "gemini-2.5-flash"},
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "env_keys": ["OPENROUTER_API_KEY"],
        "consigue": "https://openrouter.ai/keys  (gratis; modelos :free)",
        "models": {"haiku": "meta-llama/llama-3.3-70b-instruct:free",
                   "sonnet": "deepseek/deepseek-r1:free",
                   "opus": "deepseek/deepseek-r1:free"},
    },
}
DEFAULT_ORDER = ["groq", "gemini", "openrouter"]


class LLMSinClave(Exception):
    """Ningun proveedor tiene clave configurada en el entorno -> no se puede llamar a nadie."""


class LLMError(Exception):
    """Todos los proveedores de la cadena fallaron (red, cuota, error del modelo)."""


# --------------------------------------------------------------------------- resolucion de la cadena
def _env(*names: str) -> str | None:
    for n in names:
        v = os.environ.get(n)
        if v:
            return v.strip()
    return None


def _orden(cfg: dict | None) -> list:
    """Orden de proveedores a intentar: CEREBRO_LLM_PROVIDERS > toml [api].providers > DEFAULT_ORDER."""
    env = _env("CEREBRO_LLM_PROVIDERS")
    if env:
        return [p.strip() for p in env.split(",") if p.strip()]
    api = (cfg or {}).get("api", {}) if isinstance(cfg, dict) else {}
    if isinstance(api.get("providers"), list) and api["providers"]:
        return list(api["providers"])
    return list(DEFAULT_ORDER)


def cadena(cfg: dict | None = None) -> list:
    """Proveedores DISPONIBLES (con clave) en orden de respaldo. Cada item:
    {name, base_url, api_key, models}. Incluye un proveedor 'custom' si CEREBRO_LLM_BASE_URL esta puesto."""
    out = []
    # 1) proveedor CUSTOM por entorno (cualquier endpoint OpenAI-compatible) -> primero si existe.
    cbase = _env("CEREBRO_LLM_BASE_URL")
    if cbase:
        out.append({"name": "custom", "base_url": cbase.rstrip("/"),
                    "api_key": _env("CEREBRO_LLM_API_KEY") or "x", "models": {}})
    # 2) presets, en orden, solo los que tengan clave.
    overrides = (cfg or {}).get("api", {}).get("models", {}) if isinstance(cfg, dict) else {}
    for name in _orden(cfg):
        prov = PROVIDERS.get(name)
        if not prov:
            continue
        key = _env(*prov["env_keys"])
        if not key:
            continue
        models = dict(prov["models"])
        if isinstance(overrides.get(name), dict):
            models.update(overrides[name])
        out.append({"name": name, "base_url": prov["base_url"], "api_key": key, "models": models})
    return out


def modelo_para(prov: dict, tier: str) -> str:
    """Modelo a usar: CEREBRO_LLM_MODEL (global) > mapeo por tier del proveedor > su 'sonnet' > '?'."""
    forced = _env("CEREBRO_LLM_MODEL")
    if forced:
        return forced
    m = prov.get("models") or {}
    return m.get((tier or "").lower()) or m.get("sonnet") or next(iter(m.values()), "gpt-3.5-turbo")


def proveedores_listos(cfg: dict | None = None) -> list:
    """Nombres de proveedores con clave (para diagnostico / dry-run)."""
    return [p["name"] for p in cadena(cfg)]


# --------------------------------------------------------------------------- HTTP (urllib)
def _post(base_url: str, api_key: str, payload: dict, timeout: int = 60) -> dict:
    """POST {base_url}/chat/completions con Bearer. Devuelve el JSON. Aislable en tests."""
    url = base_url.rstrip("/") + "/chat/completions"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("HTTP-Referer", "https://github.com")        # OpenRouter pide referer/title
    req.add_header("X-Title", "cerebro-agent-team")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _extraer(obj: dict) -> dict:
    """De la respuesta OpenAI saca {text, tool_calls, finish_reason}."""
    try:
        msg = obj["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return {"text": "", "tool_calls": [], "finish_reason": "error"}
    tcs = []
    for tc in (msg.get("tool_calls") or []):
        fn = tc.get("function", {}) or {}
        args = fn.get("arguments")
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {"_raw": args}
        tcs.append({"id": tc.get("id", ""), "name": fn.get("name", ""), "args": args or {}})
    fr = (obj["choices"][0].get("finish_reason") if obj.get("choices") else None) or "stop"
    return {"text": msg.get("content") or "", "tool_calls": tcs, "finish_reason": fr}


# --------------------------------------------------------------------------- API publica
def chat(messages: list, tier: str = "sonnet", cfg: dict | None = None, tools: list | None = None,
         max_tokens: int = 1024, temperature: float = 0.3, timeout: int = 60) -> dict:
    """Llama al primer proveedor disponible; si falla, cae al siguiente de la cadena. COSTO = $0 en
    tiers gratuitos. Devuelve {ok, text, tool_calls, finish_reason, provider, model, cost, intentos}.
    Lanza LLMSinClave si no hay ninguna clave configurada; LLMError si TODOS fallan."""
    chain = cadena(cfg)
    if not chain:
        nombres = ", ".join(p["env_keys"][0] for p in PROVIDERS.values())
        raise LLMSinClave(
            "No hay clave de ningun proveedor gratis. Define al menos una variable de entorno: "
            f"{nombres}. Consigue una gratis (sin tarjeta) en console.groq.com / aistudio.google.com / openrouter.ai/keys.")
    intentos = []
    for prov in chain:
        model = modelo_para(prov, tier)
        payload = {"model": model, "messages": messages,
                   "max_tokens": max_tokens, "temperature": temperature}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        try:
            obj = _post(prov["base_url"], prov["api_key"], payload, timeout)
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")[:200]
            except Exception:
                pass
            intentos.append({"provider": prov["name"], "model": model, "error": f"HTTP {e.code} {body}"})
            continue
        except Exception as e:
            intentos.append({"provider": prov["name"], "model": model, "error": str(e)[:200]})
            continue
        out = _extraer(obj)
        return {"ok": True, "provider": prov["name"], "model": model, "cost": 0.0,
                "intentos": intentos, **out}
    raise LLMError(f"todos los proveedores fallaron: {intentos}")
