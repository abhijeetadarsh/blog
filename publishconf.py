# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = "https://codelog.tomiarb.com"

# Must be False for a published build. With relative URLs Pelican rewrites
# SITEURL to "." inside templates, which turned every canonical tag into
# <link rel="canonical" href="./classes.html"> -- a relative canonical is
# resolved against the current URL, so it self-referenced whatever path the
# crawler arrived on and gave Google no single authoritative URL. Open Graph
# and JSON-LD have the same absolute-URL requirement.
RELATIVE_URLS = False

FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"

DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing

# DISQUS_SITENAME = ""
# GOOGLE_ANALYTICS = ""
