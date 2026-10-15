#!/usr/bin/env python3
"""Generate the static academic website. Uses Python's standard library only."""
from pathlib import Path
from html import escape as esc
from html.parser import HTMLParser
from urllib.parse import urljoin
import json
import os

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('SITE_BASE_URL', 'http://127.0.0.1:8765').rstrip('/')
UPDATED = '15 October 2026'
SCHOLAR = 'https://scholar.google.com/citations?user=MC0hy74AAAAJ&hl=en'
ORCID = 'https://orcid.org/0000-0002-7506-3298'
VUB = 'https://researchportal.vub.be/en/persons/brecht-verbeken/'
ARXIV = 'https://arxiv.org/search/?searchtype=author&query=Verbeken%2C+B&abstracts=show&order=-announced_date_first&size=50'
EMAIL = 'brecht.verbeken@vub.be'
PAPERS = json.loads((ROOT / 'data/publications.json').read_text())
BY_ID = {p['id']: p for p in PAPERS}
MEDIA = json.loads((ROOT / 'data/media.json').read_text())
PROJECTS = json.loads((ROOT / 'data/projects.json').read_text())


def authors(p):
    result = []
    for name in p['authors']:
        value = esc(name)
        if name in p.get('author_urls', {}):
            value = f'<a href="{esc(p["author_urls"][name])}">{value}</a>'
        if 'Brecht' in name and 'Verbeken' in name:
            value = f'<strong>{value}</strong>'
        result.append(value)
    return ', '.join(result)


def paper(p, brief=True, level=3):
    title = esc(p['title'])
    if p.get('url'):
        title = f'<a href="{esc(p["url"])}">{title}</a>'
    meta = esc(p['venue'])
    if p.get('location'):
        meta += ', ' + esc(p['location'])
    if p['kind'] == 'working':
        meta += f' · {p["year"]} · arXiv:{p["arxiv"]}'
    elif p['kind'] == 'forthcoming':
        if p.get('status') == 'In preparation':
            meta += f' · {p["year"]}'
        elif p.get('status') == 'Accepted':
            meta += ' · accepted; to appear'
        elif p['venue'] != 'To appear':
            meta += f' · to appear ({p["year"]})'
    else:
        meta += f' · {p["year"]}'
    if p.get('contribution'):
        meta += ' · ' + esc(p['contribution'])
    links = []
    if p.get('pdf'):
        label = p.get('pdf_label', 'PDF')
        links.append(f'<a href="{esc(p["pdf"])}" aria-label="{esc(label)}: {esc(p["title"])}">{esc(label)}</a>')
    if p.get('arxiv') and p['kind'] != 'working':
        links.append(f'<a href="https://arxiv.org/abs/{p["arxiv"]}">arXiv record</a>')
    if p.get('scholar'):
        links.append(f'<a href="{esc(p["scholar"])}">Google Scholar record</a>')
    if p['id'] == '2609.26058':
        links.append('<a href="https://bfmave.github.io/karpelevic/">Illustrated project</a>')
    abstract = ''
    if brief and p.get('summary'):
        abstract = f'<details><summary>Overview</summary><p>{esc(p["summary"])}</p></details>'
    return f'''<li class="paper" id="paper-{p['id']}" data-topics="{' '.join(p['topics'])}">
      <h{level}>{title}</h{level}>
      <p class="paper-authors">{authors(p)}</p>
      <p class="paper-meta">{meta}</p>
      {f'<div class="paper-links">{"".join(links)}</div>' if links else ''}
      {abstract}
    </li>'''


def paper_list(ids, brief=True):
    return '<ul class="paper-list">' + ''.join(paper(BY_ID[i], brief) for i in ids) + '</ul>'


def page(title, content, filename, description, active='home'):
    home = filename == 'index.html'
    canonical = BASE + ('/' if home else '/' + filename)
    nav = [('home', './', 'About'), ('research', 'research.html', 'Research'),
           ('projects', 'projects.html', 'Projects'), ('media', 'media.html', 'Media'),
           ('mathematics', './#mathematics', 'Mathematics'), ('cv', 'cv.html', 'CV'),
           ('contact', './#contact', 'Contact')]
    nav_html = ''.join(f'<a href="{url}"'+(' aria-current="page"' if key == active else '')+f'>{label}</a>' for key, url, label in nav)
    structured = {
        '@context': 'https://schema.org', '@type': 'Person', '@id': BASE + '/#person', 'name': 'Brecht F. Verbeken',
        'alternateName': ['Brecht Felix Marc Antoon Verbeken', 'Brecht Verbeken', 'Brecht F Verbeken'],
        'identifier': ORCID,
        'url': BASE + '/', 'jobTitle': 'Postdoctoral Researcher and Guest Professor',
        'worksFor': {'@type': 'Organization', 'name': 'Vrije Universiteit Brussel'},
        'sameAs': [SCHOLAR, ORCID, VUB, 'https://github.com/BFMAVE'],
        'knowsAbout': ['Economics of artificial intelligence', 'Scientific discovery', 'Economic forecasting', 'Model evaluation']
    }
    graph = [structured]
    if filename == 'research.html':
        graph.append({'@type': 'CollectionPage', '@id': canonical, 'name': 'Research by Brecht F. Verbeken',
                      'about': {'@id': BASE + '/#person'}, 'hasPart': [scholarly_record(p) for p in PAPERS]})
    elif filename == 'media.html':
        graph.append({'@type': 'CollectionPage', '@id': canonical, 'name': 'Media and public writing',
                      'about': {'@id': BASE + '/#person'}, 'hasPart': [media_record(m) for m in MEDIA]})
    elif filename == 'index.html':
        graph.append({'@type': 'ProfilePage', '@id': canonical, 'mainEntity': {'@id': BASE + '/#person'}, 'dateModified': '2026-10-15'})
    structured = {'@context': 'https://schema.org', '@graph': graph}
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · Brecht F. Verbeken</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="Brecht F. Verbeken">
  <meta name="theme-color" content="#183d59">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="canonical" href="{canonical}">
  <link rel="describedby" href="llms.txt" type="text/plain" title="Site guide for agents and language models">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="assets/styles.css">
  <link rel="alternate" type="text/markdown" href="{filename.replace('.html', '.md')}" title="Plain-text version">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)} · Brecht F. Verbeken">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical}">
  <script type="application/ld+json">{json.dumps(structured, ensure_ascii=False)}</script>
  <script src="assets/site.js" defer></script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap header-inner">
  <a class="brand" href="./">Brecht F. Verbeken</a>
  <nav class="nav" aria-label="Main navigation">{nav_html}</nav>
