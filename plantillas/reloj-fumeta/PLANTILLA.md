# Plantilla · Reloj fumeta

Esfera de reloj para el Watch9. Hora grande (horas y minutos, los segundos no se escriben: van en el anillo), fecha corta en español, hoja de trazo fino arriba, una hoja enorme muy tenue girando despacio (una vuelta cada 240 s) y un poco de humo abajo, en canvas. Al tocar se cambia de tema. A las 4:20 y a las 16:20 entra el modo 4:20.

No lleva datos de fuera. Actualizarla es tocar constantes en el generador y volver a lanzarlo.

## Archivos

| Archivo | Rol |
|---|---|
| `docs/reloj-fumeta.html` | Esfera. Es lo que abre el reloj. |
| `docs/simulador-reloj-fumeta.html` | Simulador de móvil: fondo blanco, reloj en el centro, botón «Tamaño real». |
| `docs/src/build.py` | Genera los dos HTML. La fuente de verdad es este archivo (`FACE_CSS`, `FACE_HTML`, `FACE_JS`). |
| `docs/src/shoot.py` | Capturas con Playwright. |
| `docs/simulador-preview.png` | Captura del simulador. |
| `docs/simulador-420.png` | Captura del simulador en modo 4:20 (`?t=16:20:25`). |

`build_lluvia.py` hace `exec` de este `build.py` y parte de aquí. Si cambias nombres (`initFumetaFace`, clases `ff-*`, el corte del archivo), la lluvia se rompe. Léete también `plantillas/reloj-lluvia-hojas/PLANTILLA.md` antes de renombrar nada.

## Qué se ve y dónde está en el código

Todo sale de tres cadenas en `docs/src/build.py`:

- `FACE_CSS` — medidas, colores, modo 4:20.
- `FACE_HTML` — el esqueleto (canvas, svg, hora, fecha, «4:20», toast).
- `FACE_JS` — reloj, hoja, humo, temas. La función pública es `initFumetaFace(root)`.

Reloj del dispositivo. Para forzar una hora, la query `t`:

```
reloj-fumeta.html?t=16:19:50
reloj-fumeta.html?t=16:20
```

El regex está en `FACE_JS`: `t=HH:MM` o `t=HH:MM:SS`. Guarda `offset = hora pedida − Date.now()` y el reloj pinta `Date.now() + offset`. Sirve para las capturas y para enseñar el modo 4:20 sin esperar.

Temas, en este orden. Se ciclan con un toque en `#ffFace`. Se guardan en `localStorage` con la clave `relojFumetaTheme` (número `0`, `1` o `2`). El toast de 1,4 s enseña el nombre.

| `data-theme` | Nombre en el toast | Fondo | Acento / tinta |
|---|---|---|---|
| `0` (defecto) | Tiffany · Negro | `#000` | acento `#0ABAB5`, soft `#81D8D0`, humo `129,216,208` |
| `1` | Negro · Tiffany | `#81D8D0` | tinta y acento `#062322` / `#04110f`, humo blanco |
| `2` | Tiffany · Blanco | `#050707` | tinta `#ffffff`, acento `#81D8D0`, humo blanco |

Las variables CSS están en `.ff-face` y en `.ff-face[data-theme="1"]` / `"2"`. El array de nombres es `THEMES` en `FACE_JS`.

Modo 4:20: clase `ff-m420` en la esfera cuando la hora es 4 o 16 **y** los minutos son 20. Entonces:

- aparece el texto «4:20» (`.ff-420`),
- la marca de agua pasa de opacidad `.06` a `.16`,
- la hoja de arriba pulsa (`.ff-leaf`),
- el humo sube de 8 a 22 partículas (`target` dentro de `drawSmoke`).

Anillo de segundos: círculo de centro 219, radio 209. En los minutos pares se va llenando; en los impares se vacía desde arriba, para que no pegue un salto al cambiar de minuto. El punto `.ff-head` recorre el mismo ángulo.

Humo: canvas `.ff-smoke` de 438×438, unas 30 fps (`ts - lastSmoke > 33`). Nace abajo, cerca de y=395.

Fecha: `DIAS` y `MESES` en español corto (`dom`…`sáb`, `ene`…`dic`), formato `lun 3 nov`.

Fuente: Outfit pesos 100, 200, 300 y 400, desde `fonts.googleapis.com` (la constante `FONTS`). En el reloj eso sí pide red, solo para la fuente. No añadas otra petición.

La página escala el escenario de 438 px con `Math.min(innerWidth, innerHeight) / 438`.

Simulador (también en `build.py`: `SIM_CSS`, `SIM_HTML`, `SIM_JS`):

- Título «Reloj Fumeta».
- Botón `#toggle`. Texto «Tamaño real» / «Ampliar», `aria-pressed`.
- Tamaño cómodo: `min(innerWidth * 0.66, 360, innerHeight * 0.42)`.
- Tamaño real: 34 mm por los px/mm del móvil. En un Android con el lado corto entre 340 y 460 px usa `lado / 66` (calibre del S25). Si no, mide `100mm` en CSS.

## Cómo actualizarla

1. Edita la constante en `docs/src/build.py`. No edites `docs/reloj-fumeta.html` ni el simulador: el script los reescribe.
2. Desde cualquier directorio:

   ```bash
   python3 docs/src/build.py
   ```

   Tiene que imprimir `ok`. Reescribe los dos HTML.
3. Si el cambio también lo quieres en la lluvia de hojas (temas, tipografía de la hora, modo 4:20), lanza después `python3 docs/src/build_lluvia.py`. Si el cambio es solo de esta esfera, no hace falta.
4. Ábrete `docs/simulador-reloj-fumeta.html` en el navegador. Prueba un toque (cambia el tema y el toast) y `?t=16:20:10` (entra el modo 4:20). Prueba `?t=16:19:50` para ver el anillo casi lleno.

## Cómo verificar con capturas

Hace falta Playwright y Chrome en `/usr/bin/google-chrome`.

```bash
python3 docs/src/shoot.py
```

El script resuelve `docs/` desde su ruta. Viewport del simulador: 412×915, DPR 2, UA del S25 (`SM-S931B`). Deja en el repo:

- `docs/simulador-preview.png` (tema por defecto, hora real del momento de la captura),
- `docs/simulador-420.png` (`?t=16:20:25`, espera 5 s).

Y en `/tmp`, que no se commitea: `sim-real.png` (botón tamaño real), `sim-theme1.png`, `sim-theme2.png`, `face.png` (esfera sola a 438×438). Si en la consola sale `errors: [...]` con algo dentro, la página ha petado.

## Qué no tocar

- No rediseñes la esfera: posiciones de la hora (top 158 px), de la fecha, de la hoja, grosor del anillo.
- No cambies `initFumetaFace`, la clave `relojFumetaTheme` ni las clases `ff-*` sin actualizar `docs/src/build_lluvia.py`, que busca esos textos con `rep()` y hace `assert`.
- No partas `build.py` por encima de la línea `(OUT / 'reloj-fumeta.html')`. Lluvia y, de rebote, el simulador de bitcoin cortan el archivo por ahí para quedarse solo con las definiciones.
- No metas `fetch` de datos. No cambies la paleta a verde / amarillo / rojo.
- No borres el parámetro `?t=`: lo usan las capturas del modo 4:20.
- Las PNG de `/tmp` no van al repo. Las dos de `docs/` sí, cuando la captura nueva sea la que quieres dejar de referencia.
