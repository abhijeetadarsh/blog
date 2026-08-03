AUTHOR = 'Abhijeet Adarsh'
SITENAME = 'CodeLog'
SITESUBTITLE = 'by ' + AUTHOR
SITEDESCRIPTION = 'Notes on Python, systems and the craft of writing software.'
SITEURL = "http://127.0.0.1:8000"

ARTICLE_PATHS = ['']
PAGE_PATHS = ['pages']
PATH = "content"
STATIC_PATHS = ['images']

TIMEZONE = 'Asia/Kolkata'
LOCALE = "C"
DEFAULT_LANG = 'en'
DEFAULT_DATE_FORMAT = '%b %d, %Y'

# --- Theme ---
THEME = 'themes/codelog'
CSS_FILE = 'main.css'
DEFAULT_PAGINATION = 8

# 404 is a direct template so GitHub Pages can serve it for unknown URLs.
DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'authors', 'archives', '404']

# --- Navigation ---
DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = False
MENUITEMS = ()

# --- Plugins ---
PLUGINS = ['seo']

# SEO
SEO_REPORT = True
SEO_ENHANCER = True
SEO_ENHANCER_OPEN_GRAPH = True
SEO_ENHANCER_TWITTER_CARDS = True

# --- Third party ---
GOOGLE_ANALYTICS = 'G-L36LN32S0L'
GOOGLE_SITE_VERIFICATION = 'pN4TAHlYuoz0zqSMEIMxNhzSkiSZHYfUT4JHEg6cW5M'

# --- Advertising -------------------------------------------------------------
# The layout always reserves these slots. Flip ADS_ENABLED on, set AD_CLIENT to
# your AdSense publisher id and fill in the slot ids you want to run; any slot
# left empty keeps showing a quote instead, so the page never has a dead box.
#
#   top         leaderboard under the header, list pages
#   in_feed     between posts on the index, after the third card
#   in_article  moved beside a heading inside a post
#   sidebar     sticky unit in the right rail
#   footer      band above the footer, every page
ADS_ENABLED = False
AD_CLIENT = ''

# Shows the "Premium · ad-free reading" switch in the footer. The reader's
# choice is stored in their browser and applied before first paint: every ad
# slot is removed (not just emptied) and no ad request is made. Set to False to
# drop the control entirely.
PREMIUM_TOGGLE = True
AD_SLOTS = {
    'top': '',
    'in_feed': '',
    'in_article': '',
    'sidebar': '',
    'footer': '',
}

# Shown in any slot that has no ad. (text, attribution) — attribution may be ''.
AD_NOTES = [
    ('Perfection is achieved, not when there is nothing more to add, but when '
     'there is nothing left to take away.', 'Antoine de Saint-Exupéry'),
    ('Programs must be written for people to read, and only incidentally for '
     'machines to execute.', 'Abelson & Sussman'),
    ('Simplicity is prerequisite for reliability.', 'Edsger W. Dijkstra'),
    ('Good design is as little design as possible.', 'Dieter Rams'),
    ('Any fool can write code that a computer can understand. Good programmers '
     'write code that humans can understand.', 'Martin Fowler'),
    ('Premature optimization is the root of all evil.', 'Donald Knuth'),
    ('Talk is cheap. Show me the code.', 'Linus Torvalds'),
    ('There are only two hard things in computer science: cache invalidation '
     'and naming things.', 'Phil Karlton'),
    ('Design is not just what it looks like and feels like. Design is how it '
     'works.', 'Steve Jobs'),
    ('Content precedes design. Design in the absence of content is not design, '
     'it is decoration.', 'Jeffrey Zeldman'),
    ('The best writing is rewriting.', 'E. B. White'),
    ('Write the post you went looking for and could not find.', ''),
    ('If it was hard to debug, it is worth a paragraph.', ''),
    ('Ship the rough draft. Polish it in public.', ''),
]

# --- Author card / newsletter ---
AUTHOR_BIO = 'Engineer. Writes about Python internals, systems and the parts of the craft that are hard to google.'
# Point NEWSLETTER_ACTION at a provider form URL to switch the subscribe block on.
NEWSLETTER_ACTION = ''
NEWSLETTER_TITLE = 'Get new posts by email'
NEWSLETTER_BLURB = 'No noise, no schedule — just the next post when it is ready.'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# --- Social ---
SOCIAL = (
    ('GitHub', 'https://github.com/abhijeetadarsh'),
    ('LinkedIn', 'https://linkedin.com/in/abhijeet-adarsh'),
    ('X', 'https://x.com/adarsh_abhijeet'),
)
GITHUB_URL = 'https://github.com/abhijeetadarsh/blog'
TWITTER_USERNAME = 'adarsh_abhijeet'
