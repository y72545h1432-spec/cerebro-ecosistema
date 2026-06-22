---
name: video-editing
description: Pro video editing knowledge distilled from 7 specialist YouTube channels (~500 transcripts). Use when editing or directing any video edit — Shorts/Reels/TikTok, YouTube, ads, documentary style — or when asked about retention, storytelling, hooks, pacing, cuts, captions/subtítulos, motion/smoothness, keyframes/easing, transitions, sound design, music selection, color grading, CapCut/Premiere/After Effects technique, or making a video "más adictivo/dinámico/profesional". Also for reviewing/critiquing an edit. Complements `video-marca` (tu-tienda pipeline) and `hyperframes` (motion graphics by code). NOT FOR shooting/lighting/camera craft (use produccion-audiovisual) nor tu-tienda-branded video (use video-marca).
---

# Video Editing — conocimiento destilado (7 canales, ~2M palabras)

**Fuentes**: @diego-hh (narrativa/sonido/color) · @MattLoui (CapCut pro/documental) · @EricReche (edición adictiva) · @MirkoVigna (recursos visuales/errores) · @Jhonvargasaudiovisual (edición dinámica CapCut) · @viegasestudio (workflow Premiere/AE) · @RBGEscuela (audiovisual/growth orgánico).
**Profundizar**: notas por canal en `~\tu-tienda\_archivos_trabajo\_skill_notes\*.md`; transcripts completos en `_archivos_trabajo\<canal>\<videoid>.txt` (mapa id→título en `_archivos_trabajo\_titles_<canal>.txt`). Lee el transcript original cuando necesites el paso a paso exacto de una técnica.

## 1 · Filosofía (decide antes de tocar la timeline)

- **El sonido mata el visual (80/20)**: visual pobre + gran sonido > gran visual + sonido pobre. El sonido obliga a imaginar; el espectador "ve" lo que oye. Prioriza sonido sobre animaciones complejas.
- **La estética mata la técnica**: estética = *aisthesis* = percepción → "marco sensorial coherente que provoca un estado". Define la estética del video ANTES (cozy, dramática, premium, divertida) y que TODO (b-roll, tipografía, color, música) la cumpla. Simple+coherente > complejo+incoherente.
- **Edita con intención, no con efectos**: amateur pregunta "¿qué se ve cool?"; pro pregunta "¿qué debe SENTIR la audiencia aquí?". Cada zoom/corte/caption/sonido sirve a claridad, emoción o retención. Si no puedes explicar por qué algo está, quítalo. "Editing isn't decoration, it's direction."
- **La edición debe ser invisible**: el espectador no debe notarla, debe fluir con ella. Si nota el SFX o el cambio de canción, estaba alto o fuera de lugar. (Romperla a propósito, con moderación, despierta.)
- **Elige el camino según el espectador**: ¿busca compañía/cercanía (edición mínima: solo silencios fuera) o dopamina/estímulo (producción densa)? Sobre-editar el primero lo EMPEORA. No hay fórmula universal.
- **Corta 20% más de lo cómodo**: pausa→fuera, repetición→fuera, punto que "medio importa"→fuera. La mayoría de videos sobran 15-25%.

## 2 · Storytelling y retención

- **Curvas narrativas**: Y=intensidad emocional, X=tiempo. Plano = abandono aunque la info sea buena. Video educativo: pico en el gancho + **micro-curvas** que se reinician en cada sección/idea. El guion da la información; **la edición construye la curva emocional** (sobre todo vía sonido).
- **TNE (tensión narrativa estratégica)** — Hitchcock: "no hay terror en la explosión, solo en su anticipación". Aviso de bomba → espacio de anticipación (tensión creciente) → explosión (o cliffhanger). Error común: aviso→explosión inmediata (didáctico, 0 emoción).
- **Brecha de información**: una pregunta sin respuesta crea un vacío que el cerebro NECESITA cerrar → detiene el scroll. Abre loops ("el último punto al final") y decide conscientemente cuándo revelar/ocultar.
- El cerebro está cableado para historias: historia = activa corteza auditiva + visual + motora + amígdala → memoria. "Recordarán el video que los hizo sentir más."
- **Estructura redes**: hook-problema → desarrollo-solución (con objeciones que re-abren tensión) → CTA. En YouTube igual, con gancho de ~1 min.

## 3 · Pacing y ritmo

