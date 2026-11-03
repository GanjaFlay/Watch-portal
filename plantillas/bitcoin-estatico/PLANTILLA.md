# Plantilla · Bitcoin estático

El mismo panel que el bitcoin en vivo (precio en euros, variación, gráfica, anillo, toque para cambiar 24H / 7D / 30D), con una diferencia: los números van dentro del HTML. En el reloj no hay `fetch`, ni `setInterval`, ni pastilla de «sin conexión».

Es el panel que tiene que abrir el reloj. El menú apunta aquí (`docs/bitcoin-estatico.html`).

Para poner precios nuevos no se rediseña nada: se lanza un script, que baja los datos, los mete en un objeto `SNAP` y reescribe los dos HTML.

## Archivos

| Archivo | Rol |
|---|---|
| `docs/bitcoin-estatico.html` | Panel. Lo abre el reloj. Lleva `SNAP`, el JS y la fuente Outfit en base64. |
| `docs/simulador-bitcoin-estatico.html` | Simulador, con el mismo `SNAP` y la misma fuente. |
| `docs/src/build_bitcoin_static.py` | Baja los datos y escribe los dos HTML. |
| `docs/src/build_bitcoin.py` | Plantilla visual (CSS, HTML, JS). El script estático la ejecuta y luego le quita la red. No hace falta lanzarla para actualizar precios. |
| `docs/src/shoot_bitcoin_static.py` | Capturas en offline. Comprueba que la página no pide red. |
| `docs/bitcoin-estatico-preview.png` | Captura del simulador. |

## El snapshot que hay ahora

Generado el **2 nov 2026, 20:15** hora de Madrid, fuente **CoinGecko**. Está en el `var SNAP` de los dos HTML (y en el `<title>`, «datos 2 nov 20:15»):

| Campo | Valor |
|---|---|
| `price` | `68648` (euros, 2 decimales en el objeto; en pantalla se redondea sin decimales) |
| `chg["24h"]` | `-1.408` |
| `chg["7d"]` | `-3.906` |
| `chg["30d"]` | `-9.016` |
| `src` | `"CoinGecko"` |
| `t` | `1793646944276` (ms) |
| `label` | `"2 nov 20:15"` |
| `ranges["24h"]` | 97 puntos |
| `ranges["7d"]` | 85 puntos |
| `ranges["30d"]` | 91 puntos |

Esos largos son el recorte (96 / 84 / 90) más el punto del precio actual al final. El primer punto de 24h en este snapshot es `[1793560800000, 69607.66]` y el último es `[1793646944276, 68648]`.

El pie de la esfera sale de `label` y `src`: `datos: 2 nov 20:15 · CoinGecko`.

Al volver a lanzar el script, este bloque entero se sustituye. No lo edites a mano dentro del HTML.

## Qué hay dentro de `SNAP` y quién lo rellena

Lo construye `build_bitcoin_static.py` (biblioteca estándar: `urllib`, `json`, `zoneinfo`). Zona horaria del `label`: `Europe/Madrid`. Meses: `ene` … `dic`. Formato del label: `{día} {mes} {HH:MM}`.

Intento 1, CoinGecko (cabecera `User-Agent` de navegador, timeout 20 s):

- `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur&include_24hr_change=true` → `eur` y `eur_24h_change`.
- Para cada rango, con una pausa de **2,5 s** entre medias: `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=eur&days=1|7|30`.

Si eso lanza, imprime `CoinGecko falló: … -> Binance` y tira de Binance:

- `https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCEUR` → `lastPrice`, `priceChangePercent`.
- `klines?symbol=BTCEUR` con (`BN`): 24h intervalo `15m` límite 96, 7d `2h` / 84, 30d `8h` / 90. Precio de cada vela: el close.

Luego, para los tres rangos:

- `bucket()` deja la serie en 96, 84 o 90 puntos. Si ya venía más corta, solo redondea. Si no, parte en n tramos: cada punto es la media del tramo y el timestamp del elemento central del tramo. Después pisa **solo el primer punto** con el primer punto real de la serie (tiempo y precio). El último del recorte no se reescribe.
- Se añade al final `[ahora_ms, precio]`. Por eso en el HTML hay 97, 85 y 91 puntos, no 96, 84 y 90.
- `chg["24h"]` es el cambio 24 h que haya dado la API. `chg["7d"]` y `chg["30d"]` se calculan `(precio - primer_punto) / primer_punto * 100`.
- Precios de la serie a 2 decimales. Los cambios del objeto, a 3.

