# Working in this repo

This file is auto-loaded by Claude Code when a session starts in this directory. It exists to point a fresh session at the documents that already explain the project, rather than restate them.

## Read these first

- **[README.md](README.md)** — repo layout, local-dev commands, conventions (permalinks, Disqus identifier rule, image-floating, indented code blocks, line endings).
- **[DECISIONS.md](DECISIONS.md)** — why this site exists in the shape it does. 11 decisions covering: migrating off Octopress, picking Hugo, single-repo structure, Cloudflare Pages, URL preservation, Disqus retention, themeless approach, `/about/` vs hidden CV, `/` landing vs `/blog/` listing, port-time vs run-time shortcode rewriting, hand-authored migration script.
- **[CHANGELOG.md](CHANGELOG.md)** — the migration log. The **Pending** section is the to-do list for whoever picks the project up next; that's the most useful section if you're starting work.

## What this project is

`www.zerosharp.com` (landing), `blog.zerosharp.com` (blog), `about.zerosharp.com` (bio) — all served from one Hugo build to multiple custom domains on Cloudflare Pages (Cloudflare cutover not yet done — see CHANGELOG `Pending`).

Migrated from Octopress (Jekyll 0.11, 2012-vintage, brittle Ruby toolchain) in early May 2026. ~95 historical posts ported by `scripts/port-octopress-posts.py`.

## Operational notes

- Hugo binary: `C:\ProgramData\chocolatey\bin\hugo.exe` (Hugo extended ≥0.161, needed for SCSS pipeline).
- Local preview: `hugo server`. Default port 1313. Use `hugo server -D` to also build draft posts.
- The blog post URL pattern is `/<slug>/` (NOT `/blog/<slug>/`) — set in `hugo.toml` `[permalinks]` to preserve existing `blog.zerosharp.com/<slug>/` URLs from the Octopress era. When writing new posts, set `slug = "..."` in front-matter.
- Disqus identifiers are explicitly set in front-matter as `http://ZeroSharp.github.com/<slug>/` (the URL the original Octopress site computed). This is intentional and preserves historical comment threads. Don't drop those fields when writing new posts; the archetype includes them.
- Images for floated layout (Octopress-era `{% img right %}` translation): use `<img class="img-right" src="…" alt="…">` directly in markdown, with a blank line after — Goldmark requires the blank line or it eats the next paragraph as raw HTML.

## Pending session-scoped artefacts

- The original /loop /plan plan file from the migration session lives at `C:\Users\ra\.claude\plans\i-am-trying-to-toasty-cherny.md`. It's superseded by this repo's docs but kept for posterity.
- Memory entries from the migration session are under `C:\Users\ra\.claude\projects\c--Projects-github-octopress\memory\` — that path is hashed from the *Octopress* repo, not this one, so a new session here won't auto-load it. If anything in there is worth carrying forward, copy it to `C:\Users\ra\.claude\projects\c--Projects-github-zerosharp\memory\` (or wherever the new session's hashed projects path lands).

## How to pick up the next task

Open `CHANGELOG.md` and look at the **Pending** list. The first entries are:

1. Push to GitHub (`ZeroSharp/zerosharp.com` — repo doesn't exist on GitHub yet).
2. Cloudflare Pages connection + DNS cutover for the three custom domains.
3. Decide where the rich CV lives (it's intentionally not yet on the new site).