- **Pacing = contraste**: cortes rápidos = urgencia; largos = peso/respiro. Si todo es rápido, nada es rápido. Patrón MrBeast: intro de alta frecuencia → medio más lento (stakes) → final acelera. Pregunta clave: ¿dónde respira y dónde golpea?
- **Ritmo interno del plano**: el dinamismo viene del movimiento DENTRO de la toma (timelapse vs slow-mo), no de meter más cortes. 1-2 tomas con movimiento interno > 10 cortes lentos con música rápida.
- **Jump cuts**: corta entre FRASES, no dentro de una oración. Aprieta los cortes (mínimo silencio = dinámico) pero deja terminar las palabras (la "s" final se corta fácil → crossfade/constant power en el corte de audio).
- **No interrumpas un plano solo por entretener**: si 10 s de A-roll son interesantes, déjalos y dinamiza barato (zoom sutil, reposición, datos al lado, wiggle).
- Speed ramps: solo con propósito narrativo (producto/lugar dinámico). Nunca cámara rápida sobre alguien caminando.

## 4 · Motion y smoothness (lo que separa pro de amateur)

1. **Easing SIEMPRE**: keyframe lineal = amateur. CapCut: clic-derecho keyframe → easing, o animación variable → curva (en scale, X e Y). Para escenas: cubic ease en todos.
2. **Motion blur en toda animación** (texto, zooms, gráficos): compound clip → video → motion blur. Nítido en movimiento = falso; con blur = cinemático (lo hace el equipo de MrBeast).
3. **Eye-line consistente**: en jump cuts, guía horizontal sobre los ojos y reposiciona el clip B → corte invisible. Generalizado: minimiza saltos del foco de atención (ojos→texto abajo = fricción); cubre cambios de foco con transición.
4. **Track-in sutil** en talking heads (zoom leve inicio→fin, manteniendo eye-line): imperceptible pero "se siente".
5. **Dirección de movimiento consistente**: plano que va izq→der seguido de otro izq→der = fluidez subconsciente (Occidente lee izq→der = avance natural).
6. **Crossfade de audio 1-2 frames** en cada corte (mata pops).
7. **Micro-detalles** (se acumulan): título que invade el shot siguiente, audio residual, música sin ducking, clip rotado con bordes negros (zoom ~107%), texto fuera de safe margins.

## 5 · Captions / subtítulos

- Son refuerzo, no sustituto de animar: úsalos en intro, frase clave o palabra concreta. Abusar = "editor vago".
- **Estilo viral (CapCut)**: fuente Inter (medium/bold), sombra suave (opacidad baja+blur+distancia), animaciones de aparición SUTILES (las bruscas son feas), **asimetrías** (2-3 líneas con tamaños/pesos distintos), efecto brillo, máscara "dividir" difuminada como sombra. Palabra-a-palabra: una caja + corte por palabra → compound.
- Estilo Hormozi/smooth captions: ver matt_loui [iHiaHsXacWg, EQUyZC_cd0s, YddyvmAFxnY]. Captions quemados suben retención en mudo.

## 6 · Texto y motion graphics

- **Fuentes pro**: Special Elite, Times New Roman, Helvetica Black Condensed, Inter; identifica fuentes ajenas con WhatTheFont. Animaciones de texto a **1.5-2 s** (lento = cinematográfico/documental).
- **Recursos visuales (taxonomía Mirko)** — variar SIEMPRE: textos (contexto/tiempo/énfasis/estructura/explicativos), B-roll planificado por frase del guion (shot list, no al azar), iconos (conteo estilo MrBeast, flechas/círculos para enfocar; PNG transparente), imágenes (históricas/referencia/capturas/antes-después), GIFs de meme (humor=carisma), animaciones (conceptos difíciles).
- **Guiar la atención en una imagen (6 vías)**: resaltar/subrayar · oscurecer/desenfocar el fondo · color emocional (rojo=mal, verde=bien/dinero) · flechas/círculos · glow (Deep Glow) · que se vea bien (grading+viñeta+partículas+aberración).
- **A-roll vs B-roll vs stock vs animación**: B-roll propio casi siempre gana para explicar; stock = último recurso (genérico, impersonal; Pexels); animación = lo más premium para conceptos clave.

## 7 · Transiciones y efectos

- Regla de oro: **si algo aparece en pantalla, un SFX explica cómo llegó** (whoosh/pop/shutter).
- Prefiere transiciones **in-camera** (pasada de mano, tapar lente, movimiento) y sutiles (blur por ENCIMA del clip con keyframe que lo disuelve, shake+iluminación, máscara, zoom-out) sobre presets glitch de un clic.
- Tensión: B/N con keyframes en la frase dura, textura vintage, modificador de voz en una palabra, espacio en negro + SFX.
- **Documental (Johnny Harris/Vox) en CapCut**: switch-focus (2 imágenes recortadas + blur cruzado + parallax del fondo), on-screen research (screen recording + blend + timelapse + riser), framing de archivo (Film Frame 2 + −saturación + particles/fade 50), pantallas "Netflix" (textura glass de texturelabs.org + color burn ~39%), escenas 3D con compound+cubic ease+paste attributes atenuado al fondo. Paso a paso: matt_loui [fUkGGnsuDPQ].