</div></header>
<main id="main" class="wrap">{content}</main>
<footer class="wrap site-footer">
  <span>Brecht F. Verbeken · Brussels, Belgium</span>
  <span>Updated {UPDATED} · <a href="llms.txt">Text &amp; data</a></span>
</footer>
</body></html>
'''




def home_content():
    return f'''
<section class="intro" aria-labelledby="name">
  <div class="intro-copy">
    <h1 id="name">Brecht F. Verbeken<sup class="name-note-ref"><a id="name-note-ref" href="#name-note" role="doc-noteref" aria-label="About my name">*</a></sup></h1>
    <p>I am an economist (PhD) and mathematician (MSc) by training, and I think of myself as a data scientist. My interests centre on economics and AI, with a lasting passion for mathematics.</p>
    <p>I particularly enjoy bringing people with different specialities together and the cross-fertilisation of ideas that comes from interdisciplinary work. I often help set the research agenda and lead collaborations, as I have done since the early years of my PhD.</p>
    <p>I am a postdoctoral researcher and guest professor at the <a href="{VUB}">Vrije Universiteit Brussel</a>. More recently, I have become particularly interested in the economic impact of AI, especially how it changes scientific discovery and innovation. My work spans economic forecasting, model evaluation, and AI in mathematics and science.</p>
    <blockquote class="epigraph"><p>“I am not a donkey; I don’t have a field.”</p><cite>Falsely(?) attributed to <a href="https://maxweberstudies.org/source/files/MWSJournal/17.2pdfs/Max_Weber_Studies_17.2_LS_FINAL.pdf">Max Weber</a></cite></blockquote>
    <p>I am always curious about my colleagues’ research. My quantitative background often gives me a way to contribute, and these collaborations have taken me into many different areas. Sometimes this leads to an acknowledgement; sometimes to co-authorship. Perhaps the common thread is helping others move their research forward.</p>
    <p>I am proud of the team and colleagues I work with, at the <a href="https://data.research.vub.be/people">Data Analytics Lab</a> and beyond. Much of this work reflects our shared effort.</p>
    <div class="text-links intro-links"><a href="assets/brecht-verbeken-cv.pdf">CV (PDF)</a><a href="{SCHOLAR}">Google Scholar</a><a href="{ORCID}">ORCID</a><a href="https://github.com/BFMAVE">GitHub</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
    <p class="small metrics-note">Take citation metrics with a pinch of salt. Measures of scientific impact can be sensitive to <a href="https://doi.org/10.1038/s41586-026-10787-y">dataset artefacts</a>, as shown by <a href="https://data.research.vub.be/vincent-holst">Vincent Holst</a> and colleagues.</p>
  </div>
</section>

<section class="section current-research" id="current-research" aria-labelledby="current-heading">
  <h2 id="current-heading">Current research</h2>
  <h3 id="economics">Economics</h3>
  <p>Regarding my interests and work:</p>
  <blockquote class="epigraph"><p>“An economist who is only an economist cannot even be a good economist.”</p><cite><a href="https://static.library.ucla.edu/oralhistory/text/masters/21198-zz0008zd21-4-master.html">F. A. Hayek, interview with Leo Rosten (1978)</a></cite></blockquote>
  <p>More recently, my interests have turned to the economic effects of AI, particularly its effects on scientific discovery and innovation. This includes how AI changes the pace and direction of research, which questions receive attention, and how verification costs affect the value of automation.</p>
  <p>Colleagues at VUB, led by Andres Algaba, are exploring this line of work through <a href="https://press.vub.ac.be/onderzoeksgroep-van-vub-geselecteerd-voor-internationaal-onderzoeksprogramma-van-openai"><em>The Rate and Direction of Automated Science</em></a>, a project selected for OpenAI’s Economic Research Exchange.</p>
  <p class="project-note">Related work: <a href="research.html#paper-2606.26130">LLM-generated research methods</a> and <a href="research.html#paper-2504.02767">scientific literature and citation practices</a>.</p>
  <p id="ergodicity-economics">My economics work also includes <a href="research.html#paper-nowcasting">economic forecasting</a>, decision-making under uncertainty, <a href="research.html#paper-2509.22223">public investment and transport accessibility</a>, and <a href="research.html#paper-ergodicity">ergodicity economics</a> with <a href="https://data.research.vub.be/arne-vanhoyweghen0">Arne Vanhoyweghen</a> and colleagues.</p>
  <p>I have also served as an examiner, supervisor or co-supervisor for master’s theses spanning a wide range of economics and business topics.</p>
