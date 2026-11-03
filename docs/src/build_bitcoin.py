#!/usr/bin/env python3
"""'Cómo va el bitcoin' panel. Reuses simulator chrome from build.py (no v1 writes).
Outputs bitcoin.html (panel alone) + simulador-bitcoin.html (phone simulator)."""
import pathlib
HERE = pathlib.Path(__file__).resolve().parent
src = (HERE / 'build.py').read_text(encoding='utf-8').split("(OUT / 'reloj-fumeta.html')")[0]
ns = {'__file__': str(HERE / 'build.py')}; exec(src, ns)
OUT, W, FONTS = ns['OUT'], ns['W'], ns['FONTS']
def rep(s, a, b):
    assert a in s, a[:80]; return s.replace(a, b)

BT_CSS = """
/* ===== Bitcoin panel — native 438x438 ===== */
.bt-face{--bg:#000;--ink:#eafaf8;--accent:#0ABAB5;--soft:#81D8D0;--down:#F2A39B;--muted:rgba(129,216,208,.55);--track:rgba(129,216,208,.10);
  position:relative;width:438px;height:438px;border-radius:50%;overflow:hidden;background:var(--bg);color:var(--ink);
  font-family:'Outfit',system-ui,-apple-system,Roboto,sans-serif;-webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none;cursor:pointer;contain:strict}
.bt-face canvas{position:absolute;inset:0;width:438px;height:438px;pointer-events:none}
.bt-face svg.bt-ring{position:absolute;inset:0;pointer-events:none;overflow:visible}
.bt-track{stroke:var(--track)} .bt-arc{stroke:var(--accent);transition:stroke .6s}
.bt-face.bt-dn .bt-arc{stroke:var(--down)} .bt-dot{fill:var(--soft);transition:fill .6s} .bt-face.bt-dn .bt-dot{fill:var(--down)} .bt-tick{stroke:var(--muted)}
.bt-head{position:absolute;left:0;right:0;top:66px;display:flex;justify-content:center;align-items:center;gap:7px;
  font-size:12px;font-weight:300;letter-spacing:.32em;text-transform:uppercase;color:var(--muted);padding-left:.32em}
.bt-head svg{width:15px;height:15px;color:var(--accent)}
.bt-rng{position:absolute;left:0;right:0;top:94px;display:flex;justify-content:center;gap:18px;font-size:12px;font-weight:300;letter-spacing:.18em;color:var(--muted)}
.bt-rng span{padding:2px 0 4px;border-bottom:1px solid transparent;transition:color .4s,border-color .4s}
.bt-rng span.on{color:var(--soft);border-bottom-color:var(--accent)}
.bt-price{position:absolute;left:0;right:0;top:122px;text-align:center;font-weight:200;font-size:62px;line-height:70px;letter-spacing:-.01em;font-variant-numeric:tabular-nums}
.bt-price small{font-size:30px;font-weight:200;margin-left:6px;color:var(--soft)}
.bt-chg{position:absolute;left:0;right:0;top:196px;text-align:center;font-size:16px;font-weight:300;letter-spacing:.08em;color:var(--accent);transition:color .6s}
.bt-chg i{font-style:normal;color:var(--muted);font-size:12px;letter-spacing:.2em;margin-left:8px;text-transform:uppercase}
.bt-face.bt-dn .bt-chg{color:var(--down)}
.bt-foot{position:absolute;left:0;right:0;top:366px;text-align:center;font-size:11px;font-weight:300;letter-spacing:.16em;color:var(--muted)}
.bt-off{position:absolute;left:50%;top:388px;transform:translateX(-50%);font-size:10px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--down);border:1px solid rgba(242,163,155,.5);border-radius:99px;padding:2px 9px 2px 11px;display:none;white-space:nowrap}
.bt-face.bt-offline .bt-off{display:block}
.bt-face.bt-loading .bt-price,.bt-face.bt-loading .bt-chg{animation:bt-breath 1.6s ease-in-out infinite}
@keyframes bt-breath{50%{opacity:.35}}
"""

