#!/usr/bin/env python3
"""Render the research library using only Python's standard library."""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://astropomeai.com'
MISSION_SHA = '7f0128491ac1e998c05580b50707ee8cab7543c6'
ORDER = ['missionos-control-layer-ja', 'building-missionos', 'mission-assurance', 'world-model-stacking', 'robot-manipulation-repair', 'quadruped-delivery', 'urban-drone-recovery', 'temporal-landing-decisions', 'maritime-mission-assurance', 'starship-mission-simulation', 'dna-observation-design', 'dna-replication-completion', 'dna-initiation-mechanisms']
MEDIA_MARKER = re.compile(r'<!--\s*media:([^\s<>]+)\s*-->')
JAPANESE_CHAR = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff々〆]')
JA_LABELS = {
    'Abstract': '要旨', 'References & evidence': '参考文献・根拠資料',
    'Keywords': 'キーワード', 'Research library': '研究記事一覧',
    'Updated': '更新日', 'Not peer reviewed': '未査読草稿',
    'Watch the experiment': '実験映像を見る', 'Media provenance': 'メディアの出典',
    'Figure provenance': '図の出典', 'Article source': '記事のソース',
    'Browse all research': '研究記事一覧へ', 'Article navigation': '記事内ナビゲーション',
    'In this article': '目次', 'About the evidence': '根拠資料について',
    'View article source': '記事のソースを見る',
    'Published as part of the Astropome AI research collection.': 'Astropome AI の研究記事として公開。',
    'Use your browser’s Print command to save a reading copy as PDF.': 'ブラウザの印刷機能で PDF として保存できます。',
    'Recorded video': '記録映像', 'Open this video': 'この動画を開く',
    'Open video': '動画を開く', 'YouTube video': 'YouTube 動画',
    'Watch on YouTube': 'YouTube で見る', 'Figure · Select to enlarge': '図 · 選択して拡大',
    'Enlarge:': '拡大:', 'Full-size image': '原寸画像', 'Original source': '出典',
    'Skip to content': '本文へ移動', 'Astropome AI home': 'Astropome AI ホーム',
    'Independent research': '独立研究', 'Main navigation': 'メインナビゲーション',
    'Research': '研究記事', 'About': 'このサイトについて', 'Code': 'コード',
    'Independent research, open questions.': '独立研究と、未解決の問い。',
    'External links': '外部リンク', 'Website source': 'サイトのソース',
}
e = html.escape

def ui(language, label):
    return JA_LABELS.get(label, label) if language == 'ja' else label

def display_date(value, language='en'):
    day = date.fromisoformat(value)
    if language == 'ja':
        return f'{day.year}年{day.month}月{day.day}日'
    return f'{day.day} {day.strftime("%B %Y")}'

def words(article):
    return len(re.sub('<[^>]+>', ' ', article['abstract'] + ' '.join(s['html'] for s in article['sections']) + ' '.join(m['caption'] for m in article.get('media', []))).split())

def reading_time(article):
    if article.get('language', 'en') == 'ja':
        text = article['abstract'] + ' '.join(s['html'] for s in article['sections']) + ' '.join(m['caption'] for m in article.get('media', []))
        count = len(JAPANESE_CHAR.findall(html.unescape(re.sub('<[^>]+>', ' ', text))))
        return f'約{max(1, round(count / 500))}分で読めます'
    return f'{max(1, round(words(article) / 200))} min read'

def header(language='en'):
    return f'''<a class="skip-link" href="#main">{ui(language, 'Skip to content')}</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="/" aria-label="{ui(language, 'Astropome AI home')}"><img src="/assets/favicon.svg" alt="" width="34" height="34"><span><strong>ASTROPOME AI</strong><small>{ui(language, 'Independent research')}</small></span></a><nav class="site-nav" aria-label="{ui(language, 'Main navigation')}"><a href="/#research">{ui(language, 'Research')}</a><a href="/#about">{ui(language, 'About')}</a><a class="external secondary" href="https://github.com/pome223/missionos">{ui(language, 'Code')}</a><a class="external secondary" href="https://medium.com/@astropomeai">Medium</a></nav></div></header>'''

