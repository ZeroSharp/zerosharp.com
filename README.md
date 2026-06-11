# zerosharp.com

Source for **www.zerosharp.com**, **blog.zerosharp.com**, and **about.zerosharp.com** — built with [Hugo](https://gohugo.io/) and (eventually) deployed to Cloudflare Pages.

## Local development

From the repo root:

```powershell
hugo server
```

Then open http://localhost:1313/. Hugo rebuilds on file change with livereload.

Hugo extended v0.161+ is required (needed for the SCSS pipeline). Install via your package manager: `choco install hugo-extended` (Windows), `brew install hugo` (macOS), or [download a release binary](https://github.com/gohugoio/hugo/releases).

To produce a static build into `public/` without serving:

```powershell
hugo
```

## Repo layout

```
zerosharp/
├── hugo.toml                 # site config: baseURL, brand params, taxonomies, Chroma
├── archetypes/default.md     # template used by `hugo new …`
├── assets/
│   └── scss/                 # compiled by Hugo Pipes — main.scss is the entry
│       ├── _tokens.scss      # CSS variables for palette, type, spacing
│       ├── _base.scss        # reset, body, generic .zs-* helpers
│       ├── _site.scss        # yellow header, paper-wrap, footer, landing hero
│       ├── _post.scss        # eyebrow, title, meta, byline, post-nav, comments
│       ├── _syntax.scss      # dark Solarized code frame + token colours
│       ├── _responsive.scss  # ≤768px breakpoint
│       └── main.scss
├── content/
│   ├── _index.md             # /  (landing — actual hero is in layouts/index.html)
│   ├── about/_index.md       # /about/  (bio with floating photo)
│   └── blog/                 # /blog/  +  /<slug>/  (individual posts)
│       ├── _index.md
│       └── *.md              # one file per post (slug = filename)
├── layouts/
│   ├── index.html            # standalone landing page (does NOT use baseof)
│   ├── _default/
│   │   ├── baseof.html       # html/head/header/main/footer wrapper
│   │   ├── single.html       # post / page renderer
│   │   └── list.html         # generic section list (taxonomies)
│   ├── blog/list.html        # /blog/ — title + blurb + paginated post list
│   ├── partials/             # site-header, site-footer, post-meta, byline,
│   │                         # post-nav, comments-disqus
│   └── shortcodes/           # pullquote, gist, highlight (Octopress-era inline)
├── static/
│   ├── fonts/                # VAG Rounded Std Bold / Light / Thin .otf
│   ├── images/               # ~190 images carried over from Octopress
│   └── favicon.svg
└── scripts/
    └── port-octopress-posts.py  # one-shot Octopress → Hugo migration helper
```

## Permalinks

The blog section uses `/<slug>/` (NOT `/blog/<slug>/`) so existing
`blog.zerosharp.com/<slug>/` URLs continue to resolve. This is set in `hugo.toml`:

```toml
[permalinks]
  blog = "/:slug/"
```

When writing a new post, set `slug = "..."` in the front-matter and Hugo will emit it at `/<slug>/`.

## Adding a new post

```powershell
hugo new content blog/my-new-post.md
# then edit content/blog/my-new-post.md
```

The archetype gives you `draft = true`. To preview drafts in the local server use `hugo server -D`. Drop `draft` (or set to `false`) when ready to publish.

## Hosting

Not yet deployed. Plan: connect this repo to Cloudflare Pages with build command `hugo` and output `public/`. Custom domains:

- `zerosharp.com` (apex) and `www.zerosharp.com` → both serve the landing page
- `blog.zerosharp.com` → also serves the same site, where `/<slug>/` paths give the post pages

The same `public/` build is served at all hostnames; URL paths handle the routing.

## Notes on conventions

- **Line endings.** Repo is currently writing with whatever `core.autocrlf` is set to in your global git config. If you start seeing 200+ "modified" files showing as line-ending churn (CRLF↔LF), add a `.gitattributes` with `* text=auto eol=lf` and re-normalize.
- **Disqus identifiers.** Each ported post sets `disqus_identifier` and `disqus_url` in front-matter to the original `http://ZeroSharp.github.com/<slug>/` so historical comment threads stay attached. Don't drop those.
- **Images.** Octopress's `{% img right /p alt %}` floated images right with text wrapping. The migration script preserves this by emitting `<img class="img-{right,left,center}">` HTML; the SCSS in `_post.scss` does the float + responsive collapse on small screens.
- **Code blocks.** Fenced blocks (\`\`\`csharp) get the dark Solarized frame with traffic-light header via Chroma. 4-space-indented blocks fall back to a plainer dark frame (no traffic lights, no syntax highlighting) — see `_post.scss` `.entry-content pre`.

See [DECISIONS.md](DECISIONS.md) for the architectural rationale and [CHANGELOG.md](CHANGELOG.md) for what's been done and what's pending.
