#!/usr/bin/env python3
"""Create the short public CV; requires reportlab and a Unicode TTF font."""
from pathlib import Path
from html import escape
import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('SITE_BASE_URL', 'http://127.0.0.1:8765').rstrip('/')
SITE_LABEL = 'Website (local draft)' if BASE.startswith('http://127.0.0.1:') else BASE.removeprefix('https://').removeprefix('http://')
PAPERS = {p['id']: p for p in json.loads((ROOT / 'data/publications.json').read_text())}
FONT_DIR = Path('/System/Library/Fonts/Supplemental')
for name, file in [('Body', 'Arial.ttf'), ('Body-Bold', 'Arial Bold.ttf'), ('Body-Italic', 'Arial Italic.ttf'), ('Title', 'Times New Roman.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Body-Bold', italic='Body-Italic', boldItalic='Body-Bold')
NAVY = colors.HexColor('#183d59')
INK = colors.HexColor('#252b30')
MUTED = colors.HexColor('#626972')
styles = {
    'name': ParagraphStyle('name', fontName='Title', fontSize=27, leading=31, textColor=NAVY, spaceAfter=5),
    'subtitle': ParagraphStyle('subtitle', fontName='Body', fontSize=11, leading=15, textColor=INK, spaceAfter=8),
    'contact': ParagraphStyle('contact', fontName='Body', fontSize=8.5, leading=12, textColor=MUTED, spaceAfter=8),
    'h2': ParagraphStyle('h2', fontName='Title', fontSize=16, leading=20, textColor=NAVY, spaceBefore=15, spaceAfter=8, keepWithNext=True),
    'body': ParagraphStyle('body', fontName='Body', fontSize=9.4, leading=13.6, textColor=INK, spaceAfter=7),
    'item': ParagraphStyle('item', fontName='Body', fontSize=9.4, leading=13.4, textColor=INK, spaceAfter=3, keepWithNext=True),
    'meta': ParagraphStyle('meta', fontName='Body', fontSize=8.4, leading=11.8, textColor=MUTED, spaceAfter=4),
    'pub': ParagraphStyle('pub', fontName='Body', fontSize=8.6, leading=12.1, textColor=INK, spaceAfter=8),
}
def clean(s):
    return s.replace('–', '-').replace('—', '-').replace('’', "'").replace('“', '"').replace('”', '"')
def para(s, style='body'):
    return Paragraph(clean(s), styles[style])
def heading(s):
    return para(s, 'h2')
def item(title, meta, desc):
    return KeepTogether([para('<b>'+title+'</b>', 'item'), para(meta, 'meta'), para(desc)])

story = [para('Brecht F. Verbeken', 'name'), para('Economics | Data science | Artificial intelligence', 'subtitle'),
    para('Vrije Universiteit Brussel | Brussels, Belgium<br/>'
         '<link href="mailto:brecht.verbeken@vub.be" color="#183d59">brecht.verbeken@vub.be</link> | '
         f'<link href="{BASE}/" color="#183d59">{SITE_LABEL}</link> | '
         '<link href="https://scholar.google.com/citations?user=MC0hy74AAAAJ&amp;hl=en" color="#183d59">Google Scholar</link>', 'contact'),
    heading('Profile'),
    para('Economist (PhD) and mathematician (MSc) by training, working as a data scientist and researcher with strong interests in economics and AI. More recently, particularly interested in the economic impact of AI and its role in scientific discovery and innovation. Research experience in consumer-confidence nowcasting, model evaluation and AI in mathematics and science. Combines quantitative methods with institutional projects and reproducible analysis.'),
    heading('Appointments'),
    item('Guest Professor (10%)', 'Vrije Universiteit Brussel | September 2025 - present', 'Course holder for Mathematics II for Business Economics (6 ECTS), with responsibility for teaching and assessment; master\'s-thesis supervision.'),
    item('Postdoctoral Researcher (90%)', 'Vrije Universiteit Brussel | September 2024 - present', 'Research in model evaluation, AI capabilities and limitations, AI-assisted mathematics and stochastic systems. Institutional AI workflows, research proposal development and interdisciplinary collaboration.'),
    item('Research Associate', 'Vrije Universiteit Brussel | September 2022 - September 2024', 'Uplift-model evaluation and semi-Markov processes; mathematics teaching, thesis supervision and assessment.'),
    item('Doctoral Researcher with Teaching Duties', 'Vrije Universiteit Brussel | April 2018 - September 2022', 'Stochastic models for manpower planning; collaboration on economic nowcasting and ergodicity economics; teaching mathematics and manpower planning.'),
    heading('Education'),
    item('PhD in Applied Economic Sciences - Business Engineering', 'Vrije Universiteit Brussel | 2024', '<i>On Models and Metrics: Improving Stochastic Model Performance in Manpower Planning.</i>'),
    para('<b>Master of Mathematics - Fundamental Mathematics</b><br/>Vrije Universiteit Brussel / University of Antwerp | 2018'),
    para('<b>Bachelor of Mathematics</b><br/>Vrije Universiteit Brussel | 2016'),
    heading('Methods and tools'),
    para('Mixed-frequency nowcasting, econometrics, statistical model evaluation, treatment-effect rankings, uncertainty, simulation, stochastic and semi-Markov processes. Python, R, LaTeX; textual analysis, APIs and local model workflows; reproducible analytical pipelines.'),
    PageBreak(),
    para('Brecht F. Verbeken', 'name'),
    para('Selected research and institutional work', 'subtitle'),
    heading('Selected projects'),
    para('<b>AI and knowledge production.</b> Interested in how AI changes the pace and direction of scientific discovery and innovation, the division of work between researchers and AI, and verification costs.'),
    para('<b>AI-supported science for policy.</b> Through a VUB collaboration with the JRC, I was involved in developing evaluation templates and contributed to a validation protocol for AI-supported research outputs.'),
    para('<b>FARI / AI4Gov-X.</b> Co-authored an internal review of AI4Scale requirements and prototype validation, covering feasibility, prioritisation, deployment, governance and process ownership.'),
    para('<b>Institutional AI adoption.</b> Led technical implementation of LLM-assisted classification for an initial 4,684 course information sheets at VUB, with human validation and documented quality controls.'),
    para('<b>Public investment under uncertainty.</b> Led scenario-based research on Brussels Metro 3, using official transport and open-map data to examine accessibility and geographical differences.'),
    para('<b>Mathematics.</b> Research on stochastic matrices and spectral regions, including an illustrated Karpelevič project with Vincent Ginis. First author of a documented case study of AI-assisted mathematical proof development.'),
    heading('Selected publications and working papers'),
]
for pid in ['2508.15842', '2606.26130', '2602.18918', 'uplift', 'nowcasting']:
    p = PAPERS[pid]
    names = ', '.join(p['authors'])
    venue = p['venue']
    if p.get('location'): venue += ', ' + p['location']
    if p['kind'] == 'working': venue = 'Working paper, arXiv:' + p['arxiv']
    story.append(para(f'<b>{escape(p["title"])}</b><br/>{escape(names)} ({p["year"]}). <i>{escape(venue)}</i>. <link href="{escape(p["url"], quote=True)}" color="#183d59">Paper</link>', 'pub'))
story += [
    para(f'Full bibliography, free paper versions and mathematical papers: <link href="{BASE}/research.html" color="#183d59">All research</link>', 'meta'),
    heading('Teaching, service and languages'),
    para('University-level teaching since 2018. Course responsibility for Mathematics II for Business Economics; supervision of more than 25 master\'s theses on economics and business topics; scientific writing and interdisciplinary collaboration.'),
    para('Serve on PhD advisory committees, contributing to the assessment of doctoral research progress. HR and recruitment responsibilities at the Data Analytics Lab, including candidate selection.'),
    para('<b>Dutch:</b> native. <b>English:</b> C2 listening/reading, C1 speaking/writing. <b>French:</b> C1 listening/reading, B2 speaking, B1 writing. <b>German:</b> A1-A2 by skill. CEFR levels are self-assessed.'),
]

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Body', 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(43, 27, 'Brecht F. Verbeken | Public CV | 15 October 2026')
    canvas.drawRightString(A4[0]-43, 27, str(doc.page))
    canvas.restoreState()

if __name__ == '__main__':
    path = ROOT / 'assets/brecht-verbeken-cv.pdf'
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=43, leftMargin=43, topMargin=35, bottomMargin=43,
        title='Brecht F. Verbeken - Curriculum Vitae', author='Brecht F. Verbeken', subject='Economics, artificial intelligence and quantitative research')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(path)