def footer(language='en'):
    return f'''<footer class="site-footer"><div class="wrap footer-inner"><span>© 2026 Astropome AI · {ui(language, 'Independent research, open questions.')}</span><nav class="footer-links" aria-label="{ui(language, 'External links')}"><a class="external" href="https://github.com/pome223/missionos">MissionOS</a><a class="external" href="https://github.com/pome223/astropomeai">{ui(language, 'Website source')}</a><a class="external" href="https://medium.com/@astropomeai">Medium</a><a class="external" href="https://note.com/astropomeai">note</a></nav></div></footer>'''

def document(title, description, path, body, schema=None, library=False, media=False, language='en'):
    metadata = '' if not schema else '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    if media:
        metadata += '<script src="/assets/media.js" defer></script>'
    return f'''<!doctype html>
<html lang="{e(language)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} · Astropome AI</title><meta name="description" content="{e(description, quote=True)}"><meta name="theme-color" content="#192d32"><link rel="canonical" href="{BASE}{path}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/media.css"><meta property="og:type" content="{'website' if library else 'article'}"><meta property="og:title" content="{e(title, quote=True)}"><meta property="og:description" content="{e(description, quote=True)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:site_name" content="Astropome AI"><meta name="twitter:card" content="summary">{metadata}{'<script src="/assets/library.js" defer></script>' if library else ''}</head><body>{header(language)}{body}{footer(language)}</body></html>\n'''

def art():
    return '''<div class="hero-visual"><div class="visual-top"><span>Field notes / 001</span><span>Control · Coordination</span></div><svg viewBox="0 0 500 470" fill="none" aria-hidden="true"><defs><pattern id="grid" width="35" height="35" patternUnits="userSpaceOnUse"><path d="M35 0H0V35" stroke="#b4c5b9" stroke-opacity=".08"/></pattern></defs><rect width="500" height="470" fill="url(#grid)"/><circle cx="250" cy="224" r="145" stroke="#819990" stroke-opacity=".28"/><circle cx="250" cy="224" r="103" stroke="#819990" stroke-opacity=".35" stroke-dasharray="3 9"/><ellipse cx="250" cy="224" rx="193" ry="67" transform="rotate(-34 250 224)" stroke="#dcaa82" stroke-width="1.6"/><ellipse cx="250" cy="224" rx="165" ry="83" transform="rotate(39 250 224)" stroke="#7f9b8e" stroke-width="1.1"/><path d="M155 265L210 172L316 188L345 285L240 327Z M210 172L240 327 M155 265L316 188 M316 188L240 327" stroke="#9fb4a6" stroke-opacity=".45"/><circle cx="210" cy="172" r="6" fill="#efbd93"/><circle cx="316" cy="188" r="5" fill="#dfe9d9"/><circle cx="155" cy="265" r="5" fill="#dfe9d9"/><circle cx="345" cy="285" r="5" fill="#dfe9d9"/><circle cx="240" cy="327" r="6" fill="#efbd93"/><circle cx="250" cy="224" r="16" fill="#c2d4c3" fill-opacity=".1"/><circle cx="250" cy="224" r="4" fill="#f4f1e9"/><path d="M244 224H221M256 224H279M250 218V195M250 230V253" stroke="#f4f1e9" stroke-opacity=".5"/><circle cx="407" cy="115" r="5" fill="#e6b189"/></svg><div class="visual-bottom"><span>From autonomous missions<br> to molecular systems.</span><strong>A study in coordination ↗</strong></div></div>'''

