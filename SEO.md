# SEO for CodeLog

A record of what was wrong, what changed, why each change matters, and what
only you can do from here. Written to be read once end-to-end, then used as a
reference.

---

## 0. The honest version of "rank #1 on Google"

You cannot decide to rank first. Google ranks a *page* for a *query*, and it
does so by comparing your page against everything else that answers that query.
So the only question that matters is: **which query?**

For `python classes` you are competing with docs.python.org, W3Schools and Real
Python — sites with twenty years of history and millions of links. An 11-post
blog will not win that, and no amount of technical tuning changes it.

For `is __init__ a constructor in python` you are competing with a handful of
Stack Overflow answers and a few blog posts. That is winnable, and your post is
genuinely about exactly that.

This is the whole strategy: **win specific questions first.** Rankings on
narrow queries build the topical authority and links that later make broader
queries reachable. Everything below serves that.

Realistic timeline for a site this size: first impressions in Search Console in
1–4 weeks after indexing, meaningful positions on long-tail queries in 3–6
months, compounding after that — and only if you keep publishing.

---

## 1. What was broken

Ranked by how much damage each was doing.

### 1.1 No sitemap at all — `sitemap.xml` returned 404

A sitemap is the list of URLs you are asking Google to crawl. Without one,
Google discovers pages only by following links. Your posts had very few links
pointing at them, so some had no reliable discovery path.

**Fixed:** new plugin `plugins/seo_files.py` generates `sitemap.xml` at build
time — 13 URLs (home, 11 posts, the About page) with `<lastmod>` taken from each
post's `Modified` date.

Tag, category and author listing pages are deliberately **excluded**. They are
thin, near-duplicate pages; advertising them spends crawl budget on low-value
URLs and invites Google to rank a tag listing where the post should rank. They
stay crawlable via the nav — just not promoted.

### 1.2 `robots.txt` was a single broken line

The file contained literally `User-agent: *` and nothing else — no rules, and
crucially no sitemap reference. The `Sitemap:` line in robots.txt is one of the
two ways Google finds your sitemap (the other is manual submission, §3).

**Fixed:** the same plugin writes a real one:

```
User-agent: *
Allow: /
Disallow: /pagefind/

Sitemap: https://codelog.tomiarb.com/sitemap.xml
```

`/pagefind/` is your client-side search index — machine-readable data a crawler
gains nothing from.

### 1.3 Two conflicting `rel=canonical` tags on every page

This was the worst technical bug. Every page carried **two** canonical tags:

```html
<link rel="canonical" href="./classes.html"/>              <!-- theme -->
<link rel="canonical" href="https://codelog.tomiarb.com/classes.html"/>  <!-- plugin -->
```

A canonical tag names the one true URL for a piece of content, so Google knows
`/classes.html` and `/classes.html?utm_source=x` are the same page and pools
their ranking signals. **Two conflicting canonicals make Google discard both**
and guess instead.

The first one was also *relative*, which is worse than it looks — a relative
canonical resolves against whatever URL the crawler arrived on, so it can never
name a single authoritative URL.

Root cause: `RELATIVE_URLS = True` in `publishconf.py`. That setting rewrites
`SITEURL` to `.` inside templates, so the theme's `{{ SITEURL }}/{{ article.url }}`
collapsed to `./classes.html`. Meanwhile the `pelican-seo` plugin independently
injected its own absolute one.

**Fixed:** `RELATIVE_URLS = False` for published builds, and the duplicate
source removed (§1.4). Every page now has exactly one absolute canonical.

### 1.4 Open Graph and metadata were wrong or missing

The `pelican-seo` enhancer was producing:

- `<meta property="og:locale" content="C">` — "C" is not a locale. It leaked
  from `LOCALE = "C"`, a *date-formatting* setting, into a *language* tag.
- `og:title` with **no `og:description` and no `og:image`** — so every link
  shared to LinkedIn, X, Slack or WhatsApp rendered as a bare grey box.
- The duplicate canonical from §1.3.
- Article JSON-LD with no `dateModified`, no description and no image.

**Fixed:** `SEO_ENHANCER = False`, and the theme now emits all of it correctly,
once, in `themes/codelog/templates/base.html`:

