# Portal al reloj · Documento de diseño

_Última actualización: 3 nov 2026_

## Objetivo
Una app propia de Wear OS ("Portal") para el Samsung Galaxy Watch9 de 40 mm que muestra HTML (juegos, paneles y utilidades) generado por el bot.

## Dispositivo
- Samsung Galaxy Watch9 40 mm (SM-L340), pantalla redonda de 1,3" (34 mm) y 438×438 px.
- Móvil: Galaxy S25. Los diseños se prueban primero en el móvil con el simulador.
- Estado: el reloj aún no ha llegado.

## Arquitectura
1. **App Portal (APK):** WebView a pantalla completa con JS, localStorage y pantalla siempre encendida.
   - Para recargar: botón abajo o toque con dos dedos.
   - Compilada: `Portal-debug.apk` (compileSdk 36, minSdk 30).
   - La URL se cambia con `-PportalUrl=...`.
2. **Hosting:** GitHub Pages, rama `main`, carpeta `docs/`. URL: `https://ganjaflay.github.io/Watch-portal/`. En el repo hay que dejar Pages en «Deploy from a branch → main / docs» (a 3 nov 2026 el sitio aún no estaba activado).
3. **Instalación:** ADB por Wi-Fi, o Bugjaeger / Wear Installer 2 desde el S25. Los pasos están en `README.md`.
4. **Simulador:** cada diseño tiene una versión `simulador-*.html` con fondo blanco y el reloj en el centro, más un botón de "Tamaño real".

## Plantillas, no rediseños
- Cada diseño es una plantilla fija. Para actualizar solo se meten datos nuevos y nunca se rehace desde cero, salvo que se pida explícitamente.
- Los datos van **incrustados en el HTML** (snapshot estático), sin conexión en el dispositivo. La versión con datos en vivo no conectaba en el móvil.
- El código de las plantillas está en `docs/` (lo que publica Pages) y los scripts de generación en `docs/src/`. La guía de cada una está en `plantillas/<nombre>/PLANTILLA.md`, fuera del sitio, para que las URLs del reloj sigan siendo cortas.

## Estilo visual
- Minimalista, sobre fondo negro, con turquesa Tiffany (#0ABAB5 / #81D8D0) y la tipografía fina Outfit.
- Motivo fumeta/420 sutil (hoja de línea fina). **Nada de colores rasta.**
- Contenido dentro de la zona segura circular (~85 % del diámetro).
- Tocar la esfera cambia de tema o de vista; la elección se guarda en localStorage.
- Modo 4:20 (a las 4:20 y 16:20): efecto discreto extra.

## Diseños hechos
| Diseño | Archivos | Notas |
|---|---|---|
| Reloj fumeta | `reloj-fumeta.html`, `simulador-reloj-fumeta.html` | Anillo de segundos, hoja, humo, 3 temas |
| Lluvia de hojas | `reloj-lluvia-hojas.html`, `simulador-lluvia-hojas.html` | 18 hojas cayendo (32 en modo 4:20), sin humo |
| Bitcoin (en vivo) | `bitcoin.html`, `simulador-bitcoin.html` | CoinGecko con Binance de respaldo; no conecta en el móvil |
| Bitcoin (estático) | `bitcoin-estatico.html`, `simulador-bitcoin-estatico.html` | Datos incrustados. Para actualizar, desde la raíz del repo: `python3 docs/src/build_bitcoin_static.py` |

## Monetización (conclusiones)
- **Esferas para tiendas:** obligatorio Watch Face Format (XML, sin código), empaquetado en `.aab`. Se crean con Watch Face Studio (Samsung) o escribiendo el XML a mano.
- **Animaciones en WFF:** limitadas (transformaciones ligadas a la hora o a sensores, secuencias de imágenes o AVIF). No admite física ni aleatoriedad real.
- **Esferas nativas en Kotlin:** Play ya no las acepta como nuevas. Solo sirven para uso propio.
- **Apps normales (juegos, utilidades, paneles):** Play sí las acepta en Kotlin o con WebView. Para vender, mejor empaquetar el HTML dentro de la app.
- **Tiendas:** Galaxy Store (alta de vendedor gratis, comisión de ~30 %) o Google Play (pago único de 25 $, prueba cerrada para cuentas personales nuevas, comisión de ~15 %).
- **Fiscalidad:** al principio se puede vender como particular y declararlo en la renta. Si se vuelve una actividad habitual, consultar a una gestoría por el alta de autónomo.
- **Tema 420:** lo decorativo suele pasar la revisión; promocionar el consumo puede hacer que la rechacen.

## Pendiente / ideas
- Activar GitHub Pages en el repo (main / docs) y probar la URL en el reloj cuando llegue. El `Portal-debug.apk` del repo sigue llevando la URL vieja de ejemplo; hay que recompilar para que apunte a `https://ganjaflay.github.io/Watch-portal/`.
- Probar la APK en el Watch9 (gesto de atrás, botones físicos).
- Decidir qué otras plantillas de datos hacer (tiempo, otras criptos, agenda, fútbol...).

## Documentación para agentes (decidido 3 nov 2026)
- `AGENTS.md` en la raíz: qué es el proyecto, arquitectura (APK WebView → GitHub Pages), estilo, reglas (plantillas fijas, datos estáticos horneados) y cómo compilar/publicar. Sirve para que cualquier IA o instancia nueva trabaje sin contexto previo.
- Cada plantilla tiene su `plantillas/<nombre>/PLANTILLA.md`, que funciona como una skill: qué datos lleva, qué script los inyecta, cómo actualizar y cómo verificar, sin rediseñar.

## Menú y carpeta del sitio (3 nov 2026)
- Lo que abre el reloj es `docs/index.html`: menú con Reloj fumeta, Lluvia de hojas y Bitcoin estático. Bitcoin en vivo queda como enlace pequeño (no va en el reloj). Los simuladores van en una sección aparte, también pequeña.
- La página de prueba anterior (reloj de sistema, «Portal OK» y contador de taps en localStorage) se sustituyó por ese menú.
- `web/` pasó entero a `docs/` para poder servir Pages desde main / docs. `docs/.nojekyll` vacío. Los scripts de captura ya no apuntan a `portal-watch/web/`: resuelven `docs/` desde su propia ruta.
- `defaultPortalUrl` en `app/build.gradle.kts` es `https://ganjaflay.github.io/Watch-portal/`. El `-PportalUrl` sigue pudiendo pisarlo.

## Idea: pantalla de IA propia (3 nov 2026)
- HTML en el portal con botón de micro y respuesta en texto grande.
- La voz se obtiene con un puente en el APK (Kotlin) usando el dictado de Android, que pasa el texto al JS.
- La clave de la API va en un intermediario (p. ej. Cloudflare Worker), nunca en el HTML público.
- Alternativas existentes: Gemini viene de serie; WristAssist (ChatGPT, de pago) y WristAnswers (gratis) son de terceros.
