#!/usr/bin/env python3
import argparse,datetime,html,json
from pathlib import Path
from urllib.parse import urlsplit
def e(s): return html.escape(str(s),quote=True)
def validate(d):
 errors=[]
 try: datetime.date.fromisoformat(d['date'])
 except (ValueError,KeyError,TypeError): errors.append('Invalid date')
 for k in ('headline','dek'):
  if not isinstance(d.get(k),str) or not d[k].strip(): errors.append('Missing '+k)
 stories=d.get('stories',[])
 if not isinstance(stories,list) or not stories: errors.append('Missing stories'); stories=[]
 seen=set()
 for i,s in enumerate(stories):
  for k in ('category','title','summary','analysis','evidence_type','source_title','source_url','source_date','limitations'):
   if not isinstance(s.get(k),str) or not s[k].strip(): errors.append(f'{i}: missing {k}')
  u=s.get('source_url','')
  p=urlsplit(u)
  if p.scheme!='https' or not p.netloc or p.username or p.password or u in seen: errors.append(f'{i}: invalid/duplicate URL')
  seen.add(u)
 l=d.get('learning',{})
 if not isinstance(l,dict) or not l.get('title') or not l.get('body'): errors.append('Missing learning')
 return errors
def render(d):
 cards=[]
 for s in d['stories']:
  cards.append(f'<article class="card"><div class="tag">{e(s["category"])} · {e(s["source_date"])}</div><h2>{e(s["title"])}</h2><p>{e(s["summary"])}</p><div class="insight"><b>Lectura estratégica</b><p>{e(s["analysis"])}</p></div><p class="limit"><b>Tipo de evidencia:</b> {e(s["evidence_type"])} · <b>Límites:</b> {e(s["limitations"])}</p><a target="_blank" rel="noopener noreferrer" href="{e(s["source_url"])}">Fuente directa: {e(s["source_title"])} ↗</a></article>')
 return '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(d['headline'])+' — The Morning Brief</title><link rel="stylesheet" href="assets/style.css"></head><body><main class="page"><header><b>THE MORNING <span>BRIEF.</span></b><a href="archive/">ARCHIVO ↗</a></header><div class="hero"><div class="kicker">RED EDITION · '+e(d['date'])+'</div><h1>'+e(d['headline'])+'</h1><p>'+e(d['dek'])+'</p></div><div class="stories">'+''.join(cards)+'</div><section class="card learn"><div class="tag">APRENDE EN 3 MINUTOS</div><h2>'+e(d['learning']['title'])+'</h2><p>'+e(d['learning']['body'])+'</p></section><footer>Edición con fuentes enlazadas; las interpretaciones institucionales se distinguen de hechos verificados.</footer></main></body></html>'
p=argparse.ArgumentParser();p.add_argument('--edition',required=True);p.add_argument('--out',default='index.html');p.add_argument('--check',action='store_true');a=p.parse_args()
d=json.loads(Path(a.edition).read_text(encoding='utf8'));errs=validate(d)
if errs: raise SystemExit('\n'.join(errs))
if not a.check: Path(a.out).write_text(render(d),encoding='utf8')
print('Validation passed; source semantics still require manual review')