BT_HTML = """
<div class="bt-face bt-loading" id="ffFace" role="img" aria-label="Bitcoin">
  <svg class="bt-ring" viewBox="0 0 438 438" width="438" height="438">
    <g class="bt-ticks"></g>
    <circle class="bt-track" cx="219" cy="219" r="209" fill="none" stroke-width="1.5"/>
    <circle class="bt-dot" r="3.4" cx="219" cy="10"/>
    <circle class="bt-arc" cx="219" cy="219" r="209" fill="none" stroke-width="2.5" stroke-linecap="round" transform="rotate(-90 219 219)"/>
  </svg>
  <canvas width="438" height="438"></canvas>
  <div class="bt-head"><svg viewBox="-50 -50 100 100" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"></svg>Bitcoin</div>
  <div class="bt-rng"><span data-r="24h">24H</span><span data-r="7d">7D</span><span data-r="30d">30D</span></div>
  <div class="bt-price"><span class="bt-num">—</span><small>€</small></div>
  <div class="bt-chg">cargando…</div>
  <div class="bt-foot">&nbsp;</div>
  <div class="bt-off">sin conexión</div>
</div>
"""

BT_JS = r"""
/* ===== Bitcoin panel JS — call initBitcoinPanel(rootElement) ===== */
function initBitcoinPanel(root){
  var NS='http://www.w3.org/2000/svg', C=219, R=209, CIRC=2*Math.PI*R, N=120;
  var RANGES=['24h','7d','30d'], LBL={'24h':'24 h','7d':'7 días','30d':'30 días'}, DAYS={'24h':1,'7d':7,'30d':30};
  var BN={'24h':['15m',96],'7d':['2h',84],'30d':['8h',90]};
  var KEY='btcPanelRange', CK='btcPanelCache_';
  var fmt0=new Intl.NumberFormat('es-ES',{maximumFractionDigits:0,useGrouping:true});
  function eur(v){var s=fmt0.format(Math.round(v));return (Math.abs(v)>=1000&&s.indexOf('.')<0)?s.replace(/(\d)(?=(\d{3})+$)/g,'$1.'):s;}
  function pct(v){return (v>=0?'+':'−')+Math.abs(v).toFixed(2).replace('.',',')+' %';}
  function hhmm(t){var d=new Date(t);return ('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2);}
  function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v);}catch(e){return null;}}

  // leaf accent (thin outline)
  (function(){var L=[[0,1],[30,.82],[-30,.82],[62,.6],[-62,.6],[100,.32],[-100,.32]],d=[];
    L.forEach(function(q){var a=q[0]*Math.PI/180,l=44*q[1],w=7*q[1]+1.5,ca=Math.cos(a),sa=Math.sin(a);
      function T(x,y){return (x*ca-y*sa).toFixed(1)+' '+(x*sa+y*ca).toFixed(1);}
      d.push('M'+T(0,0)+' C'+T(w,-l*.3)+' '+T(w*.7,-l*.75)+' '+T(0,-l)+' C'+T(-w*.7,-l*.75)+' '+T(-w,-l*.3)+' '+T(0,0)+'Z');});
    d.push('M0 0 L0 14');var p=document.createElementNS(NS,'path');p.setAttribute('d',d.join(' '));p.setAttribute('transform','translate(0 8)');
    root.querySelector('.bt-head svg').appendChild(p);})();
  // ticks
  var tg=root.querySelector('.bt-ticks');
  for(var i=0;i<60;i++){var hr=i%5===0,a=i*6*Math.PI/180,r1=hr?192:197,ln=document.createElementNS(NS,'line');
    ln.setAttribute('x1',C+r1*Math.sin(a));ln.setAttribute('y1',C-r1*Math.cos(a));ln.setAttribute('x2',C+201*Math.sin(a));ln.setAttribute('y2',C-201*Math.cos(a));
    ln.setAttribute('stroke-width',hr?1:.6);ln.setAttribute('class','bt-tick');if(!hr)ln.setAttribute('opacity','.4');tg.appendChild(ln);}
  var arc=root.querySelector('.bt-arc');arc.setAttribute('stroke-dasharray',CIRC.toFixed(2));arc.style.strokeDashoffset=CIRC;
  arc.style.transition='stroke-dashoffset 1.2s cubic-bezier(.2,.8,.2,1),stroke .6s';

  var numEl=root.querySelector('.bt-num'), chgEl=root.querySelector('.bt-chg'), footEl=root.querySelector('.bt-foot'), rngEls=root.querySelectorAll('.bt-rng span');
  var range=ls(KEY); if(RANGES.indexOf(range)<0)range='24h';
  function markRange(){for(var i=0;i<rngEls.length;i++)rngEls[i].classList.toggle('on',rngEls[i].getAttribute('data-r')===range);}

  // ---------- data
  function getJSON(url){var c=window.AbortController?new AbortController():null,t=setTimeout(function(){c&&c.abort();},9000);
    return fetch(url,c?{signal:c.signal,cache:'no-store'}:{cache:'no-store'}).then(function(r){clearTimeout(t);if(!r.ok)throw new Error('HTTP '+r.status);return r.json();});}
  var cgUntil=0, CHART_TTL={'24h':5*60e3,'7d':30*60e3,'30d':60*60e3};
  function viaCoinGecko(rg){var b='https://api.coingecko.com/api/v3/';
    if(Date.now()<cgUntil)return Promise.reject(new Error('CoinGecko en pausa'));
    var c=null;try{c=JSON.parse(ls(CK+rg)||'null');}catch(e){}
    var fresh=c&&c.src==='CoinGecko'&&c.chartT&&Date.now()-c.chartT<CHART_TTL[rg]; // reuse chart, only fetch price (saves API calls)
    return Promise.all([getJSON(b+'simple/price?ids=bitcoin&vs_currencies=eur,usd&include_24hr_change=true'),
      fresh?Promise.resolve({prices:c.series.slice(0,-1),cached:1}):getJSON(b+'coins/bitcoin/market_chart?vs_currency=eur&days='+DAYS[rg])]).then(function(r){
      var s=r[1].prices; if(!s||s.length<5)throw new Error('serie vacía');
      var ct=r[1].cached?c.chartT:Date.now();
      return{price:r[0].bitcoin.eur,ch24:r[0].bitcoin.eur_24h_change,series:s,src:'CoinGecko',chartT:ct};}).catch(function(e){cgUntil=Date.now()+10*60e3;throw e;});}
  function viaBinance(rg){var b='https://data-api.binance.vision/api/v3/';
    return Promise.all([getJSON(b+'ticker/24hr?symbol=BTCEUR'),getJSON(b+'klines?symbol=BTCEUR&interval='+BN[rg][0]+'&limit='+BN[rg][1])]).then(function(r){
      return{price:+r[0].lastPrice,ch24:+r[0].priceChangePercent,series:r[1].map(function(k){return[k[0],+k[4]];}),src:'Binance',chartT:Date.now()};});}
  function load(rg){return viaCoinGecko(rg).catch(function(){return viaBinance(rg);}).then(function(d){
      d.series.push([Date.now(),d.price]);d.t=Date.now();d.range=rg;ls(CK+rg,JSON.stringify(d));return d;});}

  // ---------- chart (canvas, DPR-aware)
  var cv=root.querySelector('canvas'), cx=cv.getContext('2d'), k=1;
  function fitCanvas(){var sc=root.getBoundingClientRect().width/438||1,nk=Math.min(3,Math.max(1,sc*(window.devicePixelRatio||1)));
    if(Math.abs(nk-k)<.01&&cv.width===Math.round(438*k))return;k=nk;cv.width=cv.height=Math.round(438*k);draw();}
  window.addEventListener('resize',fitCanvas);
  var X0=56,X1=382,Y0=252,Y1=334;
  function resample(s){var out=[],t0=s[0][0],t1=s[s.length-1][0],j=0;
    for(var i=0;i<N;i++){var t=t0+(t1-t0)*i/(N-1);while(j<s.length-2&&s[j+1][0]<t)j++;
      var a=s[j],b=s[j+1]||a,f=b[0]>a[0]?(t-a[0])/(b[0]-a[0]):0;out.push(a[1]+(b[1]-a[1])*Math.max(0,Math.min(1,f)));}return out;}
  var cur=null, from=null, to=null, anim={t0:0,dur:1,mode:'draw'}, shownPrice=null, data=null;
  function ease(x){return 1-Math.pow(1-x,3);}
  function draw(){
    cx.setTransform(k,0,0,k,0,0);cx.clearRect(0,0,438,438);
    if(!cur){ // loading shimmer
      var ph=(performance.now()%1800)/1800;cx.strokeStyle='rgba(129,216,208,.18)';cx.lineWidth=1;cx.beginPath();
      for(var x=X0;x<=X1;x+=4){var y=(Y0+Y1)/2+Math.sin(x/28+ph*6.28)*10;x===X0?cx.moveTo(x,y):cx.lineTo(x,y);}cx.stroke();return;}
    var ex=data.ext,mn=Math.min(ex.vMn,Math.min.apply(null,cur)),mx=Math.max(ex.vMx,Math.max.apply(null,cur)),pad=(mx-mn)*.06||1;mn-=pad;mx+=pad;
    function px(i){return X0+(X1-X0)*i/(N-1);} function py(v){return Y1-(Y1-Y0)*(v-mn)/(mx-mn);}
    var prog=anim.mode==='draw'?ease(Math.min(1,(performance.now()-anim.t0)/anim.dur)):1, lastI=Math.max(1,Math.floor((N-1)*prog));
    var up=data&&data.chg>=0, col=up?'10,186,181':'242,163,155', colL=up?'#81D8D0':'#F2A39B';
    // clip to circle
    cx.save();cx.beginPath();cx.arc(219,219,190,0,6.2832);cx.clip();
    // baseline (start of range)
    var by=py(cur[0]);cx.setLineDash([2,4]);cx.strokeStyle='rgba(129,216,208,.18)';cx.lineWidth=.8;cx.beginPath();cx.moveTo(X0,by);cx.lineTo(X1,by);cx.stroke();cx.setLineDash([]);
    // smooth path (Catmull-Rom -> Bezier)
    function path(){cx.moveTo(px(0),py(cur[0]));for(var i=0;i<lastI;i++){var p0=cur[Math.max(0,i-1)],p1=cur[i],p2=cur[i+1],p3=cur[Math.min(N-1,i+2)],dx=(X1-X0)/(N-1);
      cx.bezierCurveTo(px(i)+dx/3,py(p1+(p2-p0)/6),px(i+1)-dx/3,py(p2-(p3-p1)/6),px(i+1),py(p2));}}
    var g=cx.createLinearGradient(0,Y0-10,0,Y1+30);g.addColorStop(0,'rgba('+col+',.22)');g.addColorStop(1,'rgba('+col+',0)');
    cx.beginPath();path();cx.lineTo(px(lastI),Y1+34);cx.lineTo(X0,Y1+34);cx.closePath();cx.fillStyle=g;cx.fill();
    cx.globalCompositeOperation='destination-out';var fl=cx.createLinearGradient(X0,0,X0+40,0);fl.addColorStop(0,'rgba(0,0,0,1)');fl.addColorStop(1,'rgba(0,0,0,0)');
    cx.fillStyle=fl;cx.fillRect(X0-2,Y0-40,42,Y1-Y0+90);cx.globalCompositeOperation='source-over';
    cx.beginPath();path();cx.strokeStyle=colL;cx.lineWidth=1.6;cx.lineJoin='round';cx.stroke();
    cx.restore();
    // head dot with glow
    var hx=px(lastI),hy=py(cur[lastI]),pulse=.5+.5*Math.sin(performance.now()/500);
    cx.fillStyle='rgba('+col+','+(.15+.15*pulse)+')';cx.beginPath();cx.arc(hx,hy,5+3*pulse,0,6.2832);cx.fill();
    cx.fillStyle=colL;cx.beginPath();cx.arc(hx,hy,2.6,0,6.2832);cx.fill();
    // min / max labels
    if(prog>=1){var ex2=data.ext;
      cx.font='300 11px Outfit, system-ui, sans-serif';cx.textAlign='center';
      [[ex2.iMx,-9,'máx ',ex2.vMx],[ex2.iMn,17,'mín ',ex2.vMn]].forEach(function(m){var x=px(m[0]),y=py(m[3]);
        cx.fillStyle='rgba(234,250,248,.55)';cx.beginPath();cx.arc(x,y,1.8,0,6.2832);cx.fill();
        cx.fillStyle='rgba(129,216,208,.75)';cx.fillText(m[2]+eur(m[3]),Math.max(96,Math.min(342,x)),y+m[1]);});}
  }
  function loop(){
    if(to&&anim.mode==='morph'){var f=ease(Math.min(1,(performance.now()-anim.t0)/anim.dur));cur=to.map(function(v,i){return from[i]+(v-from[i])*f;});}
    draw();setTimeout(function(){requestAnimationFrame(loop);},33); // ~30fps
  }
  function countTo(v){var a=shownPrice==null?v*.97:shownPrice,t0=performance.now();shownPrice=v;
    (function st(){var f=ease(Math.min(1,(performance.now()-t0)/900));numEl.textContent=eur(a+(v-a)*f);if(f<1)requestAnimationFrame(st);})();}

  function show(d,offline){
    var s=resample(d.series);
    var sm=s.map(function(v,i){var a=0,n=0;for(var j=-3;j<=3;j++){var q=s[i+j];if(q!=null){a+=q;n++;}}return a/n;});sm[N-1]=d.price;
    var t0=d.series[0][0],t1=d.series[d.series.length-1][0],ext={vMx:-1e18,vMn:1e18};
    d.series.forEach(function(p){var i=Math.round((p[0]-t0)/(t1-t0||1)*(N-1));if(p[1]>ext.vMx){ext.vMx=p[1];ext.iMx=i;}if(p[1]<ext.vMn){ext.vMn=p[1];ext.iMn=i;}});
    var chg=d.range==='24h'&&d.ch24!=null?d.ch24:(s[N-1]-s[0])/s[0]*100;
    var rangeChanged=!data||data.range!==d.range; data={range:d.range,chg:chg,ext:ext};s=sm;
    if(rangeChanged||!cur){cur=s;to=null;anim={t0:performance.now(),dur:1100,mode:'draw'};}
    else{from=cur.slice();to=s;anim={t0:performance.now(),dur:700,mode:'morph'};}
    root.classList.remove('bt-loading');root.classList.toggle('bt-dn',chg<0);root.classList.toggle('bt-offline',!!offline);
    countTo(d.price);
    chgEl.innerHTML=(chg>=0?'▲ ':'▼ ')+pct(chg)+'<i>'+LBL[d.range]+'</i>';
    footEl.textContent='act. '+hhmm(d.t)+' · '+d.src;
    var mn=Math.min.apply(null,s),mx=Math.max.apply(null,s),pos=mx>mn?(d.price-mn)/(mx-mn):.5; // ring = position of price within range
    pos=Math.max(.015,Math.min(1,pos));arc.style.strokeDashoffset=(CIRC*(1-pos)).toFixed(2);
    var dot=root.querySelector('.bt-dot'),an=pos*2*Math.PI;dot.setAttribute('cx',(C+R*Math.sin(an)).toFixed(1));dot.setAttribute('cy',(C-R*Math.cos(an)).toFixed(1));
  }
  var busy=false;
  function refresh(){if(busy)return;busy=true;var rg=range;
    load(rg).then(function(d){if(rg===range)show(d,false);}).catch(function(){
      var c=ls(CK+rg);if(c&&rg===range){try{show(JSON.parse(c),true);}catch(e){}}
      else if(rg===range){root.classList.add('bt-offline');chgEl.textContent='sin datos';}
    }).then(function(){busy=false;});}
  root.addEventListener('click',function(){range=RANGES[(RANGES.indexOf(range)+1)%3];ls(KEY,range);markRange();
    var c=ls(CK+range);if(c){try{show(JSON.parse(c),!navigator.onLine);}catch(e){}}refresh();});
  markRange();
  var c0=ls(CK+range);if(c0){try{show(JSON.parse(c0),false);footEl.textContent+=' · actualizando…';}catch(e){}}
  fitCanvas();loop();refresh();setInterval(refresh,60000);
  window.addEventListener('online',refresh);
  document.addEventListener('visibilitychange',function(){if(!document.hidden)refresh();});
}
"""

