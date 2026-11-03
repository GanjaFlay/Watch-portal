import asyncio, pathlib
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent  # docs/
BASE = ROOT.as_uri() + '/'

def _out(path):
    p = pathlib.Path(path)
    return str(p if p.is_absolute() else ROOT / p)
UA='Mozilla/5.0 (Linux; Android 15; SM-S931B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36'
async def main():
  async with async_playwright() as pw:
    b=await pw.chromium.launch(executable_path='/usr/bin/google-chrome')
    for name,out,vp in [('simulador-bitcoin-estatico.html','bitcoin-estatico-preview.png',(412,915)),('bitcoin-estatico.html','/tmp/bts-face.png',(438,438))]:
      ctx=await b.new_context(viewport={'width':vp[0],'height':vp[1]},device_scale_factor=2,is_mobile=True,has_touch=True,user_agent=UA,offline=True)
      net=[]
      async def block(route):
        if route.request.url.startswith('file:') or route.request.url.startswith('data:'): await route.continue_()
        else: net.append(route.request.url); await route.abort()
      await ctx.route('**/*',block)
      p=await ctx.new_page();errs=[]
      p.on('console',lambda m:errs.append(m.text) if m.type=='error' else None);p.on('pageerror',lambda e:errs.append(str(e)))
      await p.goto(BASE+name);await p.wait_for_timeout(3000);await p.screenshot(path=_out(out))
      fonts=await p.evaluate("document.fonts.check('200 20px Outfit')")
      print(name,'|',await p.inner_text('.bt-price'),'|',await p.inner_text('.bt-chg'),'|',await p.inner_text('.bt-foot'),'| outfit loaded:',fonts)
      if name.startswith('sim'):
        for n in ['7d','30d']:
          await p.click('#ffFace');await p.wait_for_timeout(2000);await p.screenshot(path=_out(f'/tmp/bts-{n}.png'))
          print('  ',n,await p.inner_text('.bt-chg'))
      print('  network attempts:',net,'errors:',errs);await ctx.close()
    await b.close()
asyncio.run(main())
