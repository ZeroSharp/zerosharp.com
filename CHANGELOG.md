# Migration log

What's been done, what's pending, what to pick up next. Chronological. See [DECISIONS.md](DECISIONS.md) for *why*.

## Current state (2026-07-30)

Site is live on Cloudflare Pages, has been since 2026-06-11.

- **Repo**: [`ZeroSharp/zerosharp.com`](https://github.com/ZeroSharp/zerosharp.com) on GitHub, `main` branch.
- **Hosting**: Cloudflare Pages project `zerosharp-com`. Auto-builds and deploys on every push to `main` (~30 seconds end-to-end).
- **Hostnames**: `zerosharp.com` (apex), `www.zerosharp.com`, `blog.zerosharp.com` — all serving the same site over HTTPS via Cloudflare-managed certs.
- **DNS**: on Cloudflare (nameservers `jewel.ns.cloudflare.com` + `viddy.ns.cloudflare.com`).
- **Analytics**: Cloudflare Web Analytics enabled (privacy-respecting, cookieless).
- **Comments**: Disqus. Historical threads from the Octopress era are preserved because per-post `disqus_identifier` values were carried across in the port.

### To publish a new post

1. Author at `content/blog/<slug>.md`. Set `slug = "..."` in the TOML front-matter so the `/<slug>/` permalink works.
2. Preview with `hugo server` (add `-D` to include drafts).
3. `git add …`, `git commit …`, `git push origin main`.
4. Cloudflare Pages picks up the push, builds, deploys in about 30 s. Watch the deployment in the Cloudflare dashboard → Workers & Pages → `zerosharp-com` → Deployments.

## Completed

### Toolchain modernisation (in the old Octopress repo)

Before deciding to migrate, I worked on getting the Octopress repo to build on a modern toolchain (in a separate local clone, branch `source`). Two unpushed commits:

- `c779e4cc` Modernize Ruby toolchain to build on Ruby 2.7 — bumped `rdiscount` 1.6 → 2.2, `pygments.rb` 0.2 → 2.4, pinned `ffi 1.15.5`, removed dead `RubyPython.configure` from `plugins/windows.rb`.
- `a5747549` Apply ZeroSharp blog redesign — new SCSS + Liquid templates that *almost* matched the mockup. Reached ~80% visually before the decision was made to stop fighting Octopress and migrate to Hugo.

These commits stay on the old repo as a historical record. The old `ZeroSharp/zerosharp.github.com` repo is archived on GitHub.

### Hugo bootstrap (this repo)

- `ee3cac5` Bootstrap Hugo site — `hugo new site --format toml`, hugo.toml configured with brand params, taxonomies, Chroma class-based syntax highlighting, Disqus shortname, `/blog → /:slug/` permalinks.
- `07b0895` Port ZeroSharp design from Claude Design mockup — 8 layout templates, 6 SCSS partials, fonts, favicon. Hand-authored (no theme).
- `60b59d9` Port 95 Octopress posts and supporting shortcodes/styles — ran `scripts/port-octopress-posts.py` against the old Octopress repo's `source/_posts/` directory. Output: 95 `content/blog/<slug>.md` files, ~190 images copied to `static/images/`. Custom shortcodes added: `pullquote`, `gist` (Hugo retired its built-in in 0.156), `highlight` (Octopress's fluo-span, not Jekyll syntax-highlighting).
- `fd606d6` Preserve floated image positions from Octopress posts — `{% img right %}` was being lost. Now emitted as `<img class="img-right">` with float CSS.
- `388a314` Force a blank line after floated `<img>` so Goldmark resumes markdown — Goldmark treats `<img>` at line-start as a raw HTML block; without a separator the next paragraph's markdown links rendered as literal text. Affected 18 posts.
- `d9c6454` Handle three more Octopress legacy patterns — `{% highlight %}` shortcode, simplified pullquote (was rendering as a yellow-bordered blockquote; now plain paragraphs), CSS for indented (4-space) code blocks.
- `ca35344` Make `/` the landing hero and `/blog/` the post-listing blurb — split the homepage into a standalone full-bleed hero and a `layouts/blog/list.html` for the post listing.

### Visual / behavioural verification (pre-cutover)

Walked through with Playwright MCP at desktop and mobile widths:
- Landing page (`/`): full-bleed yellow with "0#" hero, header nav, footer.
- Blog index (`/blog/`): "ZeroSharp" title + description blurb + paginated post list with category chips.
- About (`/about/`): bio paragraphs with right-floated photo of Robert.
- Sample posts: *Fast Batch Deletions With DevExpress XPO*, *Skiing on Mars*, *Two Fields Medallists*, *Has the Riemann Hypothesis Been Proven?*, *Serverless Framework Part 2*.
- Mobile breakpoint (390 × 844): header stacks, code blocks scroll horizontally inside the dark frame, byline preserved.

### Cutover to production (2026-06-11)