def media_figure(item, language='en'):
    t = lambda label: ui(language, label)
    caption_id = 'caption-' + item['id']
    source = f'<a class="citation" href="#{e(item["source_ref"])}">[{e(item["source_ref"].removeprefix("s"))}]</a>'
    if item['type'] == 'video':
        minutes, seconds = divmod(round(item['duration_seconds']), 60)
        label = f'{t("Recorded video")} · {minutes}:{seconds:02d}'
        visual = f'<video controls playsinline preload="none" poster="{e(item["poster"])}" width="{item["width"]}" height="{item["height"]}" aria-label="{e(item["title"])}" aria-describedby="{caption_id}"><source src="{e(item["src"])}" type="video/mp4"><p><a href="{e(item["src"])}">{t("Open this video")}</a>.</p></video>'
        link_label = t('Open video')
    elif item['type'] == 'youtube':
        assert re.fullmatch(r'[A-Za-z0-9_-]{11}', item['youtube_id']), item['id']
        assert item['src'] == 'https://www.youtube.com/watch?v=' + item['youtube_id'], item['id']
        minutes, seconds = divmod(round(item['duration_seconds']), 60)
        label = f'{t("YouTube video")} · {minutes}:{seconds:02d}'
        visual = f'<div class="youtube-frame" style="aspect-ratio:{item["width"]}/{item["height"]}"><img class="youtube-poster" src="{e(item["poster"])}" alt="" aria-hidden="true" loading="lazy" width="{item["width"]}" height="{item["height"]}"><iframe src="https://www.youtube-nocookie.com/embed/{item["youtube_id"]}" width="{item["width"]}" height="{item["height"]}" loading="lazy" title="{e(item["title"])}" aria-describedby="{caption_id}" referrerpolicy="strict-origin-when-cross-origin" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div>'
        link_label = t('Watch on YouTube')
    else:
        label = t('Figure · Select to enlarge')
        visual = f'<a href="{e(item["src"])}" class="zoom-link" data-zoom aria-label="{t("Enlarge:")} {e(item["title"])}"><img src="{e(item["src"])}" alt="{e(item["alt"])}" loading="lazy" decoding="async" width="{item["width"]}" height="{item["height"]}"><span class="zoom-hint" aria-hidden="true">↗</span></a>'
        link_label = t('Full-size image')
    return f'<figure class="media-item media-item--{item["type"]}" id="{e(item["id"])}"><div class="media-label">{label}</div>{visual}<figcaption id="{caption_id}"><strong>{e(item["title"])}</strong><p>{e(item["caption"])} {source}</p><div class="media-links"><a href="{e(item["src"])}">{link_label} ↗</a><a href="{e(item["source_url"])}">{t("Original source")} ↗</a></div></figcaption></figure>'

def media_at(article, section):
    items = [m for m in article.get('media', []) if m['after_section'] == section and not m.get('inline')]
    return '<div class="media-gallery">' + ''.join(media_figure(m, article.get('language', 'en')) for m in items) + '</div>' if items else ''

