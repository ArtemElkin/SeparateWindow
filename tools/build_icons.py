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
    if not {'--toolbar-only', '--app-only'}.intersection(sys.argv):
        for size in (16, 32, 48, 128, 256, 512):
            source.resize((size, size), Image.Resampling.LANCZOS).save(ROOT / f'icons/icon{size}.png')
    mark = source.crop((64, 64, 448, 448))
    if '--app-only' not in sys.argv:
        for size in (16, 32, 48):
            mark.resize((size, size), Image.Resampling.LANCZOS).save(ROOT / f'icons/action{size}.png')
    if '--toolbar-only' not in sys.argv:
        for size in (64, 256):
            mark.resize((size, size), Image.Resampling.LANCZOS).save(ROOT / f'icons/app{size}.png')
        sizes = [(size, size) for size in (16, 24, 32, 48, 64, 128, 256)]
        for path in ('icons/favicon.ico', 'docs/favicon.ico'):
            mark.save(ROOT / path, sizes=sizes)
    browser.close()
print('Rendered toolbar icons: 16, 32, 48' if '--toolbar-only' in sys.argv else 'Rendered app icons and favicon.ico')
