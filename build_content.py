"""Build Pelican content from multiple source formats.

Every source file under SOURCES is turned into a single Markdown file in
content/, named after its slug. Supported inputs:

  * .ipynb  - Jupyter notebook, metadata in a leading 'Raw NBConvert' cell
  * .md     - Markdown, metadata as Pelican key:value lines or YAML front matter

Adding a format means writing a handler that returns (metadata, body) and
registering it in HANDLERS.
"""

import base64
import re
import shutil
import uuid
from pathlib import Path

import nbformat
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import Preprocessor
from traitlets.config import Config

# --- Configuration ---
OUTPUT_DIR = Path('content')
IMAGE_DIR = OUTPUT_DIR / 'nbimages'

# (source directory, destination directory). Articles land in content/, static
# pages in content/pages/ — which is what PAGE_PATHS points at.
SOURCES = [
    (Path('notebooks'), OUTPUT_DIR),
    (Path('posts'), OUTPUT_DIR),
    (Path('pages'), OUTPUT_DIR / 'pages'),
]

# Articles need a date to be ordered; pages do not.
REQUIRED_ARTICLE_METADATA = ('Title', 'Date')
REQUIRED_PAGE_METADATA = ('Title',)

# Markdown image links that point at a local file (not a URL, not already a
# Pelican {static} link, not site-absolute).
RELATIVE_IMAGE_RE = r"!\[(.*?)\]\((?!https?://|{|/)(.*?)\)"


# --- Shared helpers ---

# Python-Markdown's meta parser only accepts [A-Za-z0-9_-] in a key, so a key
# written with a space silently becomes body text. Normalise on the way in.
KEY_ALIASES = {
    'last modified': 'Modified',
    'last_modified': 'Modified',
    'lastmod': 'Modified',
    'updated': 'Modified',
}


def normalize_key(key):
    key = key.strip()
    return KEY_ALIASES.get(key.lower(), re.sub(r'\s+', '_', key))


def parse_metadata(text):
    """Parse 'Key: value' lines into a dict, stopping at the first blank line."""
    metadata = {}
    for line in text.split('\n'):
        if not line.strip():
            break
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[normalize_key(key)] = value.strip()
    return metadata


def make_slug(metadata):
    """Return the explicit slug, else one derived from the title."""
    slug = metadata.get('Slug') or metadata.get('slug')
    if slug:
        return slug
    title = metadata.get('Title') or metadata.get('title', '')
    return re.sub(r'[^\w-]+', '-', title.lower()).strip('-')


def missing_metadata(metadata, required):
    """Return the required keys absent from metadata (case-insensitive)."""
    present = {key.lower() for key in metadata}
    return [key for key in required if key.lower() not in present]


def copy_relative_images(text, base_dir, slug):
    """Copy locally referenced images into content/ and rewrite their links."""

    def rewrite(match):
        alt_text, relative_path = match.group(1), match.group(2)
        src_path = (base_dir / relative_path).resolve()

        if not src_path.is_file():
            print(f"   [!] Image not found at {src_path}. Skipping.")
            return match.group(0)

        dest_dir = IMAGE_DIR / slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_filename = f"{uuid.uuid4().hex}{src_path.suffix}"
        shutil.copy(src_path, dest_dir / dest_filename)
        print(f"   [OK] Copied relative image: {src_path.name} -> {dest_dir / dest_filename}")

        return f"![{alt_text}]({{static}}/nbimages/{slug}/{dest_filename})"

    return re.sub(RELATIVE_IMAGE_RE, rewrite, text)


# --- Notebook preprocessors ---

class PelicanRelativePathPreprocessor(Preprocessor):
    """Rewrite relative image paths in markdown cells to Pelican static links."""

    def preprocess_cell(self, cell, resources, cell_index):
        if cell.cell_type != 'markdown':
            return cell, resources

        notebook_dir = Path(resources['metadata']['path'])
        slug = resources.get('slug', 'default-slug')
        cell.source = copy_relative_images(cell.source, notebook_dir, slug)
        return cell, resources