face_page = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Bitcoin · panel</title>{FONTS}
<style>html,body{{margin:0;height:100%;background:#000;overflow:hidden}}
#ffStage{{position:fixed;left:50%;top:50%;width:{W}px;height:{W}px;transform-origin:0 0}}
{BT_CSS}</style></head>
<body><div id="ffStage">{BT_HTML}</div>
<script>{BT_JS}
(function(){{var st=document.getElementById('ffStage');
function fit(){{var s=Math.min(innerWidth,innerHeight)/{W};st.style.transform='scale('+s+') translate(-50%,-50%)';}}
addEventListener('resize',fit);fit();initBitcoinPanel(document.getElementById('ffFace'));}})();
</script></body></html>
"""
sim_html = rep(ns['SIM_HTML'], ns['FACE_HTML'], BT_HTML)
sim_html = rep(sim_html, '<p class="sim-title">Reloj Fumeta</p>', '<p class="sim-title">Bitcoin</p>')
sim_js = rep(ns['SIM_JS'], "initFumetaFace(", "initBitcoinPanel(")
sim_js = rep(sim_js, "scaler.style.transform='scale('+(d/W)+')';", "scaler.style.transform='scale('+(d/W)+')';setTimeout(function(){window.dispatchEvent(new Event('resize'));},560);")
sim_js = rep(sim_js, "addEventListener('resize',layout);", "addEventListener('resize',function(e){if(e.isTrusted)layout();});")
sim_js = rep(sim_js, "'Toca la esfera para cambiar de tema'", "'Toca la esfera para cambiar 24h / 7d / 30d'")
sim_js = rep(sim_js, "'Toca la esfera para cambiar de tema'", "'Toca la esfera para cambiar 24h / 7d / 30d'") if "'Toca la esfera para cambiar de tema'" in sim_js else sim_js
sim_html = rep(sim_html, "Toca la esfera para cambiar de tema", "Toca la esfera para cambiar 24h / 7d / 30d")
sim_page = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#ffffff">
<title>Simulador · Bitcoin · Galaxy Watch9 40 mm</title>{FONTS}
<style>{ns['SIM_CSS']}{BT_CSS}</style></head>
<body>{sim_html}
<script>{BT_JS}{sim_js}</script></body></html>
"""
(OUT / 'bitcoin.html').write_text(face_page, encoding='utf-8')
(OUT / 'simulador-bitcoin.html').write_text(sim_page, encoding='utf-8')
print('ok')
