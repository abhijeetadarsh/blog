# CodeLog

Source for [codelog.tomiarb.com](https://codelog.tomiarb.com), a Pelican blog.

## Writing a post

Posts are written in one of the supported source formats and built into
`content/` by `build_content.py`. **Never edit `content/*.md` directly** — the
whole directory is regenerated on every build.

| Source | Where it lives | Extension | Becomes |
| --- | --- | --- | --- |
| Jupyter notebook | `notebooks/` | `.ipynb` | a post |
| Markdown | `posts/` | `.md`, `.markdown` | a post |
| Markdown | `pages/` | `.md`, `.markdown` | a standing page (About, Contact …) |

Every directory is scanned recursively. Files or directories starting with `_`
or `.` are skipped, which is a handy way to park a draft. Posts need `Title`
and `Date`; pages only need `Title`.

### Notebooks

Put the metadata in a leading **Raw NBConvert** cell:

```
Title: Basic Functions
Date: 2025-09-11 16:33
Category: Core Python 3
Tags: python, functions
Author: Abhijeet Adarsh
Summary: Basic Functions
```

Code-cell outputs (plots, etc.) and images attached to markdown cells are
extracted automatically.

### Markdown

Either Pelican's native header:

```markdown
Title: Hello Markdown
Date: 2026-08-01 10:00
Category: Notes
Tags: markdown, pelican
Summary: A short summary.

## Heading

Body text.
```

…or YAML front matter, if you prefer:

```markdown
---
title: Hello Markdown
date: 2026-08-01 10:00
category: Notes
tags:
  - markdown
  - pelican
summary: A short summary.
---

Body text.
```

`Title` and `Date` are required; everything else is optional. `Slug` defaults to
a slugified title and determines the output URL.

Keys are normalised on the way in, because Python-Markdown's metadata parser
only accepts `[A-Za-z0-9_-]` in a key — a key written with a space would
otherwise end up printed in the body of the post. `Last Modified`, `Updated`
and `Lastmod` all become Pelican's `Modified`, which the theme renders as
"Updated <date>".

### Images

Reference images with a relative path from the source file:

```markdown
![diagram](images/package-diagram.png)
```

They are copied into `content/nbimages/<slug>/` under a unique name and the link
is rewritten to a Pelican `{static}` URL. Absolute URLs are left alone.

## Building

```
make convert   # sources -> content/*.md
make content   # content/ -> output/ via Pelican
make index     # Pagefind search index over output/
make build     # all three
make listen    # local dev server
make clean     # remove generated files
```

The Makefile expects a virtualenv at `venv/` with `requirements.txt` installed.
CI (`.github/workflows/ci.yaml`) runs the same steps on push to `main` and
deploys `output/` to GitHub Pages.

## Adding another input format

`build_content.py` dispatches on file extension via the `HANDLERS` dict. A
handler takes a source `Path` and returns `(metadata, markdown_body)` — or
`None` to skip the file. Register it in `HANDLERS` and add its source directory
to `SOURCES` as a `(source dir, destination dir)` pair.

## Theme

`themes/codelog` — monochrome, system font stack, no webfonts and no runtime
dependencies. It follows the viewer's OS light/dark setting and remembers a
manual override in `localStorage`.

```
themes/codelog/
  templates/
    base.html          shell: head, masthead, main, footer, search modal
    index.html         the feed; category/tag/author extend it
    article.html       post layout, related posts, prev/next, author card
    page.html          standing pages
    archives.html  categories.html  tags.html  authors.html  404.html
    partials/
      masthead.html    sticky header, nav, search + theme buttons
      footer.html      footer columns and the footer ad slot
      ads.html         the ad slot macro (see below)
      macros.html      cards, post meta, reading time
      rail.html        right-hand rail for list pages
      search.html  pagination.html  translations.html  analytics.html
  static/
    css/main.css       tokens, layout, components — edit tokens first
    css/syntax.css     monochrome Pygments
    js/main.js         theme, nav, search, TOC, progress, copy buttons, ads
```

All colour, type and spacing lives in CSS custom properties at the top of
`main.css`. Restyling the site is mostly a matter of changing those tokens.

Behaviour in `main.js`: theme toggle, mobile nav, search modal (`/` or `⌘K`,
arrow keys, Esc), a table of contents built from the post's headings with
scroll-spy, reading progress bar, copy buttons on code blocks, and ad
placement.

### Ad slots

The layout permanently reserves five slots, so switching ads on never moves the
page around. Configure them in `pelicanconf.py`:

```python
ADS_ENABLED = True
AD_CLIENT = 'ca-pub-XXXXXXXXXXXXXXXX'
AD_SLOTS = {'top': '1234567890', 'sidebar': '...', ...}
```

| Slot | Where | Reserved |
| --- | --- | --- |
| `top` | under the header on list pages | 100px |
| `in_feed` | after the third card in the feed | 140px |
| `in_article` | moved next to a heading inside a post | 200px |
| `sidebar` | sticky, right rail | 320px |
| `footer` | band above the footer, every page | 120px |

Any slot without an id — which is all of them right now — shows a quote from
`AD_NOTES` instead, so no box is ever dead space. Notes are picked from the page
they sit on plus a per-slot offset, so one page never repeats a quote. Edit
`AD_NOTES` in `pelicanconf.py` to change the pool; entries are
`(text, attribution)` and the attribution may be empty.

To render a slot somewhere new:

```jinja
{% import 'partials/ads.html' as ads with context %}
{{ ads.slot('sidebar', 'halfpage') }}
```

Slots carry `data-pagefind-ignore`, so their text never pollutes search results.

### Other switches

| Setting | Effect |
| --- | --- |
| `SITEDESCRIPTION` | hero copy, footer tagline, default meta description |
| `AUTHOR_BIO` | the author card at the end of a post |
| `NEWSLETTER_ACTION` | set a form URL to switch the subscribe block on |
| `GOOGLE_ANALYTICS` | gtag id; omit to drop the script entirely |
| `DISQUS_SITENAME` | enables the comments section |
