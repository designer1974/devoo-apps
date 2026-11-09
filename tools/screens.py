"""Screenshot completi (tutta la pagina) dei siti, con un browser vero (Chromium).
Salva per ogni sito: screens/<host>.jpg (computer, larghezza 1440) e screens/<host>-mobile.jpg (telefono)."""
import sys, time
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

urls = [u.strip() for u in sys.argv[1].split(',') if u.strip()]
# indirizzo con #ancora: foto solo della parte visibile in quel punto (per controllare una sezione)
SCROLL_TO = True
out = Path('screens'); out.mkdir(exist_ok=True)

def shoot(page, url, path):
    page.goto(url, wait_until='networkidle', timeout=60000)
    if '#' in url:
        time.sleep(2.5)
        page.evaluate("document.querySelector(location.hash) && document.querySelector(location.hash).scrollIntoView()")
        time.sleep(3)
        page.screenshot(path=str(path), full_page=False, type='jpeg', quality=85)
        return
    # chiude i banner dei cookie (Accetta / Accetto / Accept / OK)
    for label in ['Accetta', 'Accetto', 'Accetta tutti', 'Accept', 'Accept all', 'OK', 'Ho capito']:
        try:
            btn = page.get_by_role('button', name=label, exact=True)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click(timeout=2000); time.sleep(0.8); break
        except Exception:
            pass
    # scorre fino in fondo per caricare le immagini "lazy", poi torna su
    h = page.evaluate('document.body.scrollHeight')
    for y in range(0, h, 600):
        page.evaluate(f'window.scrollTo(0,{y})'); time.sleep(0.35)
    page.evaluate('window.scrollTo(0,0)')
    try:
        page.wait_for_load_state('networkidle', timeout=15000)
    except Exception:
        pass
    time.sleep(3)
    page.screenshot(path=str(path), full_page=True, type='jpeg', quality=82)

with sync_playwright() as p:
    b = p.chromium.launch()
    for u in urls:
        if not u.startswith('http'): u = 'https://' + u
        host = urlparse(u).hostname + ('-' + urlparse(u).fragment if urlparse(u).fragment else '')
        try:
            d = b.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
            shoot(d, u, out / f'{host}.jpg'); d.close()
            m = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
            shoot(m, u, out / f'{host}-mobile.jpg'); m.close()
            print('OK', host)
        except Exception as e:
            print('ERRORE', host, e)
    b.close()
