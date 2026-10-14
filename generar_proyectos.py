#!/usr/bin/env python3
"""Genera proyectos.json a partir de la carpeta Proyectos/ (mayusculas o minusculas).

Cada subcarpeta = un proyecto. Se toman TODAS las imagenes (jpg, png, webp, gif, avif),
sin importar como se llamen, ordenadas por nombre (la primera es la portada).
Opcional: dentro de la carpeta puedes poner info.json:
    {"titulo": "Ennova Brand", "categoria": "Branding", "descripcion": "...", "link": "https://www.behance.net/..."}
Lo ejecuta GitHub Actions en cada subida; tambien puedes correrlo a mano: python generar_proyectos.py
"""
import json, os, re, subprocess
from urllib.parse import quote

EXT = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif')

def nat(s):
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r'(\d+)', s)]

def first_commit_ts(path):
    try:
        out = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%ct', '--', path],
                             capture_output=True, text=True, timeout=60).stdout.split()
        return int(out[-1]) if out else 0
    except Exception:
        return 0

root = next((d for d in sorted(os.listdir('.')) if d.lower() == 'proyectos' and os.path.isdir(d)), None)
projects = []
if not root:
    print('Aviso: no encontre la carpeta Proyectos/. Se genera un proyectos.json vacio.')
else:
    for name in sorted(os.listdir(root), key=nat):
        d = os.path.join(root, name)
        if name.startswith('.') or not os.path.isdir(d):
            continue
        files = sorted([f for f in os.listdir(d) if f.lower().endswith(EXT) and not f.startswith('.')], key=nat)
        if not files:
            continue
        info = {}
        ip = os.path.join(d, 'info.json')
        if os.path.isfile(ip):
            try:
                info = json.load(open(ip, encoding='utf-8-sig'))
            except Exception as e:
                print('Aviso: info.json invalido en', name, e)
        g = lambda *k: next((str(info[x]).strip() for x in k if info.get(x)), '')
        projects.append({
            'folder': name,
            'title': g('titulo', 'title') or re.sub(r'[-_]+', ' ', name).strip().title(),
            'cat': g('categoria', 'cat'),
            'desc': g('descripcion', 'desc'),
            'link': g('link', 'behance'),
            'imgs': ['%s/%s/%s' % (quote(root), quote(name), quote(f)) for f in files],
            't': first_commit_ts(d),
        })
        print('%-30s %3d fotos' % (name, len(files)))
    projects.sort(key=lambda p: (-p['t'], nat(p['folder'])))

with open('proyectos.json', 'w', encoding='utf-8') as f:
    json.dump({'projects': projects}, f, ensure_ascii=False, indent=1)
print('proyectos.json listo con %d proyecto(s).' % len(projects))
