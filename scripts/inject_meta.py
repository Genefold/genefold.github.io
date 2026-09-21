#!/usr/bin/env python3
"""Inject canonical/OG/Twitter/JSON-LD metadata into the static HTML pages
(engineering index, engineering articles, privacy). Idempotent: skips files
that already contain the injected marker."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.genefold.ai"
MARK = '<link rel="canonical"'

ORG = {
    "@type": "Organization",
    "@id": f"{SITE}/#organization",
    "name": "Genefold AI",
    "url": f"{SITE}/",
    "logo": f"{SITE}/favicon.ico",
    "description": (
        "Genefold AI develops spectral methods for embedding retrieval, "
        "graph analysis, drift detection, and out-of-distribution monitoring."
    ),
    "sameAs": [
        "https://github.com/Genefold",
        "https://www.linkedin.com/company/genefold-ai",
    ],
}

# url, title, description, og_type, image, published, is_article
PAGES = {
    "engineering/index.html": dict(
        url=f"{SITE}/engineering/",
        title="Engineering — Genefold",
        description=(
            "Notes on systems, algorithms, and the engineering choices behind "
            "ArrowSpace and spectral intelligence at Genefold."
        ),
        og_type="website",
        image=f"{SITE}/assets/og/genefold-default.png",
        published=None,
        section=("Engineering", f"{SITE}/engineering/"),
        article=False,
    ),
    "engineering/001.html": dict(
        url=f"{SITE}/engineering/001.html",
        title="Designing ArrowSpace and graph wiring — Genefold Engineering",
        description=None,  # reuse existing meta description
        og_type="article",
        image=f"{SITE}/assets/og/engineering-001.png",
        published="2026-07-08",
        section=("Engineering", f"{SITE}/engineering/"),
        article=True,
    ),
    "engineering/002.html": dict(
        url=f"{SITE}/engineering/002.html",
        title="Genefold First Principles: Depletion of Uncertainty — Genefold Engineering",
        description=None,
        og_type="article",
        image=f"{SITE}/assets/og/engineering-002.png",
        published="2026-07-15",
        section=("Engineering", f"{SITE}/engineering/"),
        article=True,
    ),
    "engineering/003.html": dict(
        url=f"{SITE}/engineering/003.html",
        title="Genefold First Principles: From Entropy to Epiplexity — Genefold Engineering",
        description=None,
        og_type="article",
        image=f"{SITE}/assets/og/engineering-003.png",
        published="2026-08-24",
        section=("Engineering", f"{SITE}/engineering/"),
        article=True,
    ),
    "engineering/004.html": dict(
        url=f"{SITE}/engineering/004.html",
        title="Genefold First Principles: The Curriculum Engine — Genefold Engineering",
        description=None,
        og_type="article",
        image=f"{SITE}/assets/og/engineering-004.png",
        published="2026-08-24",
        section=("Engineering", f"{SITE}/engineering/"),
        article=True,
    ),
    "engineering/005.html": dict(
        url=f"{SITE}/engineering/005.html",
        title="Synthetic Data That Teaches: A Feedback Loop for Training Beyond Static Corpora — Genefold Engineering",
        description=None,
        og_type="article",
        image=f"{SITE}/assets/og/engineering-005.png",
        published="2026-08-27",
        section=("Engineering", f"{SITE}/engineering/"),
        article=True,
    ),
    "privacy.html": dict(
        url=f"{SITE}/privacy.html",
        title="Privacy Policy & Terms — Genefold",
        description=(
            "Genefold privacy policy, terms of service, and data handling practices."
        ),
        og_type="website",
        image=f"{SITE}/assets/og/genefold-default.png",
        published=None,
        section=None,
        article=False,
    ),
}


def build_graph(spec, page_title, page_description):
    graph = [ORG, {
        "@type": "WebSite",
        "@id": f"{SITE}/#website",
        "url": f"{SITE}/",
        "name": "Genefold AI",
        "publisher": {"@id": f"{SITE}/#organization"},
        "inLanguage": "en",
    }, {
        "@type": "WebPage",
        "@id": f"{spec['url']}#webpage",
        "url": spec["url"],
        "name": page_title,
        "description": page_description,
        "isPartOf": {"@id": f"{SITE}/#website"},
        "about": {"@id": f"{SITE}/#organization"},
        "inLanguage": "en",
    }]
    if spec["article"]:
        node = {
            "@type": "TechArticle",
            "@id": f"{spec['url']}#article",
            "headline": page_title,
            "description": page_description,
            "url": spec["url"],
            "datePublished": spec["published"],
            "dateModified": "2026-09-21",
            "inLanguage": "en",
            "author": {"@type": "Organization", "name": "Genefold AI", "url": f"{SITE}/"},
            "publisher": {"@type": "Organization", "name": "Genefold AI", "url": f"{SITE}/"},
            "isPartOf": {"@id": f"{SITE}/#website"},
        }
        graph.append(node)
    if spec["section"]:
        name, surl = spec["section"]
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": name, "item": surl},
                {"@type": "ListItem", "position": 3, "name": page_title, "item": spec["url"]},
            ],
        })
    return {"@context": "https://schema.org", "@graph": graph}


def block(spec, page_title, page_description):
    p = spec
    parts = [
        f'  <link rel="canonical" href="{p["url"]}" />',
        '  <meta name="robots" content="index,follow,max-image-preview:large" />',
        "",
        f'  <meta property="og:type" content="{p["og_type"]}" />',
        '  <meta property="og:site_name" content="Genefold AI" />',
        f'  <meta property="og:title" content="{p["title"]}" />',
        f'  <meta property="og:description" content="{page_description}" />',
        f'  <meta property="og:url" content="{p["url"]}" />',
        f'  <meta property="og:image" content="{p["image"]}" />',
        '  <meta property="og:locale" content="en_US" />',
    ]
    if p["published"]:
        parts.append(f'  <meta property="article:published_time" content="{p["published"]}" />')
    parts += [
        '  <meta name="twitter:card" content="summary_large_image" />',
        f'  <meta name="twitter:title" content="{p["title"]}" />',
        f'  <meta name="twitter:description" content="{page_description}" />',
        f'  <meta name="twitter:image" content="{p["image"]}" />',
        "",
        '  <script type="application/ld+json">',
        json.dumps(build_graph(p, page_title, page_description), indent=2),
        "  </script>",
    ]
    return "\n".join(parts)


def main():
    errors = []
    for rel, spec in PAGES.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        if MARK in text:
            print(f"skip (already injected): {rel}")
            continue
        desc_start = text.find('<meta name="description" content="')
        if desc_start == -1:
            errors.append(rel)
            print(f"ERROR no description meta: {rel}")
            continue
        content_start = text.find('content="', desc_start) + len('content="')
        dend = text.find('"', content_start)
        existing_desc = text[content_start:dend]
        existing_title = text.split("<title>")[1].split("</title>")[0].strip()
        page_desc = existing_desc.replace("&mdash;", "—").replace("&amp;", "&")
        page_title = existing_title.replace("&mdash;", "—").replace("&amp;", "&")
        inj = block(spec, page_title, page_desc)
        insert_at = text.find("\n", dend)
        text = text[:insert_at] + "\n" + inj + text[insert_at:]
        path.write_text(text, encoding="utf-8")
        print(f"injected: {rel}")
    if errors:
        sys.exit(f"failed: {errors}")


if __name__ == "__main__":
    main()