def inline_media(article, section):
    items = {m['id']: m for m in article.get('media', [])}
    def replace(match):
        item = items[match.group(1)]
        assert item.get('inline') is True and item['after_section'] == section['id'], item['id']
        return '<div class="media-inline">' + media_figure(item, article.get('language', 'en')) + '</div>'
    return MEDIA_MARKER.sub(replace, section['html'])

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
        if not lead and a.get('cover'):
            cover = f'<a class="card-cover" href="/research/{a["slug"]}/" aria-label="Read {e(a["title"])}"><img src="{e(a["cover"]["src"])}" alt="{e(a["cover"]["alt"])}" loading="lazy"></a>'
        cards.append(f'''<article class="research-card" data-domain="{e(a['domain'], quote=True)}" data-search="{search}">{cover}<div class="card-top"><span class="card-domain">{e(a['domain'])}</span><span class="card-number">{i:02d}</span></div><h3><a href="/research/{a['slug']}/">{e(a['title'])}</a></h3><p>{e(a['summary'])}</p><div class="card-footer"><span>{reading_time(a)} · {e(a.get('card_label', 'Research article'))}</span><a href="/research/{a['slug']}/" aria-label="Read {e(a['title'], quote=True)}">Read article ↗</a></div></article>''')
    domains = list(dict.fromkeys(a['domain'] for a in articles))
    filters = '<button type="button" data-filter="all" aria-pressed="true">All research</button>' + ''.join(f'<button type="button" data-filter="{e(d, quote=True)}" aria-pressed="false">{e(d)}</button>' for d in domains)
    body = f'''<main id="main" class="wrap"><section class="hero" aria-labelledby="hero-title"><div><div class="eyebrow">Research at the boundaries of intelligence</div><h1 id="hero-title">How do complex<br> systems <em>coordinate?</em></h1><p>From AI that supervises a robot mission to the molecular machinery that copies a genome. Experiments, models, and the evidence behind what they can do.</p><div class="hero-links"><a href="#research">Explore the research ↓</a><a class="external" href="https://github.com/pome223/missionos">Explore MissionOS</a></div></div>{art()}</section><div class="ledger"><span><strong>{len(articles):02d}</strong> research articles</span><span><strong>{len(domains):02d}</strong> research areas</span><span>Methods · Results · Open questions</span><span class="edition">Edition 01 / 22 October 2026</span></div>{featured_films(articles)}<section class="research-section" id="research" aria-labelledby="research-title"><div class="section-head"><div><div class="eyebrow">The research library</div><h2 id="research-title">Studies &amp; experiments</h2></div><div class="search-box"><label for="research-search" class="search-label">Search by topic or keyword</label><input id="research-search" type="search" placeholder="Try world models or DNA…" autocomplete="off"></div></div><div class="filters" role="group" aria-label="Filter research by area">{filters}</div><p id="result-count" class="eyebrow" aria-live="polite">{len(articles)} articles</p><div class="research-grid">{''.join(cards)}</div><p id="empty-results" class="empty-results" hidden>No matching articles. Try another keyword or select All research.</p><noscript><p>All research articles are available below; filtering requires JavaScript.</p></noscript></section><section id="about" class="about-block" aria-labelledby="about-title"><div><div class="eyebrow">About this collection</div><h2 id="about-title">A result is only as useful<br> as its evidence.</h2></div><div><p>Astropome AI is an independent research project exploring governed AI, autonomous systems, and computational biology. These articles bring together the question, the method, the measured result, and the limits of each study.</p><p>The original MissionOS collection is based on <a href="https://github.com/pome223/missionos/tree/{MISSION_SHA}">a pinned snapshot of the public main branch</a>. Dated updates may additionally include reviewed saved-record summaries and media, identified in each article. The biology articles introduce curated summaries of saved computational studies, with links to their published biological context and supplementary evidence.</p><p>These are technical research articles, not peer-reviewed publications. Simulator outcomes, synthetic data, and empirical observations are identified within each article. Negative results remain part of the record.</p></div></section></main>'''
    schema = {'@context':'https://schema.org','@type':'CollectionPage','name':'Astropome AI research library','url':BASE+'/', 'hasPart':[{'@type':'ScholarlyArticle','headline':a['title'],'url':BASE+'/research/'+a['slug']+'/'} for a in articles]}
    (ROOT/'index.html').write_text(document('Research in AI, autonomous systems & computational biology','Independent research on MissionOS, robot learning, autonomous missions, and DNA replication. Methods, measured results, limitations, and sources.','/',body,schema,True))

