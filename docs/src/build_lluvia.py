#!/usr/bin/env python3
"""Version 2 'Lluvia de hojas': reuses the face module from build.py (without writing v1 files),
replaces smoke + watermark with a canvas leaf rain. Outputs reloj-lluvia-hojas.html + simulador-lluvia-hojas.html."""
import pathlib
HERE = pathlib.Path(__file__).resolve().parent
src = (HERE / 'build.py').read_text(encoding='utf-8')
src = src.split("(OUT / 'reloj-fumeta.html')")[0]          # definitions only, no file writes
ns = {'__file__': str(HERE / 'build.py')}; exec(src, ns)
OUT, W, FONTS = ns['OUT'], ns['W'], ns['FONTS']
FACE_CSS, FACE_HTML, FACE_JS = ns['FACE_CSS'], ns['FACE_HTML'], ns['FACE_JS']
SIM_CSS, SIM_HTML, SIM_JS = ns['SIM_CSS'], ns['SIM_HTML'], ns['SIM_JS']

def rep(s, a, b):
    assert a in s, a[:80]; return s.replace(a, b)

# ---- CSS: no watermark; 420 text a bit lower is fine as-is
FACE_CSS = rep(FACE_CSS, ".ff-face canvas.ff-smoke", ".ff-face canvas.ff-rain")
FACE_CSS += "\n.ff-wm{display:none}\n"
FACE_HTML = rep(FACE_HTML, 'class="ff-smoke" width="438" height="438"', 'class="ff-rain" width="438" height="438"')

# ---- JS: swap smoke engine for leaf rain
a = FACE_JS.index("  // --- smoke (canvas"); b = FACE_JS.index("  // --- main loop")
RAIN = r"""
  // --- leaf rain (canvas, ~30fps, DPR-aware, depth/parallax)
  var cv=root.querySelector('canvas'), cx=cv.getContext('2d'), leafCol='#81D8D0', glowCol='#0ABAB5', lastSmoke=0, k=1;
  function rainLeaf(){var parts=[],L=[[0,1],[30,.82],[-30,.82],[62,.6],[-62,.6],[100,.32],[-100,.32]];
    L.forEach(function(q){var a=q[0]*Math.PI/180,l=44*q[1],w=7*q[1]+1.5,ca=Math.cos(a),sa=Math.sin(a);
      function T(x,y){return (x*ca-y*sa).toFixed(2)+' '+(x*sa+y*ca).toFixed(2);}
      parts.push('M'+T(0,0)+' C'+T(w,-l*.3)+' '+T(w*.7,-l*.75)+' '+T(0,-l)+' C'+T(-w*.7,-l*.75)+' '+T(-w,-l*.3)+' '+T(0,0)+'Z');});
    parts.push('M0 0 L0 14');return parts.join(' ');}
  var LEAF=new Path2D(rainLeaf()); // outline only (no veins) so small leaves stay airy
  function readSmoke(){var cs=getComputedStyle(root);leafCol=cs.getPropertyValue('--soft').trim()||leafCol;glowCol=cs.getPropertyValue('--accent').trim()||glowCol;}
  function fitCanvas(){
    var sc=root.getBoundingClientRect().width/438||1, nk=Math.min(3,Math.max(1,sc*(window.devicePixelRatio||1)));
    if(Math.abs(nk-k)<.01&&cv.width===Math.round(438*k))return; k=nk;
    cv.width=Math.round(438*k);cv.height=Math.round(438*k);
  }
  window.addEventListener('resize',fitCanvas);
  var P=[], seeded=false;
  function mk(top){var z=.3+Math.random()*.7; // depth: 0.3 far .. 1 near
    return{z:z,s:(14+z*20)/100,a:.12+.45*z,vy:.35+1.05*z,vx:(.35+1.05*z)*.32,
      x:top?-90+Math.random()*500:Math.random()*438, y:top?-20-Math.random()*60:Math.random()*438,
      r:Math.random()*6.28,vr:(Math.random()-.5)*.03,ph:Math.random()*6.28,sw:.3+Math.random()*.6,fq:.02+Math.random()*.03};}
  function drawSmoke(ts){
    var target=m420?32:18;
    while(P.length<target)P.push(mk(seeded));seeded=true;
    if(P.length>target&&!m420)P.length=target;
    cx.setTransform(k,0,0,k,0,0);cx.clearRect(0,0,438,438);
    var glow=0; if(m420){glow=.5+.5*Math.sin(ts/600);} // pulsing turquoise glow in 420 mode
    cx.strokeStyle=leafCol;cx.lineJoin='round';cx.lineCap='round';
    if(glow>0){cx.shadowColor=glowCol;cx.shadowBlur=6+10*glow;}else{cx.shadowBlur=0;}
    for(var i=0;i<P.length;i++){var p=P[i], sp=m420?1.6:1;
      p.y+=p.vy*sp;p.x+=p.vx*sp+Math.sin(p.ph+p.y*p.fq)*p.sw*.6;p.r+=p.vr;
      if(p.y>460||p.x>470){P[i]=mk(true);continue;}
      // dim behind the time block (ellipse around centre)
      var dx=(p.x-219)/175, dy=(p.y-222)/78, d=dx*dx+dy*dy, m=d<1?.12+.88*Math.max(0,(d-.55)/.45):1;
      var al=p.a*m*(m420?1.25:1); if(al<.015)continue;
      cx.globalAlpha=Math.min(1,al);
      cx.setTransform(k*p.s*Math.cos(p.r),k*p.s*Math.sin(p.r),-k*p.s*Math.sin(p.r),k*p.s*Math.cos(p.r),k*p.x,k*p.y);
      cx.lineWidth=(.55+.45*p.z)*(m420?1.25:1)/p.s; // ~0.7-1px on the watch, nearer = a bit thicker
      cx.stroke(LEAF);
    }
    cx.globalAlpha=1;cx.shadowBlur=0;cx.setTransform(1,0,0,1,0,0);
  }
  fitCanvas();
"""
FACE_JS = FACE_JS[:a] + RAIN + FACE_JS[b:]
FACE_JS = rep(FACE_JS, "initFumetaFace(root){", "initLluviaFace(root){")
FACE_JS = rep(FACE_JS, "Reloj Fumeta (face) JS — call initFumetaFace", "Lluvia de hojas (face) JS — call initLluviaFace")
FACE_JS = rep(FACE_JS, "var KEY='relojFumetaTheme';", "var KEY='relojLluviaTheme';")
FACE_CSS = rep(FACE_CSS, "Reloj Fumeta (face)", "Lluvia de hojas (face)")

