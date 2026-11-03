import asyncio, pathlib
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent  # docs/
BASE = ROOT.as_uri() + '/'

def _out(path):
    p = pathlib.Path(path)
    return str(p if p.is_absolute() else ROOT / p)
async def shot(b,name,out,q='',vp=(412,915),click=None,wait=3000):
    ctx=await b.new_context(viewport={'width':vp[0],'height':vp[1]},device_scale_factor=2,is_mobile=True,has_touch=True,
      user_agent='Mozilla/5.0 (Linux; Android 15; SM-S931B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36')
    p=await ctx.new_page();errs=[]
    p.on('console',lambda m:errs.append(m.text) if m.type=='error' else None);p.on('pageerror',lambda e:errs.append(str(e)))
    await p.goto(BASE+name+q);await p.wait_for_timeout(wait)
    for c in (click or []): await p.click(c);await p.wait_for_timeout(1200)
    await p.screenshot(path=_out(out));print(_out(out),'errors:',errs);await ctx.close()
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(executable_path='/usr/bin/google-chrome')
        await shot(b,'simulador-lluvia-hojas.html','lluvia-preview.png')
        await shot(b,'simulador-lluvia-hojas.html','lluvia-420.png','?t=16:20:20',wait=5000)
        await shot(b,'simulador-lluvia-hojas.html','/tmp/ll-real.png',click=['#toggle'])
        await shot(b,'simulador-lluvia-hojas.html','/tmp/ll-t1.png',click=['#ffFace'])
        await shot(b,'reloj-lluvia-hojas.html','/tmp/ll-face.png',vp=(438,438))
        await b.close()
asyncio.run(main())
