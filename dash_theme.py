"""Tema visual COMPARTIDO de todos los dashboards del cerebro (paleta clara tipo Kaggle).

Fuente unica de la identidad visual: blanco, acento cian, bordes gris suave, fuente Figtree +
DM Mono. Lo importan los paneles (tu-proyecto-agente train_dashboard, hub, etc.) para verse IGUAL:

    import sys; sys.path.insert(0, r"~\\.cerebro")
    import dash_theme
    ... f"{dash_theme.FONTS}<style>{dash_theme.CSS}</style>" ...
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&'
         'family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">')

# Paleta canonica (mantener en sync con el hub).
TOKENS = """
 :root{color-scheme:light;
   --bg:#ffffff; --soft:#f7f9fb; --line:#e6e8ec; --line2:#eef1f4;
   --txt:#1b1f24; --mut:#5f6772; --mut2:#8a929c;
   --accent:#20beff; --accent-ink:#0a97d6; --accent-soft:#e7f7ff;
   --green:#1ea672; --amber:#e8a33d; --red:#e5484d; --idle:#c2c8d0;
   --body:'Figtree',-apple-system,Segoe UI,sans-serif; --mono:'DM Mono',ui-monospace,monospace}
"""

# Base + componentes comunes a todos los paneles (tarjetas, KPIs, chips, badges, log, barra, curva).
CSS = TOKENS + """
 *{box-sizing:border-box}
 html,body{margin:0}
 body{background:var(--bg);color:var(--txt);font-family:var(--body);font-size:15px;line-height:1.5;
   -webkit-font-smoothing:antialiased}
 a{color:var(--accent-ink);text-decoration:none}
 .wrap{max-width:920px;margin:0 auto;padding:28px 22px 56px}
 h1{font-weight:700;letter-spacing:-.02em;margin:0;font-size:clamp(22px,3.4vw,30px)}
 .sub{color:var(--mut);font-size:14px;margin-top:6px}
 .muted{color:var(--mut);font-size:13px}

 .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0}
 .kpi{position:relative;background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:14px 16px;overflow:hidden}
 .kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--c,var(--accent))}
 .kpi .k{color:var(--mut);font-size:12.5px;font-weight:500} .kpi .h{color:var(--mut2);font-size:11px;margin-top:1px}
 .kpi .v{font-size:26px;font-weight:700;margin-top:6px;letter-spacing:-.01em;color:var(--txt)}

 .card{background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:16px}
 .chip{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);border-radius:999px;
   padding:5px 12px;font-size:13px;color:var(--mut);background:var(--bg)}
 .chip b{color:var(--txt);font-weight:700}
 .badge{font-size:11px;font-weight:600;padding:3px 9px;border-radius:999px;background:var(--soft);color:var(--mut)}
 .badge.s1{background:#e7f8ef;color:#0f8a55} .badge.s2{background:#fdf1de;color:#b9772a} .badge.s1opt{background:var(--accent-soft);color:var(--accent-ink)}
 .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--idle);flex:0 0 auto}
 .dot.run,.dot.on{background:var(--green);box-shadow:0 0 0 3px color-mix(in srgb,var(--green) 22%,transparent)}
 .dot.done{background:var(--accent)} .dot.error{background:var(--red)}

 .bar{height:9px;background:var(--soft);border:1px solid var(--line);border-radius:999px;overflow:hidden;margin:4px 0 18px}
 .bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),#7bd9ff);width:0%;transition:width .4s ease}
 .chart{background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:14px}
 svg{width:100%;height:230px;display:block}

 .section{margin-top:24px}
 .section h2{font-size:13px;font-weight:600;color:var(--txt);margin:0 0 3px}
 .section .hint{color:var(--mut2);font-size:12px;margin:0 0 10px}
 .log{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--bg)}
 .log .it{font-size:13.5px;padding:10px 14px;border-bottom:1px solid var(--line2);display:flex;gap:12px;align-items:baseline}
 .log .it:last-child{border-bottom:0} .log .it:nth-child(even){background:var(--soft)}
 .log .it time{color:var(--mut2);font-size:12px;font-family:var(--mono);flex:0 0 auto}
