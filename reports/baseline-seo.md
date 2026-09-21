# Baseline SEO/GEO report — genefold.ai

Date: 2026-09-21
Scope: repository state before this branch; external link verification performed live.

## Pre-existing state (before this change)

- `_config.yaml` contained only `repository: Genefold/genefold.github.io`; no
  `url`, title, or description.
- No `robots.txt`, no `sitemap.xml`, no `feed.xml`, no `llms.txt`.
- No canonical URLs, no Open Graph / Twitter metadata, no JSON-LD on any page.
- All pages were standalone HTML without a shared template.
- `404.html` missing.

## External link verification (live HTTP checks, 2026-09-21)

| URL | Status | Action taken |
|---|---|---|
| github.com/tuned-org-uk/pyarrowspace | 200 | kept, used as canonical ArrowSpace Python source |
| github.com/tuned-org-uk/arrowspace-rs | 200 | kept; Apache-2.0 confirmed via GitHub API |
| github.com/Genefold/arrowspace | 404 | links on homepage fixed (issues/contributing) |
| github.com/Genefold/arro-memory | 404 | OSS card removed from homepage |
| github.com/Genefold/arro-cve-search | 404 | "View source" button removed from demo section |
| github.com/Genefold/arrowspace_tuner | 200 | kept |
| github.com/Genefold/arro-server | 200 | kept |
| github.com/Genefold/arrowspace-skills | 200 | kept |
| github.com/Genefold/arrowspace-mcp | 200 | kept; Apache-2.0 confirmed via GitHub API |
| pypi.org/project/arrowspace/ | 200 | used as installUrl in SoftwareSourceCode |
| tuned.org.uk/arrowspace-paper | 200 | paper page for JOSS DOI 10.21105/joss.09002 |
| arxiv.org/abs/2606.21535 | 200 | metadata fetched for research page |
| authorea.com (Epiplexity paper) | 403 (bot block) | linked only; no metadata copied |
| cve-search-engine.genefold.ai | 200 | referenced as live demo |
| linkedin.com/company/genefold-ai | 999 (bot block) | kept; not verifiable by curl |

## Tooling

- Ruby 3.4.8, github-pages gem, local Jekyll build verified.
- Python 3 with Pillow used to generate 16 OG images (1200x630) in `assets/og/`.

## Validation performed locally

- `bundle exec jekyll build` succeeds.
- `scripts/check_meta.py`: 24 built pages; unique titles/descriptions; canonical,
  OG, and Twitter tags present; JSON-LD parses; single h1; internal links resolve;
  sitemap URLs all built; robots.txt references sitemap.
- Deployed-site checks pending first deploy: HTTP 200 on robots/sitemap/llms.txt,
  Search Console submission, Lighthouse, Rich Results Test, URL inspection.