</section>

<section class="section" id="recent-papers" aria-labelledby="recent-heading">
  <div class="section-heading"><h2 id="recent-heading">Recent and forthcoming work</h2><a href="research.html">All research</a></div>
    <p>A paper on <em>Sums of Generalized Fuss–Catalan Products</em> — to appear.</p>
  {paper_list(['wealth-inequality', '2610.15634', '2509.22223'], False)}
</section>

<section class="section" id="selected-research" aria-labelledby="selected-heading">
  <div class="section-heading"><h2 id="selected-heading">Selected published papers</h2><a href="research.html#journal">All publications</a></div>
  {paper_list(['2504.02767', '2508.15842', 'uplift', 'nowcasting', '2501.14249'], False)}
</section>

<section class="section" id="applied-work" aria-labelledby="applied-heading">
  <div class="section-heading"><h2 id="applied-heading">Applied and institutional work</h2><a href="projects.html">Project details</a></div>
  <ul class="work-list">
    <li><strong><a href="projects.html#jrc">AI-supported science for policy.</a></strong> Through a VUB collaboration with the European Commission’s Joint Research Centre, I was involved in developing evaluation templates and contributed to a validation protocol for AI-supported research outputs.</li>
    <li><strong><a href="projects.html#fari">Public-sector AI review.</a></strong> For FARI within AI4Gov-X Accelerate, I co-authored an internal review of AI4Scale requirements and prototype validation, addressing feasibility, deployment and governance.</li>
    <li><strong>Public investment under uncertainty.</strong> I led a <a href="https://arxiv.org/abs/2509.22223">scenario-based study of Brussels Metro 3</a>, examining accessibility and its distribution across the city.</li>
    <li><strong><a href="projects.html#course-sheets">Course information sheets.</a></strong> I led the technical implementation of a reusable LLM-assisted classification workflow at VUB, combining human validation and quality controls. <a href="https://arxiv.org/abs/2603.13562">Paper</a>.</li>
    <li><strong><a href="projects.html#greening">Data analysis and modelling.</a></strong> In the context of greening and CO₂ neutrality.</li>
  </ul>
</section>

<section class="section" id="media" aria-labelledby="media-heading">
  <div class="section-heading"><h2 id="media-heading">Media and public writing</h2><a href="media.html">All media</a></div>
  <ul class="work-list">
    <li><a href="https://www.standaard.be/opinies/de-wereld-heeft-er-een-superhacker-bij-nu-nog-leren-hoe-we-daarmee-omgaan/159873818.html">De wereld heeft er een superhacker bij, nu nog leren hoe we daarmee omgaan</a><br><span class="small">De Standaard · Opinion article with Andres Algaba · August 2026</span></li>
    <li><a href="https://www.standaard.be/opinies/soevereiniteit-is-geen-europese-chatbot/157225846.html">Soevereiniteit is geen Europese chatbot</a><br><span class="small">De Standaard · Opinion article with Vincent Ginis and Andres Algaba · June 2026</span></li>
    <li><a href="https://phys.org/news/2026-03-chatgpt-mathematical-proofs.html">ChatGPT can provide original mathematical proofs, researchers show</a><br><span class="small">Phys.org · Research coverage from VUB · March 2026</span></li>
    <li><a href="https://www.bruzz.be/actua/mobiliteit/onderzoekers-over-metro-3-amper-voordelen-bij-halve-aanleg-2025-10-03">Onderzoekers over metro 3: ‘Amper voordelen bij halve aanleg’</a><br><span class="small">BRUZZ · Research coverage and expert comments · October 2025</span></li>
  </ul>
</section>

<section class="section" id="mathematics" aria-labelledby="math-heading">
  <div>
    <h2 id="math-heading">Mathematics</h2>
    <p>Mathematics is a lasting passion. My main mathematical research line concerns Markov chains and stochastic matrices, particularly their eigenvalues and spectral regions. It also connects to my work on semi-Markov models and applications in manpower planning.</p>
    <p>I occasionally return to algebra, closer to my <a href="research.html#paper-masters-thesis">master’s thesis on units in integral group rings</a>: <a href="research.html#paper-2608.03254">group rings</a>, the <a href="research.html#paper-2607.29105">Prime Graph Question</a>, and <a href="research.html#paper-2608.01884">braces</a>. More recently, a <a href="research.html#paper-2610.06081">paper on Ramsey graphs</a> has provided another setting in which to explore AI-assisted mathematical research.</p>
    <p>A personal project close to my heart is an <a href="https://bfmave.github.io/karpelevic/">illustrated exploration of the Karpelevič theorem</a>, developed with Vincent Ginis. It brings together a proof, geometric explanations and numerical illustrations of the possible eigenvalues of stochastic matrices. I see this kind of exposition as a service to the mathematical community—work that, in my view, is too often undervalued in science.</p>
    <div class="text-links"><a href="https://bfmave.github.io/karpelevic/">Project website</a><a href="https://arxiv.org/abs/2609.26058">Current paper</a><a href="research.html?topic=mathematics">Other mathematical papers</a></div>
  </div>
