#!/usr/bin/env python3
"""Render the research library using only Python's standard library."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://astropomeai.com'
DATE = '2026-10-22'
MISSION_SHA = '7f0128491ac1e998c05580b50707ee8cab7543c6'
ORDER = ['mission-assurance', 'world-model-stacking', 'robot-manipulation-repair', 'quadruped-delivery', 'urban-drone-recovery', 'temporal-landing-decisions', 'maritime-mission-assurance', 'starship-mission-simulation', 'dna-observation-design', 'dna-replication-completion', 'dna-initiation-mechanisms']
e = html.escape

def words(article):
    return len(re.sub('<[^>]+>', ' ', article['abstract'] + ' '.join(s['html'] for s in article['sections']) + ' '.join(m['caption'] for m in article.get('media', []))).split())

def header():
    return '''<a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="/" aria-label="Astropome AI home"><img src="/assets/favicon.svg" alt="" width="34" height="34"><span><strong>ASTROPOME AI</strong><small>Independent research</small></span></a><nav class="site-nav" aria-label="Main navigation"><a href="/#research">Research</a><a href="/#about">About</a><a class="external secondary" href="https://github.com/pome223/missionos">Code</a><a class="external secondary" href="https://medium.com/@astropomeai">Medium</a></nav></div></header>'''

def footer():
    return '''<footer class="site-footer"><div class="wrap footer-inner"><span>© 2026 Astropome AI · Independent research, open questions.</span><nav class="footer-links" aria-label="External links"><a class="external" href="https://github.com/pome223/missionos">MissionOS</a><a class="external" href="https://github.com/pome223/astropomeai">Website source</a><a class="external" href="https://medium.com/@astropomeai">Medium</a><a class="external" href="https://note.com/astropomeai">note</a></nav></div></footer>'''

def document(title, description, path, body, schema=None, library=False, media=False):
    metadata = '' if not schema else '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    if media:
        metadata += '<script src="/assets/media.js" defer></script>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} · Astropome AI</title><meta name="description" content="{e(description, quote=True)}"><meta name="theme-color" content="#192d32"><link rel="canonical" href="{BASE}{path}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/media.css"><meta property="og:type" content="{'website' if library else 'article'}"><meta property="og:title" content="{e(title, quote=True)}"><meta property="og:description" content="{e(description, quote=True)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:site_name" content="Astropome AI"><meta name="twitter:card" content="summary">{metadata}{'<script src="/assets/library.js" defer></script>' if library else ''}</head><body>{header()}{body}{footer()}</body></html>\n'''

def art():
    return '''<div class="hero-visual"><div class="visual-top"><span>Field notes / 001</span><span>Control · Coordination</span></div><svg viewBox="0 0 500 470" fill="none" aria-hidden="true"><defs><pattern id="grid" width="35" height="35" patternUnits="userSpaceOnUse"><path d="M35 0H0V35" stroke="#b4c5b9" stroke-opacity=".08"/></pattern></defs><rect width="500" height="470" fill="url(#grid)"/><circle cx="250" cy="224" r="145" stroke="#819990" stroke-opacity=".28"/><circle cx="250" cy="224" r="103" stroke="#819990" stroke-opacity=".35" stroke-dasharray="3 9"/><ellipse cx="250" cy="224" rx="193" ry="67" transform="rotate(-34 250 224)" stroke="#dcaa82" stroke-width="1.6"/><ellipse cx="250" cy="224" rx="165" ry="83" transform="rotate(39 250 224)" stroke="#7f9b8e" stroke-width="1.1"/><path d="M155 265L210 172L316 188L345 285L240 327Z M210 172L240 327 M155 265L316 188 M316 188L240 327" stroke="#9fb4a6" stroke-opacity=".45"/><circle cx="210" cy="172" r="6" fill="#efbd93"/><circle cx="316" cy="188" r="5" fill="#dfe9d9"/><circle cx="155" cy="265" r="5" fill="#dfe9d9"/><circle cx="345" cy="285" r="5" fill="#dfe9d9"/><circle cx="240" cy="327" r="6" fill="#efbd93"/><circle cx="250" cy="224" r="16" fill="#c2d4c3" fill-opacity=".1"/><circle cx="250" cy="224" r="4" fill="#f4f1e9"/><path d="M244 224H221M256 224H279M250 218V195M250 230V253" stroke="#f4f1e9" stroke-opacity=".5"/><circle cx="407" cy="115" r="5" fill="#e6b189"/></svg><div class="visual-bottom"><span>From autonomous missions<br> to molecular systems.</span><strong>A study in coordination ↗</strong></div></div>'''

def media_figure(item):
    caption_id = 'caption-' + item['id']
    source = f'<a class="citation" href="#{e(item["source_ref"])}">[{e(item["source_ref"].removeprefix("s"))}]</a>'
    if item['type'] == 'video':
        minutes, seconds = divmod(round(item['duration_seconds']), 60)
        label = f'Recorded video · {minutes}:{seconds:02d}'
        visual = f'<video controls playsinline preload="none" poster="{e(item["poster"])}" width="{item["width"]}" height="{item["height"]}" aria-label="{e(item["title"])}" aria-describedby="{caption_id}"><source src="{e(item["src"])}" type="video/mp4"><p><a href="{e(item["src"])}">Open this video</a>.</p></video>'
        link_label = 'Open video'
    else:
        label = 'Figure · Select to enlarge'
        visual = f'<a href="{e(item["src"])}" class="zoom-link" data-zoom aria-label="Enlarge: {e(item["title"])}"><img src="{e(item["src"])}" alt="{e(item["alt"])}" loading="lazy" decoding="async" width="{item["width"]}" height="{item["height"]}"><span class="zoom-hint" aria-hidden="true">↗</span></a>'
        link_label = 'Full-size image'
    return f'<figure class="media-item media-item--{item["type"]}" id="{e(item["id"])}"><div class="media-label">{label}</div>{visual}<figcaption id="{caption_id}"><strong>{e(item["title"])}</strong><p>{e(item["caption"])} {source}</p><div class="media-links"><a href="{e(item["src"])}">{link_label} ↗</a><a href="{e(item["source_url"])}">Original source ↗</a></div></figcaption></figure>'

def media_at(article, section):
    items = [m for m in article.get('media', []) if m['after_section'] == section]
    return '<div class="media-gallery">' + ''.join(media_figure(m) for m in items) + '</div>' if items else ''

def featured_films(articles):
    features = []
    for slug, label in [('starship-mission-simulation', 'Launch, deploy, return'), ('urban-drone-recovery', 'Across Yokohama'), ('world-model-stacking', 'When should a robot stop?')]:
        a = next((a for a in articles if a['slug'] == slug), None)
        lead = next((m for m in (a or {}).get('media', []) if m['after_section'] == 'lead'), None)
        if not lead:
            continue
        features.append(f'<a class="film-card" href="/research/{slug}/#{e(lead["id"])}"><span class="film-image"><img src="{e(lead["poster"])}" alt="{e(lead["alt"])}" loading="lazy" width="{lead["width"]}" height="{lead["height"]}"><span class="play-mark" aria-hidden="true">▶</span></span><span class="eyebrow">{e(a["domain"])}</span><strong>{label}</strong><span class="film-action">Watch the recorded experiment ↗</span></a>')
    return '<section class="films-section" aria-labelledby="films-title"><div class="section-head"><div><div class="eyebrow">From the experiment record</div><h2 id="films-title">See the research in motion.</h2></div><p>Saved simulations, with the evidence in view.</p></div><div class="films-grid">' + ''.join(features) + '</div></section>' if features else ''

def render_home(articles):
    cards = []
    for i,a in enumerate(articles,1):
        search = e(' '.join([a['title'], a['subtitle'], a['summary'], a['domain'], *a['keywords']]).lower(), quote=True)
        lead = next((m for m in a.get('media', []) if m['after_section'] == 'lead'), None)
        cover = f'<a class="card-cover" href="/research/{a["slug"]}/#{lead["id"]}" aria-label="Watch {e(a["title"])}"><img src="{e(lead["poster"])}" alt="" loading="lazy"><span>▶ Video &amp; figures</span></a>' if lead else ''
        cards.append(f'''<article class="research-card" data-domain="{e(a['domain'], quote=True)}" data-search="{search}">{cover}<div class="card-top"><span class="card-domain">{e(a['domain'])}</span><span class="card-number">{i:02d}</span></div><h3><a href="/research/{a['slug']}/">{e(a['title'])}</a></h3><p>{e(a['summary'])}</p><div class="card-footer"><span>{max(1,round(words(a)/200))} min read · Research article</span><a href="/research/{a['slug']}/" aria-label="Read {e(a['title'], quote=True)}">Read article ↗</a></div></article>''')
    domains = list(dict.fromkeys(a['domain'] for a in articles))
    filters = '<button type="button" data-filter="all" aria-pressed="true">All research</button>' + ''.join(f'<button type="button" data-filter="{e(d, quote=True)}" aria-pressed="false">{e(d)}</button>' for d in domains)
    body = f'''<main id="main" class="wrap"><section class="hero" aria-labelledby="hero-title"><div><div class="eyebrow">Research at the boundaries of intelligence</div><h1 id="hero-title">How do complex<br> systems <em>coordinate?</em></h1><p>From AI that supervises a robot mission to the molecular machinery that copies a genome. Experiments, models, and the evidence behind what they can do.</p><div class="hero-links"><a href="#research">Explore the research ↓</a><a class="external" href="https://github.com/pome223/missionos">Explore MissionOS</a></div></div>{art()}</section><div class="ledger"><span><strong>{len(articles):02d}</strong> research articles</span><span><strong>{len(domains):02d}</strong> research areas</span><span>Methods · Results · Open questions</span><span class="edition">Edition 01 / 22 October 2026</span></div>{featured_films(articles)}<section class="research-section" id="research" aria-labelledby="research-title"><div class="section-head"><div><div class="eyebrow">The research library</div><h2 id="research-title">Studies &amp; experiments</h2></div><div class="search-box"><label for="research-search" class="search-label">Search by topic or keyword</label><input id="research-search" type="search" placeholder="Try world models or DNA…" autocomplete="off"></div></div><div class="filters" role="group" aria-label="Filter research by area">{filters}</div><p id="result-count" class="eyebrow" aria-live="polite">{len(articles)} articles</p><div class="research-grid">{''.join(cards)}</div><p id="empty-results" class="empty-results" hidden>No matching articles. Try another keyword or select All research.</p><noscript><p>All research articles are available below; filtering requires JavaScript.</p></noscript></section><section id="about" class="about-block" aria-labelledby="about-title"><div><div class="eyebrow">About this collection</div><h2 id="about-title">A result is only as useful<br> as its evidence.</h2></div><div><p>Astropome AI is an independent research project exploring governed AI, autonomous systems, and computational biology. These articles bring together the question, the method, the measured result, and the limits of each study.</p><p>The MissionOS articles are based on <a href="https://github.com/pome223/missionos/tree/{MISSION_SHA}">a pinned snapshot of the public main branch</a>. The biology articles introduce curated summaries of saved computational studies, with links to their published biological context and supplementary evidence.</p><p>These are technical research articles, not peer-reviewed publications. Simulator outcomes, synthetic data, and empirical observations are identified within each article. Negative results remain part of the record.</p></div></section></main>'''
    schema = {'@context':'https://schema.org','@type':'CollectionPage','name':'Astropome AI research library','url':BASE+'/', 'hasPart':[{'@type':'ScholarlyArticle','headline':a['title'],'url':BASE+'/research/'+a['slug']+'/'} for a in articles]}
    (ROOT/'index.html').write_text(document('Research in AI, autonomous systems & computational biology','Independent research on MissionOS, robot learning, autonomous missions, and DNA replication. Methods, measured results, limitations, and sources.','/',body,schema,True))

def render_article(a):
    toc = ''.join(f'<li><a href="#{e(s["id"], quote=True)}">{e(s["title"])}</a></li>' for s in a['sections'])
    parts = []
    for s in a['sections']:
        content = re.sub(r'(<table\b.*?</table>)',r'<div class="table-scroll">\1</div>',s['html'],flags=re.S)
        parts.append(f'<section id="{e(s["id"], quote=True)}"><h2>{e(s["title"])}</h2>{content}{media_at(a, s["id"])}</section>')
    references = ''.join(f'<li id="{e(s["id"], quote=True)}"><a href="{e(s["url"], quote=True)}">{e(s["title"])}</a><span class="ref-detail">{e(s.get("detail",""))}</span></li>' for s in a['sources'])
    biology = a['domain'] == 'Computational biology'
    note = 'Saved computational study records, newly curated for this collection. Public literature and supplementary evidence are linked below.' if biology else f'Based on public MissionOS main, frozen at {MISSION_SHA[:8]}. Original reports and their evidence boundaries are linked below.'
    lead_media = '<div class="lead-media">' + media_at(a, 'lead') + '</div>' if a.get('media') else ''
    if a.get('media'):
        first = next(m for m in a['media'] if m['after_section'] == 'lead')
        toc = f'<li><a href="#{first["id"]}">Watch the experiment</a></li>' + toc
    media_link = ' · <a href="/assets/media/provenance.json">Media provenance</a>' if a.get('media') else ''
    figure_link = ' · <a href="/assets/figures/provenance.json">Figure provenance</a>' if any('<figure>' in part['html'] for part in a['sections']) else ''
    body = f'''<main id="main" class="wrap"><div class="breadcrumb"><a href="/#research">← Research library</a> <span aria-hidden="true"> / </span> {e(a['domain'])}</div><article><header class="article-header"><div class="eyebrow">{e(a['domain'])} / {e(a['kind'])}</div><h1>{e(a['title'])}</h1><p class="article-subtitle">{e(a['subtitle'])}</p><div class="article-meta"><span>Astropome AI</span><time datetime="{a['date']}">22 October 2026</time><span>{max(1,round(words(a)/200))} min read</span><span class="status">Not peer reviewed</span></div></header>{lead_media}<div class="article-grid"><div class="article-body"><div class="abstract" id="abstract"><h2>Abstract</h2><p>{e(a['abstract'])}</p></div><div class="keywords"><strong>Keywords</strong> / {e(' · '.join(a['keywords']))}</div>{''.join(parts)}<section class="references" id="references"><h2>References &amp; evidence</h2><ol>{references}</ol></section><div class="article-end">Published as part of the Astropome AI research collection. <a href="/content/articles/{a['slug']}.json">Article source</a>{figure_link}{media_link} · <a href="/#research">Browse all research ↗</a></div></div><aside class="article-sidebar" aria-label="Article navigation"><p class="eyebrow">In this article</p><ol class="toc"><li><a href="#abstract">Abstract</a></li>{toc}<li><a href="#references">References &amp; evidence</a></li></ol><div class="source-note"><strong>About the evidence</strong><p>{note}</p><p>Use your browser’s Print command to save a reading copy as PDF.</p><a href="/content/articles/{a['slug']}.json">View article source ↗</a></div></aside></div></article></main>'''
    path = '/research/'+a['slug']+'/'
    schema = {'@context':'https://schema.org','@type':'ScholarlyArticle','headline':a['title'],'description':a['summary'],'abstract':a['abstract'],'datePublished':a['date'],'inLanguage':'en','author':{'@type':'Organization','name':'Astropome AI'},'publisher':{'@type':'Organization','name':'Astropome AI'},'url':BASE+path,'keywords':a['keywords'],'citation':[BASE+s['url'] if s['url'].startswith('/') else s['url'] for s in a['sources']]}
    destination=ROOT/path.strip('/')
    destination.mkdir(parents=True,exist_ok=True)
    (destination/'index.html').write_text(document(a['title'],a['summary'],path,body,schema,media=bool(a.get('media'))))

def main():
    articles=[json.loads(p.read_text()) for p in (ROOT/'content/articles').glob('*.json')]
    articles.sort(key=lambda a:ORDER.index(a['slug']) if a['slug'] in ORDER else len(ORDER))
    if not articles:
        raise SystemExit('No article sources found')
    slugs=[a['slug'] for a in articles]
    if len(slugs)!=len(set(slugs)):
        raise SystemExit('Duplicate article slug')
    for a in articles:
        required={'slug','title','subtitle','domain','kind','date','summary','abstract','keywords','sections','sources'}
        assert required <= a.keys(), (a.get('slug'), required-a.keys())
        assert re.fullmatch('[a-z0-9-]+',a['slug'])
        ids=[s['id'] for s in a['sections']]+[s['id'] for s in a['sources']]+['abstract','references']+[m['id'] for m in a.get('media', [])]
        for m in a.get('media', []):
            assert m['type'] in ('image','video') and m['after_section'] in ['lead']+[s['id'] for s in a['sections']]
            assert m['source_ref'] in [r['id'] for r in a['sources']]
            assert (ROOT/m['src'].lstrip('/')).is_file()
            if m['type']=='video': assert m['duration_seconds']>0 and (ROOT/m['poster'].lstrip('/')).is_file()
        assert len(ids)==len(set(ids)),a['slug']
        render_article(a)
    render_home(articles)
    urls=['/']+['/research/'+a['slug']+'/' for a in articles]
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE}{p}</loc><lastmod>{DATE}</lastmod></url>' for p in urls)+'</urlset>\n')
    (ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    print(json.dumps({'articles':len(articles),'words':sum(words(a) for a in articles),'pages':len(urls),'slugs':slugs},indent=2))

if __name__=='__main__': main()
