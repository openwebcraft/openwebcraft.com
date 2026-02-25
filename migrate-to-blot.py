#!/usr/bin/env python3
"""
Migration script: openwebcraft.com from Kirby CMS to Blot.im

Converts Kirby .txt posts/pages to Blot-compatible Markdown,
copies images, moves legacy Blot content to archive/, and
generates a redirect list.

Posts are organized into archive/YYYY/ folders by publication year.
Each post gets an explicit Link: metadata so Blot uses the correct URL.

Usage:
    python3 migrate-to-blot.py --dry-run   (default, preview only)
    python3 migrate-to-blot.py --execute    (actually write files)
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

# --- Paths ---
KIRBY_ROOT = Path("/var/home/matthias/Code/openwebcraft.com")
KIRBY_POSTS = KIRBY_ROOT / "content" / "home"
KIRBY_PAGES = {
    "about": KIRBY_ROOT / "content" / "1_about",
    "now": KIRBY_ROOT / "content" / "2_now",
    "impressum": KIRBY_ROOT / "content" / "3_impressum",
    "privacy": KIRBY_ROOT / "content" / "4_privacy",
}
HUGO_NOTES = KIRBY_ROOT / "static" / "notes"

BLOT_ROOT = Path("/var/home/matthias/Dropbox/Apps/Blot")
BLOT_ARCHIVE = BLOT_ROOT / "archive"
BLOT_PAGES = BLOT_ROOT / "Pages"
BLOT_PUBLIC = BLOT_ROOT / "public"
BLOT_ARCHIVE_IMAGES = BLOT_PUBLIC / "archive-images"

# Page slugs that should NOT be prefixed with /archive/
PAGE_SLUGS = {"about", "now", "impressum", "privacy", "website-tech"}

# Blot year directories to move into archive
BLOT_YEAR_DIRS = ["2013", "2014", "2015"]


# --- Kirby .txt Parser ---

def parse_kirby_txt(filepath: Path) -> dict:
    """Parse a Kirby .txt file into a dict of field_name -> value."""
    text = filepath.read_text(encoding="utf-8")
    # Split on ---- separator lines
    parts = re.split(r'\n----\n', text)
    fields = {}
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Match field: value (value may be multiline)
        match = re.match(r'^(\w+):\s*(.*)', part, re.DOTALL)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            fields[key] = value
    return fields


# --- Kirby Text -> Markdown Converter ---

def convert_kirby_to_markdown(text: str, post_slug: str) -> str:
    """Convert Kirby markup tags to Markdown."""

    # (image: file.jpg) -> ![](/public/archive-images/POST-SLUG/file.jpg)
    def replace_image(m):
        filename = m.group(1).strip()
        return f"![](/public/archive-images/{post_slug}/{filename})"

    text = re.sub(
        r'\(image:\s*([^)]+)\)',
        replace_image,
        text
    )

    # (email: addr text: Display) -> [Display](mailto:addr)
    def replace_email(m):
        addr = m.group(1).strip()
        display = m.group(2).strip()
        return f"[{display}](mailto:{addr})"

    text = re.sub(
        r'\(email:\s*(.*?)\s+text:\s*(.*?)\)',
        replace_email,
        text
    )

    # (link: ...) tags - handles nested parens (e.g. markdown images in text field)
    # Uses a function to find balanced closing paren instead of regex alone
    def replace_all_links(text):
        result = []
        i = 0
        while i < len(text):
            # Look for (link: at current position
            if text[i:].startswith("(link:"):
                end = find_balanced_close(text, i)
                if end != -1:
                    inner = text[i+1:end]  # strip outer ( and )
                    converted = convert_link_tag(inner)
                    result.append(converted)
                    i = end + 1
                    continue
            result.append(text[i])
            i += 1
        return "".join(result)

    def find_balanced_close(text, start):
        """Find the closing ) that balances the ( at start, handling nesting."""
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '(':
                depth += 1
            elif text[i] == ')':
                depth -= 1
                if depth == 0:
                    return i
        return -1

    def convert_link_tag(inner):
        """Convert 'link: URL text: Display [rel: ...]' to markdown."""
        # Remove 'link: ' prefix
        inner = inner[len("link:"):].strip()
        # Extract rel: if present (remove it)
        inner = re.sub(r'\s+rel:\s*\S+', '', inner)
        # Split on ' text: '
        match = re.match(r'(.*?)\s+text:\s+(.*)', inner, re.DOTALL)
        if match:
            url = match.group(1).strip()
            display = match.group(2).strip()
            url = resolve_link_url(url)
            return f"[{display}]({url})"
        # No text: field, just a URL
        url = inner.strip()
        url = resolve_link_url(url)
        return f"[{url}]({url})"

    text = replace_all_links(text)

    return text


def resolve_link_url(url: str) -> str:
    """Resolve Kirby internal links to proper paths."""
    # Already absolute URL
    if url.startswith(("http://", "https://", "mailto:", "/", "#")):
        return url
    # Special protocol links (appstream://, etc.)
    if "://" in url:
        return url
    # feed.rss -> /feed.rss
    if url == "feed.rss":
        return "/feed.rss"
    # Page slugs stay at root
    if url in PAGE_SLUGS:
        return f"/{url}"
    # Everything else is an archived post -> /archive/slug
    return f"/archive/{url}"


# --- Post Slug Extraction ---

def get_post_slug(dirname: str) -> str:
    """Extract slug from Kirby directory name like '18_mnt-reform-...'"""
    # Remove leading number prefix
    return re.sub(r'^\d+_', '', dirname)


def extract_year(date_str: str) -> str:
    """Extract YYYY from a date string like '2021-05-26'."""
    m = re.match(r'(\d{4})', date_str)
    return m.group(1) if m else "unknown"


# --- Conversion Functions ---

def convert_kirby_posts(dry_run: bool) -> list:
    """Convert all Kirby blog posts to archive/YYYY/slug.md files. Returns redirect pairs."""
    redirects = []
    converted = 0
    skipped = 0

    for post_dir in sorted(KIRBY_POSTS.iterdir()):
        if not post_dir.is_dir():
            continue
        if post_dir.name.startswith("_"):
            skipped += 1
            continue

        post_file = post_dir / "post.txt"
        if not post_file.exists():
            print(f"  SKIP (no post.txt): {post_dir.name}")
            skipped += 1
            continue

        slug = get_post_slug(post_dir.name)
        fields = parse_kirby_txt(post_file)

        title = fields.get("Title", "Untitled")
        body = fields.get("Text", "")
        published = fields.get("Published", "")
        year = extract_year(published) if published else "unknown"

        # Convert Kirby markup to Markdown
        md_body = convert_kirby_to_markdown(body, slug)

        # Build Blot-compatible output with year-based Link
        output_lines = []
        if published:
            output_lines.append(f"Date: {published}")
        output_lines.append(f"Link: /archive/{year}/{slug}")
        output_lines.append("")
        output_lines.append(f"# {title}")
        output_lines.append("")
        output_lines.append(md_body)

        output_content = "\n".join(output_lines) + "\n"
        output_path = BLOT_ARCHIVE / year / f"{slug}.md"

        if dry_run:
            print(f"  WOULD CREATE: archive/{year}/{slug}.md ({len(output_content)} bytes)")
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output_content, encoding="utf-8")
            print(f"  CREATED: archive/{year}/{slug}.md")

        # Copy images
        image_files = [
            f for f in post_dir.iterdir()
            if f.is_file() and not f.name.endswith(".txt")
        ]
        if image_files:
            img_dest = BLOT_ARCHIVE_IMAGES / slug
            for img in image_files:
                if dry_run:
                    print(f"    WOULD COPY image: {img.name} -> public/archive-images/{slug}/")
                else:
                    img_dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img, img_dest / img.name)

        # Redirect: /slug -> /archive/YYYY/slug
        redirects.append((f"/{slug}", f"/archive/{year}/{slug}"))
        converted += 1

    print(f"\n  Posts: {converted} converted, {skipped} skipped")
    return redirects


def convert_kirby_pages(dry_run: bool):
    """Convert Kirby pages to Pages/*.md files."""
    converted = 0

    for page_slug, page_dir in KIRBY_PAGES.items():
        page_file = page_dir / "default.txt"
        if not page_file.exists():
            print(f"  SKIP (no default.txt): {page_dir.name}")
            continue

        fields = parse_kirby_txt(page_file)
        title = fields.get("Title", page_slug.capitalize())
        body = fields.get("Text", "")

        # Convert Kirby markup to Markdown
        # For pages, use the page slug for image references
        md_body = convert_kirby_to_markdown(body, page_slug)

        # Blot Pages format (matching existing Pages/About.md)
        output_lines = [
            f"Title: {title}",
            f"Slug: /{page_slug}",
            "",
            "----",
            "",
            md_body,
        ]

        output_content = "\n".join(output_lines) + "\n"

        # Capitalize first letter for filename
        filename = page_slug.capitalize() + ".md"
        output_path = BLOT_PAGES / filename

        if dry_run:
            print(f"  WOULD CREATE: Pages/{filename} ({len(output_content)} bytes)")
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output_content, encoding="utf-8")
            print(f"  CREATED: Pages/{filename}")

        # Copy page images
        image_files = [
            f for f in page_dir.iterdir()
            if f.is_file() and not f.name.endswith(".txt")
        ]
        if image_files:
            img_dest = BLOT_ARCHIVE_IMAGES / page_slug
            for img in image_files:
                if dry_run:
                    print(f"    WOULD COPY image: {img.name} -> public/archive-images/{page_slug}/")
                else:
                    img_dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img, img_dest / img.name)

        converted += 1

    print(f"\n  Pages: {converted} converted")


def extract_html_date(filepath: Path) -> str:
    """Extract publication date from a Hugo note's HTML metadata."""
    content = filepath.read_text(encoding="utf-8")
    m = re.search(r'datePublished.*?content="(\d{4}-\d{2}-\d{2})', content)
    if m:
        return m.group(1)
    m = re.search(r'<time>(\d{4}-\d{2}-\d{2})', content)
    if m:
        return m.group(1)
    return "unknown"


def html_to_markdown(html: str) -> str:
    """Convert Hugo note HTML body content to Markdown."""
    from html import unescape as html_unescape

    # Extract body content between first <hr> and <article (comments section)
    m = re.search(r'<hr>(.*?)<article\s', html, re.DOTALL)
    if not m:
        m = re.search(r'<hr>(.*?)<hr>\s*<footer', html, re.DOTALL)
    if not m:
        return "<!-- conversion failed -->"
    body = m.group(1).strip()

    # Remove social embed blocks
    body = re.sub(r'<div class="flex items-center.*?</div>', '', body, flags=re.DOTALL)

    # Convert syntax-highlighted code blocks
    def convert_code_block(m):
        lang_m = re.search(r'language-(\w+)', m.group(0))
        lang = lang_m.group(1) if lang_m else ""
        code_m = re.search(r'<code[^>]*>(.*?)</code>', m.group(0), re.DOTALL)
        if not code_m:
            return m.group(0)
        code = re.sub(r'<[^>]+>', '', code_m.group(1))
        code = html_unescape(code).strip('\n')
        return f"\n```{lang}\n{code}\n```\n"

    body = re.sub(r'<div class=highlight><pre[^>]*>.*?</pre></div>', convert_code_block, body, flags=re.DOTALL)

    # Convert plain <pre><code> blocks
    def convert_plain_code(m):
        code = re.sub(r'<[^>]+>', '', m.group(1))
        code = html_unescape(code).strip('\n')
        return f"\n```\n{code}\n```\n"

    body = re.sub(r'<pre><code>(.*?)</code></pre>', convert_plain_code, body, flags=re.DOTALL)

    # Convert inline <code>
    body = re.sub(r'<code>(.*?)</code>', r'`\1`', body)

    # Convert headings
    for i in range(6, 0, -1):
        body = re.sub(
            rf'<h{i}[^>]*>(.*?)</h{i}>',
            lambda m, level=i: f"\n{'#' * level} {re.sub(r'<[^>]+>', '', m.group(1)).strip()}\n",
            body
        )

    # Convert links
    body = re.sub(r'<a[^>]*href="?([^">\s]+)"?[^>]*>(.*?)</a>',
                  lambda m: f'[{re.sub(r"<[^>]+>", "", m.group(2))}]({m.group(1)})', body, flags=re.DOTALL)
    body = re.sub(r'<a\s+href=([^\s>]+)[^>]*>(.*?)</a>',
                  lambda m: f'[{re.sub(r"<[^>]+>", "", m.group(2))}]({m.group(1)})', body, flags=re.DOTALL)

    # Convert lists
    body = re.sub(r'<ul>(.*?)</ul>', lambda m: m.group(1), body, flags=re.DOTALL)
    body = re.sub(r'<li>(.*?)</li>', lambda m: f"- {m.group(1).strip()}\n", body, flags=re.DOTALL)

    # Convert emphasis
    body = re.sub(r'<strong>(.*?)</strong>', r'**\1**', body)
    body = re.sub(r'<em>(.*?)</em>', r'*\1*', body)
    body = re.sub(r'<del>(.*?)</del>', r'~~\1~~', body)

    # Convert paragraphs
    body = re.sub(r'<p>(.*?)</p>', lambda m: f"\n{m.group(1).strip()}\n", body, flags=re.DOTALL)

    # Remove remaining HTML tags, decode entities, clean up whitespace
    body = re.sub(r'<[^>]+>', '', body)
    body = html_unescape(body)
    body = re.sub(r'\n{3,}', '\n\n', body)

    return body.strip()


def convert_hugo_notes(dry_run: bool) -> list:
    """Convert Hugo legacy notes from HTML to Markdown in archive/YYYY/.

    Extracts body content from standalone Hugo HTML pages, converts to
    Markdown with fenced code blocks, and places them alongside other
    archive posts organized by year.
    Returns redirect pairs.
    """
    from html import unescape as html_unescape
    redirects = []
    converted = 0

    for item in sorted(HUGO_NOTES.iterdir()):
        if not item.is_dir():
            continue
        index_html = item / "index.html"
        if not index_html.exists():
            continue

        slug = item.name
        html = index_html.read_text(encoding="utf-8")
        date = extract_html_date(index_html)
        year = date[:4]

        # Extract title from <h1> tag in body
        title_m = re.search(r'<h1>(.*?)</h1>', html)
        title = html_unescape(re.sub(r'<[^>]+>', '', title_m.group(1))) if title_m else slug

        md_body = html_to_markdown(html)

        output = f"Date: {date}\nLink: /archive/{year}/{slug}\n\n# {title}\n\n{md_body}\n"
        dest = BLOT_ARCHIVE / year / f"{slug}.md"

        if dry_run:
            print(f"  WOULD CREATE: archive/{year}/{slug}.md ({len(output)} bytes)")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(output, encoding="utf-8")
            print(f"  CREATED: archive/{year}/{slug}.md")

        redirects.append((f"/notes/{slug}", f"/archive/{year}/{slug}"))
        redirects.append((f"/notes/{slug}/", f"/archive/{year}/{slug}"))
        converted += 1

    print(f"\n  Notes: {converted} converted")
    return redirects


def move_blot_year_dirs(dry_run: bool) -> list:
    """Move existing Blot 2013-2015 directories into archive/.

    Renames date-prefixed filenames (2013-05-02-slug.md) to slug-only (slug.md)
    and adds Link: metadata for proper Blot URL routing.
    Returns redirect pairs.
    """
    redirects = []

    for year in BLOT_YEAR_DIRS:
        src = BLOT_ROOT / year
        dest = BLOT_ARCHIVE / year

        if not src.exists():
            print(f"  SKIP (not found): {year}/")
            continue

        # Collect files for redirect generation
        for f in sorted(src.iterdir()):
            if f.is_file() and f.suffix == ".md":
                # Extract slug from filename like "2013-05-02-ibm-social-business-toolkit-evaluation.md"
                name = f.stem
                match = re.match(r'\d{4}-\d{2}-\d{2}-(.*)', name)
                if match:
                    slug = match.group(1)
                    redirects.append((f"/{slug}", f"/archive/{year}/{slug}"))

        if dry_run:
            file_count = sum(1 for f in src.iterdir() if f.is_file())
            print(f"  WOULD MOVE: {year}/ -> archive/{year}/ ({file_count} files)")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            shutil.rmtree(src)
            print(f"  MOVED: {year}/ -> archive/{year}/")

            # Rename date-prefixed files to slug-only and add Link: metadata
            for md_file in sorted(dest.glob("*.md")):
                content = md_file.read_text(encoding="utf-8")
                name = md_file.stem
                m = re.match(r'\d{4}-\d{2}-\d{2}-(.*)', name)
                if m:
                    slug = m.group(1)
                    # Add Link: metadata after Date: line
                    link_line = f"Link: /archive/{year}/{slug}\n"
                    if content.startswith("Date:"):
                        date_end = content.index('\n')
                        content = content[:date_end+1] + link_line + content[date_end+1:]
                    else:
                        content = link_line + content
                    # Write to slug-only filename and remove original
                    new_path = dest / f"{slug}.md"
                    new_path.write_text(content, encoding="utf-8")
                    md_file.unlink()

    return redirects



def generate_redirects(all_redirects: list, dry_run: bool):
    """Write redirects.txt for Blot bulk editor import.

    Format: '/from /to' (space-separated, one per line, no comments).
    Paste directly into Blot dashboard > Redirects > Bulk editor.

    Uses a single regex redirect to strip trailing slashes instead of
    individual trailing-slash variants. Also adds /notes -> / and
    /feed.json -> /feed.rss.
    """
    output_path = KIRBY_ROOT / "redirects.txt"

    redirects = []

    # Add all individual redirects (no trailing-slash variants needed)
    for src, dest in all_redirects:
        if not src.endswith("/"):
            redirects.append((src, dest))

    # Extra redirects for legacy paths
    redirects.append(("/notes", "/"))
    redirects.append(("/feed.json", "/feed.rss"))

    # Regex to strip trailing slashes — MUST be last to avoid
    # Blot's loop detection (it drops any redirect whose 'to'
    # matches a prior 'from' regex, and /(.*)/  matches multi-segment paths)
    redirects.append(("/(.*)/", "/$1"))

    # Deduplicate
    seen = set()
    unique = []
    for pair in redirects:
        if pair not in seen:
            seen.add(pair)
            unique.append(pair)
    redirects = unique

    # Sort, but keep regex last (must be last to avoid Blot loop detection)
    regex_line = redirects[-1]
    rest = sorted(redirects[:-1])
    redirects = rest + [regex_line]

    lines = []
    for src, dest in redirects:
        lines.append(f"{src} {dest}")

    content = "\n".join(lines) + "\n"

    if dry_run:
        print(f"\n  WOULD CREATE: redirects.txt ({len(redirects)} redirects)")
        print(f"\n--- Redirect Preview (first 20) ---")
        for src, dest in redirects[:20]:
            print(f"  {src} -> {dest}")
        if len(redirects) > 20:
            print(f"  ... and {len(redirects) - 20} more")
    else:
        output_path.write_text(content, encoding="utf-8")
        print(f"\n  CREATED: redirects.txt ({len(redirects)} redirects)")


def verify_conversion(dry_run: bool):
    """Check converted files for leftover Kirby tags."""
    if dry_run:
        print("\n  (Verification skipped in dry-run mode)")
        return

    print("\n  Checking for leftover Kirby tags...")
    issues = 0

    for md_file in BLOT_ARCHIVE.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for pattern_name, pattern in [
            ("(link:", r'\(link:\s'),
            ("(image:", r'\(image:\s'),
            ("(email:", r'\(email:\s'),
        ]:
            matches = re.findall(pattern, content)
            if matches:
                print(f"    WARNING: {md_file.relative_to(BLOT_ROOT)} contains {len(matches)}x {pattern_name}")
                issues += 1

    for md_file in BLOT_PAGES.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for pattern_name, pattern in [
            ("(link:", r'\(link:\s'),
            ("(image:", r'\(image:\s'),
            ("(email:", r'\(email:\s'),
        ]:
            matches = re.findall(pattern, content)
            if matches:
                print(f"    WARNING: {md_file.relative_to(BLOT_ROOT)} contains {len(matches)}x {pattern_name}")
                issues += 1

    if issues == 0:
        print("    No leftover Kirby tags found.")
    else:
        print(f"    {issues} issue(s) found!")


def print_summary(dry_run: bool):
    """Print final file count summary."""
    if dry_run:
        return

    total_posts = 0
    year_dirs = []
    for d in sorted(BLOT_ARCHIVE.iterdir()):
        if d.is_dir() and d.name.isdigit():
            year_dirs.append(d)
            count = sum(1 for f in d.glob("*.md"))
            total_posts += count

    pages = list(BLOT_PAGES.glob("*.md"))
    image_dirs = list(BLOT_ARCHIVE_IMAGES.iterdir()) if BLOT_ARCHIVE_IMAGES.exists() else []

    print(f"\n=== Final File Counts ===")
    print(f"  Archive posts:      {total_posts} (across {len(year_dirs)} year folders)")
    for d in year_dirs:
        count = sum(1 for f in d.glob("*.md"))
        print(f"    {d.name}/: {count} posts")
    print(f"  Pages:              {len(pages)}")
    print(f"  Image directories:  {len(image_dirs)}")


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Migrate openwebcraft.com from Kirby to Blot.im")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", default=True,
                       help="Preview changes without writing (default)")
    group.add_argument("--execute", action="store_true",
                       help="Actually perform the migration")
    args = parser.parse_args()

    dry_run = not args.execute

    mode = "DRY RUN" if dry_run else "EXECUTE"
    print(f"\n{'='*60}")
    print(f"  openwebcraft.com Migration: Kirby -> Blot.im [{mode}]")
    print(f"{'='*60}")

    if not dry_run:
        print("\n  WARNING: This will write files to your Blot Dropbox folder!")
        response = input("  Continue? (yes/no): ")
        if response.lower() != "yes":
            print("  Aborted.")
            sys.exit(0)

    all_redirects = []

    print("\n--- Step 1: Convert Kirby posts -> archive/YYYY/slug.md ---")
    post_redirects = convert_kirby_posts(dry_run)
    all_redirects.extend(post_redirects)

    print("\n--- Step 2: Convert Kirby pages -> Pages/*.md ---")
    convert_kirby_pages(dry_run)

    print("\n--- Step 3: Convert Hugo notes -> archive/YYYY/slug.md ---")
    note_redirects = convert_hugo_notes(dry_run)
    all_redirects.extend(note_redirects)

    print("\n--- Step 4: Move Blot 2013-2015 -> archive/ ---")
    blot_redirects = move_blot_year_dirs(dry_run)
    all_redirects.extend(blot_redirects)

    print("\n--- Step 5: Generate redirects.txt ---")
    generate_redirects(all_redirects, dry_run)

    print("\n--- Step 6: Verify conversion ---")
    verify_conversion(dry_run)

    print_summary(dry_run)

    print(f"\n{'='*60}")
    print(f"  Migration {'preview' if dry_run else 'complete'}!")
    if dry_run:
        print(f"  Run with --execute to perform the migration.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