</section>

<section class="section two-column" aria-label="Teaching and background">
  <div><h2>Teaching and academic service</h2><p>I have taught at university level since 2018. I currently teach Mathematics II for Business Economics at VUB, with responsibility for the course and its assessment. I have supervised more than 25 master’s theses on a range of economics and business topics.</p><p>I also serve on PhD advisory committees, contributing to the assessment of doctoral research progress. At the Data Analytics Lab, I have HR and recruitment responsibilities, including candidate selection.</p></div>
  <div><h2>Background</h2><p>My training combines fundamental mathematics with applied economic sciences. I work with Python, R and LaTeX.</p><p class="small"><a href="cv.html">Curriculum vitae →</a></p></div>
</section>

<section class="section contact-block" id="contact" aria-label="Email and affiliation">
  <address><a class="contact-email" href="mailto:{EMAIL}">{EMAIL}</a><p class="small">Data Analytics Lab · Vrije Universiteit Brussel<br>Brussels, Belgium</p></address>
</section>
<aside class="name-note small" id="name-note" role="note" aria-label="About my name">
  <p><a href="#name-note-ref" role="doc-backlink" aria-label="Back to my name">*</a> My full name is Brecht Felix Marc Antoon Verbeken. I used to go by Brecht Verbeken, but started adding F. in publications after discovering a <a href="https://research.ugent.be/web/person/brecht-verbeken-0/nl">namesake</a> who went to the same secondary school, won mathematics-olympiad prizes and also studied mathematics. He is now a PhD student at Ghent University. Perhaps one day we’ll write a Verbeken–Verbeken paper—with shared first authorship, naturally.</p>