## 8 · Sound design (el 50% de la calidad percibida)

- **Diseña el sonido PRIMERO** (tras los cortes): la música dicta estructura/secciones/moods; el visual la complementa. Proceso diego: duplicar secuencia → **seccionar por colores** (problema/transición/solución/objeción/CTA) → música por sección creando picos (drop de la canción = revelación) → recién entonces b-roll/gráficos.
- **Jerarquía**: diálogo > música > ambientes > SFX. Niveles guía: voz −6..−12 dB, música −18..−25, ambientes −20..−30, SFX −10..−20. Ducking siempre; EQ: recorta de la música los medios que compiten con la voz en vez de solo bajarla.
- **El silencio es un arma**: cortar la música rompe la monotonía y devuelve el 100% de la atención; anticipa explosiones; fade-out = "esto acaba, viene algo".
- **SFX**: capas por frecuencia (grave+medio+agudo en un mismo hit); biblioteca propia (no sonidos de reels); cada sonido tiene función (anticipar/enfatizar/mover/verosimilitud); modifícalos (pitch/velocidad/EQ/reverb); busca por la ACCIÓN no el objeto (insertar USB = clip de pistola). Invisibles que manipulan emoción: **risers** (anticipación), **booms** (liberación/impacto), **drones** (misterio).
- **Música**: bloques por emoción (colores en timeline); stems para mutear pistas; usa la forma de onda (sección estrecha=explicar, onda grande=épico); environmentaliza (efecto vinyl/radio cuando la escena entra a un interior). Mezcla final: probar en audífonos + bocinas + altavoz del teléfono.
- Voz: micro cerca de la boca al grabar + EQ paramétrico con realce vocal; NO abusar de noise reduction (voz "gelatinosa").

## 9 · Color

- **Flujo diego (gratis)**: clip crudo → DaVinci Resolve → export H.265 4K → editar el "graded" en tu editor. Grabar log/10-bit si se puede. Entorno neutro (sin RGB).
- **7 nodos**: (1) CC base: negros a 0, contraste/saturación (juzgar en B/N); (2) piel: qualifier + vectorscopio (línea skin-tone; ligeramente rojizo = vivo); (3) suavizado piel: máscara + mid-tone detail ~−60; (4) fondo: Hue vs Sat/Hue/Lum (ej. azul→teal) sin tocar piel; (5) acentos con máscaras (contraste cálido/frío); (6) viñeta (máscara invertida, −exposición) + blur radial; (7) final: contraste/sat + **sharpen ~0.48** (compensa compresión de YouTube). Split-tone: sombras al azul.
- En CapCut: LUTs (puedes generarlas con Claude: prompt → .cube → adjustment→LUT→import, intensidad ~50%) + HSL en adjustment layer para unificar imágenes dispares.

## 10 · IA en el flujo de edición

- **Claude + editor**: generar LUTs .cube por prompt; .SRT de números contando (counter premium: arrastrar → estilizar → compound → speed 10×); **motion graphics por código** (Matt usa Claude Code+Remotion; aquí usar **HyperFrames** — mismo patrón). Prompting: terminar con "ask clarifying questions", dar valores numéricos a los cambios, pedir fondo transparente para overlay.
- **Imagen/video IA**: Artlist AI Studio (Framing: personaje+localización+luz+plano; Directing: imagen→video con movimiento de cámara), modelos: Nano Banana Pro (imagen), Kling 2.6/3.0 (video). Avatar propio: 5 fotos → prompt descriptivo (ChatGPT/Claude) → referencia. Dreamina (ByteDance) fusiona hasta 6 imágenes (mapas estilo Johnny Harris).
- **Pipeline de edición 100% automatizada (Brendan)**: (1) Descript para cortes (template "remove repeating sentences, keep the last one" + shorten word gaps a 0.2 s, revisar como documento) + música; (2) Claude Code + Remotion: ffmpeg extrae audio → Whisper transcribe con timestamps → mapea gráficos al transcript → genera animaciones → preview en Remotion Studio → render. "Here is a new video, please edit this." Transcript: brendan [G0EH0xdy2-E]; ver skill `ia-aplicada` §6.
- Regla: la IA genera el RECURSO; el sentido lo da la edición (música acorde + SFX que hagan match).
- ⚠️ IG/FB premian originalidad y etiquetan IA: usar IA para representar lo no grabable, no para inundar.

