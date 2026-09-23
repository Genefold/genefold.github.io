#!/usr/bin/env python3
"""Static-site metadata and structure checks. Run after `jekyll build`:

    python3 scripts/check_meta.py

Checks (stdlib only):
- every HTML page has a unique non-empty title and description
- canonical link present, absolute, no localhost
- og:title / og:description / og:image present
- all JSON-LD blocks parse as JSON
- exactly one h1 per page
- internal hrefs resolve to generated files
- sitemap.xml URLs resolve; robots.txt exists and references the sitemap
"""
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
LOCALHOST = ("localhost", "127.0.0.1")

seen_titles: dict[str, list] = {}
seen_descriptions: dict[str, list] = {}
errors: list[str] = []


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.description = ""
        self.canonical = None
        self.og = {}
        self.h1 = 0
        self.json_ld = []
        self._in_script_json = False
        self._json_buf = []
        self.hrefs = []
        self.srcs = []
        self.robots = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = (a.get("name") or a.get("property") or "").lower()
            content = a.get("content", "")
            if name == "description":
                self.description = content
            elif name == "robots":
                self.robots = content
            elif name.startswith("og:"):
                self.og[name] = content
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
        elif tag in ("img", "script", "link") and a.get("src"):
            self.srcs.append(a["src"])
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_script_json = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_script_json:
            self._in_script_json = False
            self._json_buf.append("")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._in_script_json:
            self._json_buf.append(data)


def resolve(url: str) -> Path | None:
    """Map an internal href/src to a path under _site, or None if external."""
    u = urlparse(url)
    if u.scheme and u.scheme.startswith("http"):
        return None  # external: not checked here
    if u.scheme in ("mailto", "tel", "data"):
        return None
    path = u.path
    if path in ("", "#"):
        return None
    candidate = SITE / path.lstrip("/")
    if candidate.is_dir():
        candidate = candidate / "index.html"
    elif not candidate.exists() and not path.endswith("/"):
        candidate = candidate.parent / candidate.name.replace(".html", "") / "index.html"
        if not candidate.exists():
            return None
    return candidate


def main() -> int:
    site = SITE
    if not site.is_dir():
        raise SystemExit(f"missing build output: {site}")

    html_files = sorted(site.rglob("*.html"))
    if not html_files:
        raise SystemExit("no HTML files in _site")

    for path in html_files:
        rel = path.relative_to(site)
        text = path.read_text(encoding="utf-8")
        parser = PageParser()
        parser._in_script_json = False
        parser.feed(text)

        # title / description uniqueness
        title = parser.title.strip()
        desc = parser.description.strip()
        if not title:
            errors.append(f"{rel}: missing <title>")
        else:
            seen_titles.setdefault(title, []).append(str(rel))
        if not desc:
            errors.append(f"{rel}: missing meta description")
        else:
            seen_descriptions.setdefault(desc, []).append(str(rel))

        # canonical
        if parser.canonical is None:
            errors.append(f"{rel}: missing canonical")
        elif not parser.canonical.startswith("https://"):
            errors.append(f"{rel}: canonical not absolute: {parser.canonical}")
        elif "localhost" in parser.canonical or "127.0.0.1" in parser.canonical:
            errors.append(f"{rel}: canonical points to localhost")

        # open graph
        for key in ("og:title", "og:description", "og:image", "og:url"):
            if key not in parser.og:
                errors.append(f"{rel}: missing {key}")

        # single h1
        if parser.h1 != 1:
            errors.append(f"{rel}: expected 1 h1, found {parser.h1}")

        # JSON-LD parseable
        buf = parser._json_buf
        if buf:
            raw = "".join(buf)
            try:
                json.loads(raw)
            except json.JSONDecodeError as e:
                errors.append(f"{rel}: invalid JSON-LD: {e}")

        # no localhost anywhere
        if "localhost" in text or "127.0.0.1" in text:
            errors.append(f"{rel}: localhost reference in output")

        # internal links resolve
        for href in parser.hrefs + parser.srcs:
            target = resolve(href)
            if target is None:
                continue
            if not target.exists():
                errors.append(f"{rel}: broken internal ref {href}")

    for label, seen in (("title", seen_titles), ("description", seen_descriptions)):
        for value, paths in seen.items():
            if len(paths) > 1:
                errors.append(f"duplicate {label}: {value!r} in {paths}")

    # robots + sitemap
    if not (site / "robots.txt").exists():
        errors.append("missing _site/robots.txt")
    sitemap = site / "sitemap.xml"
    if not sitemap.exists():
        errors.append("missing _site/sitemap.xml")
    else:
        stext = sitemap.read_text(encoding="utf-8")
        for loc in [l for l in stext.split("<loc>")][1:]:
            url = loc.split("</loc>")[0].strip()
            if not url.startswith("https://www.genefold.ai"):
                errors.append(f"sitemap URL not on canonical origin: {url}")
                continue
            target = resolve(url[len("https://www.genefold.ai"):])
            if target is None or not target.exists():
                errors.append(f"sitemap URL not built: {url}")
        rtext = (site / "robots.txt").read_text(encoding="utf-8")
        if "sitemap.xml" not in rtext:
            errors.append("robots.txt does not reference the sitemap")

    if errors:
        print("FAILED:")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)
    print(f"OK: {len(html_files)} pages checked")
    for rel in sorted(p.relative_to(site) for p in html_files):
        print(f"  {rel}")


if __name__ == "__main__":
    main()