- one canonical, one description, correct `og:locale` (`en_US`)
- full Open Graph: type, title, description, url, image (+ dimensions and alt)
- Twitter cards upgraded to `summary_large_image`
- `article:published_time` / `article:modified_time` / tags on posts
- `max-snippet:-1, max-image-preview:large` so Google may show full snippets
  and large image previews rather than truncating them
- valid `BlogPosting` + `BreadcrumbList` JSON-LD, now including `dateModified`

`SEO_REPORT` stays on — the audit is useful, it was only the HTML injection
that was harmful. See §6 for how to read that report correctly.

A default share image was generated at `content/images/og-default.png`
(1200×630, the size every platform crops cleanly).

### 1.5 Every meta description was a single word

Every post had `Summary: <its own title>`, so the description Google shows
under your result was literally `Classes`, `Scope`, `Obj`.

The meta description does **not** affect ranking. It affects **click-through
rate** — and once you rank, CTR is what turns a position into a visitor.
A one-word description wastes the entire pitch.

**Fixed:** all 11 rewritten as real 125–145 character descriptions.

### 1.6 One-word titles targeting unwinnable queries

The title tag is the single strongest on-page ranking signal. Yours were
`Classes`, `List`, `Obj`, `Scope` — aimed squarely at head terms no small site
can win, and giving Google almost nothing to match a real question against.

**Fixed:** rewritten to target long-tail queries, all under 60 characters so
Google does not truncate them:

| Before | After |
|---|---|
| Classes | Python `__init__` Is an Initializer, Not a Constructor |
| Basic Functions | Python Default Arguments and the Mutable Default Trap |
| Obj | Python Assignment Binds Names, It Never Copies Objects |
| Scope | Python Scope: LEGB, Namespaces and Closures |
| Protocol | Python Protocols vs ABCs: Structural Typing Explained |
| Iterables | Python Iterables: Comprehensions, Iterators, Generators |
| Callable Objects | Callable Objects in Python: `__call__`, Lambdas and `*args` |
| Packages | Python Packages: Absolute vs Relative Imports |
| Exception | Python Exceptions: try, except, else, finally and raise |
| Strings | Python Strings: Raw Strings, f-strings and Unicode |
| List | Python Lists: In-Place Sorting and Shallow Copies |

Each one describes a *claim* or a *question*, not a topic. `Classes` matches
nothing anyone types; `is __init__ a constructor` is a real query.

### 1.7 Placeholder tags in production

`basic functions.ipynb` had `Tags: tag1,tag2`. This generated real, crawlable
`/tag/tag1.html` pages and broke the theme's shared-tag related-posts logic for
that post. Replaced with real tags.

### 1.8 Multiple `<h1>` elements per page

`scope.html` had 2, `iterables.html` had 3. The theme renders the post title as
`<h1>`, and body headings written as `#` in the notebooks produced more.

A page should state one subject. Multiple H1s are not a penalty, but they leave
the document with no single stated subject and a heading outline that jumps
from title to title.

**Fixed** in `build_content.py` via `demote_body_h1()`: body `#` headings become
`##` at build time, skipping fenced code blocks so a Python comment is never
mistaken for a heading. Only level 1 moves — that is what makes it correct here,
since the notebooks mix `#` and `##` for headings that are siblings, and
demoting just the H1s lines them up. Every page now has exactly one H1 and a
clean h1 → h2 → h3 outline.

---

## 2. Files changed

| File | Change |
|---|---|
| `plugins/seo_files.py` | **New.** Generates `sitemap.xml` and `robots.txt`. |
| `pelicanconf.py` | Registers the plugin; `SEO_ENHANCER = False`; adds `OG_DEFAULT_IMAGE`, `OG_LOCALE`. |
| `publishconf.py` | `RELATIVE_URLS = False`. |
| `themes/codelog/templates/base.html` | Full, correct head metadata block. |
| `themes/codelog/templates/article.html` | OG article tags + `BlogPosting`/`BreadcrumbList` JSON-LD. |
| `themes/codelog/templates/page.html` | Social title. |
| `themes/codelog/templates/index.html` | Self-referencing canonical + `noindex` on paginated pages. |
| `build_content.py` | `demote_body_h1()`. |
| `notebooks/*.ipynb` | Titles, summaries and tags rewritten (11 files). |
| `content/images/og-default.png` | **New.** 1200×630 share image. |