## 11 · Workflow y velocidad

- **Sistema, no heroísmo**: biblioteca propia (sonidos/música/overlays/transiciones), estructura de carpetas replicable (footage/stock/música/SFX/gráficos/proyectos), **templates propios** de textos y pantallas → velocidad + identidad de marca (repetir pantallas está BIEN).
- Duplicar secuencias por etapa (01 cortes → 02 sonido → …) para poder volver atrás.
- Premiere/AE stack (viegas): Animation/Premiere Composer (Mr. Horse), Copy Pasta (navegador→timeline), AEJuice, aescripts (True Comp Duplicator = duplicar precomps sin enlazar), PowerToys always-on-top, atajos custom. Premiere=montaje/sonido, AE=animación (Dynamic Link).
- Cortes rápidos guiándote por la forma de onda del audio (los errores se ven).

## 12 · Distribución orgánica (bonus RBG)

- 1 reel/día×3 meses = +370k: IG mayor alcance; TikTok mejor ratio visita→seguidor; **YouTube Shorts NO funciona como Reels/TikTok** (mismo video: 32k vs 40M); YouTube largo = vínculo y conversión por usuario muy superiores. Virales = metáforas físicas simples de 8-9 s. Comunidades de difusión IG retienen. Métricas: Metricool.

## Aplicación a tu-tienda short-form

- Usar con la skill `video-marca` (pipeline) y `hyperframes` (motion graphics): este documento aporta el CRITERIO (curvas, TNE, sonido primero, smoothness, captions, color).
- Para producto: hook = brecha de información sobre el beneficio (no el producto); ritmo interno alto en demos; sound design sensorial (ASMR del producto); micro-curvas cada 3-5 s en vertical; CTA tras pico emocional; estética cozy coherente con la marca (cálidos, luz ambiente) definida ANTES.

## Índice tema → fuente (transcripts exactos)

