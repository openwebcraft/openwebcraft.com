# Migration Plan: openwebcraft.com from Kirby/BSD to Blot.im

## Context

openwebcraft.com currently runs on Kirby CMS (PHP) on OpenBSD. The goal is to migrate to Blot.im (a Dropbox-synced blogging platform) with a fresh start: **all** existing content (Kirby posts, Kirby pages, old 2013-2015 Blot posts, and legacy Hugo notes) goes into a `/archive/` section. Redirects ensure old URLs keep working.

## Content Inventory

| Source | Count | Format | Current URLs |
|--------|-------|--------|-------------|
| Kirby blog posts | 36 | `.txt` (Kirby markup) | `/post-slug` |
| Kirby pages (about, now, impressum, privacy) | 4 | `.txt` (Kirby markup) | `/about`, `/now`, etc. |
| Existing Blot posts (2013-2015) | 41 | `.md` (Markdown) | `/post-slug` |
| Hugo legacy notes | 4 | `.html` (static) | `/notes/slug` |
| Existing Blot Pages/About.md | 1 | `.md` | `/about` |

## Target Structure

```
Dropbox/Apps/Blot/
├── Pages/                          # Live pages (not archived)
│   ├── About.md                    # From Kirby about (replaces existing)
│   ├── Now.md                      # From Kirby now
│   ├── Impressum.md                # From Kirby impressum
│   └── Privacy.md                  # From Kirby privacy
├── archive/                        # ALL legacy content
│   ├── 2013/                       # Moved from Blot root
│   │   └── *.md
│   ├── 2014/                       # Moved from Blot root
│   │   └── *.md
│   ├── 2015/                       # Moved from Blot root
│   │   └── *.md
│   ├── notes/                      # Hugo legacy notes
│   │   └── *.html
│   ├── semantic-web-schnell-kompakt.md    # Kirby posts
│   ├── my-regolith-linux-setup.md
│   └── ... (36 converted posts)
├── public/
│   ├── uploads/                    # Existing Blot images (keep)
│   └── archive-images/             # Kirby post images
│       ├── post-slug/
│       │   └── image.jpg
│       └── about/
│           └── photo.jpg
└── (fresh content goes here)
```

**URL mapping:**
- Kirby posts: `/post-slug` -> `/archive/post-slug`
- Kirby pages: stay at `/about`, `/now`, `/impressum`, `/privacy` (live Pages)
- Old Blot posts: their existing URLs -> `/archive/2013/...`, `/archive/2014/...`, `/archive/2015/...`
- Hugo notes: `/notes/slug` -> `/archive/notes/slug`

## Implementation Steps

### Step 1: Create Python migration script

**File:** `/var/home/matthias/Code/openwebcraft.com/migrate-to-blot.py`

The script does everything in one run with `--dry-run` (default) and `--execute` modes.

**1a. Kirby .txt parser**
- Split on `\n----\n` separators
- Extract fields: `Title`, `Text`, `Published`, `Feedurl`, `Uuid`
- Key files to parse: `content/home/*/post.txt`, `content/*/default.txt`

**1b. Kirby Text -> Markdown converter**

| Kirby Pattern | Markdown Output |
|--------------|-----------------|
| `(link: URL text: Display)` | `[Display](URL)` |
| `(link: URL text: Display rel: me)` | `[Display](URL)` |
| `(link: internal-slug text: Display)` | `[Display](/archive/internal-slug)` |
| `(image: file.jpg)` | `![](/archive-images/POST-SLUG/file.jpg)` |
| `(email: addr text: Display)` | `[Display](mailto:addr)` |

Internal link handling: links to page slugs (about, now, impressum, privacy) resolve to `/slug`; all other relative links resolve to `/archive/slug`.

**1c. Convert 36 Kirby posts -> `archive/*.md`**

Output format (matching existing Blot conventions):
```
Date: YYYY-MM-DD

# Post Title

Converted markdown body...
```

**1d. Copy post images -> `public/archive-images/{slug}/`**
- All non-`.txt` files from each Kirby post directory
- About page images too

**1e. Convert 4 Kirby pages -> `Pages/*.md`**

Output format (matching existing `Pages/About.md`):
```
Title: Page Name
Slug: /slug

----

Converted markdown body...
```

**1f. Copy 4 Hugo notes as-is -> `archive/notes/*.html`**
- HTML files preserve original formatting and syntax highlighting
- Blot natively supports `.html` files

**1g. Move existing Blot 2013-2015 content -> `archive/`**
- Move `2013/`, `2014/`, `2015/` directories into `archive/`
- Move `2026/` image into appropriate location or leave (only contains one image)

**1h. Generate redirect list -> `redirects.txt`**
- All 36 Kirby post redirects: `/old-slug` -> `/archive/old-slug`
- All Hugo notes redirects: `/notes/slug` -> `/archive/notes/slug` (with and without trailing slash)
- All old Blot post redirects (need to extract slugs from 2013-2015 filenames)
- Output as text file for manual entry into Blot dashboard

### Step 2: Dry run and review

- Run script with `--dry-run`
- Review output: file counts, conversion samples, redirect list
- Spot-check complex posts (post 18 MNT Reform, post 22 Trimir, about page)

### Step 3: Execute migration

- Run script with `--execute`
- Verify file counts match expectations

### Step 4: Configure Blot dashboard

- Add all redirects from `redirects.txt` to Blot's redirect settings (supports pattern matching)
- Configure custom domain (ALIAS record for openwebcraft.com -> blot.im)
- If Blot supports regex redirects, use `/notes/(.*)` -> `/archive/notes/$1` for notes

### Step 5: Verify

- Automated: grep converted files for leftover `(link:`, `(image:`, `(email:` tags
- Automated: verify file counts (36 archive posts, 4 pages, 4 notes, ~24 image directories)
- Manual: visit 3-5 archive URLs on live site, check rendering and images
- Manual: test old URLs redirect correctly
- Monitor Blot 404 log for missed redirects over following days

## Key Files

| File | Role |
|------|------|
| `content/home/*/post.txt` | Kirby blog posts to convert |
| `content/{1_about,2_now,3_impressum,4_privacy}/default.txt` | Kirby pages to convert |
| `static/notes/*/index.html` | Hugo legacy notes to copy |
| `Dropbox/Apps/Blot/Pages/About.md` | Existing Blot page format reference |
| `Dropbox/Apps/Blot/2015/2015-02-28-lego-small-mechanical-loom.md` | Existing Blot post format reference |
| `content/home/18_mnt-reform-*/post.txt` | Most complex post (best test case) |
| `content/1_about/default.txt` | Uses all 3 Kirby tag types + internal links |

## Edge Cases

- **Post 22** has a Kirby link wrapping a Markdown image badge -- regex must handle nested content in `text:` field
- **Privacy page** links to `impressum` 3x as internal links -- must resolve to `/impressum` (Page), not `/archive/impressum`
- **Duplicate page**: `5_how-to-mount-ext4...` at top level is same as post 36 -- skip it, redirect covers it
- **Feed links**: `(link: feed.rss ...)` in some posts -- convert to `/feed.rss` (Blot generates feeds automatically)
- **Long slug**: `stressberry-the-argon-poly-...` is 92 chars -- fine for filesystem, just noting
- **2026/ folder** in Blot root contains one image -- clarify purpose; likely leave in place or move to public/uploads
