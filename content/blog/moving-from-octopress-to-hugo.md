+++
title = "Moving from Octopress to Hugo"
date = 2026-05-02T08:00:00+01:00
slug = "moving-from-octopress-to-hugo"
categories = ["meta", "site", "octopress", "hugo"]
description = "Why I gave up on the 13-year-old Octopress toolchain and what it took to bring 95 posts over to Hugo."
+++

I have converted this whole blog from Octopress to Hugo and modernised the theme.

I haven't blogged in a while, and the prospect of getting Octopress to build on a modern machine had become its own deterrent. So before I could write anything, I had to do something about the platform. But I'm not sure I would ever have bothered until Claude Code made things easy.

## The problem with Octopress

Octopress is built on Jekyll **0.11**, released in 2012. The latest Jekyll is 4.x. Most of Octopress's plugin ecosystem assumes APIs that no longer exist. 

Claude spent about two hours bringing the existing repo back to life: installing Ruby 2.7 alongside an MSYS2 toolchain, bumping and pinning dependencies. It got everything working. I had a working Octopress install in 2026. But every dependency upgrade going forward would re-open that hole. 

I'd made a mockup of how I wanted everything to look and used [Claude Design](https://claude.ai/design) to turn it into a design system. I got Claude to try to apply the new look to Octopress and it got about 80% of where I wanted it visually. But to get the last 20%, I'd have to rewrite Octopress's templates wholesale.

So I asked Claude for recommendations and it suggested moving everything to Hugo instead.

## Picking Hugo

- The HTML of the mockup for the new theme I'd designed translates almost line-for-line to Hugo Go-templates.
- Hugo's syntax highlighter (Chroma) is **Pygments-class-compatible** — the existing Solarized SCSS survives the migration unchanged.
- It's still actively developed; Octopress hasn't seen a release since 2015.

## Porting the content

The hard part of any migration is the content. Octopress posts are Markdown files with YAML front-matter and Liquid shortcodes embedded in the body — `{% codeblock %}`, `{% img right /p alt %}`, `{% blockquote author %}…{% endblockquote %}`, `{% youtube ID %}`, the Octopress-specific `{% pullquote %}` and `{% highlight TEXT %}` plugins.

Hugo doesn't speak Liquid. So Claude Code wrote a Python script that walks `source/_posts/*.markdown` and writes out `content/blog/<slug>.md` with the front-matter rewritten to TOML and the shortcodes either translated to Hugo equivalents or rewritten to plain Markdown.

## Identifiers and links

Two small things I'm glad I thought about up front:

**Disqus identifiers.** Disqus keys threads by an identifier the page sets at render time. The original Octopress site computed it as `site.url + page.url`, which evaluated to e.g. `http://ZeroSharp.github.com/fast-batch-deletions-with-devexpress-xpo/`. The migration script writes that exact string into each post's `disqus_identifier` and `disqus_url` front-matter. Existing comment threads stay attached. Without that, every post would have started with zero comments.

**URL preservation.** Old post URLs were `blog.zerosharp.com/<slug>/`. Hugo's default would be `blog.zerosharp.com/blog/<slug>/`. A one-line `[permalinks] blog = "/:slug/"` in `hugo.toml` keeps the old paths working — no 301 redirects, no SEO loss, no broken external links. The blog index lives at `/blog/`; individual posts at `/<slug>/`.

## Blog resurrected

So a blog that was doomed has been resurrected. Thanks Claude.