> **Note on where content lives:** `content/*.md` is *generated* by
> `build_content.py` and is gitignored. The source of truth is the leading
> *Raw NBConvert* cell in each `notebooks/*.ipynb`. Editing `content/` directly
> looks like it works locally and is then silently overwritten by CI.

### On paginated pages

`index.html` previously let page 2 canonicalise to page 1, which tells Google
the deeper pages are duplicates and can cost the posts only reachable from them
their discovery path. Page 2+ now carries a self-referencing canonical plus
`noindex, follow` — *crawl these for links, do not index them as results*. The
posts themselves are what should rank, and they are all in the sitemap anyway.

---

## 3. What only you can do — do these now

Nothing above matters until Google is told. In rough priority order:

**1. Google Search Console** — <https://search.google.com/search-console>

Your verification meta tag is already in the HTML
(`GOOGLE_SITE_VERIFICATION` in `pelicanconf.py`), so the property may already
be verified. Then:

- **Sitemaps → submit** `sitemap.xml`. This is the single highest-value action
  on this list.
- **URL Inspection** → paste a post URL → *Request Indexing*. Do this for your
  three strongest posts. It is the fastest path from "published" to "indexed".
- Check **Pages** for anything reported as *Discovered – currently not indexed*.

GSC is also where you find out which queries you *already* nearly rank for —
see §5.

**2. Bing Webmaster Tools** — <https://www.bing.com/webmasters>. It imports
directly from Search Console, so it costs about two minutes. Bing also feeds
DuckDuckGo and ChatGPT search.

**3. Get the first few real links.** Links remain the strongest off-page
signal, and you currently have close to none. Legitimate options for a
technical blog: answer a Stack Overflow question in your area and link the post
where it genuinely adds depth; post to r/Python or Lobsters when a post is
substantial enough to stand on its own; add the blog to your GitHub profile
README. Do not buy links — it is the one thing that can actually get you
penalised.

**4. Decide about the Cloudflare AI-crawler block.** Your live `robots.txt` is
served through Cloudflare's *managed* robots.txt, which prepends a block that
disallows `GPTBot`, `ClaudeBot`, `CCBot`, `Google-Extended`, `Bytespider` and
others, and sets `Content-Signal: ai-train=no`. Your own rules are appended
after it, so the `Sitemap:` line still works.

Two things worth knowing:

- **This does not affect your Google Search ranking.** `Google-Extended`
  controls Gemini training and grounding only; regular Googlebot is untouched.
- It **does** remove you from AI assistants that cite sources. If you want
  visibility in ChatGPT/Perplexity answers, relax it in the Cloudflare
  dashboard (*AI Crawl Control* / *Manage robots.txt*). Blocking training while
  allowing citation-bearing crawlers is a reasonable middle position.

Your call — just make it deliberately rather than by default.

---

## 4. Remaining issues, in priority order

**1. `list.html` is 60 words.** This is the weakest page on the site by a wide
margin. Thin pages rarely rank and, in volume, drag down how Google assesses
site quality. Either expand it to 600+ words (slicing, negative indices,
`sort(key=...)`, `deepcopy`, list vs tuple vs deque) or fold it into another
post. Expanding is the better trade — the topic has real search volume.

**2. No in-body contextual links.** The theme gives every post related-post and
prev/next links (12 internal links per page — the crawl-path problem is
solved), but there are no links *inside* the prose, which carry more weight
because the surrounding text tells Google what the target is about. High-value
pairs to add, in your own words:

- `classes` → `protocol` (duck typing → structural typing)
- `obj` → `list` (assignment binds names → shallow copies)
- `scope` → `basic-functions` (closures → default argument evaluation)
- `iterables` → `callable-objects` (generators → callables)

I left the prose alone deliberately; the wording should be yours.

**3. Weak slugs.** `/obj.html` and `/list.html` say nothing to a user or a
crawler. `/python-assignment-binds-names.html` would be better. The site is new
enough that changing them costs little — but GitHub Pages has no server-side
redirects, so you would need meta-refresh stubs at the old URLs. Worth doing
only if you do it soon.