La fuente Outfit (pesos 200, 300 y 400, más los caracteres que salen en la página) se pide a Google Fonts y se incrusta como woff2 en base64. Si Google devuelve una sola URL para todos los pesos, queda un `@font-face` con `font-weight: 100 900`. Si la descarga falla, el script avisa (`Fuente no incrustada (uso system-ui)`) y el CSS de la fuente se deja vacío: la página usa `system-ui`. No dejes el HTML apuntando a `fonts.googleapis.com`.

El JS de la página es el de `build_bitcoin.py` con tres cortes:

- Se borra el bloque que va de `// ---------- data` a `// ---------- chart` (el `fetch`).
- Desde `var busy=false;` hasta el final de la función se sustituye por `showRange()`, que llama a `show()` con `SNAP` y nada más. El toque solo cambia el rango y vuelve a pintar `SNAP`.
- Parches de texto: el cambio usa `d.ch24` también fuera de 24 h (porque 7D y 30D ya vienen calculados), se quita la clase `bt-offline`, el pie pasa a `datos: ` + `SNAP.label`, y el comentario de cabecera dice `static snapshot`.

El script hace `assert 'fetch(' not in BT_JS and 'setInterval' not in BT_JS`. Si alguien reintroduce un temporizador en el JS compartido, este build falla. Bien.

`localStorage`: se sigue guardando el rango elegido en `btcPanelRange` (`24h` / `7d` / `30d`). La declaración `CK = 'btcPanelCache_'` se queda porque el script conserva el principio de `BT_JS`, pero el panel estático no lee ni escribe esa caché.

Un toque en `#ffFace`: 24H → 7D → 30D → 24H. Al cargar, `showRange` se llama a los 250 ms para que la animación de la gráfica tenga un frame.

El simulador lleva el hint «Toca la esfera para cambiar 24h / 7d / 30d» y el botón «Tamaño real», igual que el resto.

## Cómo actualizar los precios

Desde cualquier sitio, con salida a internet (CoinGecko, o Binance si CoinGecko no responde) y la base de zonas horarias del sistema (`Europe/Madrid`):

```bash
python3 docs/src/build_bitcoin_static.py
```

Al terminar imprime una línea como:

```
snapshot 3 nov 19:40 CoinGecko price 68648.0 chg {'24h': -1.408, '7d': -3.906, '30d': -9.016} font embebida
```

Reescribe, y hay que commitear:

- `docs/bitcoin-estatico.html`
- `docs/simulador-bitcoin-estatico.html`

Si además sacas captura nueva, también `docs/bitcoin-estatico-preview.png`.

No hace falta lanzar `build_bitcoin.py` para un refresco de datos. Lánzalo solo si has cambiado el aspecto en `BT_CSS` / `BT_HTML` / `BT_JS`: el estático lee esas cadenas de `build_bitcoin.py` en el momento de ejecutarse, así que un cambio visual se aplica al regenerar el snapshot, y el HTML en vivo (`bitcoin.html`) solo se entera si lanzas también `build_bitcoin.py`.

## Cómo verificar

```bash
python3 docs/src/shoot_bitcoin_static.py
```

Playwright y Chrome en `/usr/bin/google-chrome`. Abre el simulador y la esfera **en offline** y aborta cualquier petición que no sea `file:` o `data:`. Tiene que imprimir precio, cambio y pie, `outfit loaded: True` (si la fuente se incrustó), y `network attempts: []`. Si ahí aparece una URL, la página está pidiendo red y no sirve para el reloj.

Capturas:

- `docs/bitcoin-estatico-preview.png` (simulador, 412×915),
- `/tmp/bts-face.png` (esfera a 438×438),
- `/tmp/bts-7d.png` y `/tmp/bts-30d.png` (tras un toque cada una).

A ojo, en el simulador: el rango subrayado cambia, el porcentaje cambia, el precio no (es el mismo snapshot), y el pie sigue diciendo la fecha del snapshot, no «ahora».

## Qué no tocar

- No edites a mano el base64 de la fuente ni el `var SNAP`. Se regeneran.
- No añadas `fetch`, `setInterval`, ni la pastilla «sin conexión». El script estático las quita y, si el `fetch` sobrevive, el `assert` rompe el build.
- No cambies en `build_bitcoin.py` los marcadores que este script busca. La lista está en `plantillas/bitcoin/PLANTILLA.md`, sección «Qué no tocar».
- No cambies el layout (sitios de precio, gráfica, anillo, hoja) para «refrescar el diseño». Solo se refrescan los números.
- No cambies `#F2A39B`, que es el color de bajada cuando `chg < 0` (clase `bt-dn`). No lo pases a rojo o verde.
- No borres el simulador: se reescribe junto con el panel. Los dos tienen que llevar el mismo `SNAP`.
