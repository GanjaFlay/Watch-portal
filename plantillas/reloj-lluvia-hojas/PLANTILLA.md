# Plantilla · Lluvia de hojas

Misma esfera que el reloj fumeta (hora, fecha, anillo de segundos, hoja pequeña de arriba, tres temas, modo 4:20), con la marca de agua apagada y el humo cambiado por hojas de contorno que caen. En el modo 4:20 caen más y brillan un poco.

El generador no mantiene una copia del reloj: lee `build.py`, le quita el humo y escribe sus propios HTML.

## Archivos

| Archivo | Rol |
|---|---|
| `docs/reloj-lluvia-hojas.html` | Esfera. |
| `docs/simulador-lluvia-hojas.html` | Simulador (fondo blanco, reloj al centro, «Tamaño real»). |
| `docs/src/build_lluvia.py` | Genera los dos HTML. Aquí vive la lluvia. |
| `docs/src/build.py` | Módulo de la esfera base. Esta plantilla lo reutiliza; no lo edites para un cambio que sea solo de la lluvia. |
| `docs/src/shoot_lluvia.py` | Capturas. |
| `docs/lluvia-preview.png` | Simulador, hora real. |
| `docs/lluvia-420.png` | Simulador en modo 4:20 (`?t=16:20:20`). |

## Qué se ve y dónde está en el código

`build_lluvia.py` hace esto, en este orden:

1. Lee `build.py` y se queda con todo lo que hay **antes** de `(OUT / 'reloj-fumeta.html')`. Así no reescribe el reloj fumeta.
2. Lo ejecuta y saca `FACE_CSS`, `FACE_HTML`, `FACE_JS`, el CSS/HTML/JS del simulador, `OUT`, `W` (438) y `FONTS`.
3. Parches:
   - El canvas pasa de `ff-smoke` a `ff-rain`.
   - Añade `.ff-wm{display:none}` (la hoja gigante no se dibuja).
   - Sustituye el bloque de JS que va desde `// --- smoke (canvas` hasta `// --- main loop` por la cadena `RAIN`.
   - `initFumetaFace` → `initLluviaFace`.
   - La clave de `localStorage` pasa de `relojFumetaTheme` a `relojLluviaTheme`.
   - El comentario del CSS pasa a «Lluvia de hojas (face)».

Lo que se hereda igual que el reloj fumeta (sigue definido en `build.py`, y esta página lleva su propia copia generada):

- Tres temas, mismos colores, mismos nombres de toast. Clave distinta: `relojLluviaTheme`, valores `0`, `1`, `2`.
- Query `?t=HH:MM` o `?t=HH:MM:SS`.
- Modo 4:20 a las 4:20 y a las 16:20, clase `ff-m420`, texto «4:20», pulso de la hoja pequeña.
- Anillo de segundos (centro 219, radio 209), fecha en español corto, dígitos que suben.
- Outfit 100–400 desde Google Fonts.

La lluvia está solo en la cadena `RAIN` de `build_lluvia.py`:

- Hoja de 7 foliolos, solo contorno (sin nervios), un `Path2D` llamado `LEAF`.
- Objetivo de hojas: `m420 ? 32 : 18`. Al salir del modo 4:20 recorta el array a 18.
- Cada hoja tiene profundidad `z` entre 0,3 y 1 (lejos → cerca). De ahí salen escala, alpha y velocidad. Caen en diagonal, con un seno de deriva.
- Cuando una sale por abajo o por la derecha, se recoloca arriba (`mk(true)`).
- Se atenúan al cruzar la elipse de la hora: centro (219, 222), radios 175 y 78. Dentro, el alpha baja hasta 0,12.
- Canvas con DPR (`fitCanvas`), tope de escala 3. El bucle sigue llamándose `drawSmoke` porque el frame del reloj base lo invoca así; no lo renombres sin cambiar también esa llamada en `FACE_JS`.
- En modo 4:20 la velocidad se multiplica por 1,6, el alpha por 1,25, y hay un glow (`shadowBlur`) con el color de acento, pulsando con `sin(ts / 600)`.
- Colores de hoja: `--soft` para el trazo y `--accent` para el glow (`readSmoke` los lee del tema activo).

Simulador: mismo cromo que el reloj fumeta, título «Lluvia de hojas». Dos parches propios en el JS del simulador:

- Tras escalar, a los 560 ms dispara un `resize` para que el canvas recalcule el DPR.
- El `resize` del layout solo corre si `e.isTrusted`, para no entrar en bucle con ese disparo.

## Cómo actualizarla

Cambio solo de la lluvia (cuántas hojas, velocidad, glow):

1. Edita la cadena `RAIN` (o el parche CSS de `.ff-wm`) en `docs/src/build_lluvia.py`.
2. Lanza:

   ```bash
   python3 docs/src/build_lluvia.py
   ```

   Imprime `ok`. No toca `reloj-fumeta.html`.

Cambio de la esfera compartida (hora, temas, anillo, modo 4:20), y lo quieres en las dos:

1. Edítalo en `docs/src/build.py`.
2. Lanza los dos:

   ```bash
   python3 docs/src/build.py
   python3 docs/src/build_lluvia.py
   ```

   El segundo vuelve a copiar el módulo. Si solo lanzas el primero, la lluvia se queda con la esfera vieja.

No edites los HTML generados.

Para ver el modo 4:20: `docs/simulador-lluvia-hojas.html?t=16:20:20`. Un toque en la esfera cambia el tema (el color de las hojas cambia con `--soft` / `--accent`).

## Cómo verificar

```bash
python3 docs/src/shoot_lluvia.py
```

Playwright y Chrome en `/usr/bin/google-chrome`. Escribe:

- `docs/lluvia-preview.png`
- `docs/lluvia-420.png` (`?t=16:20:20`, espera 5 s)

En `/tmp`: `ll-real.png` (tamaño real), `ll-t1.png` (un toque, tema 1), `ll-face.png` (esfera a 438×438). Esas no se commitean.

## Qué no tocar

- No vuelvas a poner el humo ni la marca de agua giratoria, salvo que Nikolay lo pida. La marca de agua se apaga con `.ff-wm{display:none}` a propósito.
- No edites el HTML a mano.
- No cambies en `build.py` los textos que `rep()` busca (`class="ff-smoke"`, `initFumetaFace`, `relojFumetaTheme`, el comentario `Reloj Fumeta (face)`) sin actualizar las cadenas de `build_lluvia.py`. Si un `assert` salta, el texto ya no está.
- No renombres `drawSmoke` dentro de `RAIN` por libre: el bucle principal, que viene de `build.py`, llama a `drawSmoke(ts)`.
- No añadas `fetch`. Misma paleta que la otra esfera. El número de hojas por defecto es 18, y 32 en 4:20: si lo cambias, anótalo en `DISENO.md`, que hoy dice esos dos números.
