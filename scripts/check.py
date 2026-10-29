#!/usr/bin/env python3
"""Check generated documents, references, and optional real HTTP delivery."""
import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
MEDIA_MARKER=re.compile(r'<!--\s*media:([^\s<>]+)\s*-->')
JAPANESE_CHAR=re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff々〆]')

def japanese_length(text):
    return len(JAPANESE_CHAR.findall(html.unescape(re.sub('<[^>]*>',' ',text))))

class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.links=[]; self.h1=0; self.lang=None; self.title=False; self.canonical=False; self.missing_alt=[]; self.videos=[]; self.iframes=[]; self.media_markers=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='html':self.lang=a.get('lang')
        if tag=='h1':self.h1+=1
        if tag=='title':self.title=True
        if tag=='link' and a.get('rel')=='canonical':self.canonical=True
        if tag=='img' and 'alt' not in a:self.missing_alt.append(a.get('src'))
        if tag=='video':self.videos.append(a)
        if tag=='iframe':self.iframes.append(a)
        for attr in ('href','src','poster'):
            if attr in a:self.links.append(a[attr])
    def handle_comment(self,data):
        if data.strip().startswith('media:'):self.media_markers.append(data)

def check(base=None):
    failures=[]; docs={}; local=set(); external=set(); citations=0; videos=0; youtube_embeds=0; required_media=set()
    def require_local_media(value, article):
        if not isinstance(value,str) or not value.startswith('/') or value.startswith('//') or urlsplit(value).query or urlsplit(value).fragment:
            failures.append(f'{article}: media requires a local absolute path: {value}')
            return
        target=ROOT/value.lstrip('/')
        if not target.is_file():failures.append(f'{article}: missing media {value}')
        required_media.add(value)
    paths=[ROOT/'index.html',*sorted((ROOT/'research').glob('*/index.html'))]
    article_paths=sorted((ROOT/'content/articles').glob('*.json'))
    assert len(article_paths)>=11,'Expected full research collection'
    expected_languages={}
    for p in article_paths:
        article=json.loads(p.read_text())
        expected_languages[ROOT/'research'/article['slug']/'index.html']=article.get('language','en')
    for p in paths:
        content=p.read_text(); d=Document(content); docs[p]=d
        expected_language=expected_languages.get(p,'en')
        if not (d.lang==expected_language and d.h1==1 and d.title and d.canonical):failures.append(f'{p.relative_to(ROOT)}: missing document metadata, matching language, or unique h1')
        if p in expected_languages:
            schemas=re.findall(r'<script type="application/ld\+json">(.*?)</script>',content,re.S)
            try:
                if len(schemas)!=1 or json.loads(schemas[0]).get('inLanguage')!=expected_language:
                    failures.append(f'{p.relative_to(ROOT)}: JSON-LD language does not match article')
            except (json.JSONDecodeError,AttributeError):
                failures.append(f'{p.relative_to(ROOT)}: invalid article JSON-LD')
        if len(d.ids)!=len(set(d.ids)):failures.append(f'{p.relative_to(ROOT)}: duplicate IDs')
        if d.missing_alt:failures.append(f'{p.relative_to(ROOT)}: images without alt')
        if d.media_markers:failures.append(f'{p.relative_to(ROOT)}: unresolved inline media markers')
        for video in d.videos:
            videos+=1
            if 'controls' not in video or 'playsinline' not in video or video.get('preload')!='none' or 'autoplay' in video or not video.get('poster') or not video.get('aria-label'):
                failures.append(f'{p.relative_to(ROOT)}: video controls, loading, poster, or label contract')
        for frame in d.iframes:
            match=re.fullmatch(r'https://www\.youtube-nocookie\.com/embed/([A-Za-z0-9_-]{11})',frame.get('src',''))
            if not match:
                failures.append(f'{p.relative_to(ROOT)}: unexpected iframe or invalid YouTube embed URL')
                continue
            youtube_embeds+=1
            if frame.get('loading')!='lazy' or not frame.get('title') or frame.get('referrerpolicy')!='strict-origin-when-cross-origin' or 'allowfullscreen' not in frame or 'autoplay' in frame.get('allow',''):
                failures.append(f'{p.relative_to(ROOT)}: YouTube loading, label, referrer, fullscreen, or autoplay contract')
            if 'https://www.youtube.com/watch?v='+match.group(1) not in d.links:
                failures.append(f'{p.relative_to(ROOT)}: missing YouTube fallback link')
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
        language=a.get('language','en')
        if language not in ('en','ja'):failures.append(f'{p.name}: unsupported language')
        abstract_short=japanese_length(a['abstract'])<160 if language=='ja' else len(a['abstract'].split())<65
        if abstract_short:failures.append(f'{p.name}: abstract too short')
        if len(a['sections'])<5 or len(a['sources'])<2:failures.append(f'{p.name}: insufficient paper structure')
        text=' '.join(s['html'] for s in a['sections'])
        citations+=len(re.findall('class="citation"',text))+len(a.get('media',[]))
        if 'class="citation"' not in text:failures.append(f'{p.name}: no evidence citations')
        body_short=japanese_length(text)<1500 if language=='ja' else len(re.sub('<[^>]*>',' ',text).split())<600
        if body_short:failures.append(f'{p.name}: substantive body missing')
        raw=p.read_text()
        if re.search(r'/Users/|/home/|missionos-internal|localhost:|127\.0\.0\.1:|file://',raw):failures.append(f'{p.name}: local/private data')
        if re.search(r'<script|\son\w+\s*=|javascript:',text,re.I):failures.append(f'{p.name}: executable article content')
        if re.search(r'<iframe\b',text,re.I):failures.append(f'{p.name}: iframe must use validated media metadata')
        media_items=a.get('media',[])
        media_by_id={item['id']:item for item in media_items}
        if len(media_by_id)!=len(media_items):failures.append(f'{p.name}: duplicate media IDs')
        markers=[(section['id'], media_id) for section in a['sections'] for media_id in MEDIA_MARKER.findall(section['html'])]
        if len(re.findall(r'<!--\s*media:.*?-->',text,re.S))!=len(markers):failures.append(f'{p.name}: malformed inline media marker')
        for section_id,media_id in markers:
            item=media_by_id.get(media_id)
            if not item or item.get('inline') is not True or item.get('after_section')!=section_id:
                failures.append(f'{p.name}: invalid inline media marker {section_id}/{media_id}')
        expected_embeds=[]
        source_ids={source['id'] for source in a['sources']}
        section_ids={section['id'] for section in a['sections']}
        rendered=docs.get(ROOT/'research'/a['slug']/'index.html')
        if not rendered:failures.append(f'{p.name}: generated article missing')
        if a.get('references_before'):
            before=a['references_before']
            if before not in section_ids:
                failures.append(f'{p.name}: invalid references_before section')
            elif rendered and ('references' not in rendered.ids or before not in rendered.ids or rendered.ids.index('references')>rendered.ids.index(before)):
                failures.append(f'{p.name}: references rendered after requested section')
        for download in a.get('downloads',[]):
            url=download.get('url','')
            if not download.get('label') or not url.startswith('/') or url.startswith('//') or not (ROOT/url.lstrip('/')).is_file():
                failures.append(f'{p.name}: invalid or missing download')
            if rendered and url not in rendered.links:failures.append(f'{p.name}: missing rendered download {url}')
        for item in media_items:
            label=f'{p.name}: {item["id"]}'
            kind=item.get('type')
            if kind not in ('image','video','youtube'):
                failures.append(f'{label}: unsupported media type')
                continue
            if item.get('after_section') not in section_ids|{'lead'} or item.get('source_ref') not in source_ids or not item.get('source_url'):
                failures.append(f'{label}: invalid placement or source reference')
            if 'inline' in item and not isinstance(item['inline'],bool):failures.append(f'{label}: inline must be boolean')
            if item.get('inline') is True and markers.count((item.get('after_section'),item['id']))!=1:
                failures.append(f'{label}: expected exactly one inline marker in after_section')
            if rendered and rendered.ids.count(item['id'])!=1:failures.append(f'{label}: media must render exactly once')
            if any(not isinstance(item.get(size),int) or item[size]<=0 for size in ('width','height')):
                failures.append(f'{label}: invalid media dimensions')
            if kind=='youtube':
                youtube_id=item.get('youtube_id','')
                if not re.fullmatch(r'[A-Za-z0-9_-]{11}',youtube_id) or item.get('src')!='https://www.youtube.com/watch?v='+youtube_id:
                    failures.append(f'{label}: invalid YouTube ID or watch URL')
                else:expected_embeds.append('https://www.youtube-nocookie.com/embed/'+youtube_id)
            else:require_local_media(item.get('src'),label)
            if kind in ('video','youtube'):
                require_local_media(item.get('poster'),label)
                if not isinstance(item.get('duration_seconds'),(int,float)) or item['duration_seconds']<=0:
                    failures.append(f'{label}: invalid video duration')
        if rendered and sorted(frame.get('src','') for frame in rendered.iframes)!=sorted(expected_embeds):
            failures.append(f'{p.name}: rendered YouTube embeds do not match article media')
        if a.get('cover'):
            require_local_media(a['cover'].get('src'),p.name)
            if not a['cover'].get('alt'):failures.append(f'{p.name}: cover requires alt text')
    for p in (ROOT/'content/evidence').glob('*.json'):
        json.loads(p.read_text())
        if re.search(r'/Users/|/home/|missionos-internal|localhost:|127\.0\.0\.1:|file://',p.read_text()):failures.append(f'{p.name}: local/private data')
    media_manifest=ROOT/'assets/media/provenance.json'
    verified_media=0; manifest_paths=set()
    if media_manifest.exists():
        for media in json.loads(media_manifest.read_text())['files']:
            if media['path'] in manifest_paths:failures.append(f'{media["path"]}: duplicate media provenance')
            manifest_paths.add(media['path'])
            target=ROOT/media['path'].lstrip('/')
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=media['sha256']:
                failures.append(f'{media["path"]}: media provenance mismatch')
            else:verified_media+=1
    for path in sorted(required_media-manifest_paths):
        failures.append(f'{path}: media provenance entry missing')
    publication_manifest=ROOT/'content/evidence/control-layer-paper-publication.json'
    verified_publication_files=0
    if publication_manifest.exists():
        publication=json.loads(publication_manifest.read_text())
        publication_paths=set()
        publication_root=(ROOT/'publications').resolve()
        entries=publication.get('files')
        if not isinstance(entries,list) or not entries or not isinstance(publication.get('original_zip'),dict):
            failures.append(f'{publication_manifest.name}: missing publication files or original ZIP metadata')
        else:
            for entry in entries+[publication['original_zip']]:
                path=entry.get('path','') if isinstance(entry,dict) else ''
                if not isinstance(path,str) or not path.startswith('/publications/') or urlsplit(path).query or urlsplit(path).fragment:
                    failures.append(f'{publication_manifest.name}: invalid publication path {path}')
                    continue
                target=ROOT/path.lstrip('/')
                if not target.resolve().is_relative_to(publication_root) or path in publication_paths:
                    failures.append(f'{path}: escaped or duplicate publication path')
                    continue
                publication_paths.add(path)
                if not isinstance(entry.get('bytes'),int) or entry['bytes']<0 or not isinstance(entry.get('sha256'),str) or not re.fullmatch(r'[0-9a-f]{64}',entry['sha256']):
                    failures.append(f'{path}: invalid publication integrity metadata')
                    continue
                if not target.is_file():
                    failures.append(f'{path}: publication file missing')
                    continue
                payload=target.read_bytes()
                if len(payload)!=entry['bytes'] or hashlib.sha256(payload).hexdigest()!=entry['sha256']:
                    failures.append(f'{path}: publication size or SHA-256 mismatch')
                else:verified_publication_files+=1
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
    report={'pages':len(paths),'articles':len(article_paths),'local_targets':len(local),'external_urls':len(external),'inline_citations':citations,'videos':videos,'youtube_embeds':youtube_embeds,'verified_media_files':verified_media,'verified_publication_files':verified_publication_files,'http_routes_checked':http_count,'failures':failures}
    print(json.dumps(report,indent=2))
    return bool(failures)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url');args=parser.parse_args()
    raise SystemExit(check(args.url))
