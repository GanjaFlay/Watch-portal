# Plantilla · Bitcoin en vivo (deprecada)

Panel «Bitcoin» en euros, con precio, variación, gráfica y un anillo que marca dónde está el precio dentro del rango del gráfico. Un toque pasa de 24H a 7D y a 30D.

**No la uses en el reloj.** Pide red (`fetch`) y en el móvil no llegaba a conectar. La regla del proyecto es que los paneles van con los datos ya metidos en el HTML. La versión que sí se enseña es `bitcoin-estatico` (`plantillas/bitcoin-estatico/PLANTILLA.md`).

Este archivo se queda porque `build_bitcoin_static.py` ejecuta `build_bitcoin.py` y reutiliza su CSS, su HTML y su JS. Si lo borras o le cambias los marcadores, el panel estático deja de poder regenerarse.

## Archivos

| Archivo | Rol |
|---|---|
| `docs/bitcoin.html` | Panel suelto, con red. |
| `docs/simulador-bitcoin.html` | Simulador. |
| `docs/src/build_bitcoin.py` | Genera los dos HTML. Define `BT_CSS`, `BT_HTML`, `BT_JS`. |
| `docs/src/shoot_bitcoin.py` | Capturas. Necesita red de verdad. |
| `docs/bitcoin-preview.png` | Captura del simulador (la que haya podido cargar). |
| `docs/src/build.py` | Solo se lee para copiar el cromo del simulador (`SIM_CSS`, `SIM_HTML`, `SIM_JS`) y `W` / `FONTS`. |

## Qué hace el JS

Función pública: `initBitcoinPanel(root)`, con `root` = `#ffFace`.

Rangos, en este orden: `24h`, `7d`, `30d`. Etiquetas en pantalla: 24H, 7D, 30D. Etiqueta larga del cambio: «24 h», «7 días», «30 días».

`localStorage`:

| Clave | Qué guarda |
|---|---|
| `btcPanelRange` | `24h`, `7d` o `30d`. Si no hay nada válido, empieza en `24h`. |
| `btcPanelCache_24h`, `btcPanelCache_7d`, `btcPanelCache_30d` | JSON de la última carga de ese rango. |

Un toque hace: rango siguiente → guarda la clave → pinta la caché si existe → lanza `refresh()`.

De dónde salen los datos (esto corre **en el dispositivo**, por eso no vale):

1. CoinGecko, con `AbortController` a los 9 s.
   - Precio: `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur,usd&include_24hr_change=true`
   - Se usan `bitcoin.eur` y `bitcoin.eur_24h_change`. El `usd` se pide y no se pinta.
   - Serie: `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=eur&days=1|7|30` (`DAYS`: 24h→1, 7d→7, 30d→30).
   - Si la caché de ese rango es de CoinGecko y está fresca, no vuelve a pedir la serie. Caducidad (`CHART_TTL`): 24h 5 min, 7d 30 min, 30d 60 min.
   - Cualquier fallo pausa CoinGecko 10 min (`cgUntil`).
2. Si CoinGecko falla, Binance (`data-api.binance.vision`):
   - `GET /api/v3/ticker/24hr?symbol=BTCEUR` → `lastPrice`, `priceChangePercent`.
   - `GET /api/v3/klines?symbol=BTCEUR` con intervalo y límite (`BN`): 24h `15m` / 96, 7d `2h` / 84, 30d `8h` / 90. De cada vela se queda `[openTime, close]`.

El resultado se guarda en la caché y se le añade un punto final `[Date.now(), precio]`.

Refresco: al abrir, cada 60 s (`setInterval(refresh, 60000)`), al evento `online`, y cuando la pestaña vuelve a ser visible.

Sin red y con caché: pinta la caché, pone la clase `bt-offline` y enseña la pastilla «sin conexión». Sin caché: texto «sin datos» y la misma clase.

Gráfica: canvas, `N = 120` puntos remuestreados, caja del gráfico `X0=56`, `X1=382`, `Y0=252`, `Y1=334`. Unos 30 fps. Subida en turquesa, bajada (cambio &lt; 0, clase `bt-dn`) en `#F2A39B`. El anillo (radio 209, centro 219) no es el tiempo: es la posición del precio entre el mínimo y el máximo de la serie.

Pie: `act. HH:MM · CoinGecko` o `· Binance`. Precio en euros, formato `es-ES`, sin decimales (`eur()`).

Fuente: Outfit desde Google Fonts, igual que las esferas (`FONTS` de `build.py`).

El simulador cambia el hint a «Toca la esfera para cambiar 24h / 7d / 30d» y, al escalar, dispara un `resize` a los 560 ms para el canvas (con el mismo guarda `e.isTrusted` que la lluvia).

## Cómo regenerar los HTML (solo si hace falta tocar la plantilla)

Los datos no se hornean aquí. El script solo escribe página y simulador:

```bash
python3 docs/src/build_bitcoin.py
```

Imprime `ok`. Para cambiar colores, textos o la gráfica, se editan `BT_CSS`, `BT_HTML` o `BT_JS` en `docs/src/build_bitcoin.py` y se vuelve a lanzar. Luego hay que lanzar también `python3 docs/src/build_bitcoin_static.py` si el cambio debe llegar al panel que sí usa el reloj: el estático copia estas cadenas al vuelo y reescribe `bitcoin-estatico.html`.

## Cómo verificar

Con red, Playwright y Chrome en `/usr/bin/google-chrome`:

```bash
python3 docs/src/shoot_bitcoin.py
```

Abre el simulador, espera, guarda `docs/bitcoin-preview.png`, pulsa la esfera para 7D y 30D (`/tmp/bt-7d.png`, `/tmp/bt-30d.png`), vuelve a 24H, pone el contexto offline, recarga y guarda `/tmp/bt-offline.png`. También abre `bitcoin.html` a 438×438 en `/tmp/bt-face.png`. Imprime precio, cambio y pie. Si CoinGecko y Binance fallan, la captura se queda en «cargando…» o «sin datos»: es el fallo por el que esta página está deprecada, no una señal para reescribirla.

## Qué no tocar

- No la pongas como destino del menú principal ni de `PORTAL_URL`. En `docs/index.html` ya cuelga como enlace pequeño: «Bitcoin en vivo · no va en el reloj».
- No le añadas más APIs «para que conecte» salvo que Nikolay lo pida. El arreglo que ya está decidido es el snapshot estático.
- No borres ni reordenes estos marcadores, que `build_bitcoin_static.py` busca con `assert` por el texto exacto:
  - el corte `(OUT / 'bitcoin.html')` al final del script (el estático lee solo hasta ahí),
  - en `BT_JS`: `// ---------- data`, `// ---------- chart`, `var busy=false;`,
  - `chg=d.range==='24h'&&d.ch24!=null?d.ch24:`,
  - `root.classList.toggle('bt-offline',!!offline);`,
  - `footEl.textContent='act. '+hhmm(d.t)+' · '+d.src;`,
  - el comentario `Bitcoin panel JS — call initBitcoinPanel`,
  - en `BT_HTML`, el bloque `sin conexión`.
- No cambies `initBitcoinPanel` ni los `data-r` (`24h`, `7d`, `30d`) por otros nombres: el estático y el menú dependen de ellos.
- No cambies el salmón `#F2A39B` por rojo o verde.
