"""Render the existing arrow mark as Chrome PNG icons and a favicon."""
from pathlib import Path
import sys
import tempfile
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

with sync_playwright() as p, tempfile.TemporaryDirectory() as temp:
    browser = p.chromium.launch(channel='chromium', headless=True)
    page = browser.new_page(viewport={'width': 128, 'height': 128}, device_scale_factor=4)
    page.set_content('<style>html,body{margin:0;background:transparent}svg{display:block}</style>' + (ROOT / 'icons/mark.svg').read_text())
    raw = Path(temp) / 'master.png'
    page.screenshot(path=str(raw), omit_background=True)
    source = Image.open(raw).convert('RGBA')
    if '--toolbar-only' not in sys.argv:
        for size in (16, 32, 48, 128, 256, 512):
            source.resize((size, size), Image.Resampling.LANCZOS).save(ROOT / f'icons/icon{size}.png')
        source.save(ROOT / 'icons/favicon.ico', sizes=[(16,16), (32,32), (48,48)])
    # Toolbar icons use the full canvas; store icons retain their required padding.
    toolbar = source.crop((64, 64, 448, 448))
    for size in (16, 32, 48):
        toolbar.resize((size, size), Image.Resampling.LANCZOS).save(ROOT / f'icons/action{size}.png')
    browser.close()
print('Rendered toolbar icons: 16, 32, 48' if '--toolbar-only' in sys.argv else 'Rendered toolbar/store icons and favicon.ico')
