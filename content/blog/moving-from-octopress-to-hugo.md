+++
title = "Moving from Octopress to Hugo"
date = 2026-05-02T08:00:00+01:00
slug = "moving-from-octopress-to-hugo"
categories = ["meta", "site", "hugo"]
description = "Why I gave up on the 13-year-old Octopress toolchain and what it took to bring 95 posts over to Hugo."
+++

The site you're reading this on used to run on [Octopress](http://octopress.org/). For thirteen years. The last post before this one was in 2018. The toolchain was a Ruby 1.9.3 install, a long Gemfile of 2012-vintage gems, and a `rake` deploy script that pushed to GitHub Pages.

I haven't blogged in a while, and the prospect of getting Octopress to build on a modern machine had become its own deterrent. So before I could write anything, I had to do something about the platform. This is what I did.

## The problem with Octopress

Octopress is built on Jekyll **0.11**, released in 2012. The latest Jekyll is 4.x. Most of Octopress's plugin ecosystem assumes APIs that no longer exist. Two of its core dependencies — `pygments.rb 0.2.x` and `rdiscount 1.6.x` — fail to compile against modern GCC, and `pygments.rb 0.2` depends on the long-abandoned `rubypython` gem to bridge to Python.

I spent about two hours bringing the existing repo back to life: installing Ruby 2.7 alongside an MSYS2 toolchain, bumping `rdiscount` to 2.2 and `pygments.rb` to 2.4, pinning `ffi` to 1.15.5 to escape the abandoned `rubypython` chain, and gutting the `RubyPython.configure` line from `plugins/windows.rb` because the new pygments wrapper doesn't need it.

It built. I had a working Octopress install in 2026. But every dependency upgrade going forward would re-open that hole. I'd applied a beautiful new design (built with [Claude Design](https://claude.ai/design)) and reached about 80% of where I wanted it visually — but the legacy `hentry`/`entry-title`/`subscription`-icon HTML structure that Octopress emits doesn't match the new design's clean class structure (`zs-site-header`, `post-eyebrow`, `cat-chip`, `byline-avatar`). To get the last 20%, I'd have to rewrite Octopress's templates wholesale.

At which point I might as well rewrite them somewhere else.

## Picking Hugo

I considered Astro and Eleventy and a Jekyll 4 upgrade. They all have merits. Hugo won on a single criterion: **zero runtime dependencies**. One 30 MB binary, no Ruby, no Node, no MSYS2. Builds the entire site — 95 posts, 280-something pages including category and tag aggregators — in around 130 milliseconds.

The other things that mattered:

- The mockup HTML I had translates almost line-for-line to Hugo Go-templates.
- Hugo's syntax highlighter (Chroma) is **Pygments-class-compatible** — the existing Solarized SCSS for `.k`, `.s`, `.nc`, `.kt` survives the migration unchanged.
- Hugo Pipes compiles SCSS natively. No `gulp`, no `webpack`, no `package.json`.
- It's still actively developed; Octopress hasn't seen a release since 2015.

## Porting the content

The hard part of any migration is the content. Octopress posts are Markdown files with YAML front-matter and Liquid shortcodes embedded in the body — `{% codeblock %}`, `{% img right /p alt %}`, `{% blockquote author %}…{% endblockquote %}`, `{% youtube ID %}`, the Octopress-specific `{% pullquote %}` and `{% highlight TEXT %}` plugins.

Hugo doesn't speak Liquid. So I wrote a small Python script — about 250 lines, one regex per shortcode — that walks `source/_posts/*.markdown` and writes out `content/blog/<slug>.md` with the front-matter rewritten to TOML and the shortcodes either translated to Hugo equivalents or rewritten to plain Markdown:

- `{% codeblock lang:csharp %}…{% endcodeblock %}` → fenced code blocks (\`\`\`csharp). Chroma highlights them with the same Solarized Dark theme.
- `{% img right /p "alt" %}` → `<img class="img-right" src="/p" alt="alt">` raw HTML. Markdown's `![]()` syntax can't carry a class, and losing the `right` float would break image-heavy posts where text is supposed to wrap around the figure.
- `{% blockquote author %}…{% endblockquote %}` → standard `>` Markdown quote with an attribution line below.
- `{% youtube ID %}` → `{{< youtube ID >}}` (Hugo's built-in shortcode).
- `{% gist user id %}` → `{{< gist user id >}}` — Hugo retired its built-in gist shortcode in 0.156.0, so I replaced it with a small custom shortcode that uses GitHub's own embed script.
- `{% pullquote %}…{% endpullquote %}` and `{% highlight TEXT %}` → custom Hugo shortcodes that mimic the Octopress styling.

## Things that broke and how I noticed

I expected most of the friction to come from the content port. In practice the posts came over cleanly; the friction was in three small renderer-vs-author-intent disagreements that surfaced during spot-checks.

**Goldmark and floated images.** Goldmark, Hugo's CommonMark parser, treats an `<img>` at the start of a line as a raw HTML block, and a raw HTML block extends until the next blank line. So this:

```
<img class="img-right" src="…" alt="…">
Tomorrow could be an exciting moment in the history of maths. [Sir Michael Atiyah](https://…) is presenting…
```

…rendered with the markdown link unparsed, as literal text. Adding a blank line after the `<img>` fixes it. The migration script now does that automatically.

**Indented code blocks.** Goldmark emits a plain `<pre><code>` for 4-space-indented code, without the `.highlight` wrapper Chroma uses for fenced code. My SCSS targeted only `.highlight` so indented blocks rendered as monospace text with no frame. Fix: a fallback `.entry-content pre` rule for the unwrapped case, with the same dark Solarized fill but no traffic-light header (visually quieter for shell snippets like `$ cd nodejscomponent`).

**Pullquote rendering.** Octopress's `{% pullquote %}` shortcode marked phrases inside `{"…"}` braces for sidebar pull-out display. The mockup design doesn't have a sidebar, so my first pass styled the whole pullquote as a yellow-bordered block — which made it look like a blockquote it wasn't. Simplified: render the body as plain paragraphs, strip the `{"…"}` braces. Pull-quote behaviour gone, paragraph content preserved.

## Identifiers and links

Two small things I'm glad I thought about up front:

**Disqus identifiers.** Disqus keys threads by an identifier the page sets at render time. The original Octopress site computed it as `site.url + page.url`, which evaluated to e.g. `http://ZeroSharp.github.com/fast-batch-deletions-with-devexpress-xpo/`. The migration script writes that exact string into each post's `disqus_identifier` and `disqus_url` front-matter. Existing comment threads stay attached. Without that, every post would have started with zero comments.

**URL preservation.** Old post URLs were `blog.zerosharp.com/<slug>/`. Hugo's default would be `blog.zerosharp.com/blog/<slug>/`. A one-line `[permalinks] blog = "/:slug/"` in `hugo.toml` keeps the old paths working — no 301 redirects, no SEO loss, no broken external links. The blog index lives at `/blog/`; individual posts at `/<slug>/`.

## What it looks like now

A single Git repo containing the landing page (the giant "0#" mark on full-bleed yellow that's been the front of zerosharp.com for years), the about page, and the blog. Everything Hugo, everything Markdown, deployed from `git push` to Cloudflare Pages.

The decision document and changelog for the whole migration live in the repo at `DECISIONS.md` and `CHANGELOG.md` — partly so I have a record, partly because the migration itself feels like the right subject for the first post in eight years.

There's a Python script in `scripts/port-octopress-posts.py` that did the content rewrite, in case any of this is useful to someone else stuck with an old Octopress repo.

Now I just need to remember what I used to write about.