</aside>'''


def research_content():
    groups = [
        ('journal', 'Journal articles', [p for p in PAPERS if p['kind'] == 'journal']),
        ('working', 'Working papers', [p for p in PAPERS if p['kind'] == 'working' and 'mathematics' not in p['topics']]),
        ('forthcoming', 'Forthcoming work', [p for p in PAPERS if p['kind'] == 'forthcoming']),
        ('mathematical', 'Mathematical working papers', [p for p in PAPERS if p['kind'] == 'working' and 'mathematics' in p['topics']]),
        ('theses', 'Theses', [p for p in PAPERS if p['kind'] == 'thesis']),
    ]
    body = f'''<div class="page-heading"><p class="eyebrow">Papers and publications</p><h1>Research</h1>
    <p>My economics work includes forecasting, decision-making under uncertainty, public investment and <a href="./#ergodicity-economics">ergodicity economics</a>. I also work on AI evaluation and quantitative methods. My mathematical research centres on Markov chains and stochastic matrices, alongside work on group rings and braces and recent explorations of AI-assisted research in Ramsey theory.</p>
    <p>More recently, my interests have turned to the economic impact of AI, particularly its effects on scientific discovery and innovation.</p>
    <p>I have also served as an examiner, supervisor or co-supervisor for master’s theses spanning a wide range of economics and business topics.</p>
    <div class="text-links" style="margin-top:15px"><a href="{SCHOLAR}">Google Scholar</a><a href="{ARXIV}">arXiv</a><a href="{VUB}">VUB research profile</a><a href="assets/publications.bib" download>BibTeX</a></div></div>
    <div class="filter-bar" data-filters hidden role="group" aria-label="Filter papers by subject">
    <button type="button" data-filter="all" aria-pressed="true">All</button>
    <button type="button" data-filter="economics" aria-pressed="false">Economics</button>
    <button type="button" data-filter="ai" aria-pressed="false">AI &amp; science</button>
    <button type="button" data-filter="methods" aria-pressed="false">Methods</button>
    <button type="button" data-filter="mathematics" aria-pressed="false">Mathematics</button>
    <span class="results-note" role="status" aria-live="polite" data-results></span></div>'''
    for key, label, papers in groups:
        ordered = sorted(papers, key=lambda p: (p['year'], p['date']), reverse=True)
        body += f'<section class="section" id="{key}" data-paper-group aria-labelledby="{key}-heading"><h2 id="{key}-heading">{label}</h2>'
        body += '<ul class="paper-list">' + ''.join(paper(p) for p in ordered) + '</ul></section>'
    return body


def projects_content():
    body = '<div class="page-heading"><h1>Projects</h1><p>Research and institutional work connecting economics, data science and AI.</p></div>'
    for p in PROJECTS:
        body += f'<section class="section" id="{p["id"]}" aria-labelledby="{p["id"]}-heading"><h2 id="{p["id"]}-heading">{esc(p["name"])}</h2>'
        body += f'<p class="small">{esc(p["context"])}</p>'
        body += ''.join('<p>' + esc(t) + '</p>' for t in p['paragraphs'])
        body += '<div class="text-links project-links">' + ''.join(f'<a href="{esc(link["url"])}">{esc(link["label"])}</a>' for link in p['links']) + '</div></section>'
    return body


def media_content():
    body = '<div class="page-heading"><h1>Media and public writing</h1><p>Opinion articles and explainers I co-wrote, reporting on our research, and coverage of related projects.</p></div>'
    for kind, title in [('authored', 'Opinion articles and explainers'), ('coverage', 'Research coverage'), ('project-coverage', 'Project announcements and coverage')]:
        body += f'<section class="section" aria-labelledby="{kind}-heading"><h2 id="{kind}-heading">{title}</h2><ul class="paper-list">'
        for m in sorted([m for m in MEDIA if m['kind'] == kind], key=lambda m: m['date'], reverse=True):
            body += f'<li class="paper" id="{m["id"]}"><h3><a lang="{m["language"]}" href="{esc(m["url"])}">{esc(m["title"])}</a></h3>'
            body += f'<p class="paper-meta">{esc(m["outlet"])} · {esc(m["display_date"])} · {esc(m["type"])}</p>'
            if m.get('authors'):
                body += f'<p class="paper-authors">{esc(", ".join(m["authors"]))}</p>'
            body += f'<p class="media-description">{esc(m["description"])}</p>'
            if m.get('alternative'):
                body += f'<div class="text-links"><a href="{esc(m["alternative"])}">{esc(m["alternative_label"])}</a></div>'
            body += '</li>'
        body += '</ul></section>'
    return body


def author_record(name, url=None):
    record = {'@type': 'Organization' if 'Consortium' in name else 'Person', 'name': name}
    if url:
        record['url'] = url
    if 'Brecht' in name and 'Verbeken' in name:
        record.update({'@id': BASE + '/#person', 'sameAs': ORCID})
    return record


def scholarly_record(p):
    record = {
        '@type': 'Thesis' if p['kind'] == 'thesis' else 'ScholarlyArticle', '@id': BASE + '/research.html#paper-' + p['id'],
        'name': p['title'], 'headline': p['title'], 'inLanguage': 'en',
        'author': [author_record(name, p.get('author_urls', {}).get(name)) for name in p['authors']],
        'creativeWorkStatus': p.get('status') or {'journal': 'Published', 'working': 'Preprint', 'forthcoming': 'Forthcoming', 'thesis': 'Published'}[p['kind']],
        'keywords': p['topics'], 'mainEntityOfPage': BASE + '/research.html',
    }
    if p.get('url'):
        record['url'] = p['url']
    if p['kind'] == 'journal':
        record['isPartOf'] = {'@type': 'Periodical', 'name': p['venue']}
        if len(p['date']) == 10:
            record['datePublished'] = p['date']
    if p.get('status') == 'Accepted':
        record['isPartOf'] = {'@type': 'Periodical', 'name': p['venue']}
    if p.get('doi'):
        record['identifier'] = 'https://doi.org/' + p['doi']
    elif p.get('arxiv'):
        record['identifier'] = 'arXiv:' + p['arxiv']
    if p['kind'] == 'thesis':
        record['inSupportOf'] = p['degree']
        record['sourceOrganization'] = {'@type': 'CollegeOrUniversity', 'name': p['school']}
    if p.get('summary'):
        record['description'] = p['summary']
    if p.get('pdf'):
        record['encoding'] = {'@type': 'MediaObject', 'contentUrl': p['pdf'], 'encodingFormat': 'application/pdf'}
    return record


def media_record(m):
    record = {'@type': 'Article', 'headline': m['title'], 'url': m['url'], 'inLanguage': m['language'],
              'publisher': {'@type': 'Organization', 'name': m['outlet']}, 'description': m['description'],
              'genre': m['type'], 'about': {'@id': BASE + '/#person'}}
    if len(m['date']) == 10:
        record['datePublished'] = m['date']
    if m.get('authors'):
        record['author'] = [author_record(n) for n in m['authors']]
    return record


class PlainText(HTMLParser):
    """Export the same main-page content in Markdown, including accessible links."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.out = []
        self.hrefs = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'main': self.in_main = True
        if not self.in_main: return
        if tag in ['h1', 'h2', 'h3']:
            self.out.append('\n\n' + '#' * int(tag[1]) + ' ')
        elif tag in ['p', 'div', 'section', 'blockquote', 'ul', 'dl']:
            self.out.append('\n\n')
        elif tag == 'li': self.out.append('\n- ')
        elif tag == 'br': self.out.append('\n')
        elif tag == 'a':
            self.out.append('[')
            self.hrefs.append(urljoin(BASE + '/', a.get('href', '')))
        elif tag == 'strong': self.out.append('**')
        elif tag == 'em': self.out.append('*')
        elif tag == 'dt': self.out.append('\n\n**')
    def handle_endtag(self, tag):
        if tag == 'main': self.in_main = False
        if not self.in_main: return
        if tag == 'a' and self.hrefs: self.out.append('](' + self.hrefs.pop() + ') ')
        elif tag in ['h1', 'h2', 'h3', 'p', 'section', 'li', 'address', 'cite']: self.out.append('\n')
        elif tag == 'strong': self.out.append('**')
        elif tag == 'em': self.out.append('*')
        elif tag == 'dt': self.out.append('**\n')
    def handle_data(self, data):
        if self.in_main and data.strip():
            import re
            self.out.append(re.sub(r'\s+', ' ', data))
    def markdown(self):
        import re
        text = ''.join(self.out)
        text = re.sub(r'[ \t]+\n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'(?m)^-\n\n(?=###)', '', text)
        text = re.sub(r'\) +([.,;:])', r')\1', text)
        return text.strip() + '\n'


APPOINTMENTS = [
    ('2025–present', 'Guest Professor (10%)', 'Vrije Universiteit Brussel', 'Course holder for Mathematics II for Business Economics (6 ECTS); teaching, assessment and master’s-thesis supervision.'),
    ('2024–present', 'Postdoctoral Researcher (90%)', 'Vrije Universiteit Brussel', 'Research in model evaluation, AI in science and mathematics, and stochastic systems; institutional AI workflows and interdisciplinary collaboration.'),
    ('2022–2024', 'Research Associate', 'Vrije Universiteit Brussel', 'Research on uplift-model evaluation and semi-Markov processes; mathematics teaching and thesis supervision.'),
    ('2018–2022', 'Doctoral Researcher', 'Vrije Universiteit Brussel', 'Stochastic models for manpower planning; collaboration on economic nowcasting and ergodicity economics; teaching duties.'),
]
EDUCATION = [
    ('2024', 'PhD in Applied Economic Sciences', 'Vrije Universiteit Brussel · Business Engineering', 'On Models and Metrics: Improving Stochastic Model Performance in Manpower Planning.'),
    ('2018', 'Master of Mathematics', 'Vrije Universiteit Brussel / University of Antwerp', 'Fundamental Mathematics.'),
    ('2016', 'Bachelor of Mathematics', 'Vrije Universiteit Brussel', ''),
]


def timeline(items):
    return '<ul class="timeline">' + ''.join(f'<li><span class="dates">{esc(d)}</span><div><h3>{esc(t)}</h3><p>{esc(org)}</p>{f"<p>{esc(desc)}</p>" if desc else ""}</div></li>' for d, t, org, desc in items) + '</ul>'


def cv_content():
    return f'''<div class="page-heading cv-top"><div><p class="eyebrow">Curriculum vitae · {UPDATED}</p><h1>Brecht F. Verbeken</h1><p>Economics · Data science · Artificial intelligence</p><p class="small">Vrije Universiteit Brussel · Brussels, Belgium</p></div><a class="download-link" href="assets/brecht-verbeken-cv.pdf" download>Download CV (PDF)</a></div>
    <section class="section cv-section"><h2>Profile</h2><p>I am an economist (PhD) and mathematician (MSc) by training, and I think of myself as a data scientist. My interests centre on economics and AI. More recently, I have become particularly interested in the economic impact of AI and its role in scientific discovery and innovation. My research spans economic forecasting, model evaluation and AI in mathematics and science.</p></section>
    <section class="section cv-section"><h2>Appointments</h2>{timeline(APPOINTMENTS)}</section>
    <section class="section cv-section"><h2>Education</h2>{timeline(EDUCATION)}</section>
    <section class="section cv-section"><h2>Selected projects</h2><ul class="work-list">
    <li><strong>AI and scientific discovery.</strong> Interested in how AI changes the pace and direction of knowledge production, the division of work between researchers and AI, and verification costs.</li>
    <li><strong>AI-supported science for policy.</strong> Through a VUB collaboration with the JRC, I was involved in developing evaluation templates and contributed to a validation protocol for AI-supported research outputs.</li>
    <li><strong>FARI / AI4Gov-X.</strong> Co-authored an internal review of AI4Scale requirements and prototype validation, covering feasibility, prioritisation, deployment, governance and process ownership.</li>
    <li><strong>Brussels Metro 3.</strong> Led scenario-based public-transport accessibility research using official transport and open-map data.</li>
    <li><strong>Institutional AI adoption.</strong> Technical implementation lead for LLM-assisted classification of an initial 4,684 course information sheets, combining human validation and quality controls.</li>
    <li><strong>Mathematics and AI-assisted discovery.</strong> Research on stochastic matrices and spectral regions; an illustrated <a href="https://bfmave.github.io/karpelevic/">Karpelevič project</a> and a documented case study of AI-assisted proof development.</li></ul></section>
    <section class="section cv-section"><div class="section-heading"><h2>Selected publications and working papers</h2><a href="research.html">All papers →</a></div>{paper_list(['2508.15842','2606.26130','2602.18918','uplift','nowcasting'], False)}</section>
    <section class="section cv-section"><h2>Methods and tools</h2><dl class="cv-skills"><dt>Economic and quantitative analysis</dt><dd>Mixed-frequency nowcasting; econometrics; model evaluation; treatment-effect rankings; uncertainty; simulation; stochastic and semi-Markov processes.</dd><dt>Implementation</dt><dd>Python, R, LaTeX; data preparation; textual analysis; APIs and local model workflows; reproducible analytical pipelines.</dd><dt>Teaching and communication</dt><dd>University-level teaching since 2018; course responsibility, assessment, supervision of more than 25 master’s theses on economics and business topics, scientific writing and interdisciplinary collaboration.</dd></dl></section>
    <section class="section cv-section"><h2>Academic service and recruitment</h2><p>I serve on PhD advisory committees, contributing to the assessment of doctoral research progress. At the Data Analytics Lab, I have HR and recruitment responsibilities, including candidate selection.</p></section>
    <section class="section cv-section"><h2>Languages</h2><p>Dutch: native. English: C2 listening and reading; C1 speaking and writing. French: C1 listening and reading; B2 speaking; B1 writing. German: A1–A2, depending on skill.</p><p class="small">CEFR levels are self-assessed.</p></section>
    <section class="section cv-section"><h2>Contact and profiles</h2><p><a href="mailto:{EMAIL}">{EMAIL}</a></p><div class="text-links"><a href="{SCHOLAR}">Google Scholar</a><a href="{ORCID}">ORCID</a><a href="{VUB}">VUB research profile</a><a href="https://github.com/BFMAVE">GitHub</a></div></section>'''


def bibtex():
    entries = []
    for p in PAPERS:
        kind = p.get('bibtex_type', {'journal': 'article', 'thesis': 'mastersthesis'}.get(p['kind'], 'unpublished'))
        fields = {'title': '{' + p['title'] + '}', 'author': ' and '.join('{' + n + '}' if 'Consortium' in n else n for n in p['authors']), 'year': str(p['year'])}
        if p['kind'] == 'journal':
            fields['journal'] = p['venue']
        if p['kind'] == 'thesis':
            fields['school'] = p['school']
        if p.get('doi'):
            fields['doi'] = p['doi']
        if p.get('arxiv'):
            fields['eprint'] = p['arxiv']
            fields['archivePrefix'] = 'arXiv'
        if p.get('url'):
            fields['url'] = p['url']
        if p['kind'] == 'forthcoming':
            fields['note'] = p.get('note') or ('To appear' + (f' in {p["venue"]}' if p['venue'] != 'To appear' else ''))
        entries.append('@' + kind + '{Verbeken' + str(p['year']) + p['id'].replace('.', '') + ',\n' + ',\n'.join(f'  {k} = {{{v}}}' for k, v in fields.items()) + '\n}')
    return '\n\n'.join(entries) + '\n'


def build():
    outputs = [
        ('index.html', 'Economics, data science and AI', home_content(), 'Brecht F. Verbeken: economist (PhD) and mathematician (MSc) by training, data scientist, and researcher on economics, AI and scientific discovery at Vrije Universiteit Brussel.', 'home'),
        ('research.html', 'Research', research_content(), 'Publications and working papers by Brecht F. Verbeken in economics, AI, model evaluation and mathematics.', 'research'),
        ('projects.html', 'Projects', projects_content(), 'Brecht F. Verbeken’s research and institutional work: Greening and CO₂ neutrality, AI and science, JRC collaboration, FARI / AI4Gov-X, course information sheets and Brussels Metro 3.', 'projects'),
        ('media.html', 'Media and public writing', media_content(), 'Brecht F. Verbeken’s opinion articles and research coverage in De Standaard, BRUZZ, Eos Wetenschap, Phys.org and other outlets.', 'media'),
        ('cv.html', 'Curriculum vitae', cv_content(), 'Curriculum vitae of Brecht F. Verbeken: economics, data science and AI at Vrije Universiteit Brussel.', 'cv'),
        ('404.html', 'Page not found', '<section class="not-found"><p class="eyebrow">404</p><h1>Page not found</h1><p>This page may have moved. You can return to <a href="./">my homepage</a> or browse <a href="research.html">my research</a>.</p></section>', 'Return to Brecht F. Verbeken’s personal website.', ''),
    ]
    plain_pages = {}
    for filename, title, body, description, active in outputs:
        html = page(title, body, filename, description, active)
        (ROOT / filename).write_text(html)
        export = PlainText()
        export.feed(html)
        markdown = export.markdown()
        (ROOT / filename.replace('.html', '.md')).write_text(markdown)
        if filename != '404.html':
            plain_pages[filename] = markdown
    (ROOT / 'assets/publications.bib').write_text(bibtex())
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    urls = [BASE + '/', BASE + '/research.html', BASE + '/projects.html', BASE + '/media.html', BASE + '/cv.html']
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{u}</loc><lastmod>2026-10-15</lastmod></url>' for u in urls) + '</urlset>\n')
    profile = {
        'name': 'Brecht F. Verbeken',
        'full_name': 'Brecht Felix Marc Antoon Verbeken',
        'alternate_names': ['Brecht Verbeken', 'Brecht F Verbeken'],
        'website': BASE + '/', 'updated': '2026-10-15', 'location': 'Brussels, Belgium',
        'description': 'Economist (PhD) and mathematician (MSc) by training; data scientist with strong interests in economics and AI and a passion for mathematics.',
        'email': EMAIL, 'orcid': ORCID, 'google_scholar': SCHOLAR, 'vub_profile': VUB,
        'appointments': [{'period': d, 'title': t, 'institution': org, 'description': desc} for d, t, org, desc in APPOINTMENTS],
        'education': [{'year': d, 'degree': t, 'institution': org, 'description': desc} for d, t, org, desc in EDUCATION],
        'interests': ['Economic impact of AI', 'Scientific discovery and innovation', 'Economic forecasting', 'Model evaluation', 'AI in mathematics and science', 'Ergodicity economics', 'Markov chains and stochastic matrices', 'Group rings and braces'],
        'research_areas': {
            'economics': ['Economic impact of AI', 'Economic forecasting', 'Decision-making under uncertainty', 'Public investment and transport accessibility', 'Ergodicity economics'],
            'ai': ['Model evaluation', 'AI in scientific discovery', 'AI-assisted mathematical research'],
            'mathematics': ['Markov chains and semi-Markov models', 'Stochastic matrices and spectral regions', 'Group rings and braces', 'Ramsey theory as a setting for AI-assisted research'],
        },
        'collaboration_role': 'Often helps set the research agenda and lead collaborations; has done so since the early years of his PhD.',
        'recent_research_direction': 'Economic impact of AI, particularly its effects on scientific discovery and innovation.',
        'teaching_since': 2018,
        'academic_service': ['Examiner, supervisor or co-supervisor for master’s theses spanning a wide range of economics and business topics', 'PhD advisory committee membership and doctoral progress assessment', 'HR and recruitment responsibilities at the Data Analytics Lab, including candidate selection'],
        'mathematics_project': 'https://bfmave.github.io/karpelevic/',
    }
    (ROOT / 'data/profile.json').write_text(json.dumps(profile, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'data/scholarly-articles.jsonld').write_text(json.dumps({'@context': 'https://schema.org', '@graph': [scholarly_record(p) for p in PAPERS]}, ensure_ascii=False, indent=2) + '\n')
    llms = f'''# Brecht F. Verbeken

