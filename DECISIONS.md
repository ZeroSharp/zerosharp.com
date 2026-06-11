# Migration decisions

This document captures *why* the site was migrated from Octopress to Hugo, what was chosen instead, and what was deliberately left behind. The matching task list / status is in [CHANGELOG.md](CHANGELOG.md).

## Starting point

Three artifacts:

1. **Landing page** — hand-written static HTML/CSS in a Mercurial repo, hosted on Amazon S3 as `www.zerosharp.com`.
2. **Blog** — Octopress (Jekyll 0.11, 2012-vintage), hosted on GitHub Pages as `blog.zerosharp.com`. ~95 posts, last touched in 2018.
3. **Claude Design mockup** — defines the visual target with a clean modern HTML class structure (`zs-site-header`, `post-eyebrow`, `cat-chip`, `byline-avatar`, etc.) that does *not* match Octopress's legacy `hentry`/`entry-title` markup.

## Decision 1 — Migrate off Octopress

Why:

- Octopress's Ruby toolchain is brittle. Getting the existing repo to build on a clean Windows + Ruby 2.7 install required ~2 hours of work: MSYS2, MinGW toolchain, custom CFLAGS, and bumping three gems (`rdiscount` 1.6 → 2.2, `pygments.rb` 0.2 → 2.4, pinning `ffi` to 1.15.5 to escape the abandoned `rubypython` dependency chain). Every future dependency upgrade re-opens that hole.
- The Claude Design mockup uses an entirely new class structure. Retrofitting it onto Jekyll 0.11's templates means rewriting most includes anyway — at which point the "fix Octopress" path is roughly the same effort as "leave Octopress" but produces a worse outcome (still on Jekyll 0.11).
- Low blogging cadence (≤1 post/month). Build-friction tax compounds for years.

## Decision 2 — Pick Hugo over Astro / 11ty / modern Jekyll

Why Hugo specifically:

- Single 30 MB Go binary. **Zero runtime dependencies** — no Ruby, no Node, no npm, no MSYS2.
- Builds 280+ pages (95 posts × posts + categories + paginators) in ~130 ms.
- Mockup HTML translates almost 1:1 to Hugo Go-templates.
- Active project (versions out monthly).
- Built-in SCSS pipeline (Hugo Pipes) — no separate Sass install.
- Built-in syntax highlighter (Chroma) is **Pygments-class-name compatible** — the existing Solarized SCSS for `.k`, `.s`, `.nc`, `.kt` etc. survives the migration unchanged.

Alternatives considered and why they lost:

- **Astro / 11ty** — pull in Node.js + npm for no benefit on a text-first blog.
- **Modern Jekyll 4** — keeps Ruby. Just spent 2 h on Ruby. No.
- **Stay on Octopress and finish the SCSS redesign** — cosmetic-only fix; the toolchain is still 2012-vintage and gets worse over time.
- **Hand-coded HTML** — fine for a 1-page landing, becomes tedious as soon as you need a blog index, RSS, tag pages, pagination.

## Decision 3 — Single Git repo containing landing + blog + about

Why:

- Two repos = two deploy stories = two sources of drift. For one post a month, the overhead is disproportionate.
- The landing page repo is currently in **Mercurial** with no remote. Modern deploy hosts (Cloudflare Pages, Netlify, GitHub Pages) all auto-deploy from `git push`. We were going to migrate to Git anyway.