class PelicanMarkdownAttachmentsPreprocessor(Preprocessor):
    """Extract images attached to markdown cells, save them, update the link."""

    def preprocess_cell(self, cell, resources, cell_index):
        if cell.cell_type != 'markdown' or not hasattr(cell, 'attachments'):
            return cell, resources

        slug = resources.get('slug', 'default-slug')
        post_image_path = IMAGE_DIR / slug
        post_image_path.mkdir(parents=True, exist_ok=True)

        for filename, attachment in cell.attachments.items():
            for mimetype, b64_data in attachment.items():
                ext = mimetype.split('/')[-1]
                unique_filename = f"{uuid.uuid4().hex}.{ext}"
                output_filepath = post_image_path / unique_filename

                with open(output_filepath, 'wb') as f:
                    f.write(base64.b64decode(b64_data))
                print(f"   [OK] Markdown attachment saved to {output_filepath}")

                pelican_url = f"{{static}}/images/{slug}/{unique_filename}"
                cell.source = cell.source.replace(f"attachment:{filename}", pelican_url)

        return cell, resources


# --- Handlers: source file -> (metadata, markdown body) ---

def handle_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    if not notebook.cells or notebook.cells[0].cell_type != 'raw':
        print(f"   [!] Warning: First cell in {notebook_path.name} is not a 'Raw NBConvert' cell. Skipping.")
        return None

    metadata = parse_metadata(notebook.cells.pop(0).source)
    if missing_metadata(metadata, ('Title',)):
        print(f"   [!] ERROR: Missing Title in {notebook_path.name}. Skipping.")
        return None

    slug = make_slug(metadata)
    metadata['Slug'] = slug

    config = Config()
    # Images produced by code cells (e.g. plots).
    config.ExtractOutputPreprocessor.output_filename_template = (
        f"images/{slug}/{{unique_key}}_{{cell_index}}_{{index}}{{extension}}"
    )
    # Images referenced or embedded by markdown cells.
    config.MarkdownExporter.preprocessors = [
        PelicanRelativePathPreprocessor,
        PelicanMarkdownAttachmentsPreprocessor,
    ]

    resources = {
        'slug': slug,
        'metadata': {'path': str(notebook_path.parent), 'name': notebook_path.name},
    }
    body, resources = MarkdownExporter(config=config).from_notebook_node(notebook, resources)

    for filename, data in resources.get('outputs', {}).items():
        output_path = OUTPUT_DIR / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(data)
        print(f"   [OK] Code output image saved to {output_path}")

    return metadata, body


def split_front_matter(text):
    """Split a markdown source into (metadata dict, body).

    Accepts YAML front matter delimited by '---' as well as Pelican's native
    'Key: value' header block.
    """
    text = text.lstrip('﻿')

    if text.startswith('---'):
        parts = re.split(r'^---\s*$', text, maxsplit=2, flags=re.MULTILINE)
        if len(parts) == 3:
            return parse_yaml_front_matter(parts[1]), parts[2].lstrip('\n')

    header, _, body = text.partition('\n\n')
    if not re.match(r'^[A-Za-z][\w \-]*:', header.split('\n')[0]):
        # No metadata block at all.
        return {}, text
    return parse_metadata(header), body.lstrip('\n')


def parse_yaml_front_matter(text):
    """Parse the flat subset of YAML used in front matter: scalars and lists."""
    metadata = {}
    key = None

    for line in text.split('\n'):
        if not line.strip() or line.lstrip().startswith('#'):
            continue

        # Block list item belonging to the previous key: "  - python"
        item = re.match(r'\s*-\s+(.*)$', line)
        if item and key:
            value = strip_scalar(item.group(1))
            metadata[key] = f"{metadata[key]}, {value}" if metadata[key] else value
            continue

        if ':' not in line:
            continue

        key, value = line.split(':', 1)
        key, value = normalize_key(key), value.strip()

        # Inline list: "[a, b]"
        if value.startswith('[') and value.endswith(']'):
            items = [strip_scalar(i) for i in value[1:-1].split(',') if i.strip()]
            value = ', '.join(items)
        else:
            value = strip_scalar(value)

        metadata[key] = value

    return metadata


