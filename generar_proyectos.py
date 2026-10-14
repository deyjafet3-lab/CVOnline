#!/usr/bin/env python3
"""Lee la carpeta proyectos/ y actualiza la lista de fotos de cada proyecto en index.html.

Uso (en la carpeta donde estan index.html y proyectos/):
    python generar_proyectos.py

- Cada subcarpeta de proyectos/ es un proyecto; sus imagenes (jpg, png, webp, gif, avif)
  se ordenan por nombre (foto1, foto2, ... foto10) y la primera es la portada.
- Si el proyecto ya existe en index.html (mismo nombre de carpeta o mismo titulo),
  conserva su titulo, categoria, descripcion y link de Behance; solo actualiza las fotos.
- Si es nuevo, lo agrega con el nombre de la carpeta como titulo.
"""
import json, os, re, sys, unicodedata
from urllib.parse import quote

INDEX = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
ROOT = 'proyectos'
EXT = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif')

def slug(t):
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def nat(s):
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r'(\d+)', s)]

html = open(INDEX, encoding='utf-8').read()
m = re.search(r'(<script id="data" type="application/json">)(.*?)(</script>)', html, re.S)
if not m:
    sys.exit('No encontre <script id="data"> en ' + INDEX)
D = json.loads(m.group(2))
P = D.setdefault('projects', [])
by = {}
for p in P:
    by[slug(p.get('folder') or p.get('title', ''))] = p

if not os.path.isdir(ROOT):
    sys.exit('No existe la carpeta ' + ROOT + '/ junto a ' + INDEX)

nuevos = actualizados = 0
for name in sorted(os.listdir(ROOT), key=nat):
    d = os.path.join(ROOT, name)
    if not os.path.isdir(d):
        continue
    files = sorted([f for f in os.listdir(d) if f.lower().endswith(EXT)], key=nat)
    if not files:
        continue
    imgs = ['%s/%s/%s' % (ROOT, quote(name), quote(f)) for f in files]
    p = by.get(slug(name))
    if p:
        actualizados += 1
    else:
        p = {'id': int.from_bytes(name.encode()[:6], 'big'), 'title': re.sub(r'[-_]+', ' ', name).strip().title(),
             'cat': '', 'desc': '', 'link': ''}
        P.insert(0, p)
        nuevos += 1
    p['folder'] = name
    p['imgs'] = imgs
    print('%-28s %2d fotos' % (name, len(imgs)))

out = json.dumps(D, ensure_ascii=False).replace('<', '\\u003c')
open(INDEX, 'w', encoding='utf-8').write(html[:m.start(2)] + out + html[m.end(2):])
print('Listo: %d nuevos, %d actualizados.' % (nuevos, actualizados))