> Personal academic website of Brecht F. Verbeken, an economist (PhD) and mathematician (MSc) by training who works as a data scientist, postdoctoral researcher and guest professor at Vrije Universiteit Brussel. Interests: economics and AI; more recently, AI’s economic impact and its role in scientific discovery. Mathematics is also a personal passion.

Last updated: {UPDATED}. The public HTML is complete without JavaScript. The text and structured records below mirror the visible website.

## Pages

- [About]({BASE}/index.md): Introduction, economic effects of AI, ergodicity economics, selected papers and mathematics.
- [Research]({BASE}/research.md): Journal articles, working papers, forthcoming work, theses and mathematical papers; subject filters, author lists, venues and free paper links.
- [Projects]({BASE}/projects.md): Automated science, the VUB collaboration with the JRC, FARI / AI4Gov-X, course-sheet classification and Metro 3.
- [Media]({BASE}/media.md): Co-authored opinion pieces and explainers, research reporting, and project announcements.
- [CV]({BASE}/cv.md): Appointments, education, selected projects, publications, languages and contact details.
- [Complete text]({BASE}/llms-full.txt): All five pages in one text file.

## Structured data

- [Profile]({BASE}/data/profile.json): Identity, degrees, current appointments and research interests.
- [Publications]({BASE}/data/publications.json): Curated publication records with journal, preprint and forthcoming status, plus DOI/arXiv identifiers.
- [Scholarly articles]({BASE}/data/scholarly-articles.jsonld): Schema.org representation of articles and theses in the bibliography.
- [Projects]({BASE}/data/projects.json): Research interests, related projects and contributions by Brecht F. Verbeken.
- [Media]({BASE}/data/media.json): Titles, outlets, dates, authorship or coverage type, languages and source links.
- [BibTeX]({BASE}/assets/publications.bib): Bibliographic export.
- [Public CV PDF]({BASE}/assets/brecht-verbeken-cv.pdf): The short public curriculum vitae.