def strip_scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def handle_markdown(markdown_path):
    text = markdown_path.read_text(encoding='utf-8')
    metadata, body = split_front_matter(text)

    if missing_metadata(metadata, ('Title',)):
        print(f"   [!] ERROR: Missing Title in {markdown_path.name}. Skipping.")
        return None

    slug = make_slug(metadata)
    metadata['Slug'] = slug

    body = copy_relative_images(body, markdown_path.parent, slug)
    return metadata, body


HANDLERS = {
    '.ipynb': handle_notebook,
    '.md': handle_markdown,
    '.markdown': handle_markdown,
}


# --- Driver ---

def iter_sources():
    """Yield (source file, destination dir) pairs, skipping hidden/underscored ones."""
    for source_dir, dest_dir in SOURCES:
        if not source_dir.is_dir():
            continue
        for path in sorted(source_dir.rglob('*')):
            if path.suffix.lower() not in HANDLERS or not path.is_file():
                continue
            if any(part.startswith(('.', '_')) for part in path.relative_to(source_dir).parts):
                continue
            if '.ipynb_checkpoints' in path.parts:
                continue
            yield path, dest_dir


def demote_body_h1(text):
    """Turn body '# Heading' into '## Heading'.

    The theme already renders the post title as the page's <h1>, so a body
    heading at level 1 produced a second (and in one post, a third) <h1>. That
    leaves a document with no single stated subject and a heading outline that
    skips straight from title to title.

    Only level 1 moves; deeper levels stay put, which is what makes the result
    correct here -- the notebooks mix '# X' and '## Y' for headings that are
    siblings, and demoting just the H1s lines them up. Fenced code blocks are
    skipped so a Python comment is never mistaken for a heading.
    """
    lines = text.split('\n')
    in_fence = False
    for index, line in enumerate(lines):
        if line.lstrip().startswith(('```', '~~~')):
            in_fence = not in_fence
        elif not in_fence and re.match(r'^# \S', line):
            lines[index] = '#' + line
    return '\n'.join(lines)


def build(source_path, dest_dir, seen_slugs):
    print(f"-> Processing: {source_path}")

    result = HANDLERS[source_path.suffix.lower()](source_path)
    if result is None:
        return False
    metadata, body = result
    body = demote_body_h1(body)

    required = REQUIRED_ARTICLE_METADATA if dest_dir == OUTPUT_DIR else REQUIRED_PAGE_METADATA
    absent = missing_metadata(metadata, required)
    if absent:
        print(f"   [!] ERROR: Missing {', '.join(absent)} in {source_path.name}. Skipping.")
        return False

    slug = metadata['Slug']
    key = (dest_dir, slug)
    if key in seen_slugs:
        print(f"   [!] ERROR: Slug '{slug}' already used by {seen_slugs[key]}. Skipping.")
        return False
    seen_slugs[key] = source_path

    header = "\n".join(f"{key}: {value}" for key, value in metadata.items())
    dest_dir.mkdir(parents=True, exist_ok=True)
    output_path = dest_dir / f"{slug}.md"
    output_path.write_text(f"{header}\n\n{body}", encoding='utf-8')

    print(f"   [OK] Markdown file saved to {output_path}\n")
    return True


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Clean up old generated content to avoid orphans.
    for _, dest_dir in SOURCES:
        for md_file in dest_dir.glob('*.md'):
            md_file.unlink()
    print("Cleaned old .md files from content/ directory.")

    if IMAGE_DIR.exists():
        shutil.rmtree(IMAGE_DIR)
        print("Cleaned old image directory.\n")
    IMAGE_DIR.mkdir(exist_ok=True)

    seen_slugs = {}
    built = 0
    for source_path, dest_dir in iter_sources():
        if build(source_path, dest_dir, seen_slugs):
            built += 1

    print(f"✅ Content build complete: {built} post(s) written to {OUTPUT_DIR}/.")


if __name__ == '__main__':
    main()
