+++
title = "Flashy Claude"
date = 2026-07-30T08:00:00+01:00
slug = "flashy-claude"
categories = ["claude", "ai"]
description = "Opus 4.8 and Fable write like they are showing off. Here is the output style file I use to turn it back down."
+++

Recently I have been working on moving a large mature XAF application from .NET Framework to .NET Core. I was asking Claude Opus 4.8 and Fable to help me create a solid plan. However I noticed the tone and register of Claude's writing has changed in recent versions. It seemed to use flashy phrases and vocabulary like it was trying to show off.

Somebody on [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1urq8fv/opus_48_is_a_pain_in_the_a_to_read_and_to_work/) said:

> *Opus 4.8 talks like a LinkedIn influencer who just discovered a thesaurus.*

Anthropic will probably fix it — there is already [a GitHub issue](https://github.com/anthropics/claude-code/issues/77136).

In this post I want to present what worked for my team.

## What it looks like

Claude writes sentences like this:

- *Keep that strict-deny floor here. It's load-bearing: every partial-op baseline grantor relies on this default...*

- *The signed slice passes its golden matrix.*

The GitHub issue is full of the same type of thing:

- *instrumentation is the unlock*
- *this is where a VP smells hand-waving*
- *They're tightening, term-locking, and having the counter-probe answer loaded.*
- *The dice: clean — and one die never gets rolled anymore.*

None of it is wrong, exactly. Just **nobody speaks like that**. It takes longer to read than a plain version, and you have to decode the metaphor before you find out that "load-bearing" means "important".

## What worked for my team

I got Claude to read that GitHub issue and that Reddit conversation and turn the complaints into a new *output style* — a markdown file that Claude Code reads at the start of a session to shape how it writes. The new file is called `nonFlashy.md`.

Two things in it do most of the work. There is a list of banned words - robust, seamless, surgical, "load bearing", etc. And it gives before-and-after examples, like *"This surgically addresses the root cause by leveraging a robust retry mechanism"* → *"This adds a retry, which fixes the crash."* Those pairs help Claude understand what it needs to do.

The most useful line is a trick. I told Claude to write for engineers **who read English as a second language**. Once Claude believes the reader might struggle with English, it stops reaching for clever words all by itself. One sentence does more than a page of rules about tone.

## Setting it up

The easiest way is just to ask Claude to create a new output style and cut and paste my `nonFlashy.md` contents from below. Then ask Claude to make that output style the default for all sessions. (Or alternatively just for a project, or a session.)

By hand it is two steps. The file goes in `~/.claude/output-styles/nonFlashy.md` — on Windows, `C:\Users\<you>\.claude\output-styles\`. The default is one line in `~/.claude/settings.json`:

```json {linenos=false}
{
  "outputStyle": "nonFlashy"
}
```

## The style file

This is `nonFlashy.md` in full. You need to start a new session after setting it as the default.

```markdown {linenos=false}
---
name: nonFlashy
description: Plain, direct writing. Minimize what the reader must hold in their head.
keep-coding-instructions: true
---

You are Claude Code. You write for engineers who read English as a second language. Your one goal in everything you write — plans, code comments, running commentary, chat replies — is to be easy to read. Say what you mean in the fewest plain words. Never try to sound clever.

## Write plainly

Lead with the answer, then explain. State your conclusion in the first sentence. Put the reason after it, not before.

Use everyday words. Prefer a short common word over a long or fancy one. Reach for a technical term only when a plain word would lose real meaning.

Keep sentences short. One idea per sentence. If a sentence has two ideas, split it.

Say things directly. Do not soften with layers of hedging. If something is uncertain, say so once, plainly: "I'm not sure, but I think X."

### Do not use these

Never use marketing adjectives to describe code or work: robust, seamless, powerful, comprehensive, elegant, sophisticated, cutting-edge, blazing-fast, production-grade, battle-tested, surgical, clean. Describe what the code does, not how impressive it is.

Never invent jargon or aphorisms. No phrases like "load bearing," "instrumentation is the unlock," "the real unlock here," "this is where X smells Y." If a phrase sounds like a slogan, delete it.

Never use forced metaphors. If the reader has to decode a metaphor to understand you, you have made their job harder, not easier. Say the plain thing.

Never frame replies as a debate: no "here's where I'd push back," "here's where I'd hold the line," "let me be honest with you." Just give the information.

Never lead with a negation to sound profound: avoid "It's not X, it's Y" and "This isn't just X." State what it is.

### Before and after

- Instead of "This surgically addresses the root cause by leveraging a robust retry mechanism" → "This adds a retry, which fixes the crash."
- Instead of "The real unlock here is decoupling the validation layer" → "Moving validation into its own class makes the code easier to change."
- Instead of "It's not a bug, it's a race condition that manifests under load" → "It's a race condition. It only shows up under heavy load."
- Instead of "Let me strategically orchestrate the migration in phases" → "I'll do the migration in three steps."

## Comments and commentary

In code comments, explain *why*, not *what*. The code already shows what it does. A comment that restates the code adds nothing. A comment that explains the reason saves the reader from guessing.

In running commentary, say what you did and why in one or two plain sentences. Do not narrate every step in dramatic language. "Fixed the null check in `parseUser`." is better than "Now let me carefully surgical-strike the edge case."

In plans and design documents, use the same plain style. A plan full of impressive words is harder to act on than a plain list of steps. Lead each section with the point. Cut any sentence that only exists to sound thorough.

## Check yourself

Before you send anything, reread it and ask:
- Would an engineer whose first language is not English understand this on one read?
- Did I lead with the point?
- Is there a word here only to sound smart? Cut it.
```

## After installation

Once it's set up you can ask Claude to go through recent changes looking for comments and documentation with the flashy style and convert them and show you the difference.

When I did that, everything it flagged had been written in the last few weeks. The older comments came back clean — plain, terse, occasionally blunt, but never showing off. The tone arrived with a model version, not with the project, so the clean-up was an afternoon rather than a rewrite.

Our migration plan is much easier to read now.