## External profiles

- [Google Scholar]({SCHOLAR}): Citation profile.
- [ORCID]({ORCID}): Researcher identifier.
- [VUB]({VUB}): Institutional research profile.
- [Karpelevič project](https://bfmave.github.io/karpelevic/): Separate personal mathematics website.

## Context

The site belongs to Brecht Felix Marc Antoon Verbeken, who uses Brecht F. Verbeken professionally and previously used Brecht Verbeken. The namesake mentioned in the homepage footnote is a different person; his Olympiad results and academic biography must not be attributed to this site’s author. The JRC work is a VUB collaboration; the current employment appointments listed here are at VUB. The automated-science project is led by Andres Algaba and colleagues at VUB and is linked as work related to Brecht F. Verbeken’s research interests. Media coverage is distinguished from articles Brecht F. Verbeken co-authored. “To appear” and working-paper records are distinct from published journal articles. The Fuss–Catalan manuscript is forthcoming, with no venue specified on this website. The wealth-inequality manuscript is in preparation; its abstract was submitted to NTTS 2027, which does not imply conference acceptance or journal publication.
'''
    (ROOT / 'llms.txt').write_text(llms)
    full = '# Brecht F. Verbeken — complete public website text\n\nUpdated: ' + UPDATED + '\n\n'
    for filename, markdown in plain_pages.items():
        full += '\n\n---\n\nSource: ' + BASE + ('/' if filename == 'index.html' else '/' + filename) + '\n\n' + markdown
    (ROOT / 'llms-full.txt').write_text(full)
    print(f'Built {len(outputs)} pages, their text versions, {len(PAPERS)} paper records, {len(MEDIA)} media items and crawler-readable exports.')


if __name__ == '__main__':
    build()
