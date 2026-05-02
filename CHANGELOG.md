# Migration log

What's been done, what's pending, what to pick up next. Chronological. See [DECISIONS.md](DECISIONS.md) for *why*.

## Completed

### Toolchain modernisation (in the old Octopress repo)

Before deciding to migrate, I worked on getting the Octopress repo to build on a modern toolchain. Lives at `C:\Projects\github\octopress`, branch `source`. Two unpushed commits:

- `c779e4cc` Modernize Ruby toolchain to build on Ruby 2.7 — bumped `rdiscount` 1.6 → 2.2, `pygments.rb` 0.2 → 2.4, pinned `ffi 1.15.5`, removed dead `RubyPython.configure` from `plugins/windows.rb`.
- `a5747549` Apply ZeroSharp blog redesign — new SCSS + Liquid templates that *almost* matched the mockup. Reached ~80% visually before the decision was made to stop fighting Octopress and migrate to Hugo.

These commits stay on the old repo as a historical record. Don't push them — `ZeroSharp/zerosharp.github.com` is being abandoned in favour of the new repo.

### Hugo bootstrap (this repo)

- `ee3cac5` Bootstrap Hugo site — `hugo new site --format toml`, hugo.toml configured with brand params, taxonomies, Chroma class-based syntax highlighting, Disqus shortname, `/blog → /:slug/` permalinks.
- `07b0895` Port ZeroSharp design from Claude Design mockup — 8 layout templates, 6 SCSS partials, fonts, favicon. Hand-authored (no theme).
- `60b59d9` Port 95 Octopress posts and supporting shortcodes/styles — ran `scripts/port-octopress-posts.py` against `C:\Projects\github\octopress\source\_posts\`. Output: 95 `content/blog/<slug>.md` files, ~190 images copied to `static/images/`. Custom shortcodes added: `pullquote`, `gist` (Hugo retired its built-in in 0.156), `highlight` (Octopress's fluo-span, not Jekyll syntax-highlighting).
- `fd606d6` Preserve floated image positions from Octopress posts — `{% img right %}` was being lost. Now emitted as `<img class="img-right">` with float CSS.
- `388a314` Force a blank line after floated `<img>` so Goldmark resumes markdown — Goldmark treats `<img>` at line-start as a raw HTML block; without a separator the next paragraph's markdown links rendered as literal text. Affected 18 posts.
- `d9c6454` Handle three more Octopress legacy patterns — `{% highlight %}` shortcode, simplified pullquote (was rendering as a yellow-bordered blockquote; now plain paragraphs), CSS for indented (4-space) code blocks.
- `ca35344` Make `/` the landing hero and `/blog/` the post-listing blurb — split the homepage into a standalone full-bleed hero (port of the existing `Website/index.html`) and a `layouts/blog/list.html` for the post listing.
- (uncommitted, on disk) `/about/` rename — `content/cv/` moved to `content/about/`; nav and post-meta links updated.
- (uncommitted, on disk) Spelling fixes — `indispensible`, `shoudl`, `mascohistic`, `hisotry`, `sucessfully` in two posts.
- (uncommitted, on disk) `_index.md` content edits to the about page (Lisbon/Geneva location, bio rewrite). Edited by the user.
- (uncommitted, on disk) Hidden CV image fix — `content/about/_index.md` had a stray `{% img right ... %}` Liquid shortcode that was rendering as literal text; converted to direct HTML.

### Visual / behavioural verification

Walked through with Playwright MCP at desktop and mobile widths:
- Landing page (`/`): full-bleed yellow with "0#" hero, header nav, footer.
- Blog index (`/blog/`): "ZeroSharp" title + description blurb + paginated post list with category chips.
- About (`/about/`): bio paragraphs with right-floated photo of Robert.
- Sample posts: *Fast Batch Deletions With DevExpress XPO* (the post the mockup was designed against — matches almost pixel-for-pixel), *Skiing on Mars* (image-heavy with multi-image floats), *Two Fields Medallists* (blockquote with attribution), *Has the Riemann Hypothesis Been Proved?* (floated image followed by markdown links — caught the Goldmark issue), *Serverless Framework Part 2* (pullquote, highlight callout, indented code blocks — caught three issues).
- Mobile breakpoint (390 × 844): header stacks, code blocks scroll horizontally inside the dark frame, byline preserved.

## Pending — pick up here

In rough order. None are blocking each other; pick what's most valuable first.

### Push to GitHub

Repo is local-only at `C:\Projects\github\zerosharp`. Branch `main`, ~7 commits. Steps:

1. Create the GitHub repo `ZeroSharp/zerosharp.com` via the github.com web UI (no `gh` CLI installed locally).
2. From this repo:
   ```powershell
   git remote add origin git@github.com:ZeroSharp/zerosharp.com.git
   git push -u origin main
   ```
3. Confirm SSH auth — your existing zerosharp.github.com remote uses SSH so the key is presumed to be set up.

### Cloudflare Pages + DNS cutover

1. Connect repo to Cloudflare Pages. Build command `hugo`, output `public/`, environment variable `HUGO_VERSION=0.161.0` (or whatever current — check with `hugo version`).
2. Add custom domains: `zerosharp.com` (apex), `www.zerosharp.com`, `blog.zerosharp.com`. *Optionally* `cv.zerosharp.com` later.
3. Update DNS at the registrar:
   - Apex: ALIAS / ANAME to the Cloudflare Pages CNAME (or use Cloudflare DNS for free CNAME-flattening).
   - `www`, `blog`: CNAME to the Pages site.
4. Smoke-test each hostname (every page returns 200, fonts load, no mixed-content warnings).
5. Once verified, **leave S3 + GitHub Pages running for ~30 days** as rollback. Then tear them down.

### Decide where the rich CV lives

The full CV from `C:\Projects\ZeroSharp\Website\cv\index.html` is intentionally *not* on the new site yet. The user wants it served at a URL that's not linked from anywhere — given out by hand. Options:

- `/cv-rga/` (random suffix to make it un-guessable)
- `/resume-2026/`
- A hash-named path
- Continue using `cv.zerosharp.com` for it

Once a URL is chosen, port the content into `content/<path>/_index.md` (or `content/<path>.md` for a single page), add a layout if the design needs to differ from `single.html`, and confirm it doesn't appear in any sitemap, RSS, or auto-generated section list. (The default Hugo behaviour will leak it into `sitemap.xml`; we may need a `sitemap_exclude: true` front-matter param + a custom sitemap template.)

### `_redirects` for old sub-paths

`blog.zerosharp.com/blog/categories/<cat>/` was the Octopress URL for category pages. Hugo emits them at `blog.zerosharp.com/blog/categories/<cat>/` too — *should* already work. Spot-check a couple of category URLs from the Wayback Machine and confirm they 200, otherwise add `_redirects` rules.

### Optional: Mercurial → Git for the Website

Use `hg-fast-export` to bring `C:\Projects\ZeroSharp\Website` history into a git repo for archival. Not gating — the Website content is already ported into this repo (landing + about); we just don't have its commit history.

### Optional: Add a `.gitattributes` to lock down line endings

Currently the repo is at the mercy of your global `core.autocrlf`. If you start seeing 200+ files showing as "modified" with `git diff --shortstat` showing balanced inserts/deletes, add:

```
* text=auto eol=lf
```

…and re-normalize with `git add --renormalize .`.

### Optional: Site search

If/when you want it. Hugo can render a JSON index of all pages; pair with a small client-side fuzzy-search (lunr.js, fuse.js, or pagefind). Defer until you actually want it.

### Optional: Switch from Disqus

Disqus has a tracker-heavy reputation. If you decide later to move to giscus / utterances (GitHub-issue-backed) you'd lose the historical threads — that's the trade-off. Existing partial is `layouts/partials/comments-disqus.html`; swap it for a `comments-giscus.html` partial when ready.

## Known minor cosmetic issues

- The Disqus comments box shows "We were unable to load Disqus" at `localhost`. This is expected — Disqus refuses to load on localhost. It will work once the site is on a real domain.
- The `{{< youtube >}}` embeds may fail at localhost due to CSP; should also resolve in production.
- Console shows occasional 404s for tracking-pixel-style URLs from old posts. Not critical, but a `lychee` link-check pass on the rendered `public/` would surface and quantify them.
