#!/usr/bin/env python3
"""
Custom Pagefind indexing script that only indexes individual article pages,
excluding category pages, tag pages, author pages, and the home page.
"""

import asyncio
import logging
import re
from pathlib import Path
from pagefind.index import PagefindIndex, IndexConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def main():
    """Build search index with only article pages."""
    
    # Configuration for Pagefind
    config = IndexConfig(
        root_selector="main",  # The theme wraps every page body in <main>
        # Chrome, sponsored slots and end-of-post modules carry
        # data-pagefind-ignore in the theme so they stay out of the index.
        exclude_selectors=["nav", "aside", "[data-pagefind-ignore]"],
        force_language="en",
        verbose=True,
        logfile="pagefind_index.log",
        output_path="./output/pagefind",
    )
    
    async with PagefindIndex(config=config) as index:
        log.info("Starting Pagefind indexing...")
        
        # Get all HTML files in the output directory
        output_dir = Path("./output")
        html_files = list(output_dir.glob("*.html"))
        
        # Filter to only include article pages (exclude category, tag, author, archive pages)
        article_files = []
        excluded_patterns = [
            "archives.html", "authors.html", "categories.html", "tags.html",  # Archive pages
            "404.html",
        ]
        
        for html_file in html_files:
            filename = html_file.name
            
            # Skip excluded files, plus every page of the paginated home feed
            # (index.html, index2.html, index3.html …)
            if filename in excluded_patterns or re.fullmatch(r"index\d*\.html", filename):
                log.info(f"Excluding: {filename}")
                continue
                
            # Skip if it's in a subdirectory (category/, tag/, author/)
            if html_file.parent != output_dir:
                log.info(f"Excluding subdirectory file: {html_file}")
                continue
                
            # This should be an article page
            article_files.append(html_file)
            log.info(f"Including article: {filename}")
        
        # Index each article file
        indexed_count = 0
        for article_file in article_files:
            try:
                with open(article_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add the file to the index
                result = await index.add_html_file(
                    content=content,
                    url=f"/{article_file.name}",
                )
                
                indexed_count += 1
                log.info(f"Indexed: {article_file.name} ({result.get('page_word_count', 0)} words)")
                
            except Exception as e:
                log.error(f"Failed to index {article_file}: {e}")
        
        log.info(f"Indexing complete! Indexed {indexed_count} article pages.")
        
        # Get final statistics
        files = await index.get_files()
        log.info(f"Total files in index: {len(files)}")

if __name__ == "__main__":
    asyncio.run(main())