| Tema | Canal/video |
|---|---|
| Sonido>visual, estética>técnica | diego [T9OqS7xgkaA] |
| 7 errores (ritmo interno, dirección, composición, jerarquía sonora…) | diego [rv4_1UNtmkE] |
| Curvas narrativas + narrativa sonora paso a paso | diego [djb09e2Y6L4] |
| TNE/anticipación, brecha de información, cerebro | diego [iKiuMxe6Yns] |
| 8 reglas sound design | diego [9dfkQlHyQDg] |
| Sistema de color 7 nodos DaVinci | diego [vAGlRCBt4CQ] |
| 7 hábitos pro CapCut (smoothness, motion blur, pacing, ruthless cut, micro-detalles) | matt [Ykc6v0oTLRs] |
| 6 técnicas documental (Johnny Harris/Vox) | matt [fUkGGnsuDPQ] |
| Sound design sensorial CapCut (ticking, break&pacing, ASMR, environmentalización) | matt [eDuEd5TMjSQ] |
| Claude+CapCut (LUTs, SRT counters, Remotion) | matt [8oIFBQ9BhVU] |
| Fórmula 4 pasos edición adictiva (camino, variedad, continuidad, sonido) | eric [nl6gn_JZ29w] |
| Recursos visuales (taxonomía) + IA Artlist | mirko [JSKRB3wQmyU] |
| 9 errores que te frenan | mirko [Qx-ZsbtlBzY] |
| Edición dinámica CapCut completa (subtítulos virales, esquemas) | jhon [8PXsg_SdkEQ] |
| Editar 200% más rápido PR/AE (plugins/scripts) | viegas [XgImNp6cjUA] |
| Growth orgánico reels (1/día×3 meses) | rbg [qqI5MKVrsA0] |
| Edición automatizada Descript+Claude Code+Remotion | brendan [G0EH0xdy2-E, 3hzXfTjqiKg] (carpeta `<canal-cliente-2>\`) |

## Canales adicionales (biblioteca consultable, carpetas en `_archivos_trabajo\`)

- **@Joeyedits_** (`joeyedits`, ~125 vids): CapCut PC a fondo — efectos estilo After Effects SIN AE [1XOkK2wxCP8, TzcLO2X1zwg], 40 trucos beginner→pro [gz7kzp1EXR8], graph editor [km1_lRYHjI8], compound clips [4hKvkM82hw0], keyframing [DI-ziBV87Ho], **Claude+CapCut god mode [Ht_RxaXqBnc] y Codex+CapCut 7 tricks [wFjEGB8gdPM]**, mapas animados [T5Je2kkh7uI], text match cut estilo Vox/Johnny Harris [7Ynggiy8_m8], color grading en CapCut [kCvbnf3IFRc], series "editar como X": MagnatesMedia (4 partes) / Iman Gadzhi / Ali Abdaal / Vox / Dhruv Rathee / Devin Jatho, edición de hooks [5n4pQCQouDE], 7 cortes esenciales [YLzbwWumNe0].
- **@NaughtyyJuan** (`naughtyyjuan`, 59): After Effects — animaciones Apple-style UI/shape morphing [y5Q-AhxPh9A, 5j4HmfgPCDI], 3D camera/tracking [3sxjU3tZl4M, O1pAc2hte1Q], graph editor AE [7kTXWbJZNGI], "por qué tus edits se ven baratos" [aLybC9zYGAQ], edits que se ven caros [i_G9pE89jD8], negocio editor ($50→$900/cliente) [6KRdXW0LE7o].
- **@tarikvideoeditor** (`tarik`, 15): short-form viral en AE — SaaS animations [IBrgDq_96vA, EicGPYk7cFc], reels animados/motion graphics [PrEdG3pX44I, 39WkSrZSZ7A], Iman Gadzhi 3D [RnT0Uqet8K8], Apple UI [vTjsCkAnjZ8], Vox style [ads_xuXsFs0].
- **@finzar** (`finzar`, 98): comparativas de software (mejor editor 2026 [ZI-L1eVMGu4], todo software gratis [1To8rUm2do8, E2n5ZjWZS-M]), cómo animar 2026 [RutTgrCATwk], guía editar YouTube 2026 [xmfSCKV7qUE], dinero editando [2QPpIl0_ZbE].
- **@josephvideoediting** (`josephvideoediting`, 84): reels virales en Premiere [MNG51L8ikQw], talking-head IG 2026 [HQvV75kjblY], subtítulos virales PR [8qVVSHjEbxc], documental cinemático AE [ucCO_QAHisk], **Claude editó mi video completo [uyN-nAEuIjw], reels con Claude [LAHAcxbhNgE], editor pro vs IA [PfGd2djacE0]**, guía short-form 2026 [ds7DDgGgiVs].
- **@CaseyFaris** (`caseyfaris`, 387): LA referencia de **DaVinci Resolve y color** — curso completo Resolve 21 [gjxiH2Tm4JE], por qué tus grades no matchean [4xbOws9Cnp4], qué es un "look" [xGoBcesIHqk], color grading sin estrés [OqweEQ8bZg0], organización de timeline [fUcA8r5h4EQ].
- **@GakuLange** (`gaku_lange`, ~150): transiciones creativas/interactivas (kick/toss/tap/whip pan/dolly ramp/barrel) [Fra5BEhpOFQ, 6mUPfKf_r3g, yzRFA0wyZjY, nWhQZAxUlkE], speed ramps suaves [qk2kwQoHTVY, lVYQkejspR8], **RADIO EDIT destilado [35vM3GjK7n0]** (leído 2026-06-10; "me ahorró cientos de horas"): editar partiendo del AUDIO, nunca de lo visual — flujo: (1) colocar la música y marcar (tecla M) los 3-4 cambios de ritmo → secciones; (2) poner risers/whooshes/impactos en cada transición ANTES de mirar un solo clip (los SFX actúan de placeholders del ritmo); (3) rellenar cada sección con clips relacionados entre sí, sincronizados al beat; (4) recién al final, transiciones visuales finas (flash de cámara, etc.) y ajuste. En videos hablados: diseñar la música para que el beat-drop caiga en los primeros 4s (el hook) y usar las PAUSAS del voiceover como puntos de transición/b-roll. Para transiciones novedosas: describirle el concepto a Claude y pedir variaciones creativas. → tu-tienda: aplicar en video-marca — música y marcadores primero, capas visuales después, 9 secretos de sound design [PIBj2y029_k], 5 efectos de voiceover [woH7KNE4pQM], fórmula 6 clips para intros cinemáticas [ktzPven4QVc], por qué tus edits se sienten choppy [EWqrpI1IAyI], color vibrante [7imay44H3_Q], Premiere/Resolve hacks [oWEKtTSTJu4, 3J4mX83LhUY].

Más temas: buscar el título en `_archivos_trabajo\_titles_<canal>.txt` y leer `_archivos_trabajo\<canal>\<videoid>.txt`.
