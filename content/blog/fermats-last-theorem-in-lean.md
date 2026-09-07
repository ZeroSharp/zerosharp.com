+++
title = "Fermat's Last Theorem in Lean"
date = 2026-09-07T08:00:00+01:00
slug = "fermats-last-theorem-in-lean"
categories = ["mathematics", "lean", "claude", "ai"]
description = "Anthropic's models formalised Wiles' proof of Fermat's Last Theorem."
+++

Fermat's Last Theorem has been [formally verified](https://www.anthropic.com/research/formalizing-fermats-last-theorem)! Anthropic translated the proof into Lean, and the machine checked it. The code is [on GitHub](https://github.com/anthropics/fermats-last-theorem).

## 1991

<img class="img-right" src="/images/blog/fermats-last-theorem-in-lean-extended-essay.jpg" alt="The typewritten title page of my 1991 extended essay: Fermat's Last Theorem, an extended essay by Robert Anderson">

I feel peripherally connected to this result. In 1991 at the International School of Geneva, I wrote my International Baccalaureate extended essay on Fermat's Last Theorem. At that time nobody had proved it. It had been open for 350 years. Andrew Wiles announced his proof two years later, in 1993. It took another two years and a repaired gap before it was accepted.

## 2019

In 2019 I briefly joined [Kevin Buzzard's Xena project](https://xenaproject.wordpress.com/). I had been inspired by [this video](https://www.youtube.com/watch?v=Dp-mQ3HxgDE). At the time he was formalising the Imperial College undergraduate maths syllabus in Lean. He ran a Discord server where people did speed runs — racing to prove things in as few lines as possible. When I started at Imperial in 1992, I was part of the very first cohort of students taking their new Joint Maths and Computing degree. Some of the material we were formalising still looked familiar.

My own contribution was small. I [fixed some typos](https://github.com/ImperialCollegeLondon/natural_number_game/pull/15) in the [Natural Number Game](https://adam.math.hhu.de/#/g/leanprover-community/nng4), a tutorial where you prove basic facts about the natural numbers. That was the level we were at: getting `zero_mul` and `mul_succ` stated correctly in the teaching material.

## 2024

Kevin Buzzard obtained funding for [a five year project](https://gtr.ukri.org/projects?ref=EP%2FY022904%2F1) to formalise Fermat's Last Theorem in Lean.

## 2026

AI verified the proof in Lean in under two weeks. This also closes [Freek Wiedijk's list of 100 theorems to formalise](https://www.cs.ru.nl/~freek/100/). Fermat's Last Theorem was the last one standing, twenty years after the list was drawn up.

Kevin has written about it here: [FLT: Anthropic has beaten me to it](https://xenaproject.wordpress.com/2026/09/04/flt-anthropic-has-beaten-me-to-it/). He points out that his project has a different goal — to add formalised modern number theory back into Mathlib, and to produce something humans can read and explore.

## What it looks like in Lean

Lean is a programming language for writing and checking proofs. Fermat's Last Theorem looks like this.

```lean {linenos=false}
theorem fermat_last_theorem (n : ℕ) (hn : 3 ≤ n) (a b c : ℕ)
    (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    a ^ n + b ^ n ≠ c ^ n
```

Proving the statement took Claude:

- 11 days.
- About 13 million lines of Lean. Mathlib, the community maths library that took years to build, is about a fifth of that size.
- 30,300 theorems proved, of which 29,500 are used in the final proof.
- Roughly six billion output tokens.
- 60,475 modules. Five and a half hours to compile on a 96-core machine.

The agents worked together through a platform called Prove2Me, which keeps a dependency graph of what has been proved and lets an agent search for an existing theorem by describing it in English. Earlier attempts without it failed because the agents kept losing track of where the project was.

Anthropic are honest about the shape of the result. The proof is _likely much longer than it needs to be_, and about 7% of the lines are left over from attempts that did not work out.