**4. No `Description` field.** The theme derives the meta description from
`Summary`, which is also the index-card excerpt. They have different jobs (one
sells the click, one previews the post). Splitting them is a refinement, not a
fix — the current output is correct.

---

## 5. The ongoing playbook

Technical SEO is now done. It is a one-time fix, and it is finished. From here
ranking is entirely a content problem.

### Find queries from your own data

Once Search Console has a few weeks of data, this is the highest-yield loop
there is:

1. **Performance → Queries**, filter to **position 8–25**.
2. Those are queries where Google *already* thinks you are relevant but you sit
   below the fold.
3. For each: either strengthen the existing post to answer it directly, or
   write a dedicated post if the query deserves its own page.

Improving a position 12 to position 5 produces far more traffic than adding a
brand-new post, because the relevance is already established.

### Write for a question, not a topic

Before writing, the post should have one sentence answering: *what would
someone type into Google to want this?* If you cannot answer, the post will not
rank. Then:

- Put that phrasing in the title, the H1 and the first 100 words.
- Answer the question in the opening paragraph. Do not make readers scroll —
  Google increasingly extracts direct answers from the top of a page.
- Use H2s that are themselves questions (`When are default values evaluated?`).
  These are what get pulled into "People also ask".
- 800–2,000 words for a substantive technical post. Length is not itself a
  ranking factor; it is a proxy for actually covering the topic.

### What actually moves the needle, ranked

1. Publishing genuinely useful posts on a consistent cadence
2. Earning links from real sites
3. Targeting queries you can realistically win
4. Improving pages already ranking 8–25
5. Technical SEO ← **you are done here; it is table stakes, not an advantage**

Consistency beats intensity. One good post a fortnight for a year beats twenty
posts this month and nothing after.

### Your natural niche

Your best posts share a shape: *a widely-held belief about Python that is
wrong*. `__init__` is not a constructor; assignment never copies; defaults are
evaluated once at `def` time. That is a genuinely underserved category — most
Python content is beginner tutorials. Lean into it. Post ideas in the same
vein: why `is` is not `==`, why mutable default arguments persist, what `self`
actually is, why `+=` on a list differs from `+`, how the GIL affects (and does
not affect) your code.

---

## 6. How to verify, and reading the SEO report correctly

After any build:

```bash
python build_content.py
pelican content -s publishconf.py

grep -c '<loc>' output/sitemap.xml                    # expect 13
cat output/robots.txt                                 # expect a Sitemap: line
grep -c 'rel="canonical"' output/classes.html         # expect exactly 1
grep -o '<h1' output/classes.html | wc -l             # expect exactly 1
```

External validators, once deployed:

- **Rich Results Test** — <https://search.google.com/test/rich-results>
- **Open Graph preview** — <https://www.opengraph.xyz/>
- **PageSpeed Insights** — <https://pagespeed.web.dev/> (Core Web Vitals are a
  real, if minor, ranking factor)

### The `pelican-seo` report contains false positives

`seo_report.html` will still report three "problems" per post. All three are
artefacts of the plugin inspecting only the *article body* HTML, not the
rendered page:

| Report says | Reality |
|---|---|
| "You need to declare a description" | It checks Pelican's `Description` field; the theme correctly emits `<meta name="description">` from `Summary`. Verified present on every page. |
| "You're missing a content title" | It looks for an `<h1>` inside the body. The theme renders the title as the page `<h1>` — which is correct, and having a second one in the body is exactly the bug fixed in §1.8. |
| "It's better to include internal links" | It counts links in the body only. Each page has 12 internal links from related-posts and prev/next. |

Trust the `grep` checks above and the external validators over that report.

---

## 7. One-paragraph summary

The blog had no sitemap, a broken `robots.txt`, two conflicting canonical tags
on every page, one-word meta descriptions, one-word titles aimed at
unwinnable queries, placeholder tags in production, and up to three H1s per
page. All of that is fixed and verified. What remains is not technical:
submit the sitemap in Search Console, expand the thin `list` post, earn a few
real links, and keep publishing posts that correct a specific widely-held
misconception about Python. Rank on the questions you can win; the broad terms
follow from that, or not at all.