def render_article(a):
    language = a.get('language', 'en')
    t = lambda label: ui(language, label)
    published_date = display_date(a['date'], language)
    updated_meta = f'<span>{t("Updated")} <time datetime="{e(a["updated"], quote=True)}">{display_date(a["updated"], language)}</time></span>' if a.get('updated') else ''
    references_label = e(a.get('references_label', t('References & evidence')))
    references_before = a.get('references_before')
    reference_toc = f'<li><a href="#references">{references_label}</a></li>'
    toc = ''.join((reference_toc if s['id'] == references_before else '') + f'<li><a href="#{e(s["id"], quote=True)}">{e(s["title"])}</a></li>' for s in a['sections'])
    references = ''.join(f'<li id="{e(s["id"], quote=True)}"><a href="{e(s["url"], quote=True)}">{e(s["title"])}</a><span class="ref-detail">{e(s.get("detail",""))}</span></li>' for s in a['sources'])
    reference_section = f'<section class="references" id="references"><h2>{references_label}</h2><ol>{references}</ol></section>'
    parts = []
    for s in a['sections']:
        if s['id'] == references_before:
            parts.append(reference_section)
        content = re.sub(r'(<table\b.*?</table>)',r'<div class="table-scroll">\1</div>',inline_media(a, s),flags=re.S)
        parts.append(f'<section id="{e(s["id"], quote=True)}"><h2>{e(s["title"])}</h2>{content}{media_at(a, s["id"])}</section>')
    references_at_end = reference_section if not references_before else ''
    reference_toc_at_end = reference_toc if not references_before else ''
    biology = a['domain'] == 'Computational biology'
    note = 'Saved computational study records, newly curated for this collection. Public literature and supplementary evidence are linked below.' if biology else f'Based on public MissionOS main, frozen at {MISSION_SHA[:8]}. Original reports and their evidence boundaries are linked below.'
    if language == 'ja':
        note = '保存済みの計算研究記録を本コレクション向けに整理しました。公開文献と補足資料は下記に示します。' if biology else f'公開 MissionOS main の固定版 {MISSION_SHA[:8]} に基づきます。元の報告と根拠の範囲は下記に示します。'
    if a.get('evidence_note'):
        note = e(a['evidence_note'])
    lead_gallery = media_at(a, 'lead')
    lead_media = '<div class="lead-media">' + lead_gallery + '</div>' if lead_gallery else ''
    first = next((m for m in a.get('media', []) if m['after_section'] == 'lead' and not m.get('inline')), None)
    if first:
        toc = f'<li><a href="#{first["id"]}">{t("Watch the experiment")}</a></li>' + toc
    abstract_label = e(a.get('abstract_label', t('Abstract')))
    abstract_paragraphs = ''.join('<p>' + e(paragraph) + '</p>' for paragraph in re.split(r'\n\s*\n', a['abstract']))
    media_link = f' · <a href="/assets/media/provenance.json">{t("Media provenance")}</a>' if a.get('media') else ''
    figure_link = f' · <a href="/assets/figures/provenance.json">{t("Figure provenance")}</a>' if any('<figure>' in part['html'] for part in a['sections']) else ''
    status_label = e(a.get('status_label', t('Not peer reviewed')))
    downloads = ''.join(f'<a href="{e(item["url"], quote=True)}">{e(item["label"])}</a>' for item in a.get('downloads', []))
    if downloads:
        downloads = '<div class="article-downloads">' + downloads + '</div>'
    body = f'''<main id="main" class="wrap"><div class="breadcrumb"><a href="/#research">← {t('Research library')}</a> <span aria-hidden="true"> / </span> {e(a['domain'])}</div><article><header class="article-header"><div class="eyebrow">{e(a['domain'])} / {e(a['kind'])}</div><h1>{e(a['title'])}</h1><p class="article-subtitle">{e(a['subtitle'])}</p><div class="article-meta"><span>Astropome AI</span><time datetime="{a['date']}">{published_date}</time>{updated_meta}<span>{reading_time(a)}</span><span class="status">{status_label}</span></div>{downloads}</header>{lead_media}<div class="article-grid"><div class="article-body"><div class="abstract" id="abstract"><h2>{abstract_label}</h2>{abstract_paragraphs}</div><div class="keywords"><strong>{t('Keywords')}</strong> / {e(' · '.join(a['keywords']))}</div>{''.join(parts)}{references_at_end}<div class="article-end">{t('Published as part of the Astropome AI research collection.')} <a href="/content/articles/{a['slug']}.json">{t('Article source')}</a>{figure_link}{media_link} · <a href="/#research">{t('Browse all research')} ↗</a></div></div><aside class="article-sidebar" aria-label="{t('Article navigation')}"><p class="eyebrow">{t('In this article')}</p><ol class="toc"><li><a href="#abstract">{abstract_label}</a></li>{toc}{reference_toc_at_end}</ol><div class="source-note"><strong>{t('About the evidence')}</strong><p>{note}</p><p>{t('Use your browser’s Print command to save a reading copy as PDF.')}</p><a href="/content/articles/{a['slug']}.json">{t('View article source')} ↗</a></div></aside></div></article></main>'''
    path = '/research/'+a['slug']+'/'
    schema = {'@context':'https://schema.org','@type':'ScholarlyArticle','headline':a['title'],'description':a['summary'],'abstract':a['abstract'],'datePublished':a['date'],'inLanguage':language,'author':{'@type':'Organization','name':'Astropome AI'},'publisher':{'@type':'Organization','name':'Astropome AI'},'url':BASE+path,'keywords':a['keywords'],'citation':[BASE+s['url'] if s['url'].startswith('/') else s['url'] for s in a['sources']]}
    if a.get('updated'):
        schema['dateModified'] = a['updated']
    destination=ROOT/path.strip('/')
    destination.mkdir(parents=True,exist_ok=True)
    (destination/'index.html').write_text(document(a['title'],a['summary'],path,body,schema,media=bool(a.get('media')),language=language))

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
        assert a.get('language', 'en') in ('en', 'ja'), a['slug']
        if a.get('references_before'):
            assert a['references_before'] in [s['id'] for s in a['sections']], a['slug']
        for item in a.get('downloads', []):
            assert item['label'] and item['url'].startswith('/') and not item['url'].startswith('//'), a['slug']
            assert (ROOT/item['url'].lstrip('/')).is_file(), item['url']
        ids=[s['id'] for s in a['sections']]+[s['id'] for s in a['sources']]+['abstract','references']+[m['id'] for m in a.get('media', [])]
        markers = [(section['id'], media_id) for section in a['sections'] for media_id in MEDIA_MARKER.findall(section['html'])]
        inline_items = {m['id']: m for m in a.get('media', []) if m.get('inline') is True}
        for section_id, media_id in markers:
            assert media_id in inline_items and inline_items[media_id]['after_section'] == section_id, (a['slug'], section_id, media_id)
        for media_id, item in inline_items.items():
            assert markers.count((item['after_section'], media_id)) == 1, (a['slug'], media_id, 'expected one inline marker')
        if a.get('cover'):
            assert a['cover']['src'].startswith('/') and not a['cover']['src'].startswith('//')
            assert (ROOT/a['cover']['src'].lstrip('/')).is_file() and a['cover']['alt']
        for m in a.get('media', []):
            assert m['type'] in ('image','video','youtube') and m['after_section'] in ['lead']+[s['id'] for s in a['sections']]
            assert m['source_ref'] in [r['id'] for r in a['sources']]
            assert isinstance(m['width'], int) and m['width'] > 0 and isinstance(m['height'], int) and m['height'] > 0
            if 'inline' in m: assert isinstance(m['inline'], bool)
            if m['type'] == 'youtube':
                assert re.fullmatch(r'[A-Za-z0-9_-]{11}', m['youtube_id']), m['id']
                assert m['src'] == 'https://www.youtube.com/watch?v=' + m['youtube_id'], m['id']
            else:
                assert m['src'].startswith('/') and not m['src'].startswith('//')
                assert (ROOT/m['src'].lstrip('/')).is_file()
            if m['type'] in ('video','youtube'):
                assert m['duration_seconds'] > 0 and m['poster'].startswith('/') and not m['poster'].startswith('//')
                assert (ROOT/m['poster'].lstrip('/')).is_file()
        assert len(ids)==len(set(ids)),a['slug']
        render_article(a)
    render_home(articles)
    urls=['/']+['/research/'+a['slug']+'/' for a in articles]
    modified = {'/research/'+a['slug']+'/': a.get('updated', a['date']) for a in articles}
    modified['/'] = max(modified.values())
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE}{p}</loc><lastmod>{modified[p]}</lastmod></url>' for p in urls)+'</urlset>\n')
    (ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    print(json.dumps({'articles':len(articles),'words':sum(words(a) for a in articles),'pages':len(urls),'slugs':slugs},indent=2))

if __name__=='__main__': main()
