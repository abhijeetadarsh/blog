"""Generate sitemap.xml and robots.txt.

Pelican ships neither, and without a sitemap Google has to discover every post
by following links. The blog has almost no internal links, so several posts were
effectively invisible. robots.txt exists mainly to advertise the sitemap.

Only canonical, indexable URLs go in the sitemap: articles, pages, and the index.
Tag/category/author listings are thin, near-duplicate pages -- listing them in a
sitemap invites Google to spend crawl budget on them and can dilute which page
ranks for a term. They stay crawlable (linked in the nav), just not advertised.
"""

from __future__ import annotations

import os
from xml.sax.saxutils import escape

from pelican import signals
from pelican.generators import ArticlesGenerator, PagesGenerator

# Rough relevance hints. Google treats these as advisory at best, but a
# consistent scheme costs nothing and does no harm.
PRIORITY = {"index": "1.0", "article": "0.8", "page": "0.5"}
CHANGEFREQ = {"index": "daily", "article": "monthly", "page": "monthly"}


def _iso_date(document):
    """Prefer the modified date -- it is what <lastmod> is supposed to mean."""
    date = getattr(document, "modified", None) or getattr(document, "date", None)
    return date.strftime("%Y-%m-%d") if date else None


def _url_entry(location, lastmod, kind):
    parts = [f"    <loc>{escape(location)}</loc>"]
    if lastmod:
        parts.append(f"    <lastmod>{lastmod}</lastmod>")
    parts.append(f"    <changefreq>{CHANGEFREQ[kind]}</changefreq>")
    parts.append(f"    <priority>{PRIORITY[kind]}</priority>")
    body = "\n".join(parts)
    return f"  <url>\n{body}\n  </url>"


def _collect(generators):
    """Return (siteurl, entries) with drafts and hidden content excluded."""
    context = generators[0].context
    siteurl = context.get("SITEURL", "").rstrip("/")

    entries = [_url_entry(f"{siteurl}/", None, "index")]

    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            for article in generator.articles:
                entries.append(
                    _url_entry(
                        f"{siteurl}/{article.url}", _iso_date(article), "article"
                    )
                )
        elif isinstance(generator, PagesGenerator):
            for page in generator.pages:
                entries.append(
                    _url_entry(f"{siteurl}/{page.url}", _iso_date(page), "page")
                )

    return siteurl, entries


def write_seo_files(generators):
    siteurl, entries = _collect(generators)
    if not siteurl:
        return

    # This signal fires before the writers run, and DELETE_OUTPUT_DIRECTORY
    # (set in publishconf) means the directory may not exist yet on a clean
    # build -- which is exactly what CI does every time.
    output_path = generators[0].output_path
    os.makedirs(output_path, exist_ok=True)

    joined = "\n".join(entries)
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{joined}\n"
        "</urlset>\n"
    )
    with open(os.path.join(output_path, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(sitemap)

    # Allow everything. The 404 page carries its own noindex meta tag, and the
    # search index under /pagefind/ is data the crawler gains nothing from.
    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /pagefind/\n"
        "\n"
        f"Sitemap: {siteurl}/sitemap.xml\n"
    )
    with open(os.path.join(output_path, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(robots)


def register():
    signals.all_generators_finalized.connect(write_seo_files)