"""

# --- Tema OSCURO (suave, limpio, no agresivo) — se activa con <html data-theme="dark"> ---
DARK = """
 :root[data-theme="dark"]{
   --bg:#0f1419; --soft:#161c24; --line:#262d38; --line2:#1d2530;
   --txt:#e7ebf1; --mut:#9aa4b2; --mut2:#6c7682;
   --accent:#38c7ff; --accent-ink:#8bdcff; --accent-soft:#10303d;
   --green:#3fb98a; --amber:#e3ad45; --red:#f0676b; --idle:#39424f}
 :root[data-theme="dark"] .badge.s1{background:#10301f;color:#5fd39b}
 :root[data-theme="dark"] .badge.s2{background:#33260f;color:#e3ad55}
 :root[data-theme="dark"] .badge.s1opt{background:#10303d;color:#8bdcff}
 :root[data-theme="dark"] img,:root[data-theme="dark"] iframe{filter:none}
"""

# --- Panel de CONFIGURACION compartido (gear + opciones). Usa fallbacks para servir
#     tanto a los paneles dash_theme (--accent) como a tu-tienda (--teal). ---
SETTINGS_CSS = """
 .gearbtn{position:fixed;top:14px;right:16px;z-index:60;width:38px;height:38px;border-radius:10px;
   border:1px solid var(--line);background:var(--bg);color:var(--mut,var(--dim));cursor:pointer;font-size:17px;
   display:flex;align-items:center;justify-content:center;box-shadow:0 2px 12px rgba(0,0,0,.10)}
 .gearbtn:hover{color:var(--txt,var(--ink));border-color:var(--accent,var(--teal))}
 .setpanel{position:fixed;top:60px;right:16px;z-index:60;width:248px;background:var(--bg);
   border:1px solid var(--line);border-radius:14px;padding:15px;box-shadow:0 16px 50px rgba(0,0,0,.22);
   display:none;font-family:var(--body,inherit)}
 .setpanel.open{display:block}
 .setpanel h3{font-size:13.5px;margin:0 0 12px;font-weight:700;color:var(--txt,var(--ink))}
 .setrow{margin-bottom:14px} .setrow:last-child{margin-bottom:0}
 .setrow .lab{font-size:12px;color:var(--mut,var(--dim));margin-bottom:7px}
 .seg{display:flex;border:1px solid var(--line);border-radius:9px;overflow:hidden}
 .seg button{flex:1;border:0;background:var(--bg);color:var(--mut,var(--dim));padding:7px 0;font-size:12.5px;
   cursor:pointer;font-family:inherit;border-left:1px solid var(--line)}
 .seg button:first-child{border-left:0}
 .seg button.on{background:var(--accent-soft,var(--inset));color:var(--accent-ink,var(--teal));font-weight:600}
 .tog{display:flex;align-items:center;justify-content:space-between}
 .sw{width:40px;height:22px;border-radius:999px;background:var(--line);position:relative;cursor:pointer;transition:background .2s;flex:0 0 auto}
 .sw.on{background:var(--accent,var(--teal))} .sw i{position:absolute;top:2px;left:2px;width:18px;height:18px;border-radius:50%;background:#fff;transition:left .2s}
 .sw.on i{left:20px}
 .reduce-motion *{animation:none!important;transition:none!important}
"""

SETTINGS_HTML = """
 <button class="gearbtn" id="gear" title="Configuración" aria-label="Configuración">⚙</button>
 <div class="setpanel" id="setpanel">
   <h3>Configuración</h3>
   <div class="setrow"><div class="lab">Tema</div>
     <div class="seg" id="seg-theme"><button data-v="light">Claro</button><button data-v="dark">Oscuro</button><button data-v="auto">Auto</button></div></div>
   <div class="setrow"><div class="lab">Actualizar cada</div>
     <div class="seg" id="seg-refresh"><button data-v="1500">1.5s</button><button data-v="3000">3s</button><button data-v="10000">10s</button><button data-v="0">⏸</button></div></div>
   <div class="setrow tog"><div class="lab" style="margin:0">Reducir animaciones</div><div class="sw" id="sw-motion"><i></i></div></div>
 </div>
"""

# JS generico: tema (claro/oscuro/auto), frecuencia de refresco y reducir-animaciones.
# Persiste en localStorage; respeta ?theme=/?refresh= de la URL (para iframes embebidos).
SETTINGS_JS = """
(function(){
 var LS=window.localStorage;
 var def={theme:'light',refresh:'1500',motion:'0'};
 function get(k){ var s=LS&&LS.getItem('dash_'+k); return (s!=null?s:def[k]); }
 function resolveTheme(){ var t=get('theme'); if(t==='auto'){ t=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'; } return t; }
 function applyTheme(){ document.documentElement.setAttribute('data-theme', resolveTheme()); }
 function applyMotion(){ document.documentElement.classList.toggle('reduce-motion', get('motion')==='1'); }
 window.dashTheme=resolveTheme;
 var timer=null, fn=null;
 window.dashTick=function(f){ fn=f; try{f();}catch(e){} reschedule(); };
 function reschedule(){ if(timer)clearInterval(timer); var ms=parseInt(get('refresh'))||0; if(ms>0&&fn)timer=setInterval(fn,ms); }
 function wireSeg(id,key,after){ var seg=document.getElementById(id); if(!seg)return;
   Array.prototype.forEach.call(seg.children,function(b){ if(b.dataset.v===get(key))b.classList.add('on');
     b.onclick=function(){ if(LS)LS.setItem('dash_'+key,b.dataset.v);
       Array.prototype.forEach.call(seg.children,function(x){x.classList.remove('on');}); b.classList.add('on'); if(after)after(); }; }); }
 function init(){
   var gear=document.getElementById('gear'), panel=document.getElementById('setpanel');
   if(gear&&panel){ gear.onclick=function(e){ e.stopPropagation(); panel.classList.toggle('open'); };
     document.addEventListener('click',function(e){ if(!panel.contains(e.target)&&e.target!==gear)panel.classList.remove('open'); }); }
   wireSeg('seg-theme','theme',applyTheme); wireSeg('seg-refresh','refresh',reschedule);
   var sw=document.getElementById('sw-motion'); if(sw){ if(get('motion')==='1')sw.classList.add('on');
     sw.onclick=function(){ var v=sw.classList.toggle('on')?'1':'0'; if(LS)LS.setItem('dash_motion',v); applyMotion(); }; }
   try{ matchMedia('(prefers-color-scheme:dark)').addEventListener('change',applyTheme); }catch(e){}
 }
 applyTheme(); applyMotion();
 if(document.readyState!=='loading') init(); else document.addEventListener('DOMContentLoaded',init);
})();
"""

CSS = CSS + DARK + SETTINGS_CSS
