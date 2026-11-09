"""Fotografa ogni scheda dello slideshow di devoo.it in versione telefono (controllo)."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
out = Path('screens'); out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    m = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    m.goto('https://devoo.it/?v=' + str(int(time.time())) + '#progetti', wait_until='networkidle', timeout=60000)
    time.sleep(2)
    m.evaluate("document.querySelector('#progetti').scrollIntoView()")
    for k in range(5):
        m.evaluate(f"dvPrj.to({k}, true)"); time.sleep(2.5)
        info = m.evaluate(f"""(() => {{ const c = document.querySelectorAll('.prj-card')[{k}]; const i = c.querySelector('img');
           const f = c.querySelector('.prj-shot').getBoundingClientRect(); const r = i.getBoundingClientRect();
           return [i.currentSrc.split('/').pop(), i.naturalWidth, i.naturalHeight, Math.round(f.width), Math.round(f.height), Math.round(r.width), Math.round(r.height)]; }})()""")
        print('card', k, info)
        m.screenshot(path=str(out / f'check-card-{k}.jpg'), type='jpeg', quality=80)
    b.close()
