#!/usr/bin/env python3
"""Check generated documents, references, and optional real HTTP delivery."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.links=[]; self.h1=0; self.lang=None; self.title=False; self.canonical=False; self.missing_alt=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='html':self.lang=a.get('lang')
        if tag=='h1':self.h1+=1
        if tag=='title':self.title=True
        if tag=='link' and a.get('rel')=='canonical':self.canonical=True
        if tag=='img' and 'alt' not in a:self.missing_alt.append(a.get('src'))
        for attr in ('href','src','poster'):
            if attr in a:self.links.append(a[attr])

def check(base=None):
    failures=[]; docs={}; local=set(); external=set(); citations=0
    paths=[ROOT/'index.html',*sorted((ROOT/'research').glob('*/index.html'))]
    article_paths=sorted((ROOT/'content/articles').glob('*.json'))
    assert len(article_paths)>=11,'Expected full research collection'
    for p in paths:
        content=p.read_text(); d=Document(content); docs[p]=d
        if not (d.lang=='en' and d.h1==1 and d.title and d.canonical):failures.append(f'{p.relative_to(ROOT)}: missing document metadata or unique h1')
        if len(d.ids)!=len(set(d.ids)):failures.append(f'{p.relative_to(ROOT)}: duplicate IDs')
        if d.missing_alt:failures.append(f'{p.relative_to(ROOT)}: images without alt')
        if any(x in content for x in ('/Users/','/home/','missionos-internal','localhost:','127.0.0.1:','file://')):failures.append(f'{p.relative_to(ROOT)}: private/local reference')
        for link in d.links:
            u=urlsplit(link)
            if u.scheme in ('http','https'):
                external.add(link);continue
            if u.scheme:continue
            target=ROOT/unquote(u.path).lstrip('/') if u.path.startswith('/') else p.parent/unquote(u.path)
            if not u.path:target=p
            if target.is_dir():target=target/'index.html'
            if not target.exists():failures.append(f'{p.relative_to(ROOT)}: broken {link}');continue
            if u.fragment and target.suffix=='.html':
                other=docs.get(target) or Document(target.read_text())
                if unquote(u.fragment) not in other.ids:failures.append(f'{p.relative_to(ROOT)}: broken anchor {link}')
            if target.suffix=='.json':json.loads(target.read_text())
            local.add('/'+str(target.relative_to(ROOT)))
    for p in article_paths:
        a=json.loads(p.read_text())
        if len(a['abstract'].split())<65:failures.append(f'{p.name}: abstract too short')
        if len(a['sections'])<5 or len(a['sources'])<2:failures.append(f'{p.name}: insufficient paper structure')
        text=' '.join(s['html'] for s in a['sections'])
        citations+=len(re.findall('class="citation"',text))
        if 'class="citation"' not in text:failures.append(f'{p.name}: no evidence citations')
        if len(re.sub('<[^>]*>',' ',text).split())<600:failures.append(f'{p.name}: substantive body missing')
        raw=p.read_text()
        if re.search(r'/Users/|/home/|missionos-internal|localhost:|127\.0\.0\.1:|file://',raw):failures.append(f'{p.name}: local/private data')
        if re.search(r'<script|\son\w+\s*=|javascript:',text,re.I):failures.append(f'{p.name}: executable article content')
    for p in (ROOT/'content/evidence').glob('*.json'):
        json.loads(p.read_text())
        if re.search(r'/Users/|/home/|missionos-internal|localhost:|127\.0\.0\.1:|file://',p.read_text()):failures.append(f'{p.name}: local/private data')
    http_count=0
    if base:
        routes=set(local)|{'/','/assets/site.css','/assets/library.js','/assets/favicon.svg','/sitemap.xml','/robots.txt'}
        routes.update('/research/'+json.loads(p.read_text())['slug']+'/' for p in article_paths)
        for route in sorted(routes):
            try:
                with urlopen(base.rstrip('/')+route,timeout=20) as r:
                    body=r.read()
                    if r.status!=200 or not body:raise ValueError(f'status {r.status} or empty body')
                    if route.endswith(('.html','/')) and b'ASTROPOME AI' not in body:raise ValueError('wrong HTML document')
                    if route.endswith('.json'):json.loads(body)
                http_count+=1
            except Exception as ex:failures.append(f'HTTP {route}: {ex}')
    report={'pages':len(paths),'articles':len(article_paths),'local_targets':len(local),'external_urls':len(external),'inline_citations':citations,'http_routes_checked':http_count,'failures':failures}
    print(json.dumps(report,indent=2))
    return bool(failures)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url');args=parser.parse_args()
    raise SystemExit(check(args.url))
