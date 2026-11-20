"""Build the static Russian and English Separate Window landing pages."""

import json
import re
import tarfile
from html import escape
from pathlib import Path
from shutil import copyfile
from string import Template

from PIL import Image


SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parent
OUTPUT = ROOT / 'dist' / 'website'
HOST = 'https://separate.maark.ru'
STORE = 'https://chromewebstore.google.com/detail/separate-window/fhcafcdfknddjfgbbkhpglgamceiclcm'
ROUTES = {'ru': '/', 'en': '/en/'}


def write(path, content):
    target = OUTPUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8', newline='\n')


def main():
    template = Template((SOURCE / 'index.html').read_text(encoding='utf-8'))
    copy = json.loads((SOURCE / 'copy.json').read_text(encoding='utf-8'))
    for lang, path in ROUTES.items():
        variables = {key: escape(value, quote=True) for key, value in copy[lang].items()}
        current = ' aria-current="page"'
        page = template.substitute(
            **variables, lang=lang, home=path, canonical=HOST + path, store=STORE,
            current_ru=current if lang == 'ru' else '',
            current_en=current if lang == 'en' else '',
        )
        write(path.lstrip('/') + 'index.html', page)
    write('404.html', (SOURCE / '404.html').read_text(encoding='utf-8'))
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {HOST}/sitemap.xml\n')
    urls = '\n'.join(f'  <url><loc>{HOST}{path}</loc></url>' for path in ROUTES.values())
    write('sitemap.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n'
                         f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')

    privacy = (ROOT / 'docs' / 'privacy.html').read_text(encoding='utf-8')
    style = re.search(r'<style>(.*?)</style>', privacy, flags=re.DOTALL)
    write('assets/privacy.css', style.group(1).strip() + '\n')
    privacy = privacy.replace(style.group(), '<link rel="stylesheet" href="/assets/privacy.css">')
    privacy = privacy.replace('src="store/assets/icon128.png"', 'src="/assets/icon.png"')
    privacy = privacy.replace('<body><main>', '<body><main><p><a href="/">Separate Window</a></p>')
    write('privacy.html', privacy)

    assets = OUTPUT / 'assets'
    store_assets = ROOT / 'docs' / 'store' / 'assets'
    promo = store_assets / 'promo-1400x560.png'
    copyfile(ROOT / 'icons' / 'favicon.ico', OUTPUT / 'favicon.ico')
    copyfile(ROOT / 'icons' / 'icon128.png', assets / 'icon.png')
    copyfile(promo, assets / 'share.png')
    for filename in ('site.css', 'site.js'):
        copyfile(SOURCE / filename, assets / filename)
    with Image.open(promo) as artwork:
        artwork.crop((880, 180, 1336, 437)).convert('RGB').save(assets / 'landscape.webp', quality=88)

    bundle = OUTPUT.with_name('separate-window-website.tar.gz')
    with tarfile.open(bundle, 'w:gz') as archive:
        archive.add(OUTPUT, arcname='public')
        for config in sorted(SOURCE.glob('nginx-*.conf')):
            archive.add(config, arcname=config.name)
    print(f'Built {bundle.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
