#!/usr/bin/env python3
"""Render and structurally validate a curated, manually verified JSON edition."""
import argparse, datetime, html, json
from pathlib import Path
from urllib.parse import urlsplit

def esc(s): return html.escape(str(s), quote=True)
def validate(d):
    errs=[]
    try: datetime.date.fromisoformat(d['date'])
    except (KeyError,ValueError,TypeError): errs.append('date must be ISO')
    for name in ('headline','dek'):
        if not isinstance(d.get(name),str) or not d[name].strip(): errs.append(f'missing {name}')
    stories=d.get('stories',[])
    if not isinstance(stories,list) or not stories: errs.append('stories must be nonempty list'); stories=[]
    urls=set(); titles=set()
    fields=('category','title','summary','analysis','evidence_type','source_title','source_url','source_date','limitations')
    for i,s in enumerate(stories):
        for k in fields:
            if not isinstance(s.get(k),str) or not s[k].strip(): errs.append(f'story {i}: missing {k}')
        u=s.get('source_url','')
        p=urlsplit(u)
        if p.scheme!='https' or not p.netloc or p.username or p.password: errs.append(f'story {i}: invalid HTTPS URL')
        if u in urls: errs.append(f'story {i}: duplicate source URL')
        if s.get('title') in titles: errs.append(f'story {i}: duplicate headline')
        urls.add(u); titles.add(s.get('title'))
        dt=s.get('source_date','unknown')
        if dt!='unknown':
            try: datetime.date.fromisoformat(dt)
            except ValueError: errs.append(f'story {i}: invalid source_date')
    l=d.get('learning')
    if not isinstance(l,dict) or not all(isinstance(l.get(k),str) and l[k].strip() for k in ('title','body')): errs.append('learning requires title/body')
    return errs

def render(d):
    articles=''.join(f'<article class="card"><div class="tag">{esc(s["category"])} · {esc(s["source_date"])}</div><h2>{esc(s["title"])}</h2><p>{esc(s["summary"])}</p><div class="insight"><b>Lectura estratégica</b><p>{esc(s["analysis"])}</p></div><p class="limit"><b>Evidencia:</b> {esc(s["evidence_type"])} · <b>Límites:</b> {esc(s["limitations"])}</p><a href="{esc(s["source_url"])}" target="_blank" rel="noopener noreferrer">Fuente directa: {esc(s["source_title"])} ↗</a></article>' for s in d['stories'])
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#121215"><title>{esc(d['headline'])} — The Morning Brief · {esc(d['date'])}</title><link rel="stylesheet" href="/morning-brief/assets/style.css"></head><body><main class="page"><header><b>THE MORNING <span>BRIEF.</span></b><a href="/morning-brief/archive/">ARCHIVO ↗</a></header><section class="hero"><div class="kicker">RED EDITION · {esc(d['date'])}</div><h1>{esc(d['headline'])}</h1><p>{esc(d['dek'])}</p></section><section class="stories">{articles}</section><section class="card learn"><div class="tag">APRENDE EN 3 MINUTOS</div><h2>{esc(d['learning']['title'])}</h2><p>{esc(d['learning']['body'])}</p></section><footer>Curaduría con fuentes enlazadas. Las aplicaciones institucionales son análisis editoriales, no hechos institucionales.</footer></main></body></html>'''

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--edition',required=True); ap.add_argument('--out',default='index.html'); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
    d=json.loads(Path(args.edition).read_text(encoding='utf-8')); errors=validate(d)
    if errors: raise SystemExit('Validation failed:\n'+'\n'.join(errors))
    if not args.check:
        Path(args.out).write_text(render(d),encoding='utf-8'); print(f'Rendered {args.out}')
    else: print('Structural validation passed; editorial source verification must be manual.')
if __name__=='__main__': main()