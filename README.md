# Brecht F. Verbeken — personal website

Public academic website for Brecht F. Verbeken: quantitative economics, data science and AI, with mathematics as a personal passion.

Status: publication authorised by Brecht on 15 October 2026. Public site: https://bfmave.github.io/. This repository contains the reviewed website and its generators.

## Editing

The site is static HTML and CSS. No framework, build service, external fonts, trackers or JavaScript rendering is needed to read the content. The small script in `assets/site.js` adds optional publication filters and automatic update checks.

- Edit biography, page structure and appointments in `scripts/build.py`.
- Edit publication records in `data/publications.json`.
- Edit project descriptions in `data/projects.json`.
- Edit media records in `data/media.json`.
- Edit presentation in `assets/styles.css`.

Regenerate the public pages, Markdown, JSON-LD, BibTeX, sitemap and LLM-readable exports:

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8765 --bind 127.0.0.1
```

The generators default to `http://127.0.0.1:8765` for canonical URLs, CV links and machine-readable exports, so the offline draft is self-contained. `SITE_BASE_URL` can be set to a public URL only when publication is explicitly authorised.

Build the public version with its public canonical URL before deployment:

```sh
SITE_BASE_URL=https://bfmave.github.io python3 scripts/build_cv.py
SITE_BASE_URL=https://bfmave.github.io python3 scripts/build.py
python3 scripts/check.py
```

GitHub Pages serves the repository’s main branch from the root directory. `.nojekyll` keeps the static files unchanged. Continue future drafts locally and publish content changes only when Brecht authorises them.

## Automatic updates

The build writes a deterministic release identifier to every HTML page and `version.json`. Styles, scripts and public CV links include content hashes, so changed assets use fresh URLs. Build the CV before the website when changing both, so the PDF hash matches the final file.

With JavaScript enabled, the page fetches the small version manifest without browser caching and with a unique query to bypass shared cached responses. It checks on arrival, on return to a tab and every minute while visible. An outdated page navigates to a fresh URL, preserving query filters and anchors; the temporary update parameters are removed once the expected release loads. Failed requests leave the page usable, and a delayed deployment cannot cause an immediate refresh loop.

An already-cached page from before these checks existed still needs its normal cache expiry or one refresh. JavaScript-disabled clients continue to use ordinary HTTP caching. This does not purge visitors’ devices or change GitHub’s HTTP cache headers.

Validate the update behaviour with `node --test scripts/test-site-updates.mjs` and the normal `python3 scripts/check.py`.

## Public CV

`assets/brecht-verbeken-cv.pdf` is a short public CV. Its source is `scripts/build_cv.py`, which uses ReportLab and the Arial and Times New Roman fonts. The font directory defaults to the macOS system fonts; adjust `FONT_DIR` for another operating system. Regenerate it separately after content changes, then render and inspect both pages before publishing.

The application documents used for biographical research, unpublished manuscript files and private working notes are not included in this repository.

## Data and crawlability

All substantive content is present in the HTML. Each main page also has a Markdown version, and `llms.txt` indexes those versions, `llms-full.txt`, and the JSON/BibTeX exports. Schema.org metadata describes the person, papers and media records. The same facts and publication status appear in both the human-readable and machine-readable content. `robots.txt` allows crawlers; `sitemap.xml` lists the public pages.

These files make access easier but do not guarantee that any search engine or AI service will index the site.

## Bibliography notes

The bibliography was checked against Brecht’s Google Scholar profile, arXiv, journal/DOI records and institutional sources on 15 October 2026. Published papers, preprints and forthcoming work are labelled separately. Preprints that subsequently appeared in a journal are listed once, with a link to their free version. The Fuss–Catalan manuscript with Arne Vanhoyweghen and Vincent Ginis is marked “Work in progress”.

The separate Karpelevič website remains at https://bfmave.github.io/karpelevic/.

The words, personal information and original site content belong to their respective authors. Linked journal articles, news stories and third-party material remain subject to their original terms.
