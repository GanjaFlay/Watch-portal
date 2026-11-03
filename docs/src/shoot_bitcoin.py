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
    ctx=await b.new_context(viewport={'width':412,'height':915},device_scale_factor=2,is_mobile=True,has_touch=True,user_agent=UA)
    p=await ctx.new_page();errs=[]
    p.on('console',lambda m:errs.append(m.text) if m.type=='error' else None);p.on('pageerror',lambda e:errs.append(str(e)))
    await p.goto(BASE+'simulador-bitcoin.html');await p.wait_for_timeout(600);await p.screenshot(path=_out('/tmp/bt-loading.png'))
    await p.wait_for_timeout(5000);await p.screenshot(path=_out('bitcoin-preview.png'))
    print('24h:',await p.inner_text('.bt-price'),'|',await p.inner_text('.bt-chg'),'|',await p.inner_text('.bt-foot'))
    for n in ['7d','30d']:
      await p.click('#ffFace');await p.wait_for_timeout(4500);await p.screenshot(path=_out(f'/tmp/bt-{n}.png'))
      print(n,':',await p.inner_text('.bt-price'),'|',await p.inner_text('.bt-chg'),'|',await p.inner_text('.bt-foot'))
    await p.click('#ffFace');await p.wait_for_timeout(3000)  # back to 24h
    await ctx.set_offline(True);await p.reload();await p.wait_for_timeout(4000);await p.screenshot(path=_out('/tmp/bt-offline.png'))
    print('offline:',await p.inner_text('.bt-chg'),'|',await p.inner_text('.bt-foot'),'| class',await p.get_attribute('#ffFace','class'))
    print('errors:',[e for e in errs if 'ERR_INTERNET_DISCONNECTED' not in e and 'Failed to load resource' not in e], 'all:',len(errs))
    await ctx.set_offline(False)
    c2=await b.new_context(viewport={'width':438,'height':438},device_scale_factor=2);p2=await c2.new_page();e2=[]
    p2.on('pageerror',lambda e:e2.append(str(e)));p2.on('console',lambda m:e2.append(m.text) if m.type=='error' else None)
    await p2.goto(BASE+'bitcoin.html');await p2.wait_for_timeout(5000);await p2.screenshot(path=_out('/tmp/bt-face.png'));print('face errors',e2)
    await b.close()
asyncio.run(main())