face_page = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Lluvia de hojas · esfera</title>{FONTS}
<style>html,body{{margin:0;height:100%;background:#000;overflow:hidden}}
#ffStage{{position:fixed;left:50%;top:50%;width:{W}px;height:{W}px;transform-origin:0 0}}
{FACE_CSS}</style></head>
<body><div id="ffStage">{FACE_HTML}</div>
<script>{FACE_JS}
(function(){{var st=document.getElementById('ffStage');
function fit(){{var s=Math.min(innerWidth,innerHeight)/{W};st.style.transform='scale('+s+') translate(-50%,-50%)';}}
addEventListener('resize',fit);fit();initLluviaFace(document.getElementById('ffFace'));}})();
</script></body></html>
"""
sim_html = rep(SIM_HTML, '<p class="sim-title">Reloj Fumeta</p>', '<p class="sim-title">Lluvia de hojas</p>')
sim_js = rep(SIM_JS, "initFumetaFace(", "initLluviaFace(")
sim_js = rep(sim_js, "scaler.style.transform='scale('+(d/W)+')';", "scaler.style.transform='scale('+(d/W)+')';setTimeout(function(){window.dispatchEvent(new Event('resize'));},560);")
# layout() fires on resize too; guard against recursion
sim_js = rep(sim_js, "addEventListener('resize',layout);", "addEventListener('resize',function(e){if(e.isTrusted)layout();});")
sim_page = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#ffffff">
<title>Simulador · Lluvia de hojas · Galaxy Watch9 40 mm</title>{FONTS}
<style>{SIM_CSS}{FACE_CSS}</style></head>
<body>{sim_html}
<script>{FACE_JS}{sim_js}</script></body></html>
"""
(OUT / 'reloj-lluvia-hojas.html').write_text(face_page, encoding='utf-8')
(OUT / 'simulador-lluvia-hojas.html').write_text(sim_page, encoding='utf-8')
print('ok')