GitHub home: [`ZeroSharp/zerosharp.com`](https://github.com/ZeroSharp/zerosharp.com). The original `ZeroSharp/zerosharp.github.com` will be left as a frozen historical archive.

## Decision 4 — Cloudflare Pages over GitHub Pages / Netlify / S3

Why:

- Free, fast edge network, auto-deploy on `git push`.
- Native `_redirects` support — useful if we later decide to move blog URLs.
- No per-build CI minutes to manage.
- Can serve **multiple custom domains pointing at the same `public/` build** — important for our hostname plan (see Decision 5).

GitHub Pages is also free but has slower edges and no native redirects. Netlify is roughly equivalent to Cloudflare but marginally slower historically.

## Decision 5 — Preserve `blog.zerosharp.com` URLs

Existing post URLs are `blog.zerosharp.com/<slug>/`. Decision: keep them as-is rather than moving to `www.zerosharp.com/blog/<slug>/`.

Why:

- No 301 redirects needed. No SEO loss. External links keep working.
- Disqus threads are keyed by `disqus_identifier`; preserving URLs preserves comments.

How: Hugo emits posts at `/<slug>/` (not `/blog/<slug>/`) thanks to a `[permalinks] blog = "/:slug/"` rule in `hugo.toml`. Cloudflare Pages serves the same `public/` build at multiple custom domains; the path `/<slug>/` resolves at both `www.zerosharp.com` and `blog.zerosharp.com`. The blog index lives at `/blog/`.

## Decision 6 — Disqus stays

Disqus is the existing comment system. Switching (e.g. to utterances/giscus) is a separate decision and would lose existing threads. Out of scope for this migration.

We do explicitly set `disqus_identifier = "http://ZeroSharp.github.com/<slug>/"` and `disqus_url` to the same value on every ported post, because that's the identifier the original Octopress site computed (from `site.url + page.url`) and which existing comment threads are keyed by. Hugo's Disqus partial uses these in preference to Hugo's auto-computed URL.

## Decision 7 — Themeless

We did not pick a Hugo theme. Layouts are hand-authored from the Claude Design mockup. Reasons:

- The mockup is a small, opinionated design — fighting a theme to match it is more work than writing it from scratch.
- One less moving part / dependency / breaking change to track.

Total custom layout code: 8 templates + 6 SCSS partials. Maintainable.

## Decision 8 — `/` is the landing hero; `/blog/` is the post-listing blurb

Initially `/` was the post-listing-with-blurb, but the user clarified they want the existing `Website/index.html` hero (giant "0#" mark on full-bleed yellow) to stay at `/`. The post-listing blurb moved to `/blog/` (so anyone who already had `blog.zerosharp.com/` bookmarked sees the blurb-style page, not just a "Blog" header).

## Decision 9 — Octopress shortcodes rewritten in the migration script, not at runtime

The migration script (`scripts/port-octopress-posts.py`) statically rewrites Octopress Liquid shortcodes (`{% codeblock %}`, `{% img %}`, `{% blockquote %}`, `{% pullquote %}`, `{% youtube %}`, `{% gist %}`, `{% imgcap %}`, `{% raw %}`, `{% highlight %}`) into Hugo equivalents (fenced code, raw HTML img tag, `>` markdown quote, Hugo `{{< youtube >}}` / `{{< gist >}}` / `{{< pullquote >}}` / `{{< highlight >}}` shortcodes) at port time.

Alternative was to write a Hugo shortcode for each Octopress tag and process them at render time. Rejected because:

- Adds runtime complexity for a one-time port.
- Octopress's `{% codeblock %}` and `{% img %}` are the bulk of the volume and translate cleanly to standard Markdown — no shortcode needed at all.
- Only 3 Octopress tags don't have a clean Markdown equivalent (`pullquote`, `gist`, `highlight`); those keep dedicated Hugo shortcodes.

## Decision 10 — Hand-authored migration script, not a rewrite engine

The script in `scripts/` is straightforward: one regex per shortcode, one Python file, ~250 lines. Could a more "principled" port use a Liquid AST library or a Hugo content adapter? Yes. But:

- It's a one-shot batch. The output is what's checked in.
- 95 files. Failures are easy to spot.
- We're not married to any particular import path going forward.

The script lives in the repo so we have a written record of the rewrites; there's no expectation that we'll run it again.

## Out of scope

- Switching the comment system away from Disqus.
- Site search.
- Drafts/scheduled-publish workflow beyond what Hugo gives by default.
- Migrating the Octopress `zerosharp.github.com` repo's commit history into the new repo. The historical posts are content-ported; the git history is not preserved (it stays at the original repo as an archive).
- Migrating the Mercurial history of the old landing-page repo into git. Optional later step using `hg-fast-export`; not gating.