- Pushed to `ZeroSharp/zerosharp.com` on github.com.
- Cloudflare Pages project `zerosharp-com` created and connected to the repo.
- DNS zone `zerosharp.com` added to Cloudflare; 13 records imported from Route 53 (MX, TXT, ACM validation CNAMEs, subdomains preserved).
- Registrar nameservers on Route 53 Domains switched to Cloudflare's.
- Custom domains added to the Pages project: apex, `www`, `blog`. All active with Cloudflare-issued certs.
- `static/_redirects` created for `/atom.xml`, `/blog/atom.xml` → `/blog/index.xml` (rescues Octopress-era feed subscribers).
- Disqus trusted domains updated in the Disqus admin.
- Fixed a Disqus embed double-JSON-encoding bug (`{{ jsonify }}` inside a `<script>` where Hugo's html/template already auto-encodes). All posts were shipping malformed disqus_config; the fix restored historical comment thread attachment.
- Disqus template updated to use `.Permalink` for `disqus.url` (so the trusted-domain check sees a live host, not the defunct Octopress URL). `disqus_identifier` stays as the Octopress-era value so historical threads still attach.

### Post-cutover polish (2026-07)

- Added `layouts/404.html` so Pages returns a proper 404 status (previously served landing page with 200 on every unknown path — was leaking duplicates to Google Search Console).
- Resolved three Google Search Console coverage warnings:
  - `/has-the-riemann-hypothesis-been-proved/` — added `aliases = [...]` to the renamed post so the old slug 301s to the new one.
  - `/blog/archives/` — added a 301 to `/blog/` in `static/_redirects`.
  - `/blog/categories/meta/` — added `<link rel="canonical" href="{{ .Permalink }}">` to `layouts/_default/baseof.html` and `layouts/index.html` so all three hostnames consolidate to `www.zerosharp.com` canonicals.
- Deleted three stale AWS Route 53 health checks left over from the S3/CloudFront era; they had been contributing ~1M requests/month of noise to Cloudflare account-level analytics.

### Phase 8 — AWS decommission (2026-07-30)

- S3 bucket `www.zerosharp.com` — emptied (26 objects, including the old landing page and the pre-migration CV files) and deleted.
- CloudFront distribution `EZT2ZRJZUPYCW` (old apex + `www` origin) — disabled and deleted.
- CloudFront distribution `EDNWWFPKYMQCQ` (unused, was an incomplete attempt at HTTPS-fronting `mumbai.zerosharp.com`) — disabled and deleted.
- ACM certs `a1f39849` (expired) and `6abb4370` (`*.zerosharp.com`) — deleted.
- Route 53 hosted zone `zerosharp.com` — 11 records deleted, zone deleted (had been orphaned since the June nameserver switch to Cloudflare).
- `ZeroSharp/zerosharp.github.com` GitHub repo — archived (preserves URL history for any external commit references).
- Only remaining zerosharp AWS resource: empty S3 bucket `zerosharp.com` (eu-west-1) — user to delete manually via the AWS Console.

## Pending — optional, defer until needed

None of these are gating anything. Each is independent.

### Rich CV migration

The full CV lives at `C:\Projects\ZeroSharp\Website\cv\index.html` (local Mercurial repo). Not yet ported to the new site. The intent is to host it at a URL that's not linked from anywhere on the site — shared by hand when relevant. When ready:

- Port into `content/<path>/_index.md` (or `content/<path>.md`).
- Confirm it doesn't appear in `sitemap.xml` (may need `sitemap_exclude: true` front-matter + a custom sitemap template).
- Add DNS record if using a subdomain, or just use a path-based URL.

### Mercurial → Git for the old Website repo

Use `hg-fast-export` to bring the old landing-page Mercurial repo's history into a git repo for archival. Not gating — content is already ported. Only the commit history isn't preserved.

### `.gitattributes` for line endings

Currently the repo is at the mercy of your global `core.autocrlf`. If you start seeing 200+ files showing as "modified" with `git diff --shortstat` showing balanced inserts/deletes, add:

```
* text=auto eol=lf
```

…and re-normalize with `git add --renormalize .`.

### Site search

If/when you want it. Hugo can render a JSON index of all pages; pair with a small client-side fuzzy-search (lunr.js, fuse.js, or pagefind). Defer until you actually want it.

### Switch from Disqus

Disqus has a tracker-heavy reputation. If you decide later to move to giscus / utterances (GitHub-issue-backed) you'd lose the historical threads — that's the trade-off. Existing partial is `layouts/partials/comments-disqus.html`; swap it for a `comments-giscus.html` partial when ready.

### Re-proxy `www` and `blog` on Cloudflare

Currently only the apex is orange-cloud (proxied); `www` and `blog` are gray-cloud (DNS-only). Consequence: zone-level Cloudflare analytics only see apex traffic. This was a workaround from initial Pages custom-domain verification and never got reverted. If you want accurate zone analytics for all three hostnames, flip `www` and `blog` back to proxied — small risk of triggering another Pages verification quirk, easy to revert.

## Known minor cosmetic issues

- The Disqus comments box shows "We were unable to load Disqus" at `localhost`. This is expected — Disqus refuses to load on localhost. Works fine in production.
- The `{{< youtube >}}` embeds may fail at localhost due to CSP; should also resolve in production.
- Console shows occasional 404s for tracking-pixel-style URLs from old posts (Google Analytics beacons, etc). Not critical, but a `lychee` link-check pass on the rendered `public/` would surface and quantify them.
