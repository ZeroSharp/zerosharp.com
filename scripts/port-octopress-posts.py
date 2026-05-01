#!/usr/bin/env python3
"""Port Octopress posts to Hugo.

Reads `<src>/source/_posts/*.markdown` and writes
`<dst>/content/blog/<slug>.md` with Hugo-compatible TOML front-matter
and Liquid shortcodes rewritten to Hugo equivalents (or fenced code).

Usage:
    python port-octopress-posts.py --src C:/Projects/github/octopress \
                                   --dst C:/Projects/github/zerosharp
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml  # PyYAML — `pip install pyyaml` if missing


# Octopress filename: 2012-04-06-setting-up-octopress-on-windows.markdown
FILENAME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.(?:markdown|md)$")

# Original site URL — Disqus identifiers were computed from this.
ORIGINAL_SITE_URL = "http://ZeroSharp.github.com"

# {% codeblock [title] [lang:foo] %} ... {% endcodeblock %}
CODEBLOCK_RE = re.compile(
    r"\{%\s*codeblock\s*(?P<args>[^%]*?)\s*%\}\n?(?P<body>.*?)\n?\{%\s*endcodeblock\s*%\}",
    re.DOTALL,
)

# {% blockquote [opts...] %} ... {% endblockquote %}
BLOCKQUOTE_RE = re.compile(
    r"\{%\s*blockquote\s*(?P<args>[^%]*?)\s*%\}\n?(?P<body>.*?)\n?\{%\s*endblockquote\s*%\}",
    re.DOTALL,
)

# {% pullquote %} ... {% endpullquote %}
PULLQUOTE_RE = re.compile(
    r"\{%\s*pullquote\s*%\}\n?(?P<body>.*?)\n?\{%\s*endpullquote\s*%\}",
    re.DOTALL,
)

# {% raw %} ... {% endraw %} — Liquid escape; Hugo doesn't need it.
RAW_RE = re.compile(
    r"\{%\s*raw\s*%\}(?P<body>.*?)\{%\s*endraw\s*%\}",
    re.DOTALL,
)

# {% img [class] /path [w h] [alt text] %}
IMG_RE = re.compile(r"\{%\s*img\s+(?P<args>[^%]*?)\s*%\}")

# {% imgcap [class] /path [caption] %}
IMGCAP_RE = re.compile(r"\{%\s*imgcap\s+(?P<args>[^%]*?)\s*%\}")

# {% youtube ID %}
YOUTUBE_RE = re.compile(r"\{%\s*youtube\s+(?P<id>\S+)\s*%\}")

# {% gist USERNAME/ID %} or {% gist ID %}
GIST_RE = re.compile(r"\{%\s*gist\s+(?P<args>\S+(?:\s+\S+)?)\s*%\}")

# {% highlight TEXT %} — Octopress plugin (plugins/highlight.rb).
# Renders TEXT as inline highlighted text (span.fluo). The TEXT
# itself can contain Markdown, so we keep it as Markdown and wrap
# in a span via raw HTML.
HIGHLIGHT_RE = re.compile(r"\{%\s*highlight\s+(?P<text>[^%]+?)\s*%\}", re.DOTALL)


def split_img_args(args: str) -> tuple[str | None, str, str | None]:
    """Split `[class] /path [alt]` into (class, path, alt).

    Octopress accepts:
        {% img /path %}
        {% img right /path %}
        {% img right /path "alt with spaces" %}
        {% img right /path Alt without quotes %}
    """
    args = args.strip()
    parts: list[str] = []

    # Pull off a leading position keyword if present.
    cls = None
    head = args.split(maxsplit=1)
    if head and head[0] in {"left", "right", "center"}:
        cls = head[0]
        args = head[1] if len(head) > 1 else ""

    # First remaining token is the path.
    if not args:
        return cls, "", None
    if " " in args:
        path, rest = args.split(maxsplit=1)
        # rest is the alt — strip quotes if present
        rest = rest.strip()
        if (rest.startswith('"') and rest.endswith('"')) or (
            rest.startswith("'") and rest.endswith("'")
        ):
            rest = rest[1:-1]
        return cls, path, rest if rest else None
    return cls, args, None


def replace_img(match: re.Match) -> str:
    cls, path, alt = split_img_args(match.group("args"))
    alt = alt or ""
    # Octopress `{% img right /p %}` floats the image. We need to
    # preserve that — markdown's ![]() can't carry a class, so emit
    # raw HTML which Markdown still accepts inside a paragraph.
    # The trailing blank line is critical for Goldmark: an <img> at
    # the start of a line is treated as a raw HTML block and would
    # swallow the following paragraph's markdown without a separator.
    if cls in {"left", "right", "center"}:
        return f'<img class="img-{cls}" src="{path}" alt="{alt}">\n'
    return f"![{alt}]({path})"


def replace_imgcap(match: re.Match) -> str:
    cls, path, caption = split_img_args(match.group("args"))
    caption = caption or ""
    return (
        f'<figure>\n'
        f'  <img src="{path}" alt="{caption}">\n'
        f"  <figcaption>{caption}</figcaption>\n"
        f"</figure>"
    )


def replace_youtube(match: re.Match) -> str:
    return f'{{{{< youtube "{match.group("id")}" >}}}}'


def replace_gist(match: re.Match) -> str:
    args = match.group("args").strip().split()
    if len(args) == 2:
        user, gist_id = args
    else:
        # Single arg: ID or user/ID
        if "/" in args[0]:
            user, gist_id = args[0].split("/", 1)
        else:
            user, gist_id = "", args[0]
    if user:
        return f'{{{{< gist {user} {gist_id} >}}}}'
    return f'{{{{< gist anonymous {gist_id} >}}}}'


def replace_codeblock(match: re.Match) -> str:
    args = match.group("args").strip()
    body = match.group("body")

    # Pull lang:xxx out of args
    lang = ""
    title = ""
    lang_match = re.search(r"lang:(\S+)", args)
    if lang_match:
        lang = lang_match.group(1)
        args = (args[: lang_match.start()] + args[lang_match.end() :]).strip()
    # Anything left is the title
    title = args.strip().strip('"').strip("'")

    if title:
        return f"```{lang}\n# {title}\n{body}\n```"
    return f"```{lang}\n{body}\n```"


def replace_blockquote(match: re.Match) -> str:
    args = match.group("args").strip()
    body = match.group("body").strip()

    # Octopress: `author, source URL, title` (commas optional).
    # Just turn the whole thing into a Markdown blockquote with an
    # attribution line below if args are non-empty. Imperfect but
    # readable, and we avoid a custom shortcode for one feature.
    quoted = "\n".join(f"> {line}" if line else ">" for line in body.splitlines())
    if args:
        return f"{quoted}\n>\n> — {args}"
    return quoted


def replace_pullquote(match: re.Match) -> str:
    body = match.group("body").strip()
    return f'{{{{< pullquote >}}}}\n{body}\n{{{{< /pullquote >}}}}'


def replace_raw(match: re.Match) -> str:
    return match.group("body")


def replace_highlight(match: re.Match) -> str:
    """Octopress {% highlight TEXT %} -> Hugo highlight shortcode.

    Inner text may contain Markdown (e.g. links). We delegate to a
    custom Hugo shortcode (layouts/shortcodes/highlight.html) which
    renders `.fluo` and runs the inner content through markdownify.
    """
    text = match.group("text").strip()
    return f'{{{{< highlight >}}}}{text}{{{{< /highlight >}}}}'


def transform_body(body: str) -> str:
    # Order matters: codeblock first so we don't process its inner content,
    # then raw (which is inside other markup), then the rest.
    body = CODEBLOCK_RE.sub(replace_codeblock, body)
    body = BLOCKQUOTE_RE.sub(replace_blockquote, body)
    body = PULLQUOTE_RE.sub(replace_pullquote, body)
    body = RAW_RE.sub(replace_raw, body)
    body = HIGHLIGHT_RE.sub(replace_highlight, body)
    body = YOUTUBE_RE.sub(replace_youtube, body)
    body = GIST_RE.sub(replace_gist, body)
    body = IMGCAP_RE.sub(replace_imgcap, body)
    body = IMG_RE.sub(replace_img, body)
    return body


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_yaml = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    fm = yaml.safe_load(fm_yaml) or {}
    return fm, body


def build_toml_frontmatter(fm: dict, slug: str) -> str:
    """Emit Hugo TOML front-matter from the Octopress YAML map."""
    out: list[str] = ["+++"]

    title = fm.get("title", slug.replace("-", " ").title())
    out.append(f'title = {toml_string(title)}')

    # Date: Octopress uses `2012-04-06 17:11`. PyYAML may parse it as
    # a naive datetime, a date, or a string depending on the format.
    # TOML accepts unquoted RFC3339 — emit that.
    raw = fm.get("date")
    date_str = None
    if isinstance(raw, datetime):
        if raw.tzinfo is None:
            raw = raw.replace(tzinfo=timezone(timedelta(hours=1)))  # BST default
        date_str = raw.strftime("%Y-%m-%dT%H:%M:%S%z")
        date_str = date_str[:-2] + ":" + date_str[-2:]  # add colon in offset
    elif hasattr(raw, "isoformat"):  # datetime.date
        date_str = raw.isoformat() + "T00:00:00+01:00"
    elif isinstance(raw, str):
        # Try common Octopress patterns: "2012-04-06 17:11" or "2012-04-06"
        for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d %H:%M %z",
                    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
                    "%Y-%m-%d"):
            try:
                d = datetime.strptime(raw.strip(), fmt)
                if d.tzinfo is None:
                    d = d.replace(tzinfo=timezone(timedelta(hours=1)))
                date_str = d.strftime("%Y-%m-%dT%H:%M:%S%z")
                date_str = date_str[:-2] + ":" + date_str[-2:]
                break
            except ValueError:
                continue
    if date_str:
        out.append(f"date = {date_str}")

    out.append(f'slug = "{slug}"')

    if cats := fm.get("categories"):
        if isinstance(cats, str):
            cats = [c.strip() for c in cats.split() if c.strip()]
        cats = [str(c) for c in cats]
        out.append("categories = " + toml_array(cats))

    if desc := fm.get("description"):
        out.append(f"description = {toml_string(desc)}")

    # Stable Disqus identifier so existing threads stay attached.
    out.append(
        f'disqus_identifier = "{ORIGINAL_SITE_URL}/{slug}/"'
    )
    out.append(f'disqus_url        = "{ORIGINAL_SITE_URL}/{slug}/"')

    out.append("+++\n")
    return "\n".join(out)


def toml_string(s: str) -> str:
    if "\n" in s or '"' in s:
        # Use literal multiline if needed
        return "'" + s.replace("'", "\\'") + "'"
    return f'"{s}"'


def toml_array(xs: list[str]) -> str:
    return "[" + ", ".join(f'"{x}"' for x in xs) + "]"


def port_one(src: Path, dst_dir: Path) -> str | None:
    m = FILENAME_RE.match(src.name)
    if not m:
        return f"skip (filename pattern): {src.name}"
    slug = m.group(4)

    text = src.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)

    body = transform_body(body)

    out = build_toml_frontmatter(fm, slug) + body
    if not out.endswith("\n"):
        out += "\n"

    dst_path = dst_dir / f"{slug}.md"
    dst_path.write_text(out, encoding="utf-8", newline="\n")
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=Path,
                    help="Octopress repo root")
    ap.add_argument("--dst", required=True, type=Path,
                    help="Hugo repo root")
    args = ap.parse_args()

    posts_dir = args.src / "source" / "_posts"
    out_dir = args.dst / "content" / "blog"
    out_dir.mkdir(parents=True, exist_ok=True)

    posts = sorted(posts_dir.glob("*.markdown")) + sorted(posts_dir.glob("*.md"))
    if not posts:
        print(f"no posts found under {posts_dir}", file=sys.stderr)
        return 2

    skipped: list[str] = []
    for p in posts:
        msg = port_one(p, out_dir)
        if msg:
            skipped.append(msg)
            print(msg, file=sys.stderr)

    print(f"ported {len(posts) - len(skipped)} of {len(posts)} posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
