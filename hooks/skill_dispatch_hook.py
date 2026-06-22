#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hook PreToolUse para el tool 'Skill' -> registra el disparo en skill_dispatch_log.jsonl.
Backlog II_SKILLS #13. Lee el JSON del evento por stdin (formato hooks de Claude Code) y
extrae el nombre de la skill invocada. NO bloquea nunca (exit 0): es solo telemetria.

Para cablearlo (lo decide el USUARIO — toca settings.json GLOBAL, afecta sesiones en caliente):
  "hooks": {
    "PreToolUse": [
      { "matcher": "Skill",
        "hooks": [ { "type": "command",
          "command": "py ~\\\\.cerebro\\\\hooks\\\\skill_dispatch_hook.py" } ] }
    ]
  }
El campo 'correcta' queda null (pendiente de anotar a mano). Falsos negativos: anotar al cierre
con `cerebro_skill_dispatch.py miss <skill>`.
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main():
    try:
        try:
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        raw = sys.stdin.read()
        ev = json.loads(raw) if raw.strip() else {}
    except Exception:
        return  # nunca romper el flujo del usuario
    # El payload de PreToolUse trae tool_name y tool_input. La skill viene en tool_input.skill
    # (o .name segun version). Tomamos lo que haya sin asumir esquema rigido.
    ti = ev.get("tool_input") or {}
    skill = ti.get("skill") or ti.get("name") or ti.get("skill_name") or "?"
    tarea = ev.get("prompt") or ti.get("args") or ""
    try:
        from cerebro_skill_dispatch import log_disparo
        log_disparo(str(skill), str(tarea))
    except Exception:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)  # PreToolUse: exit 0 = permitir (no bloquea jamas)
