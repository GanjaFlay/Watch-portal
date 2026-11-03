# Watch Portal — para quien llega sin contexto

Léete esto entero antes de tocar nada. Después abre la `PLANTILLA.md` del diseño que vayas a cambiar. Si tomas una decisión de diseño, apúntala en `DISENO.md` (fecha corta y qué se decidió).

Proyecto personal de **Nikolay** (GitHub [GanjaFlay](https://github.com/GanjaFlay)). No es un producto de equipo: el criterio de estilo y de «no rehagas esto» es el suyo.

## Qué es

Una app de Wear OS llamada **Portal** (`com.nikolay.portalwatch`) para su Samsung Galaxy Watch9 de 40 mm. La app casi no tiene lógica: es un WebView a pantalla completa que carga una URL fija. Las esferas, los juegos y los paneles son HTML de este repo, servidos por GitHub Pages.

El reloj abre el menú:

`https://ganjaflay.github.io/Watch-portal/`

(la caja del path importa: `Watch-portal`, con esa W y ese guion).

Para cambiar lo que se ve en el reloj se cambia `docs/` y se hace push a `main`. No hace falta recompilar el APK, salvo que cambie la URL o el código Kotlin.

## Reloj: medidas y tacto

- Samsung Galaxy Watch9 **40 mm** (en `DISENO.md` figura el modelo SM-L340). Pantalla **redonda**.
- Las esferas se dibujan a **438×438 px**. En `docs/src/build.py` eso es `W = 438`. Samsung da la pantalla como 1,34" (~34 mm); el simulador usa `DISPLAY_MM = 34`.
- El móvil donde se previsualiza es un **Galaxy S25**. Cada diseño tiene su `simulador-*.html`: fondo blanco, reloj en el centro, botón «Tamaño real». El tamaño real calibra el S25 cuando el user agent es Android y el lado corto de la pantalla cae entre 340 y 460 px: usa `lado_corto / 66` px por mm. En otro sitio cae a milímetros CSS.
- El bisel se come las esquinas. `DISENO.md` pide el contenido importante dentro de una zona circular de unos **85 % del diámetro**. El cuadrado que cabe entero en el círculo lleva un padding de ~14,6 % por lado (`(1 - 1/√2) / 2`); el menú (`docs/index.html`) usa ese padding (`--safe: 14.6vmin`). Las esferas pintan el círculo de 438 y colocan hora y textos hacia el centro, no pegados al borde.
- El dedo en 40 mm no afina. Un toque en la esfera lo maneja la página (cambia de tema o de rango). El borde de abajo lo usa la app para el botón de recarga: un toque en el 18 % inferior de la pantalla (`y` mayor que el 82 % de la altura) lo vuelve a enseñar. No pongas ahí el único control de la página.

## Arquitectura

```
Portal-debug.apk  →  WebView  →  https://ganjaflay.github.io/Watch-portal/
                                      docs/index.html y el resto de HTML
```

App (`app/src/main/java/com/nikolay/portalwatch/MainActivity.kt`):

- JavaScript encendido.
- `localStorage` encendido (`domStorageEnabled`; también `databaseEnabled`).
- Pantalla encendida mientras la app está delante (`FLAG_KEEP_SCREEN_ON`).
- HTTP sin cifrar permitido (`usesCleartextTraffic` en el manifest).
- App Wear independiente (`com.google.android.wearable.standalone` = true). No necesita una app en el móvil para abrirse.
- minSdk 30, compileSdk y targetSdk 36, build-tools 36.0.0. AGP 8.13.0, Kotlin 2.1.21, Java 17, Gradle 8.14.3 (wrapper).
- Caché del WebView: `LOAD_DEFAULT`. Si tras publicar sigues viendo la página vieja, recarga a mano.

La URL vive en un solo sitio, `app/build.gradle.kts`:

```kotlin
val defaultPortalUrl = "https://ganjaflay.github.io/Watch-portal/"
```

Se pisa por build sin editar el archivo: `./gradlew assembleDebug -PportalUrl=https://otra/`.

El `Portal-debug.apk` que está en la raíz (~2,3 MB, pensado para instalarlo desde el móvil) se compiló con la URL vieja `https://example.github.io/watch-portal/`. Cambiar el gradle no reescribe ese APK. Hasta que alguien recompile y reinstale, el reloj sigue abriendo la URL vieja. Esta entrega no recompiló el APK.

Controles (todo en la Activity, no en el HTML):

| Gesto | Qué hace |
|---|---|
| Botón ↻ abajo en el centro (40 dp) | Recarga. Se esconde a los 3 s. |
| Toque en el 18 % inferior | Vuelve a enseñar el botón. |
| Toque con dos dedos | Recarga. |
| Pulsación larga de `KEYCODE_STEM_1`, `_2` o `_3` | Recarga. La pulsación corta solo enseña el botón. La tecla Home no se puede interceptar. |
| Bisel o corona | `window.scrollBy` en la página. |
| Atrás (tecla o gesto) | Historial del WebView; si no hay, cierra la app. |

Si la carga de la página principal falla, la app enseña un HTML de error con enlace Retry. Al volver a primer plano, si seguía fallida, reintenta sola.

## Mapa del repo

```
app/                         módulo Android
  build.gradle.kts           PORTAL_URL
  src/main/                  MainActivity, manifest, cuatro recursos
docs/                        sitio de GitHub Pages (main / docs)
  index.html                 menú que abre el reloj
  reloj-fumeta.html          esfera
  reloj-lluvia-hojas.html    esfera
  bitcoin-estatico.html      panel con datos horneados
  bitcoin.html               panel en vivo, deprecado
  simulador-*.html           vista de móvil de cada diseño
  *-preview.png, lluvia-*.png, simulador-420.png
  src/                       generadores y capturas (no son páginas)
  .nojekyll
plantillas/<nombre>/PLANTILLA.md
Portal-debug.apk             APK de debug ya compilado
DISENO.md                    decisiones. Se sigue escribiendo aquí.
```

Los HTML de las esferas y de los paneles **salen de los scripts** de `docs/src/`. El siguiente build pisa cualquier edición a mano. La excepción es `docs/index.html`: el menú está escrito a mano y no tiene generador.

## Plantillas

| Plantilla | Qué es | Página del reloj | Guía |
|---|---|---|---|
| reloj-fumeta | Esfera con anillo de segundos, hoja, humo, 3 temas, modo 4:20 | `docs/reloj-fumeta.html` | [plantillas/reloj-fumeta/PLANTILLA.md](plantillas/reloj-fumeta/PLANTILLA.md) |
| reloj-lluvia-hojas | La misma esfera, con lluvia de hojas en vez de humo | `docs/reloj-lluvia-hojas.html` | [plantillas/reloj-lluvia-hojas/PLANTILLA.md](plantillas/reloj-lluvia-hojas/PLANTILLA.md) |
| bitcoin | Panel en vivo (CoinGecko, Binance de respaldo). Deprecado: no va en el reloj. Se queda porque el estático se genera a partir de él | `docs/bitcoin.html` | [plantillas/bitcoin/PLANTILLA.md](plantillas/bitcoin/PLANTILLA.md) |
| bitcoin-estatico | El mismo panel con un snapshot horneado. Es el que se usa | `docs/bitcoin-estatico.html` | [plantillas/bitcoin-estatico/PLANTILLA.md](plantillas/bitcoin-estatico/PLANTILLA.md) |

URLs cuando Pages esté sirviendo `main` / `docs` (el prefijo es siempre `https://ganjaflay.github.io/Watch-portal/`):

| | Diseño | Simulador |
|---|---|---|
| Menú | `/` (`docs/index.html`) | — |
| Reloj fumeta | `/reloj-fumeta.html` | `/simulador-reloj-fumeta.html` |
| Lluvia de hojas | `/reloj-lluvia-hojas.html` | `/simulador-lluvia-hojas.html` |
| Bitcoin estático | `/bitcoin-estatico.html` | `/simulador-bitcoin-estatico.html` |
| Bitcoin en vivo | `/bitcoin.html` | `/simulador-bitcoin.html` |

Claves de `localStorage` que ya existen (no inventes otras al lado):

| Clave | Dónde | Valores |
|---|---|---|
| `relojFumetaTheme` | reloj fumeta | `0`, `1`, `2` |
| `relojLluviaTheme` | lluvia de hojas | `0`, `1`, `2` |
| `btcPanelRange` | los dos paneles de bitcoin | `24h`, `7d`, `30d` |
| `btcPanelCache_24h` / `_7d` / `_30d` | solo el bitcoin en vivo | JSON de la última respuesta |

Para previsualizar una hora en las dos esferas: `?t=HH:MM` o `?t=HH:MM:SS`. Ejemplo: `reloj-fumeta.html?t=16:20:25`. El parámetro no existe en los paneles de bitcoin.

## Compilar el APK

Hace falta JDK 17 y el Android SDK con build-tools 36.0.0. `ANDROID_HOME` (o `ANDROID_SDK_ROOT`) tiene que apuntar al SDK. El wrapper baja Gradle 8.14.3.

```bash
./gradlew assembleDebug
./gradlew assembleDebug -PportalUrl=https://ganjaflay.github.io/Watch-portal/
cp app/build/outputs/apk/debug/app-debug.apk Portal-debug.apk
```

`local.properties` no se commitea. El release usa la firma debug y no minifica (`app/build.gradle.kts`).

## Instalarlo

### ADB por Wi-Fi

1. Reloj: Ajustes → Acerca del reloj → Software → toca «Versión de software» 7 veces.
2. Ajustes → Opciones de desarrollador: activa Depuración ADB y Depuración inalámbrica. Misma Wi-Fi que el ordenador.
3. Emparejar dispositivo nuevo. Anota el `ip:puerto` de emparejamiento y el código de 6 dígitos.
4. En el ordenador, con platform-tools:

   ```bash
   adb pair 192.168.1.50:37123        # ip:puerto de emparejar; luego metes el código
   adb connect 192.168.1.50:41234     # ip:puerto de la pantalla de depuración (otro puerto)
   adb install -r Portal-debug.apk
   ```

   Esos números son un ejemplo. Los reales los enseña el reloj.
5. Abre Portal en la lista de apps. Para una versión nueva: `adb connect` y `adb install -r`.

Apaga la depuración inalámbrica al acabar. Gasta batería.

### Desde el Galaxy S25

Los pasos 1–3 del reloj son los mismos. Copia `Portal-debug.apk` al móvil y usa una app de Play Store:

- **Bugjaeger**: empareja (ip:puerto + código), conecta al ip:puerto de depuración, Paquetes → Instalar, elige el APK.
- **Wear Installer 2**: IP/puerto del reloj, empareja con el código, elige el APK, Instalar.

## Publicar

1. Lee la `PLANTILLA.md` y cambia solo lo que describe.
2. Regenera con el script de `docs/src/` cuando el diseño tenga uno.
3. Mira el simulador (ábrelo en el navegador o en el S25) y, si tienes Playwright y Chrome en `/usr/bin/google-chrome`, lanza el `shoot_*.py`.
4. Commit de lo generado en `docs/`. Si cambió el contrato de la plantilla o una decisión, actualiza la `PLANTILLA.md` y `DISENO.md`.
5. Push a `main`.

Pages tiene que estar en **Deploy from a branch → main → /docs**. A 3 nov 2026 el repo todavía no tenía Pages activado (la API respondía 404), así que el primer merge no basta: hay que encender ese setting una vez. `docs/.nojekyll` ya está, vacío, para que Jekyll no toque los HTML.

Los scripts de build y de capturas resuelven las rutas desde `__file__`. Se lanzan desde cualquier sitio:

```bash
python3 docs/src/build.py
python3 docs/src/shoot.py
```

Los generadores usan solo la biblioteca estándar. Las capturas necesitan `playwright` y el Chrome de `/usr/bin/google-chrome`. Las PNG con ruta relativa caen en `docs/`. Las de `/tmp/` son de depuración y no se commitean.

## Reglas duras

1. **Estilo.** Minimalista. Fondo negro, turquesa Tiffany `#0ABAB5` y `#81D8D0`, tipografía fina Outfit. Motivos 420 / fumeta sutiles (hoja de trazo fino, el texto «4:20» solo en ese modo). Nada de colores rasta (verde, amarillo y rojo de esa paleta). El salmón `#F2A39B` que ya usa el panel de bitcoin cuando el precio baja se queda: es el color de bajada de esa plantilla, no una paleta nueva.
2. **Plantilla fija.** Cada diseño es una plantilla. Para actualizar, se meten datos nuevos en la plantilla que ya existe. No se rediseña desde cero salvo que Nikolay lo pida con esas palabras.
3. **Paneles estáticos.** En un panel de datos, el agente baja los datos en su máquina al generar el HTML y los deja horneados. En el reloj no hay `fetch` ni refresco periódico. El bitcoin en vivo se conserva como referencia y está marcado como deprecado; no lo vuelvas a poner como página principal.
4. **Simulador.** Cada diseño lleva su `simulador-*.html` (fondo blanco, reloj centrado, botón «Tamaño real»). Si generas la esfera, genera el simulador en el mismo paso. Los scripts ya lo hacen.
5. **Decisiones.** Lo que se decida de diseño se anota en `DISENO.md`.

Las esferas de reloj leen la hora del dispositivo y piden Outfit a `fonts.googleapis.com`. Eso es la fuente, no un panel de datos: no les añadas APIs. El bitcoin estático lleva Outfit en base64 dentro del HTML y no pide nada a la red.

## Orden de trabajo cuando te pidan un cambio

1. Mira la tabla de arriba y abre esa `PLANTILLA.md`.
2. Haz el paso «Cómo actualizarla».
3. Verifica con lo que dice la plantilla.
4. Si Nikolay pidió un diseño nuevo, primero una línea en `DISENO.md`, luego carpeta nueva en `plantillas/`, HTML en `docs/`, simulador, y una fila en la tabla de este archivo. Mismo estilo, misma zona segura, mismos gestos (toque = cambiar de vista, y se recuerda en `localStorage`).
