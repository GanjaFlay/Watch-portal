#!/usr/bin/env python3
"""Static (offline) Bitcoin panel. One command makes a fresh snapshot:
    python3 docs/src/build_bitcoin_static.py
Fetches EUR price + 24h/7d/30d series (CoinGecko, fallback Binance), bakes them into the HTML as a JS constant,
embeds a subset of the Outfit font as base64 woff2 (falls back to system-ui if that fails), no network code at all.
Outputs bitcoin-estatico.html + simulador-bitcoin-estatico.html."""
import json, time, re, base64, pathlib, urllib.request, datetime
from zoneinfo import ZoneInfo
HERE = pathlib.Path(__file__).resolve().parent
src = (HERE / 'build_bitcoin.py').read_text(encoding='utf-8').split("(OUT / 'bitcoin.html')")[0]
ns = {'__file__': str(HERE / 'build_bitcoin.py')}; exec(src, ns)
OUT, W = ns['OUT'], ns['W']
def rep(s, a, b):
    assert a in s, a[:80]; return s.replace(a, b)

# ------------------------------------------------------------------ 1. data snapshot
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36', 'Accept': 'application/json'}
def get(url, raw=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        b = r.read(); return b if raw else json.loads(b)
def bucket(series, n):
    """Downsample to ~n points (bucket means), keeping first and last points exact."""
    if len(series) <= n: return [[int(t), round(p, 2)] for t, p in series]
    out, size = [], len(series) / n
    for i in range(n):
        ch = series[int(i * size):max(int((i + 1) * size), int(i * size) + 1)]
        out.append([int(ch[len(ch) // 2][0]), round(sum(p for _, p in ch) / len(ch), 2)])
    out[0] = [int(series[0][0]), round(series[0][1], 2)]
    return out
DAYS, NPTS = {'24h': 1, '7d': 7, '30d': 30}, {'24h': 96, '7d': 84, '30d': 90}
BN = {'24h': ('15m', 96), '7d': ('2h', 84), '30d': ('8h', 90)}
def snap_coingecko():
    b = 'https://api.coingecko.com/api/v3/'
    pr = get(b + 'simple/price?ids=bitcoin&vs_currencies=eur&include_24hr_change=true')['bitcoin']
    ranges = {}
    for rg, d in DAYS.items():
        time.sleep(2.5)  # be gentle with the free API
        ranges[rg] = get(b + f'coins/bitcoin/market_chart?vs_currency=eur&days={d}')['prices']
    return pr['eur'], pr['eur_24h_change'], ranges, 'CoinGecko'
def snap_binance():
    b = 'https://data-api.binance.vision/api/v3/'
    tk = get(b + 'ticker/24hr?symbol=BTCEUR')
    ranges = {rg: [[k[0], float(k[4])] for k in get(b + f'klines?symbol=BTCEUR&interval={iv}&limit={n}')] for rg, (iv, n) in BN.items()}
    return float(tk['lastPrice']), float(tk['priceChangePercent']), ranges, 'Binance'
try: price, ch24, raw, srcname = snap_coingecko()
except Exception as e:
    print('CoinGecko falló:', e, '-> Binance'); price, ch24, raw, srcname = snap_binance()
now_ms = int(time.time() * 1000)
series, chg = {}, {}
for rg in DAYS:
    s = bucket(raw[rg], NPTS[rg]); s.append([now_ms, round(price, 2)]); series[rg] = s
    chg[rg] = ch24 if rg == '24h' else (price - s[0][1]) / s[0][1] * 100
MESES = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
mad = datetime.datetime.fromtimestamp(now_ms / 1000, ZoneInfo('Europe/Madrid'))
label = f"{mad.day} {MESES[mad.month-1]} {mad:%H:%M}"
SNAP = {'price': round(price, 2), 'chg': {k: round(v, 3) for k, v in chg.items()}, 'ranges': series, 'src': srcname, 't': now_ms, 'label': label}

# ------------------------------------------------------------------ 2. static JS / HTML
BT_JS = ns['BT_JS']
a = BT_JS.index('  // ---------- data'); b = BT_JS.index('  // ---------- chart')
BT_JS = BT_JS[:a] + BT_JS[b:]
a = BT_JS.index('  var busy=false;')
BT_JS = BT_JS[:a] + r"""  // ---------- static snapshot (no network)
  function showRange(){show({price:SNAP.price,ch24:SNAP.chg[range],series:SNAP.ranges[range],src:SNAP.src,t:SNAP.t,range:range});}
  root.addEventListener('click',function(){range=RANGES[(RANGES.indexOf(range)+1)%3];ls(KEY,range);markRange();showRange();});
  markRange();fitCanvas();loop();setTimeout(showRange,250);
}
"""
BT_JS = rep(BT_JS, "chg=d.range==='24h'&&d.ch24!=null?d.ch24:", "chg=d.ch24!=null?d.ch24:")
BT_JS = rep(BT_JS, "root.classList.toggle('bt-offline',!!offline);", "")
BT_JS = rep(BT_JS, "footEl.textContent='act. '+hhmm(d.t)+' · '+d.src;", "footEl.textContent='datos: '+SNAP.label+' · '+d.src;")
BT_JS = rep(BT_JS, "Bitcoin panel JS — call initBitcoinPanel", "Bitcoin panel (static snapshot) JS — call initBitcoinPanel")
assert 'fetch(' not in BT_JS and 'setInterval' not in BT_JS
SNAP_JS = 'var SNAP=' + json.dumps(SNAP, separators=(',', ':')) + ';\n'
OFF = '\n  <div class="bt-off">sin conexión</div>'
BT_HTML = rep(ns['BT_HTML'], OFF, '')
sim_html = rep(ns['sim_html'], OFF, '')
BT_CSS = re.sub(r'\.bt-off\{[^}]*\}\n?|\.bt-face\.bt-offline \.bt-off\{[^}]*\}\n?', '', ns['BT_CSS'])
sim_js = ns['sim_js']

def pages(font_css):
    face = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Bitcoin · panel (datos {label})</title>
<style>{font_css}html,body{{margin:0;height:100%;background:#000;overflow:hidden}}
#ffStage{{position:fixed;left:50%;top:50%;width:{W}px;height:{W}px;transform-origin:0 0}}
{BT_CSS}</style></head>
<body><div id="ffStage">{BT_HTML}</div>
<script>{SNAP_JS}{BT_JS}
(function(){{var st=document.getElementById('ffStage');
function fit(){{var s=Math.min(innerWidth,innerHeight)/{W};st.style.transform='scale('+s+') translate(-50%,-50%)';}}
addEventListener('resize',fit);fit();initBitcoinPanel(document.getElementById('ffFace'));}})();
</script></body></html>
"""
    sim = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#ffffff">
<title>Simulador · Bitcoin (datos {label}) · Galaxy Watch9 40 mm</title>
<style>{font_css}{ns['ns']['SIM_CSS']}{BT_CSS}</style></head>
<body>{sim_html}
<script>{SNAP_JS}{BT_JS}{sim_js}</script></body></html>
"""
    return face, sim

# ------------------------------------------------------------------ 3. embedded font subset (Outfit 200/300/400)
def font_css_for(text):
    chars = ''.join(sorted(set(text) | set('0123456789.,:%+−-€ ')))
    chars = ''.join(c for c in chars if c.isprintable())
    q = urllib.parse.quote(chars)
    css = get(f'https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400&text={q}&display=swap', raw=True).decode()
    def inline(m):
        return 'url(data:font/woff2;base64,' + base64.b64encode(get(m.group(1), raw=True)).decode() + ") format('woff2')"
    urls=re.findall(r"url\((https://[^)]+)\)\s*format\('woff2'\)", css)
    if urls and len(set(urls))==1:  # variable font: one file covers all weights -> single @font-face
        b64=base64.b64encode(get(urls[0], raw=True)).decode()
        return "@font-face{font-family:'Outfit';font-style:normal;font-weight:100 900;font-display:swap;src:url(data:font/woff2;base64,"+b64+") format('woff2')}\n"
    return re.sub(r"url\((https://[^)]+)\)\s*format\('woff2'\)", inline, css)
import urllib.parse
face, sim = pages('')
visible = re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', face + sim, flags=re.S))
extra = 'BITCOIN 24H 7D 30D máx mín días h datos · CoinGecko Binance ' + ' '.join(MESES) + ' ≈ tamaño real (pantalla de 34 mm, calibrado para S25) Ampliar Tamaño real Toca la esfera para cambiar 24h / 7d / 30d'
try:
    fcss = font_css_for(visible + extra)
    assert 'base64' in fcss
except Exception as e:
    print('Fuente no incrustada (uso system-ui):', e); fcss = ''
face, sim = pages(fcss)
(OUT / 'bitcoin-estatico.html').write_text(face, encoding='utf-8')
(OUT / 'simulador-bitcoin-estatico.html').write_text(sim, encoding='utf-8')
print('snapshot', label, srcname, 'price', SNAP['price'], 'chg', SNAP['chg'], 'font', 'embebida' if fcss else 'system-ui')
