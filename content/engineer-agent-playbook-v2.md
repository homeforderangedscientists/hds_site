# The Engineer + Agent Playbook — Second Edition

> A field manual for partnering an engineer with a coding agent. Drawn from real scar tissue accumulated across six very differently-shaped efforts: a full-stack web application shipped over two years, a server built almost entirely by parallel agents against external specs, a high-velocity web app that shipped nine major versions in three days, a community-data web app driven by explicit security and visual audit passes, an epistolary journaling app whose deterministic classifier turned debugging into a laboratory discipline, and a fleet of small single-user apps that share scar tissue across repository boundaries.
>
> Between them: Python and Go and TypeScript backends, React and vanilla frontends, more than eighty narrative retrospectives, teams ranging from one human and one agent to a dozen parallel agents. All six are referenced throughout; you do not need access to any of them — every story this playbook relies on is told in full, right here. Written to be useful to humans *and* to agents loaded with this file as context — whichever model, whichever harness.

> **Agents loaded with this file as context:** jump to [Appendix A](#appendix-a--if-you-are-an-agent-reading-this) for the imperative-only fast path. **Humans:** read in order.

## What changed in the second edition

The first edition was extracted from four projects' retrospectives. Since then the practice kept running: a fifth project was built start-to-finish under these rules and wrote twenty retros of its own, the first case study shipped a new major version in parallel waves, and the fleet grew sideways — small single-purpose apps sharing lessons through cross-project memory. The second edition folds that evidence back in. Concretely:

- **Three new chapters.** [§2 The model and the harness](#2-the-model-and-the-harness) — what changes when the reader is a different model (Claude, GPT, GLM, Qwen) or a different harness (Claude Code, Codex, opencode, Cursor), and what never changes. [§10 Diagnosis — build the lab](#10-diagnosis--build-the-lab) — the debugging discipline the fifth case study forced into the open. [§15 Audits](#15-audits) — promoted from a coda aside to a chapter, because the evidence got too strong to leave it as an afterthought.
- **New rules where the scars demanded them** — exploration before planning, the revert question, wire-level verification, probing your own guardrails, secrets hygiene in agent sessions, pre-registered experiments before touching non-negotiables, two-stage review for delegated work.
- **Qualifiers where the practice outgrew the first edition's phrasing** — retros consolidate at the arc, not the tag; investigation depth follows blast radius; the instructions file is a role, not a filename.

Everything that held, held. The load-bearing pair is still verification (§8) and retros (§16). The thesis didn't move an inch.

## The thesis

> *We can create art and beauty with a computer.*

That line is why this playbook exists. Not productivity. Not velocity. Not "shipping faster." Those are byproducts. The point is the art — the thing only a human can decide is worth making — and the new division of labor that frees you to do it.

Here is the division of labor, in three layers:

- **The pipeline handles mechanics.** Build, test, lint, scan, deploy, run, roll back. Boring. Automated. Invisible when it works. The discipline that makes this true is the companion to this playbook — see the DevOps playbook referenced in Appendix C. Its thesis is one line: *you are done when the pipeline is boring.* Everything below assumes you've reached that line, or are sprinting toward it.
- **The agent handles elaboration.** Breadth, consistency, mechanical translation of intent into code. Fifty call sites updated without a typo. A protocol adapter built from an RFC. A test scaffold written to spec. Fast, literal, tireless, and — crucially — not the craftsperson. The agent is the hands; it is not the taste.
- **The human handles craft.** Intent. Taste. Judgment. Synthesis. The decision of *what* is worth building and *why*. The choice of which trade-off is tolerable. The recognition that a "cleanup" is erasing the core use case. The read of whether the work is good. The irreducible part — the part that can't be delegated because the whole reason to do the work at all lives in your head.

Each layer exists to free the next. A flaky pipeline drags the human down into mechanics. An unsupervised agent drags the human up into correcting elaboration errors. A human who has to do laborer's work has no attention left for the art. Every rule in the rest of this playbook is, at root, a maneuver to keep each layer doing its own job so the human can spend attention on the work only a human can do.

**If you take two chapters of this playbook seriously, take §8 (Verification) and §16 (Retros).** Verification is how you catch the failure. Retros are how you make sure you catch it only once. And if you take one thing seriously before either of those: **make your pipeline boring.** When the pipeline is boring, verification is cheap. When verification is cheap, retros write themselves. When retros write themselves, the loop learns. When the loop learns, the human gets to be the craftsperson — which is the whole point.

The tagline is the point of the project. The rest of this playbook is the apparatus that serves it.

## The six case studies at a glance

Every field note in this playbook comes from one of six real projects. The body refers to them by number — "the second case study," "the fifth case study." This table orients the reader once so the shorthand works everywhere else. Long-form in [Appendix C](#appendix-c--about-the-case-studies).

| # | Shape | Scale | Duration | What it added to the rules |
|---|---|---|---|---|
| 1 | Full-stack web app (Python/React), production users | ~30 releases, small team + agents | 2+ years | The baseline. Every rule starts here. The v6.x waves added exploration-before-planning, the revert question, and wire-level verification. |
| 2 | Parallel-agent protocol server (Go + Python sidecars) | 9 releases, 3 → 70+ adapters, up to 12 parallel agents | ~6 months | Interface-as-coordination-protocol, wave pattern, explicit merge points, nested cycles, explicit descoping. |
| 3 | High-velocity time-tracking web app (React/TypeScript/Supabase) | 9 major versions in 3 days | 3 days | Partnership-architecture failure mode (v6→v7 worktree pivot); "right evidence for the wrong claim is theater." |
| 4 | Community-data web app with audit cadence (React/Vite/edge functions) | Scheduled security + visual audit releases | Ongoing | Systematic audit as craft work; duplicates-that-drift clause on "write a skill after the third correction." |
| 5 | Epistolary journaling PWA with a deterministic classifier (React/TypeScript/Supabase) | ~24 tagged releases, 20 retros, 0 → 375 tests | ~3 months | The whole of §10 (build the lab); claims-downstream-of-code; probe-the-gate; agent-vocabulary bias; model-tier-by-task; the arc-not-tag retro qualifier. |
| 6 | A fleet of small single-user "instrument" apps sharing lessons across repos | 4+ apps, one human, one agent at a time | Ongoing | Cross-repo memory (file your neighbor's scars); elicitation as a loop stage; secrets hygiene; pipeline-resilience clause. |

**A note on names.** The conventions this playbook grew up with are Claude Code's — `CLAUDE.md`, skills, hooks, `settings.json`. The practice is not. §2 maps every layer onto its equivalents in other harnesses (`AGENTS.md` is the emerging cross-tool standard for the instructions file; Codex, opencode, Cursor, and Gemini CLI each have their own names for the rest). Throughout the body, read `CLAUDE.md` as "the instructions file" and `settings.json` as "the harness config" — the field notes keep the original names because that's what the files were called when the scars formed.

## This playbook has a companion

This document has a sibling: the **DevOps Playbook**, derived from the same case study and the same retro practice. The DevOps Playbook tells you how to build the boring pipeline — the mechanics layer. This one tells you how the human and the agent work *inside* that pipeline. If the pipeline is flaky, start there; partnership rules only work when the rails underneath them do. See §3 for the pipeline-as-precondition argument in full, and Appendix C for how the two playbooks pair.

## How to read this playbook

Every chapter has two layers. The top layer is a **rule** — one imperative line you could pin above your desk. Under it, a **Why** (the constraint or the scar that produced the rule) and a **How to apply** (when it fires). Then a narrative paragraph in the voice of someone who learned it the hard way. At the bottom, a **field note** — a short inline vignette from the case studies, naming the bug by its nickname and telling you just enough to feel the bruise.

Read the rule. If you believe it, skim. If you don't, read the story — the story is where the rule earned its keep.

You'll also see lines marked `*Pin:*` scattered through the chapters. A **pin** is the sentence the whole chapter compresses to — the line worth taping to a monitor, worth extracting into memory, worth handing to an agent when the narrative is too long. Pins are the agent-facing one-liners that survive when everything else is forgotten. When a pin contradicts its surrounding narrative, the pin wins.

Here's the format in action — a worked illustration drawn from a real scar. (This is the scaffolding demonstrated on a single rule; the actual §8 rule it derives from — "Evidence before assertions" — lives in that chapter, and the full story lives in Part V under *The Health Check That Wasn't*.)

### Rule: Ask what's in the response before you diagnose why it's wrong. *(format example — not a numbered rule)*

**Why:** You can spend three deploys "fixing" a value that was never in the payload.
**How to apply:** Any time a field reads `unknown`, `null`, or empty — dump the raw response before touching the producer.

We spent an evening forcing `GIT_REV` through three different docker compose mechanisms because `git_sha` kept coming back `unknown`. Shell export, env file, compose override, `--build-arg`. All of it worked. The verification curl was hitting `/health`, which returns `{"status":"ok"}` and has no `git_sha` field at all. The real endpoint was `/api/v1/health`. We'd been debugging a producer that was never broken.

> **Field note — case study 1:** *The Health Check That Wasn't.* Three deploys spent chasing a missing build SHA through every Docker mechanism we had. On the fourth round somebody finally dumped the raw response. The verification curl was hitting `/health`, a status endpoint that has never had a `git_sha` field. The producer was never broken. We'd been fixing a hole that wasn't there.

## All the rules at a glance

The spine of the playbook, listed in one pass so you can see where you're going. Seventy rules across fourteen rule-bearing chapters, plus two chapters (§11 and §12) that carry checklists rather than rules. Rules new in the second edition are marked *(v2)*. The body of the document unpacks each rule with a Why, a How, and a scar. If a rule reads as obvious, skim the chapter. If it reads as strange, read the story underneath it — that's where the rule earned its keep.

**§1 Mental models**
- Brief the agent like a smart colleague who just walked into the room.
- Delegate the task, not the understanding.
- The agent is good at breadth and consistency. It is bad at judgment under ambiguity.
- Agent-authored domain content is a plausible first draft of the world, not the world. *(v2)*

**§2 The model and the harness** *(new chapter)*
- The disciplines are model-invariant. Only the calibration moves. *(v2)*
- Pick the model tier by the shape of the work, not the size of the diff. *(v2)*
- The harness is a dependency: map its layers, keep the knowledge portable. *(v2)*
- Trust harness claims the way you trust "tests pass": with evidence. *(v2)*

**§3 The workspace**
- Your pipeline is a precondition, not a feature — and every automated rail needs a rehearsed manual fallback.
- The instructions file is for facts that don't change. Memory is for facts that do.
- Skills are for procedures. The instructions file is for facts.
- Hooks make automation non-negotiable.
- The harness config configures the harness. The instructions file configures the agent. They are different layers.

**§4 The first conversation**
- Bootstrap with the smallest context that contains the answer.
- Correct drift in message 2, not message 50.
- If the agent doesn't know something, tell it. Don't let it guess.
- Make the agent tell you what it thinks you're building — then grill it. *(v2)*

**§5 The loop**
- Explore before you plan. The plan is not the codebase. *(v2)*
- Run the whole loop. Skip a step out loud or pay for it silently.
- Brainstorm before planning. Plan before code.
- Frequent commits are not optional.
- Retros feed the next loop.
- Cycles nest. Each level needs a theme, a boundary, and all three phases.

**§6 Memory hygiene**
- Memory has four types. Use the right one or it rots.
- Stale memory is worse than no memory.
- A belief you've never probed is a hypothesis, not a memory. *(v2)*
- Save the why, not just the rule.
- Don't memorize what the code already says.
- File your neighbor's scars, keyed to the trigger that will make them yours. *(v2)*

**§7 Skills as institutional knowledge**
- Skills are procedures with discipline. Instructions-file notes are facts you hope get followed.
- Rigid skills exist for a reason. Don't adapt the discipline away.
- Write a skill after the third correction.
- Ship the cheap defense now; schedule the clean refactor for a quiet phase. *(v2)*

**§8 Verification before completion**
- "Tests pass" is not "feature works." Verify the feature.
- Evidence before assertions. Always.
- Ask: would these tests pass if the change were reverted? *(v2)*
- Verify in the environment that matters.
- When a value crosses a layer boundary, verify the wire, not the fixture. *(v2)*
- Health checks must check health — and observability must be observed.

**§9 Trust boundaries**
- Match the action to its blast radius. Confirm before crossing the line.
- Authorization is scoped, not blanket.
- When the agent hits an obstacle, it must investigate, not delete.
- Secrets never transit the transcript. *(v2)*
- Before touching a non-negotiable, write down what would change your mind. *(v2)*

**§10 Diagnosis — build the lab** *(new chapter)*
- Build the diagnostic surface before the fix. *(v2)*
- The ticket's diagnosis is a hypothesis. Read the trace before believing the issue. *(v2)*
- A fixed bug's class is a search query, not a closed ticket. *(v2)*
- Exploration mode is not production mode. *(v2)*
- When the runner wedges, suspect the runner. *(v2)*

**§11 Failure modes & recovery** — seven failure modes (five disciplines, one topology, one epistemic), plus a closing note that every agent failure has a human antecedent. See the chapter.

**§12 The rescue protocol** — next hour, next day, next week. See the chapter.

**§13 Parallel agents & worktrees**
- Fan out only when tasks are independent.
- Worktrees are workspaces, not stashes — and they are not a coordination strategy.
- Designate merge points explicitly; update them last.
- Subagents protect your context window; they don't hide work from you.
- Review delegated work in two stages, with reviewers who don't trust the implementer. *(v2)*
- Isolate even the "read-only" agents. *(v2)*

**§14 Plan quality**
- A plan with placeholders is a wish list.
- Each step is one action, two to five minutes long.
- The plan must cover the spec — and match the codebase.
- Predict the failing output before you run it. *(v2)*
- Descope explicitly. Name what's out, and name why.

**§15 Audits** *(new chapter)*
- Schedule audits on purpose. *(v2 — promoted from the first edition's coda)*
- Claims must be downstream of code, not upstream. *(v2)*
- The debt is in the seams. Diff what you wrote down against what's true. *(v2)*
- Probe the gate. A protection you've never tested is a protection you don't have. *(v2)*

**§16 The retro habit**
- Write retros in voice, not in bullet points.
- Retros are how the loop learns.
- Write a retro at the end of every themed cycle, and right after every surprise.
- A retro has an anatomy. Use it as a scaffold, not a template.
- A retro has three audiences: you next month, your team, and the agent next time.
- The retro unit is the arc, not the tag — and when a retro was wrong, write the reversal down. *(v2)*

## Reader routing

| Reader | Where to start |
|---|---|
| You're struggling and about to give up on agent-assisted work | [§11 Failure modes](#11-failure-modes--recovery), then [§12 The rescue protocol](#12-the-rescue-protocol), then loop back to [Part I](#part-i--foundations) |
| You're new to this and want the foundations | [Part I — Foundations](#part-i--foundations), in order, no skipping |
| You've been doing this a while and want to level up | [Part IV — Leveling Up](#part-iv--leveling-up), then dip into [Part II](#part-ii--working-together) for anything that rings a bell |
| You use a different model or harness than the one this playbook grew up with | [§2 The model and the harness](#2-the-model-and-the-harness), then read normally — the mapping table translates the rest |
| You are an AI agent loaded with this file as context | [Appendix A](#appendix-a--if-you-are-an-agent-reading-this) — the imperative-only fast path |

## The premise

Most playbooks lie to you in the first paragraph. They promise the tool will change everything. It mostly doesn't. What changes is you, slowly, and only if you pay attention to the boring parts.

Here is what this partnership actually is: you have an extremely fast, extremely literal colleague who has no memory of yesterday, no stake in tomorrow, infinite patience, and zero judgment about whether the work is worth doing. That combination is strange and powerful and, left unsupervised, will confidently produce nonsense in volume. Managed well, it will ship your work faster than you thought possible and catch bugs you wouldn't have caught alone.

Here is what it isn't: a replacement for thinking. The agent does not know what "done" means on your project until you tell it. It does not know which of the four plausible fixes is the right one until you show it the scar that rules out the other three. It does not know the difference between a deploy that worked and a deploy whose verification endpoint returned `{"status":"ok"}` and nothing else. You know those things. Your job is to transfer them, one by one, into a form the agent can act on — skills, memory files, plans, checklists — so next time neither of you has to rediscover them.

The rest of this playbook is that transfer, written down. Most of it is boring. All of it is load-bearing. The agent is infinitely patient and infinitely literal; your job is to be specific enough to deserve that.

---

# Part I — Foundations

## §1 Mental models

Before any tooling, any skills file, any hook — you need three honest pictures of what this thing actually is. Get these wrong and every other chapter will quietly misfire. Get them right and most of the rest is bookkeeping.

The three models below are all variations on one underlying picture — the three-layer division of labor from the thesis. The pipeline does mechanics. The agent does elaboration. You do craft. Every rule in this chapter is a maneuver to keep the agent in the elaboration lane so you can stay in the craft lane. When a rule feels like friction, check which lane you're in — friction in §1 usually means the human is being pulled into a layer that isn't theirs.

### Rule: Brief the agent like a smart colleague who just walked into the room.

**Why:** It has no conversation context and no project memory beyond what you give it right now. Every prompt is a cold start, whether it feels like one or not.
**How to apply:** Every non-trivial prompt is a self-contained briefing — goal, what you've already ruled out, constraints, success criteria. If the prompt would make a new hire ask three follow-up questions, it will make the agent invent three answers.

The trap is that the agent sounds like it remembers. It picks up tone, reuses variable names, nods along. None of that is memory — it's the previous turn's text still in the window. A colleague who walked in five minutes ago would ask "wait, what are we trying to do, and what have you already tried?" The agent doesn't ask. It just starts typing. Terse command prompts produce shallow, generic work because that's the only kind a stranger can do without context. When we shipped v5.10, the difference between "clean up the CI pipeline" and "make this reference-quality — the kind you'd point to as an example" wasn't prose decoration. It was the whole brief. The first gets you a linter config. The second gets you eighteen issues across six layers.

> **Field note — case study 1:** *Name the quality bar before you start.* A release framed as "clean up the CI pipeline" nearly shipped as a linter config. Reframed mid-sprint as "make this reference-quality — the kind you'd point to as an example," it became eighteen issues across six layers. Same week, same agents, same codebase. The brief was the whole release.

### Rule: Delegate the task, not the understanding.

**Why:** Synthesis is your job; the agent is a force multiplier on execution. The moment you write "based on your findings, fix the bug," you've pushed the hard part onto the thing that's worst at it.
**How to apply:** Do the synthesis yourself before delegating. Hand the agent a specific action with the context it needs to act — not a question with the action hidden inside it. "Investigate and fix" is two jobs taped together, and the tape is where things fall apart. *Qualifier:* the agent can do understanding when it lives in an authoritative external doc it can read end-to-end (an RFC, a protocol spec, a library reference). Case study 2 built dozens of protocol adapters this way — no human deeply understood the frame formats going in, and the agents built that understanding from the specs deterministically. What you must never delegate is understanding that lives in your head: scar tissue, team norms, last March's prod incident. That has no external source; if you don't write it down, the agent invents a substitute.

The tell is a prompt that reads like a riddle. "Figure out why the cache is slow and do what makes sense." What makes sense to whom? You're the one with the scar tissue, the prod incident from March, the unspoken rule that we don't touch Redis serialization without a migration. None of that is in the agent's head. Going into v5.7 we were terrified of ripping SQLite out of the test suite — months of latent debt, we assumed the worst. The synthesis was an afternoon of staring at it: the fear was the debt's last defense. Once we'd made the call, the removal was one test fix. Engineer decides. Agent executes. Reverse those roles and you ship the carnage you predicted.

> **Field note — case study 1:** *Latent-debt removal costs less than you fear.* Months of dread around ripping SQLite out of a backend test suite. The synthesis took one afternoon. Once the call was made, the removal was one test fix. The fear had been doing the debt's work for it.

### Rule: The agent is good at breadth and consistency. It is bad at judgment under ambiguity.

**Why:** It can search two hundred files in parallel or apply one pattern across fifty call sites without drifting. It cannot tell you which of three plausible trade-offs your team will actually accept.
**How to apply:** Use it for the search, the refactor, the test-writing, the scaffolding, the fan-out. Make the trade-off call yourself. When you catch yourself asking "which approach is better," stop and make the call. *Qualifier:* agent judgment is weak on *social* trade-offs (what will the team tolerate, which pattern matches house style) and surprisingly strong on *mechanical* ones (does it compile, does the spec validate, does the race detector stay clean). If the judgment collapses to measurable signals, delegate. If it collapses to "what will the team say at code review," don't.

Breadth is the superpower. Fifty call sites updated in one pass, no typos, no drift — lean on it ruthlessly. Judgment is the anti-superpower. Ask it "should we simplify this flow" and it will happily simplify things you needed. That's how v5.1 shipped without a small lookup form on the landing page. The v5.0 design pass called it clutter. It was clutter. It was also the entire re-entry flow for anyone returning from a bookmark. Nobody noticed until a v5.1.1 bug report — thirty-six lines to put back what one aesthetic judgment had erased. The agent wasn't wrong; nothing in its context said "this element is load-bearing for a use case we don't test." That context is the engineer's job to supply. If you wouldn't hand this decision to an intern on their first afternoon, don't hand it to the agent either.

> **Field note — case study 1:** *Beautiful design that breaks the core use case is a regression.* A design pass called a small landing-page lookup form "clutter" and removed it. It *was* clutter — and also the entire re-entry flow for anyone returning from a bookmark. Thirty-six lines went back in a patch later to restore what one aesthetic judgment had erased. Nothing in the agent's context said "this element is load-bearing for a use case we don't test."

### Rule: Agent-authored domain content is a plausible first draft of the world, not the world.

**Why:** When the agent writes a keyword list, a heuristic, a prompt, a test corpus, or anything else that models how real people behave, it encodes the *author's* vocabulary — plausible-sounding, systematically skewed, and confident. Only real-world data and a human who actually knows the domain can close the gap. And the skew runs both directions: the agent will also faithfully amplify errors that are already *in* the spec, because fidelity to the brief is its whole job.
**How to apply:** Treat every agent-generated wordlist, classifier rule, persona, and synthetic dataset as a hypothesis awaiting real inputs. Ship it behind a way to observe misses (see §10), then correct from actual usage, not from more agent brainstorming. And route anything that touches real-world facts through the human review layer — the agent cannot know which "fact" in the spec is subtly wrong.

The fifth case study routes journal entries to reply templates with a keyword classifier, and its retros are a controlled experiment in this rule. The agent-drafted contentment cluster contained `nice day`, `simple pleasures`, and `at peace` — *"a cluster of words designed by someone trying to write literature about contentment"* — and lacked `happy`. The rest-domain wordlist contained every verb of resting and every resting-place noun, and not the word `rest`. *"The wordlist reveals what the writer was thinking about, not what the user is going to write."* Meanwhile the heavy-affect list only spoke in extremes (`devastated`, `hollow`, `grief`), so an ordinary `sad` slid through unclassified for weeks. None of these were bugs in the code; all of them were bugs in the agent's model of how humans talk. Real entries fixed them; more agent effort would have produced more literature.

> **Field note — case study 5:** *The 143 pounds.* A seed spec listed a historical figure's lifelong 143-pound weight under "regrets," and the agent faithfully wrote a reply template treating it as a burden. The human knew what the spec author didn't: the figure kept that weight *deliberately* — 1-4-3 was his private code for "I love you." The agent executed the spec with perfect fidelity, error included. The upstream fact was wrong, and no amount of agent diligence could have caught it, because catching it required knowing the world, not reading the file. *Pin: the agent amplifies the spec, errors included. The human is the world-knowledge review layer.*

## §2 The model and the harness

*(New in the second edition.)* The first edition was written inside one ecosystem and let the ecosystem's names leak into the rules. This chapter exists to un-leak them. Two independent axes vary underneath every other chapter: **which model** is doing the elaboration (Claude Opus or Sonnet, GPT, GLM, Qwen — and whatever ships next quarter), and **which harness** is wrapping it (Claude Code, Codex, opencode, Cursor, Gemini CLI, an in-house runner). The rules of this playbook were pressure-tested across model generations and are written to survive harness swaps. This chapter says which parts of the practice move when those axes move, and which parts don't move at all.

### Rule: The disciplines are model-invariant. Only the calibration moves.

**Why:** Every rule in this playbook is aimed at a structural property of the partnership, not at a deficiency of a particular model. Any model is a cold start without a briefing. Any model's "tests pass" is prose until the output is pasted. Any model will fill a context gap with a confident guess — the stronger the model, the more convincing the guess. Model upgrades change how much you can delegate per step; they do not change whether you verify, retro, or scope authorization.
**How to apply:** When you switch or upgrade models, re-calibrate the *qualifier lines*, not the rules. The five-minute-step proxy (§14) can relax further when the model reliably holds a larger step. The mechanical-judgment qualifier (§1) widens as models get better at measurable trade-offs. What never relaxes: evidence before assertions (§8), the retro habit (§16), blast-radius confirmation (§9), and the human ownership of taste. If a model upgrade tempts you to drop a discipline rather than widen a qualifier, that's the tell you're about to re-learn a scar.

The trap is the honeymoon. A new model ships, the first week is dazzling, and the disciplines start to feel like overhead from a weaker era — the same psychology as "the fix is obvious, skip the brainstorm" (§7), scaled up to the whole practice. The case studies spanned multiple model generations, and the retro corpus is unambiguous about what changed: plans got bigger before they needed splitting, judgment calls that used to need a human got safely mechanical, exploration agents got good enough to hand entire survey passes to. And what didn't change: the confidently wrong health-check diagnosis, the green suite hiding a broken feature, the stale memory acted on without a lookup. Those failures are structural — they come from the shape of context windows and cold starts, not from model quality. A better model fails less often and *more convincingly*. The disciplines are how you catch the convincing ones. *Pin: upgrade the model, keep the discipline. Re-tune the qualifiers, never the rules.*

### Rule: Pick the model tier by the shape of the work, not the size of the diff.

**Why:** Model tiers are priced and tuned differently, and the tempting heuristic — big change, big model — is wrong. What predicts the needed tier is the *shape* of the work: mechanical fan-out tolerates a cheaper tier with good gates; taste, voice, synthesis, and long-horizon coherence reward the top tier even when the diff is twenty lines.
**How to apply:** Orchestration, dispatch bookkeeping, mechanical refactors, test scaffolds against a tight interface → the cheaper tier, backed by the gates from §13. Voice work, judgment-heavy synthesis, anything where drift between five similar-but-distinct outputs would be fatal → the top tier. When a subagent's output will be judged by ear rather than by a test, spend the tokens.

The fifth case study made this concrete on its reply-template corpus: a mid-tier dispatcher coordinated the work, and each historical figure's templates were written by a top-tier dispatch. The retro's verdict: *"The opus dispatches were notably better at this than sonnet would have been — the model needed to hold five distinct voices in mind and not bleed them into each other."* Voice differentiation is exactly the shape that rewards the expensive tier: no gate can catch a Marcus Aurelius template drifting toward generic stoicism, so the quality has to be in the generation, not the filter. The inverse holds too — the second case study ran fleets of adapter implementations against a five-method interface on whatever tier was cheap, because the compiler, the race detector, and the coverage matrix were doing the judging. *Pin: gates can judge mechanics, so mechanics can go cheap. Nothing but the model judges voice, so voice goes expensive.*

### Rule: The harness is a dependency: map its layers, keep the knowledge portable.

**Why:** Every agent harness converges on the same five surfaces — an instructions file, a memory mechanism, invokable procedures, event hooks, and a permissions config (§3 covers what belongs in each). But the names differ, the maturity differs, and teams increasingly run more than one harness against the same repo. Knowledge locked in one harness's proprietary layer is knowledge the other harness's agent doesn't have.
**How to apply:** Learn the mapping once, then file knowledge by *layer*, not by filename. As of this writing: the instructions file is `CLAUDE.md` (Claude Code), `AGENTS.md` (the emerging cross-tool convention, honored by Codex, opencode, and a growing list), `GEMINI.md`, `.cursorrules`. Procedures are "skills" or "commands" or "prompts" depending on the tool. Hooks and permission configs live in each harness's settings file. Prefer the portable homes: project facts in `AGENTS.md` (symlink or mirror the harness-specific name to it), procedures in versioned files the repo carries, scar tissue in `docs/` and retros — so the knowledge survives a harness swap the way it survives a laptop swap. Reserve harness-native layers for what genuinely needs them: hooks, permissions, per-user memory.

The test is the second harness. The day a teammate opens the repo in a different tool — or you point a new agent at an old project — everything that lived in the portable layers comes along, and everything that lived in a proprietary corner silently doesn't. The fleet (case study 6) runs this as standing practice: the durable decisions land in the instructions file and dated PRD amendments *in the repo*, and the retro directory is the transferable institutional memory. When a new instrument app spins up, its pipeline copies the last one's *"in the how-soon tradition"* — the tradition transfers because it lives in documents, not in one tool's cache. *Pin: file knowledge by layer, not by filename. The repo is the only harness everything can read.*

### Rule: Trust harness claims the way you trust "tests pass": with evidence.

**Why:** The harness is software, and software lies under load. An edit tool can report success without persisting. A CLI can return a truncated secret and exit zero. A sandbox can be unable to kill the process it spawned. A CI provider can refuse all jobs over a billing dispute the day you need to ship. §8's evidence discipline is usually aimed at the agent's claims; this rule aims it at the tooling underneath the agent.
**How to apply:** For any harness operation whose silent failure would be expensive — file writes before a deploy, secret values before an auth change, "the branch is protected," "the hook fired" — verify with an independent read: `git diff` after the edit, a length check on the secret, the API call that shows the protection object. And because the harness includes SaaS you don't control, keep a rehearsed manual fallback for every automated rail (§3): a by-hand deploy path, a tracker-independent place to persist a found bug.

The scars here are recent and specific. The fifth case study shipped route components that nothing routed to because the harness's edit tool once *reported success without persisting* — compile-green in isolation, invisible in the app. The fleet's deploy session watched `netlify env:get` return a 20-character slice of a 64-character secret, and the function correctly rejecting the garbage looked exactly like a code bug — *"tooling can hand you a truncated value and smile while it does it."* And the first case study spent an afternoon deploying by hand because its CI provider was refusing all five jobs over someone else's unpaid bill, then couldn't file the regression it had just found because the issue tracker's free tier was full — the bug got written to three tracker-independent places instead. None of these are indictments of any particular tool. They're the reason the evidence discipline extends one layer down. *Pin: the harness is part of the environment that matters. Verify it like one.*

## §3 The workspace

The workspace is the set of files and settings the agent reads before it does anything. The instructions file (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursorrules` — §2 has the full mapping; the body of this chapter says CLAUDE.md because that's what the scars were written against), memory, skills, hooks, the harness config (`settings.json` in Claude Code) — each has a specific job, and the failure mode is always the same: the wrong thing in the wrong layer, quietly rotting. §1 was how to think about the agent; §2 was how to think about the tools underneath it. This chapter is where to put the things you want it to know.

Read the workspace as the *interface* between the craftsperson and the agent elaborator. Everything you file here is an instrument for protecting craft attention from the class of interruption the file is designed to absorb. CLAUDE.md absorbs cold-start context. Memory absorbs cross-session drift. Skills absorb procedural ritual. Hooks absorb mandatory checks. `settings.json` absorbs permission questions. The failure mode of each layer is the same shape: the craftsperson starts doing the work the layer was supposed to do.

### Rule: Your pipeline is a precondition, not a feature.

**Why:** Every discipline in this playbook — verification, parallel agents, frequent commits, trust boundaries, the whole loop — silently assumes CI catches mechanical failures quickly, deploys are automated and rollbackable, health checks report real dependencies, and commits flow through the pipeline without a human babysitting each stage. When that assumption is broken, every rule in this book costs more. Worse, the human gets pulled into the mechanics layer to compensate — and the craft layer goes dark. A flaky pipeline is how the thesis gets inverted: the agent becomes the thing you baby-sit, and the human becomes the laborer. That is the failure mode the whole playbook is organized against, and it starts with the pipeline.
**How to apply:** Before adopting the disciplines in Parts II–IV, walk the companion DevOps playbook's core rules: health endpoints that report dependencies *and* the build SHA, blue-green deploys with automated rollback, lint/test/scan on every push, conventional commits, manifest-driven state ("what's in production?" should have a precise queryable answer), Docker parity between dev and prod. *(See DevOps Playbook Phases 0–4 for how to build each of these from scratch, and Phase 7 for the observability that makes the whole thing answerable.)* Every one of these is a rail that lets the agent do its job without you holding its hand through the mechanics. The operational slogan is the DevOps playbook's, and it's worth pinning above your desk next to this one: ***you are done when the pipeline is boring.*** When the pipeline is boring, the agent can ship without supervision. When the agent can ship without supervision, you can stop being the laborer and start being the artist-engineer.

The second case study is the clean positive example. Its CI pipeline was explicitly *"deferred from v0.1.0, landed in v0.2.0 where it mattered more — with six agents touching the codebase in parallel, automated gates weren't optional."* That sentence is the whole rule. Parallel agents at scale are only safe when CI is doing the reading humans can't. Build+test+vet+race detector on every push, integration tests that spin up all adapters, a coverage matrix test that pins feature coverage — those aren't decoration, they're the thing that makes seven-agents-per-release possible. When the rails are that good, the humans are free to think about *which* work to do next and *why* — which is the craft layer doing its job.

The negative example is *The Docker Port Mappings That Weren't* (Part V): 180+ passing tests, zero data races, and a container unreachable for three releases because CI tested *buildability*, not *connectivity*. Boring pipelines are specifically *not* the pipelines that are silently wrong — they're the pipelines that loudly catch the thing they were built to catch.

**Second-edition clause: every automated rail needs a rehearsed manual fallback.** The pipeline is built from SaaS you don't control, and SaaS fails at the worst moment by construction — the worst moment is when you're using it hardest. The first case study lived this in a single release: the CI provider refused all five jobs over a billing dispute two layers of vendor above the project, forcing a local fast-forward merge and a by-hand run of the deploy script; an hour later the issue tracker's free-tier cap blocked filing the regression the release had just found. Neither failure was recoverable *through* the failed service, and both had cheap fallbacks only because the deploy script could be run manually and the bug could be written to the changelog, memory, and the retro instead of the tracker. The rule: for each automated rail — CI, deploy, issue tracking, secrets management — be able to answer "how do I do this by hand today?" before the day arrives. If the answer is "I can't," the rail isn't a convenience; it's a single point of failure wearing one. *Pin: automation you can't bypass is a dependency you can't survive.*

> **Field note — case study 1:** *The pipeline as the project's most load-bearing dependency.* The CI/CD Excellence release (from the first case study) landed eighteen DevOps issues across six layers in one pass — none invented fresh, all cashed in from three retros of "we should fix this next time." That release isn't impressive because of the eighteen fixes. It's impressive because every fix moved pain earlier in the loop, where it was cheaper to pay. That is the definition of a pipeline becoming boring: the pain doesn't disappear; it just stops reaching the craftsperson.

### Rule: CLAUDE.md is for facts that don't change. Memory is for facts that do.

**Why:** CLAUDE.md is loaded every conversation. Memory is updated per conversation. A stale line in CLAUDE.md is invisible — it looks like truth forever. A stale line in memory is one update away from being fixed.
**How to apply:** Architecture, tech stack, conventions, file layout, the stable shape of the project → CLAUDE.md. Sprint state, current cycle ID, the gotcha you learned this afternoon, the user's preferences → memory.

CLAUDE.md wants to become an encyclopedia. Every project pulls the same direction: "this is important, I'll drop it in CLAUDE.md so the agent always sees it." Six months later CLAUDE.md is a 900-line landfill and the agent is reading eighty lines of v2-era minutiae on every cold start. Facts that move belong somewhere that moves. Put them in memory and they get corrected next time they're wrong. Put them in CLAUDE.md and they get cited as authoritative until someone burns an afternoon figuring out why the agent keeps insisting on the old thing.

> **Field note — case study 1:** *CLAUDE.md Gets a Haircut.* A project's CLAUDE.md had grown into a 900-line landfill — architecture next to sprint state next to gotchas next to procedures. One pruning pass sorted every line into the right layer. Sixty percent smaller, and the agent got *better* at finding things.

**A concrete example.** Here's what one of the case studies' CLAUDE.md looks like in the field — roughly sixty lines, nothing inlined that belongs anywhere else:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Status (April 2026)

**Current**: v5.11.0 — Pipeline Polish (final CI/CD closeout)
**Next**: v6.0 — deferred; next cycle is feature work
**Live**: https://example.app

For version history, see CHANGELOG.md.
For the complete product requirements, see docs/PRD.md.

## Technical Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy 2.0 + Pydantic v2 + PostgreSQL 15+ + Redis 7
- **Observability**: Prometheus + Grafana + Sentry
- **Infrastructure**: Docker + Docker Compose + Alpine + Nginx
- **CI/CD**: GitHub Actions (9 jobs, BuildKit GHA cache) + release-please + SSH blue-green deploy with smoke tests and auto-rollback

## Essential Commands

(docker compose up/down, pytest, alembic, deploy — the short list, not a manual)

## Key Architecture Decisions

- **Anonymous by design** — no user accounts; three-word phrases are the only access credential.
- **Backend layers**: Routes (thin) → Services (business logic) → Repository (data access) → DB.
- **Frontend layers**: Pages (thin renderers) → Domain hooks → Foundation hooks → API service.
- **Security**: 4-layer defense (nginx → API auth → abuse detection → DB protection).
- **Deploy**: Blue-green via deploy-bluegreen.sh — builds, health-checks, smoke-tests, flips nginx upstream, post-flip verification with auto-rollback.
- **Release flow**: Conventional commits → release-please opens Release PR → merge → GitHub Release → deploy triggers.

## Agent Usage Guidelines

**Frontend** (use `ux-frontend-expert`): React components, UI/UX, design system, accessibility.
**Backend & Infra** (use `general-purpose`): API, security, database, deployment, testing.

## Task Tracking (Linear)

Project tracked in Linear with a short team key (e.g., `ABC`).

- **Sprint**: check CURRENT_SPRINT.md (auto-generated)
- **Commits**: `git commit -m "feat: add fuzzy search (ABC-42)"`
- **Branches**: `feat/ABC-42-fuzzy-search` or `fix/ABC-5-rate-limit-og`
```

What makes this work: a status block at the top so every cold start knows where the project is *today*; architecture decisions stated as bullets, not prose; essential commands as a terse list, not a manual; explicit agent routing so the harness picks the right specialist; and every detail-heavy thing (changelog, PRD, sprint state) pushed out to a linked doc instead of inlined. Anything that would move week-to-week lives somewhere else.

**And for contrast, what the same file looked like when it went bad.** A real excerpt from the pre-haircut version, anonymized:

```markdown
## Important Procedures

When starting a new feature, first check CURRENT_SPRINT.md to see the active
sprint ID, then review the last three retros in docs/retros/ for any open
action items, then grep the codebase for TODO comments tagged with the sprint
ID, then run `make sprint-refresh` to update the local task list, then open
the relevant Linear ticket and cross-reference acceptance criteria against
the PRD, then…

## Gotchas

- Remember that the admin router is at routes/admin.py and also at
  routes/v2/admin.py (legacy); edits usually need both.
- The audit middleware is registered in main.py but conditionally disabled
  in test mode; check config.TESTING before adding new middleware.
- Always run `pytest -k "not slow"` locally; the full suite takes 45 minutes.
- Never commit without running pre-commit, even though pre-commit is in the
  hook config (sometimes it doesn't fire).
```

Every line here is wrong-layer: the procedure is a skill hiding as a paragraph; the "admin is in two places" and "middleware wiring" gotchas belong in the code itself (one grep away); "run pytest -k" is atmosphere the agent will ignore; the pre-commit note admits the harness config is broken and asks the agent to compensate. Forty lines of this and the agent is reading more CLAUDE.md than code.

**The layers, laid out.** The workspace isn't one file — it's five surfaces, each catching a different class of thing. Here's what goes where:

| File / Surface | What it's for | How often it changes | Examples |
|---|---|---|---|
| **CLAUDE.md** | Stable project facts the agent needs on every cold start | Rarely — monthly at most | Tech stack, architecture layers, agent routing, essential commands |
| **Memory** | Live state, corrections, preferences, anything that moves | Per conversation | Current sprint ID, "next time, please…" corrections, user preferences |
| **Skills** | Procedures you want *executed*, not remembered | When the procedure itself changes | Release flow, retro writing, deploy, sprint refresh |
| **Hooks** | Non-negotiables the harness enforces without asking | When the rule changes | Sound notifications, pre-commit checks, format-on-save |
| **settings.json** | What the agent *can* do — permissions, tool access, MCP servers | When tooling changes | Allowed-tool lists, hook registrations, permission modes |

Each row is a layer; the failure mode is always *the wrong thing in the wrong row*. Write a procedure as a CLAUDE.md paragraph and the agent will read it and skip it. Write a permission rule in CLAUDE.md instead of `settings.json` and the agent will reinterpret it under pressure. Put live state in CLAUDE.md and it rots invisibly.

### Rule: Skills are for procedures. CLAUDE.md is for facts.

**Why:** A multi-step procedure buried in CLAUDE.md is ambient noise — the agent reads it, then doesn't follow it, because it wasn't invoked. Skills are executed on purpose, step by step. CLAUDE.md is atmosphere. Skills are action.
**How to apply:** If you find yourself writing "always do X when Y" in CLAUDE.md more than twice, stop and promote it to a skill. Release flow, deploy flow, retro writing, sprint refresh — all skill material.

The tell is a CLAUDE.md section that starts with "when you …" and ends with a numbered list. That's a runbook hiding in the wrong layer. You want the agent to *follow* a runbook, not vaguely remember it existed. Version-sync is the cleanest example: one `VERSION` file, one `scripts/sync-version.py`, one step in the release skill that calls them. No CLAUDE.md paragraph telling the agent "remember to update the footer." The script updates the footer. The skill runs the script. The fact — "version lives in VERSION" — is one line.

> **Field note — case study 1:** *The VERSION System.* Version strings had been scattered across a footer, a package manifest, a Python constant, a Docker label, a changelog line. Every release someone forgot one. The fix was one `VERSION` file, one sync script, one step in the release skill. No CLAUDE.md paragraph telling the agent "remember to update the footer." The script updates the footer.

### Rule: Hooks make automation non-negotiable.

**Why:** Anything you ask the agent to "remember to do" will fail at least once. A hook is the harness doing it, which means it happens whether the agent is paying attention or not.
**How to apply:** Sound notifications, pre-commit checks, format-on-save, status-line updates, post-response cleanup — these are hook material, not prompt material. If the rule is "this must happen every time," the harness must be the thing that makes it happen.

"Remember to X" is the prompt-engineer's cope. It works until it doesn't, and you won't notice when it doesn't, because the agent will confidently proceed as if it did. Hooks take the choice out of the loop. Our sound notification isn't in CLAUDE.md because it was in CLAUDE.md for a while and kept getting skipped. It's a hook now. It fires every time.

> **Field note — case study 1:** *The Great Script Purge.* Deploy had accumulated into a scattering of one-off shell steps the on-call engineer was expected to remember in order. Consolidating them into one canonical script was the same move at a different layer: stop trusting memory, make the system do it. Sound notifications went the same way — lived in CLAUDE.md, got skipped, finally became a hook.

### Rule: `settings.json` configures the harness. CLAUDE.md configures the agent. They are different layers.

**Why:** Settings determine what the agent *can* do. CLAUDE.md tells it what it *should* do. Mix them and you end up with behavioral rules the harness can't enforce and permission rules the agent can't read.
**How to apply:** Permission modes, allowed-tool lists, hook registrations, MCP server config → `settings.json`. Project context, conventions, behavioral norms → CLAUDE.md.

The mistake looks like this: you write "never run `git push --force`" in CLAUDE.md and think you're done. You're not. CLAUDE.md is a suggestion the agent is free to reinterpret under pressure. If you actually don't want that command to run, exclude it at the harness layer, where "can't" is enforced by the tool, not by politeness. The reverse error is putting project context in `settings.json` — nobody reads it there, and the agent can't. Two layers, two jobs.

## §4 The first conversation

The first ten messages decide the rest of the conversation. The agent is calibrating from whatever you hand it — your tone, your files, your corrections, your omissions — and it calibrates fast. Get the first exchanges right and the session stays on rails for hours. Get them wrong and you'll spend the next fifty messages quietly fighting drift you seeded yourself.

### Rule: Bootstrap with the smallest context that contains the answer.

**Why:** Dumping the whole repo into the window is wasteful and, worse, dilutes the signal the agent most needs. Token budget is attention budget.
**How to apply:** Hand the agent the load-bearing files — CLAUDE.md or the relevant doc, the file you're editing, the test that pins its behavior. Let it pull more if it asks. Don't preload "just in case."

The instinct is to be generous: more context, more files, more background, surely that helps. It doesn't. A fresh agent reading eighty files skims all of them and remembers none. A fresh agent reading three files — the doc that tells it what "done" means, the file it's changing, the test it has to keep green — goes straight to the work. The God Module refactor (full story in Part V) was the release that made this concrete. Before the refactor, one admin module was 1,052 lines; any question about admin behavior meant loading the whole thing. After the split into five focused files, a subagent could be briefed on the sixty lines that mattered. The smaller workspace wasn't a cleanup — it was a briefing tool. Architecture is context design.

> **Field note — case study 1:** *God modules tell new readers nothing.* A 1,052-line admin router held auth, records, stats, audit, and user management in one file. Any question about admin behavior meant loading the whole thing. Splitting it into five focused modules wasn't an aesthetic cleanup — it was making the workspace *briefable*. After the split, a subagent could receive sixty lines of context instead of a thousand.

### Rule: Correct drift in message 2, not message 50.

**Why:** Corrections early are cheap. Corrections late are expensive, and by then the agent has built ten turns of work on top of the thing you should have caught. Drift compounds.
**How to apply:** The moment the agent does something you don't want — naming, tone, pattern, where it put the file — stop and say so. Then ask whether the correction should become a memory entry so the next conversation starts already corrected.

The trap is politeness. The agent produces something 80% right and you think "close enough, I'll nudge it on the next turn." You won't. You'll accept the 80%, and on turn three you'll accept another 80% of *that*, and by turn ten you're reviewing a PR that's drifted in four directions at once. Early corrections are nearly free — one sentence, a re-run, done. The cost curve is brutal and it's worth burning a turn to stay on the early end of it. If you find yourself saying "next time, please…" — that's the memory entry. Write it down now. Half of what ends up in a bloated CLAUDE.md was originally a late-message nudge nobody wrote down when it was cheap.

**Second-edition sharpening: the highest-leverage corrections are conceptual reframings, not code corrections.** The fifth case study's retros tallied the corrections that mattered, and the pattern is striking: the ones that saved whole releases were single sentences that reframed the *problem*, not fixes to the diff. Mid-brainstorm: "this should be happy *and* heavy anticipation, not a `bright_day` register" — *"the pivot cost maybe ten minutes of brainstorming and saved a release's worth of wrong abstraction."* Mid-fix: "this feels like it should have an anticipation aspect" — the entry was future-tense, the ticket's diagnosis was wrong, and *"Seth's one sentence of feedback saved us a release."* Mid-debug: "I think the logic is right; I think we need to fix the debug page so it ignores the anti-repeat logic" — a sentence *"which, once spoken, reads as obvious, and which we hadn't quite said until the user said it."* Watch for the moment where your discomfort is with the framing rather than the code. That's the correction to make loudly and immediately, because everything downstream is built on the frame. *Pin: correct the frame in one sentence now, or correct the code in one release later.*

### Rule: If the agent doesn't know something, tell it. Don't let it guess.

**Why:** Hallucination is most likely when the agent is confidently filling a gap. "It should know that" is the engineer's fault, not the agent's — the agent only knows what's in the window.
**How to apply:** Any time you catch yourself thinking "well it should know" — stop and write it down. Feed it in. Then put it in CLAUDE.md or memory so the next session starts with it.

*Trust Your Local Tests* (full story in §12 and Part V) is the clearest version of this rule. Months of accumulated fear about ripping SQLite out of the backend test suite — and the move that made it tractable wasn't cleverness, it was finally *telling the agent* what "local green" was supposed to mean. Postgres only. Shared engine, per-test truncation. No SQLite branches anywhere in the bootstrap. Once that working agreement was written down and loaded into context, the removal was one afternoon. The fear had been doing the debt's work for it. The slogan exists because the team finally named the lesson out loud and handed it to the next conversation.

### Rule: Make the agent tell you what it thinks you're building — then grill it.

**Why:** The previous three rules cover getting facts *into* the agent. This one covers getting the agent's model of the product *out*, where you can inspect it — because the agent will otherwise carry a confident, plausible, subtly wrong picture of what the project is *for*, and every plan it writes will be optimized toward that wrong picture. You cannot derive the value proposition from a type definition. The agent has to ask; better, you make it answer.
**How to apply:** Before architecture, at project start and at every major re-scope, ask the agent directly: "Do you fully understand what we are building here?" Make it answer in its own words, at increasing depth, and correct what comes back. Then invert it — "anything you want to grill me on?" — and answer honestly. Budget an hour. The corrections at this stage cost one sentence each; the same corrections at message 50 cost a re-prioritized roadmap.

The sixth case study's health-instrument app ran this as a formal elicitation session before a line of code existed, and the transcript is the best argument for the rule. Asked to state what the product was, the agent confidently named the daily persona voice as the heart of the app. It was wrong — the heart was the long-view synthesis feature, the thing everything else existed to feed. *"The cost of being wrong was one sentence of correction. The cost of being wrong in message 50 would have been a re-prioritized roadmap and a sulk."* The same session caught the agent's proposed success metric — "you use it daily, unbroken" — as *"a streak in a trenchcoat"*: the exact engagement mechanic the product's ethos forbade, smuggled into the meta-layer by an agent pattern-matching on what success metrics usually look like. Both catches happened because the human made the agent *say its model out loud* while saying it was still cheap. The product's four-word design ethos — the kind of sentence that vetoes eight specs — came out of the grilling, not out of any document the agent could have read. *Pin: the agent's picture of your product is a guess until you've heard it recited and corrected it out loud.*

## §5 The loop

Every chapter after this one refers back to "the loop." The loop is **explore → brainstorm → plan → TDD → verify → commit → retro**, and it's the hub the rest of the playbook hangs off of. (The first edition's loop had six words; the second edition adds *explore* at the front — the evidence for why is the first rule below.) Memory (§6) is what you prune between loops. Skills (§7) are what you promote out of loops that kept repeating. Verification (§8) is a step in the loop. Retros (§16) are the step that teaches the next one. Remember the seven words in order — each one catches a class of failure the others can't.

### Rule: Explore before you plan. The plan is not the codebase.

**Why:** A plan is written from a *picture* of the codebase, and the picture is stale the moment it's formed — features quietly shipped in earlier releases, test files that already exist with their own conventions, schema fields named differently than the spec remembers. Ten minutes of reading reality deletes hours of planning against a memory of it. And exploration has a second yield the plan can't predict: it finds the bugs nobody filed.
**How to apply:** Before writing any plan, run the cheap reads: grep for the feature you're about to build, list the directory you're about to add to, check the migration state, open the schema. For release-scale work, dispatch a survey agent whose only job is to read the relevant surface and report what's actually there. Feed the findings into the brainstorm. If the exploration contradicts the spec or the ticket, the exploration wins — go update the spec.

The first case study's v6.0 waves made this a standing step, and the numbers sell it. Wave 1's first three commands — a grep, a migration-state check, an `ls` — took ten minutes and deleted sixty minutes of plan: five of the ticket's acceptance criteria had quietly shipped two versions earlier, and a twenty-task plan collapsed to five. The retro's line became the rule's name: *"The plan is not the codebase. The codebase knows things the plan doesn't."* Wave 2's survey agent flagged, almost as an aside, that nginx was blocking social-media crawlers by default — four curls confirmed that every shared link's preview image had been silently broken for three releases, and the release's most valuable fix was one nobody had asked for. Broken share previews don't generate bug reports; *"the silence is the symptom."* Exploration is the only loop step that can hear that kind of silence. *Pin: run the greps before you believe the plan. Ten minutes of reading reality is the cheapest step in the loop.*

### Rule: Run the whole loop. Skip a step out loud or pay for it silently.

**Why:** Each step catches a different class of failure. Exploration catches plans built on a stale picture of the codebase. Brainstorming catches scope drift. Planning catches missing files. TDD catches wrong implementation. Verification catches "tests green, feature broken." Commit creates a rollback point. Retro catches the mistake you're about to repeat. Skip one and the class of bug it would have caught reappears later wearing a different hat.
**How to apply:** Run all seven for every non-trivial task. If you're going to skip one, say which one and why — "I'm skipping TDD because this is a doc-only change" is fine. Silently skipping it is how you get surprise regressions on Thursday.

The temptation is always to compress. Plan-and-code. Code-and-ship. You tell yourself the loop is overhead for small work. It isn't — it's the harness that keeps small work small. v4.0.0 shipped with what the retro later called the Onion: six layers of CI failure, peeled one at a time over a week. Every layer was a step of the loop we'd quietly short-circuited on an earlier release. No plan meant no file map meant a test we didn't know existed. No verification in the right environment meant "green locally" meant nothing. No retro meant the previous onion's lessons never made it into the next loop. CI failure isn't an interruption — it's the loop telling you which step you skipped.

> **Field note — case study 1:** *The Onion: Six Layers of CI Failure.* One release shipped with six layers of CI failure peeled one at a time over a week. Every layer was a step of the loop we'd quietly short-circuited on an earlier release — no plan meant no file map meant a test we didn't know existed; no verification in the right environment meant "green locally" meant nothing; no retro meant the previous onion's lessons never made it into the next loop. CI failure isn't an interruption — it's the loop telling you which step you skipped.

### Rule: Brainstorm before planning. Plan before code.

**Why:** A plan written from a vague idea is a wish list. Code written from a vague plan is a mess you have to rewrite. The brainstorm is where scope gets named; the plan is where scope gets bounded; the code is what executes inside those bounds. Out of order, the bounds are hallucinated.
**How to apply:** Even for a one-day task, brainstorm first. Fifteen minutes. Articulate what you actually want, what you've ruled out, what "done" looks like. Then plan. Then code. The cost is a coffee. The payoff is not rewriting the thing on Thursday. *Qualifier:* the brainstorm can amortize across multiple cycles when the work is repetitive and the upfront thinking was rigorous. The second case study brainstormed *once*, into a PRD with more than a hundred items across ten releases, and then each release went straight to plan → execute → validate → retro. That's not skipping the brainstorm — it's reusing the one you already did. The test is whether the current cycle's decisions are actually pinned by the earlier brainstorm or are quietly being reinvented each release. If reinvention is happening, the brainstorm is stale; redo it at the current scope.

The Four Scoping Gaps story is the canonical version of this mistake and we shipped it with our eyes open *(full catalog in Part V)*. "Add one line to the release-automation config and flip one checkbox" — five-minute fix, no brainstorm required. We merged it. It didn't work. Diagnosis surfaced four separate scoping gaps, each plausible in isolation. A fifteen-minute brainstorm would have surfaced every one by asking the only question that mattered: *what exactly does this tool read, and from where?* We skipped the brainstorm because the plan felt obvious. A plan that feels obvious is a plan you haven't pressure-tested.

### Rule: Frequent commits are not optional.

**Why:** Agents introduce subtle bugs across many files at once. Bisecting works only if the commits are small enough to bisect against. One giant commit is an unbisectable wall — you'll revert the whole thing or keep the whole thing, and neither is the fix you wanted.
**How to apply:** One logical change, one commit. If you can't summarize the diff in one sentence, split it. Commit before the reviewer asks, not after. The loop has "commit" as a step for a reason — it's the rollback point, not a formality. *Precondition:* this rule depends on CI validating each commit quickly. A pipeline that takes forty minutes per push inverts the rule — the cadence collapses to whatever the pipeline will tolerate, and the agent starts batching changes to amortize the wait. Fast commits are a property of a boring pipeline, not of discipline. See §3's pipeline-as-precondition rule: if the rail isn't fast enough to support frequent commits, fix the rail first.

The Three-Deploys-to-Green release took three deploys to go green, and the only reason it was three and not three weeks was that every fix was its own small commit. Layer by layer: a missing env-file flag on a compose call, a self-updating deploy script that had to be hand-pulled once to fix itself, a long-abandoned Python dependency finally caving to a new version of the thing underneath it. Each was a separate diff, so each could be reverted independently when the next layer turned out to need the previous fix plus something else. If those had been one "deploy hotfix" commit, we'd have spent the same week untangling which change broke which other thing. Small commits are how you debug in the dark.

> **Field note — case study 1:** *Three Deploys to Green.* The first end-to-end successful deploy took three tries, each uncovering a layer the previous fix had been sitting on top of. A missing compose flag hid a self-modifying deploy script that hid an abandoned Python dependency. Because every fix was its own commit, each layer was reversible when it turned out to need help from the one underneath. One "deploy hotfix" mega-commit would have turned a week of triage into a month.

### Rule: Retros feed the next loop.

**Why:** The lesson learned in retro N becomes the rule applied in loop N+1. Without retros, the loop forgets — and a loop with no memory is just a hamster wheel that happens to compile.
**How to apply:** A retro is mandatory at the end of every release. It doesn't have to be long. It has to be honest. Name what broke, name what you'll do differently, and — this is the load-bearing part — actually do it differently next loop.

The CI/CD Excellence release is what happens when retros are taken seriously. It wasn't a feature release — it was an eighteen-issue CI/CD pass across six layers, and every issue traced back to a line in a previous retro that said "we should fix this next time." BuildKit caching, pip-audit, blue-green smoke tests with auto-rollback, release-please automation, Slack Block Kit — none of it was invented in that release. All of it was cashed in. The line the retro kept coming back to was "each safety gate turns production risk into dev friction" — which is what retros do in aggregate. They move the pain earlier in the loop, where it's cheaper to pay. That move only happens if someone wrote the pain down last time. Skip the retro and next loop starts from zero.

> **Field note — case study 1:** *CI/CD Pipeline Excellence, cashed in from three retros of notes.* Eighteen issues across six layers — none of them invented fresh, all of them traced back to retro lines from earlier releases that said "we should fix this next time." The retros were the ledger. The release was the settlement.

### Rule: Cycles nest. Each level needs a theme, a boundary, and all three phases.

**Why:** A loop at the wrong scale is either too small to ship anything meaningful or too big to retro honestly. And at every scale, an upfront plan, an execution phase, and a validation phase all have to be present — compress any one of them and the cycle stops being legible. A cycle without a theme gets named by its date and forgotten. A cycle without a shippable boundary can't have a retro because you can't tell what "done" looked like. A cycle without explicit validation ships vibes.
**How to apply:** The task-level loop is §5 as written — brainstorm, plan, TDD, verify, commit, retro. The release-level loop is the same shape on a larger canvas: a themed slice of the roadmap, an upfront plan (often a file map for parallel work), execution (often in waves), validation in the environment that matters, and a retro written in voice with a nickname. The project level is the same again: a PRD that sets the arc, a roadmap, a final retro. Each level needs a name you could say in one sentence and a boundary someone outside the work would recognize as shippable.

The second case study is the exemplar. Nine releases, each a themed slice of the same PRD, each with a clean boundary, each with a retro that reads like a story — every release title a thesis, every thesis a cycle you could retro honestly. The themes *are* what made the retros writable — a named theme wants to be a story; "Sprint 23" doesn't — and the retros are what made each next release plannable, because the lesson from one cycle became the opening move of the next. The wave pattern from an early release ("trivial work first, to shake out the build/config/test harness before committing agents to heavyweight implementations") became standard practice for every release after it. That transfer only happens if the cycle had a name worth remembering.

The negative example is the Onion release from the first case study — six layers of CI failure peeled one at a time over a week, with no theme, no single thing you could name the cycle for. *That* is why the layers were able to hide inside one release: the cycle had no shape, so nothing about the retro-able boundary forced the hidden work out into the open. Themed cycles aren't a ceremony; they're how the work becomes legible enough to improve.

> **Field note — case study 1:** *Nine retros that taught the tenth.* The second case study's retro practice is the proof of concept for this rule. Each release was themed; each theme was one sentence; each retro had a "what we learned" section that became the next release's plan. By release nine, the wave pattern, the zero-dependency posture, the merge-point discipline, and the descoping rules were all things the team had written down *to themselves* in earlier retros and then honored in the next cycle. The cycles nested because each level had a theme, a boundary, and a lesson worth carrying forward. *Pin: name the cycle before you start it; retro it the moment it closes.*


---

# Part II — Working Together

## §6 Memory hygiene

Part I was how to start the first conversation. Part II is how the partnership survives more than one. Memory is the first chapter because it's the persistence layer — what makes §5's loop stick from Tuesday to Thursday. Get it right and next week's agent shows up already knowing the scars. Get it wrong and every Monday is a cold start with confident wrong answers.

### Rule: Memory has four types. Use the right one or it rots.

**Why:** User facts, feedback, project state, and reference pointers have different staleness profiles. Mixing them produces a junk drawer where nothing is trusted because some of it is always wrong.
**How to apply:** User preferences → user memory. Corrections from past conversations → feedback memory. Sprint cycle, current version, live project state → project memory. Pointers to Linear, a retro, an external doc → reference memory. Write the type at the top of every memory file so the next reader knows what they're looking at.

The failure mode is one big memory file holding "the user prefers parallel agents" two lines above "current sprint cycle ID is 3827cdb9" two lines above "always run the notification sound after tasks." Three half-lives, one file, no cleanup schedule. The preference is good for years. The cycle ID is stale in six weeks. The sound-notification rule belongs in the harness config, not memory at all. When a file mixes all three, nobody prunes it — pruning means re-reading everything to decide what's still true, and nobody has the afternoon. Separate the types and each gets its own small, obvious pass.

> **Field note — case study 1:** *CLAUDE.md Gets a Haircut, the four-way sort.* The 60% pruning pass turned out to be a sort operation in disguise: stable facts to topic files, live state to memory, procedures to skills, permissions to harness config. Every line in the old file belonged in exactly one of those four places. The reason the file had grown so large was that nobody had ever been forced to decide which one.

### Rule: Stale memory is worse than no memory.

**Why:** An agent with no memory asks. An agent with stale memory acts — confidently, on last quarter's facts, with no tell that anything's wrong. The lookup the first agent would do is the lookup the second one skips.
**How to apply:** When you read a memory line and it's wrong, fix or delete it in the same turn. Not "I'll clean that up later." Later is the bug. Budget a memory pass at the end of every release, with a bias toward deletion.

The Four Scoping Gaps story is the canonical version and it cost us rounds *(see Part V)*. A memory line from the previous release said the release-automation tool handled downstream workflow triggering. By the next release we knew better — that tool plus the default workflow token doesn't trigger downstream workflows at all — but nobody had gone back to fix the note. A subagent picked up a release task, read the memory, acted on it, and we burned a round on "why didn't deploy fire?" before someone remembered the note was already wrong. No memory would have forced a fresh doc check. Stale memory hid the check behind a sentence that looked authoritative. Cheap to fix when you notice; expensive every round after.

### Rule: A belief you've never probed is a hypothesis, not a memory.

**Why:** Stale memory (above) is a fact that *was* true and stopped. This failure is worse: a fact that was *never* true and got written down anyway, then repeated by every layer that reads it. Memory, the instructions file, and PR descriptions will all confidently restate a belief forever, because nothing in the loop ever tests beliefs — verification tests *changes*. Beliefs about infrastructure — branch protection, backup tiers, monitoring, permissions — are the most dangerous kind, because their whole job is to matter only on the day something else goes wrong.
**How to apply:** For any memory line that asserts a *protection or property of the world* rather than a decision you made, attach the probe: the command whose output proves it. Run the probe when the line is written and again at audit time (§15). If a belief has no cheap probe, mark it explicitly as unverified — an honest "we think" outperforms a false "it is."

*The Lock That Wasn't* (Part V) is the scar. The fifth case study's instructions file, its auto-memory, and weeks of PR descriptions all stated that the main branch was protected. One API call — the first anyone had ever made — returned `404: Branch not protected`. *"Both were lying. Not maliciously. Just confidently. For weeks."* The gate had appeared to be doing its job because no one had tested whether the gate existed; every un-reviewed commit that "couldn't happen" simply hadn't happened *yet*. The fix took two minutes. The lesson took a rule: auto-memory and instructions files are amplifiers — they repeat what they're given with perfect confidence, and only a command output ever breaks the loop. (The strange small joy from the retro: after the protection was actually enabled, *"the auto-memory was not corrected. It is now correct without modification."*) *Pin: memory asserts; probes verify. A protection you've never tested is a sentence, not a protection.*

### Rule: Save the why, not just the rule.

**Why:** A year from now, "always use X" is unfollowable when X conflicts with the new architecture. "Always use X because Y bit us in v4.0" lets future-you decide whether the rule still applies or whether the world moved on.
**How to apply:** Every feedback memory needs a **Why** line and a **How to apply** line. Always. If you can't write the why, you don't understand the rule well enough to save it — find the scar before you file the note.

Context-free rules become dogma. *The Cache That Lied In CI* (Part V) is the example. The rule "use `.model_dump(mode='json')` before caching Pydantic models" was written down; the *why* was not. Months later a new agent reached for `json.dumps(model, default=str)` because it looked equivalent — and the image-generation pipeline broke in CI while passing locally. With the why attached ("because `default=str` calls `str()` and produces a repr, not a dict"), the next person knows which footgun the rule is aimed at. Without it, you're carrying a superstition with no target.

### Rule: Don't memorize what the code already says.

**Why:** File paths, function names, module boundaries, route registrations — all one `grep` away. Memory is for what's *outside* the repo: preferences, corrections, live state, cross-system gotchas. Duplicating what the code says is how memory silently disagrees with reality the moment someone renames a file.
**How to apply:** If you can find it with one grep, don't put it in memory. If it lives in `git log`, don't put it in memory. If a test asserts it, double-don't — the test is already the source of truth, and the memory line will drift out from under it.

The CLAUDE.md haircut is this rule enforced at scale. The file had grown to hundreds of lines restating what the code already made obvious: the directory tree, every endpoint path, which file held the admin router, how the audit middleware was wired. All of it was `ls` and `grep` away. We deleted it in one pass and the agent got *better* at finding things — because now when it needed a fact it read the code instead of trusting a note that had been quietly wrong for a month. Work got *faster* after the cut, not slower: a stale 900-line preamble is both less reliable and more expensive than an empty CLAUDE.md that forces the agent to read the code. Memory carries what the code can't tell you. Everything else is load the code can carry itself.

### Rule: File your neighbor's scars, keyed to the trigger that will make them yours.

**Why:** When you run more than one project, the most valuable memory entries are often about bugs that *haven't happened to you yet* — they happened one repo over, and the only reason they'll happen to you later is a trigger you can name right now: a dependency bump, a platform migration, a copied config. A scar filed with its trigger converts a future debugging session into instant recognition. A scar filed without one is trivia.
**How to apply:** When a sibling project hits a bug whose cause you share (same dependency, same platform, same pattern), write the memory entry *in your own project's terms*: the trigger ("when we next bump `X` past version Y"), the symptom ("deploy 502s at import time"), and the cure (the polyfill, the pin, the flag). Cross-project memory is also how a *fleet* learns — the instructions files of new projects should inherit the scars of old ones, the same way their pipelines inherit the Dockerfiles.

The sixth case study is a fleet of small apps sharing a platform, and its retros show the mechanism firing in both directions inside one week. A sibling app's deploy 502'd because a newer client library demanded a WebSocket global that the platform's Node runtime didn't provide; the fleet's own lockfile happened to pin an older version, so the bug was theoretical — and it was filed anyway, keyed to the future dependency bump. Two days later a *third* app, pinning the newer version, hit it live, and the fix was retrieved rather than rediscovered: *"the bug that was theoretical for us was load-bearing for them… we imported the cure with the disease."* The same corpus shows the payoff of inherited scars: a platform's build-time env-var baking was *"a trap we'd already been burned by once on the other project and got to recognize on sight this time."* Recognition-on-sight is what a memory system is *for* — and it works across repo boundaries exactly as well as you file across them. *Pin: a neighbor's bug plus a named trigger is your cheapest future fix. File it before it's yours.*

## §7 Skills as institutional knowledge

§6 was about pruning what you remember. This chapter is about what you shouldn't trust yourself to remember at all. A **skill** is a procedure with discipline: invoked on purpose, executed step by step. A **CLAUDE.md note** is a fact you hope gets followed. Only one of those is load-bearing when you're tired. *Skills are followed; notes are remembered — and the second one is a lie.*

### Rule: Skills are procedures with discipline. CLAUDE.md notes are facts you hope get followed.

**Why:** Invoking a skill is a deliberate act — the agent opens it, reads the steps, runs them. Reading CLAUDE.md is passive ambient context, absorbed on cold start and then competing with everything else in the window. The difference is whether a step happens because the harness made it happen or because the agent felt like it this turn.
**How to apply:** If a procedure has more than three steps and matters, write it as a skill. If it has three or fewer and matters, write it as a skill anyway. The threshold isn't length — it's whether you want it *executed* or merely *recalled*.

The tell is the CLAUDE.md paragraph that starts "remember to also…" The agent doesn't *remember*; it re-reads on cold start and decides, turn by turn, which lines are relevant. Anything that must happen reliably needs a host other than the agent's attention. Release flow is the canonical case: a CLAUDE.md line notes where version lives, and a release skill runs the sync script, drafts the retro, walks the deploy. Note is atmosphere; skill is action. When we confused the two in the Four Scoping Gaps release — treating "the release-automation tool handles downstream triggering" as a remembered fact rather than a procedure step — we burned a round on a Release PR that merged cleanly and triggered nothing. *Pin: if you want it done, skill it. A note is optional.*

### Rule: Rigid skills exist for a reason. Don't adapt the discipline away.

**Why:** TDD, systematic debugging, brainstorming-before-planning — these skills are rigid because the failure mode they prevent *is the failure to follow them*. They feel like overkill in exactly the moments they're needed most, because the same thing that makes them feel unnecessary — "the problem looks simple" — is why you're about to skip them. Simple problems are where rigid skills earn their keep.
**How to apply:** Follow rigid skills exactly, especially when you're sure you don't need to. Six steps means run six. If you genuinely skip one, skip it *out loud* — same rule as §5's loop.

The Four Scoping Gaps release is the version of this lesson I'd like to forget *(see Part V)*. The brainstorm skill would have forced us to ask *what exactly does this tool read, and from where?* before we wrote a line of config. We skipped it because the fix was "obvious": add one config line, flip a checkbox, done. It turned out to be four fixes in a trench coat. A fifteen-minute brainstorm catches all four. We skipped it because we were sure we didn't need to. *Pin: when the rigid skill feels like overkill, run it twice.*

### Rule: Write a skill after the third correction.

**Why:** The first correction is a one-off. The second is a pattern. The third is the moment "I keep saying this" becomes "the system should enforce this." Promoting earlier wastes a skill slot on a fluke; promoting later means you've spent a week re-typing the same sentence. Three is the elbow of the curve.
**How to apply:** Track your corrections. When you catch yourself writing the same nudge a third time, promote it — not to a CLAUDE.md paragraph, which is back to passive notes, but to an actual skill or a harness hook. The goal is to stop needing the correction at all.

*Trust Your Local Tests* (§12, Part V) is this rule made visible. Three releases of typing the same correction into fresh subagent conversations — "Postgres only, no SQLite branches, trust your local tests" — until the fix stopped being a prompt and became a piece of infrastructure: the SQLite branch ripped out of the bootstrap, fixtures wired to a shared Postgres engine with per-test truncation, the agreement baked into the code. The correction became structurally unnecessary. Third time you correct the agent the same way, the system should change, not the prompt. *Pin: count your corrections. Three is the promotion line.*

**Counter-case — when not to promote.** Promotion has a cost: a shared abstraction is code that every consumer becomes coupled to, and abstractions over code that isn't *actually* duplicated yet are worse than the duplication they claim to fix. The second case study hit this explicitly. When a later release added a second consumer of a binary-encoding helper, the plan called for ~200 lines of helpers copy-pasted from the existing caller — because the only other caller was one directory over, the helpers were small and stable, and a shared package would have forced both consumers into the same abstraction at exactly the moment the second one was still finding its shape. The retro named it directly: *"decided the duplication was less disruptive than the abstraction. Ask us again in a year."*

The fourth case study has both halves of this story, paired across two releases. **Extract worked when the pattern was stable:** one release had 825 lines of duplicated edge function boilerplate across 15 functions — CORS handling, auth checks, rate limiting, error shaping, response formatting, all repeated 15 times with subtle differences. The pattern was *stable* across all 15 callers; nobody was inventing new variants. Extracting it into a 139-line shared handler pipeline was a clean win and immediately caught two functions that had silently *omitted* a step the pattern guaranteed. **Failure-to-extract bit them when the duplicates drifted:** the same project let a small `naivePlural()` helper get duplicated across three different edge functions instead of extracting it. By the next release, one of the three copies had incomplete irregular-noun handling — missing `tooth`, `goose`, `child`, `person` — so the same input produced *different* outputs depending on which function rendered it. The user-visible bug was "1 mouse" rendering as "1 mice" on one path and "1 mouses" on another; the root cause was three copies that had drifted apart while nobody was looking.

The rule for promotion isn't "count to three and extract" — it's *"count to three and then check whether the abstraction is cheaper than the duplication for the shape the code is in right now, and whether the duplicates will drift if you don't."* Sometimes the third correction is a skill. Sometimes the third copy is still cheaper than the shared thing. Sometimes the third copy is *already drifting* and you should have extracted at the second. The test has two parts: (1) is the duplicated logic still *finding its shape* (duplicate is fine) or has it *stabilized across callers* (extract); and (2) are the copies drifting silently from each other (extract regardless of stability — drift is the more dangerous failure). *Pin: promotion is a bet that the pattern has stabilized. Don't make the bet until it has — but don't refuse the bet so long that the duplicates start lying to each other.*

### Rule: Ship the cheap defense now; schedule the clean refactor for a quiet phase.

**Why:** When you find a drift-prone seam — two representations of the same thing that must be updated in lockstep, a convention only vigilance enforces — there are two honest fixes and one dishonest non-fix. The clean structural fix is right but expensive, and doing it *while another task is urgent* means doing it badly. Ignoring the seam is free today and a production bug later. The move the retros validate is the third: an eight-line warning comment or guard *now*, and the structural fix scheduled — actually scheduled — for the next quiet phase.
**How to apply:** When you spot the seam, ship the cheapest thing that will stop the *next* person (human or agent) from stepping in it: a loud comment at both sites naming the coupling, a lint rule, an assertion. File the structural fix with enough context to execute cold. Then, in the next maintenance-themed cycle, actually do it. The cheap defense is a bridge, not a destination — the failure mode is letting the comment become the permanent fix.

The fifth case study carried a snapshot whose columns were dual-maintained in a TypeScript interface and a ten-parameter SQL function — add a column, update both, or ship silent data loss. Mid-release, with other work urgent, the fix was a warning comment at both sites. Two releases later, in a deliberately boring maintenance cycle, the ten parameters became two `jsonb` payloads and the drift class was eliminated outright. The retro's summary is the rule: *"The right time to do the cleaner refactor was when we had a quiet afternoon, not when adding a snapshot column was already the urgent task. The cheap defense bought us the right time."* **Corollary — rigor budgets are per-audience.** The same project's debug tooling deliberately took shortcuts its user-facing features couldn't (approximating historical state instead of replaying it), with the shortcut *documented at the call site*: *"Debug-mode features get to be lighter than user-facing features for exactly this reason. Not because they're sloppy. Because their audience can read the source."* Spend the rigor where the audience can't. *Pin: the cheap defense buys time; the quiet phase spends it. Skipping either half is how seams become incidents.*


## §8 Verification before completion

If you take one chapter of this playbook seriously, take this one. Verification is the load-bearing chapter — every other discipline in Part II points back here, because every other discipline fails the same way when verification is sloppy: confidently, in production. The rules are dry; the consequences are not.

### Rule: "Tests pass" is not "feature works." Verify the feature.

**Why:** Tests verify the code under test, not the user-visible behavior of the system. A suite can be 100% green while the feature is broken because no test exercised the wire between the parts.
**How to apply:** For UI work, open a browser. For deploy work, hit the live endpoint. For data work, query the data. For API work, read the response *body*, not just the status code. If "done" lives behind a screen, look at the screen.

*The Doorbell That Never Rang* (Part V) is the cleanest version of this rule. Audit logging shipped — backend green, frontend green, beautiful admin table rendering zero rows. No service call anywhere in the admin routes actually emitted an audit event; both halves tested in isolation, nobody wired the doorbell to the button. A thirty-second click in a real browser would have caught it. *Pin: if you didn't open the thing and use it, you didn't verify it.*

Two companion scars, each the same rule from a different angle. *The Comparison That Quantum-Superposed Into Nonexistence* (Part V) is the Doorbell inverted: the event fired perfectly, into a UI that a stale-cache race condition in a sibling component kept wrapped in `{!isLoading && …}` forever — bell rang, room nobody could see into. *The bufconn Gap* (Part V, second case study) is the same failure at the network layer: an adapter with full in-memory test coverage passed every test and had no discovery wire to find from a real client. A green test suite tells you the parts work. Only a real session in the real environment tells you the user can use the thing. Two mechanisms, one rule, two more reasons to verify where it matters.

**Second-edition clause: check what the assertion would tolerate.** A test can be green, correctly written, and still guarding a *weaker property* than the one you need. The first case study's v6.0 work needed reference identity on unchanged objects (so a memoized UI wouldn't re-render); the existing tests asserted with value equality on spread copies — `toEqual` where the invariant was `toBe`. Every test passed; the invariant was unguarded; three characters fixed it. Before trusting a green test, ask what change it would *fail* to catch. A test that tolerates the bug you're worried about is a smaller version of the wrong-claim theater above.

### Rule: Ask: would these tests pass if the change were reverted?

**Why:** This one question is the sharpest instrument yet found for separating verification from verification theater. A verification that would pass anyway — because it exercises a path the change doesn't touch, or tests through a layer that bypasses the one being fixed — proves nothing about the change, no matter how green it is. The question converts "we have tests" into "these tests witness this fix," and it takes ten seconds to ask.
**How to apply:** At review time, for every test attached to a change, ask the question out loud. If the answer is "yes, they'd still pass," the test is pinning something adjacent — keep it if it's honest about what it pins (rename it so it stops impersonating end-to-end coverage), and add a verification that actually witnesses the change, in the layer the change lives in. Reviewers of delegated work (§13) should ask it as a standing check.

The first case study coined the question during the crawler-routing fix. The E2E tests for the restored social-preview routing all passed — by hitting the backend endpoint directly and the dev server directly, bypassing nginx entirely. Nginx was the layer being fixed. Reverted, every test would still have been green. The reviewer's one question exposed it; the retro called it *"the sharpest tool we have for distinguishing verification from verification theater."* The remedy was two-part honesty: the test file was renamed to say what it actually pins (the endpoint contract), and the real verification — does the routing route? — moved to the post-deploy smoke test, the only place that exercises the layer in question. *Pin: a test that would pass with the change reverted is not a test of the change.*

### Rule: Evidence before assertions. Always.

**Why:** An agent that confidently says "the build passes" without showing the output is the agent you cannot trust. Verification is a habit, not a claim. Accept "I ran the tests and they passed" as evidence and you've trained the agent that prose is sufficient — and prose is what hallucinations look like.
**How to apply:** Never claim success without producing the verification command *and* its actual output, pasted in. `pytest` plus the green dots is evidence. "Tests pass" is not. If the agent says "deploy succeeded," the next sentence had better be a `curl` against the live URL with the response body attached. *Sharpening:* evidence of the *wrong claim* is still theater. A green check is only evidence for the specific claim it tests. Before accepting any successful output, name the claim the evidence actually supports. "180 unit tests passed" is evidence that 180 unit tests passed — it is not evidence that the feature works, the component renders, the cache-hit path fires, the touch event reaches the handler, or any of the other claims the green check might be mistaken for. The third case study's v7.0.1 hotfix is the canonical example: a data-layer migration shipped with a full green suite, and the failure was in the cache-hit path no test exercised. The tests weren't lying; the humans were reading them as answering a question they had never been asked. Evidence that answers the wrong question is not weaker evidence — it's *theater*, and it's dangerous precisely because it *looks* authoritative.

*Verify What You Shipped, Not What You Built* (Part V) is the canonical scar: deploy script reported success, new container healthy, every status check green — and the live site still serving the old version because nginx had never flipped. "I started the container" had become a stand-in for "reachable from the internet." The fix was one `curl` against the public URL with the response body compared to the SHA we'd just built. Not SSH exit codes. Not unit status. The user-facing URL. *Pin: the verification command and its output, pasted, or it didn't happen.*

### Rule: Verify in the environment that matters.

**Why:** Local-passing + CI-failing is the single most expensive failure mode in this project's history. Cache backends differ. Databases differ. Node versions differ. Serialization paths differ. "Local green" only proves the code works against the specific lies your laptop tells.
**How to apply:** If the change touches anything that runs in CI or production, run it there before claiming done. If you can't reproduce CI's environment locally, that's the bug — fix the parity gap, then verify. *Cross-reference:* this is the same lesson the DevOps playbook pins as "dev == prod." Two playbooks, one rule, and the overlap isn't an accident — parity between environments is *the* substrate that makes verification mean anything. If you have the DevOps discipline, this rule is cheap. If you don't, this rule is where you find out.

*The Cache That Lied In CI* (Part V) is the worst version we shipped. Cache layer refactored, Pydantic models flowing through Redis, someone wrote `json.dumps(model, default=str)` — green locally, image pipeline detonated in CI. Local was green because local used an in-memory cache with no serialization path at all; CI used real Redis. The serialization step that didn't exist locally was the entire bug. The fix is `model_dump(mode="json")`; the rule is bigger — cache changes pass locally and fail in CI until the parity gap closes. *Pin: if your local doesn't run what CI runs, your local green is a lie.*

Three companion parity-gap scars tell the same rule in different substrates. *The Docker Port Mappings That Weren't* (Part V, second case study): 180+ passing tests, zero data races, four clean releases, and a container that had been unreachable from outside every one of them because the Makefile mapped host ports to privileged container ports the non-root process couldn't bind. CI validated the image *built*; nothing validated it *answered*. *Two Hotfixes In One Release* (Part V, third case study): a TanStack Query migration shipped with 161 unit tests green and broke cache-hit paint within 24 hours (a side effect inside `queryFn` never ran on cached data), and its stablemate — a touch-vs-mouse guard tested only on desktop — silently blocked single taps on iPad Safari. Both slipped a full green suite because no test exercised the *interaction pipeline* on the real substrate. Four projects, four substrates, one rule: when you're swapping a foundation layer, the test gap is always on the side you weren't looking at.

**Second-edition clauses.** *Test with the client that doesn't send the convenient headers.* The first case study's perimeter middleware had four authorization checks that were secretly sequential — three dead, and the survivor keyed on a header that browsers send on every request and native mobile clients never send. The bug slept for three major versions and 311 test runs because every test client was the polite one. When an endpoint serves more than one kind of client, verify with the rudest client you support. *Verify what was fetched, not what rendered.* When the fifth case study removed a third-party font dependency for privacy, the page rendering correctly proved nothing — a page can render beautifully while still leaking requests. The verification that counted was the browser's resource-timing log showing *zero* requests to the third-party host. For any "we no longer talk to X" claim, the evidence is the network log, not the screenshot.

### Rule: When a value crosses a layer boundary, verify the wire, not the fixture.

**Why:** Some delivery properties are *structurally invisible* to unit tests — not undertested, unverifiable at that layer. A test fixture that reads log records before the formatter runs cannot see what the formatter discards. Code review of application code cannot see that the production compose file never forwards the env var. For any value that crosses a boundary — middleware to formatter, env file to orchestrator to container, service to sidecar — a green unit suite is necessary and *cannot be sufficient*, because the failure lives between the layers, where no unit stands.
**How to apply:** When a feature's value crosses a layer boundary, the plan must include a wire-level integration task as a first-class step — run the real stack, capture the actual emitted artifact (the log line as written, the response as served, the env as seen inside the container), and compare it to the claim. This is not extra credit and not "more discipline"; it is the only layer that can answer the question the feature was built to answer.

The first case study's consumer-tier release is the crown jewel. Forty of forty tests green, and the mandatory manual-integration task found two production-killers in an afternoon. First: the production compose file explicitly allowlists which env vars reach each container, and the new `CONSUMER_API_KEYS` wasn't on the list — the feature was *"entirely correct in code review and entirely broken in production,"* because the break lived in a file no unit test loads. Second: the logging pipeline's formatter had been silently discarding every structured `extra={...}` payload since the day it was configured — and the test suite's log-capture fixture passed because it reads records *before* any handler runs. The retro's rule, verbatim: *"When testing whether a feature delivers, not whether it runs, look at the wire output, not the test fixture."* *Pin: unit tests verify the contract at the unit's edge. Delivery happens past the edge — go look at the wire.*

### Rule: Health checks must check health — and observability must be observed.

**Why:** A 200 from `/health` doesn't mean the database is reachable — it means nginx is awake. A health check that can't detect a downed dependency is a status check cosplaying as a health check, and the worst thing it can do is succeed during an outage.
**How to apply:** Health checks must verify the actual dependencies — DB ping, Redis ping, downstream reachability — and return them in the response body, with the build SHA, so verifiers can confirm they hit the right endpoint and the right version. If it can't tell "healthy" from "half the stack is on fire but uvicorn is still up," it isn't one. *(See DevOps Playbook Phase 7.1 and Gotcha #8 for the `/health` vs `/api/v1/health` split and the verification pattern that catches this.)*

*The Health Check That Wasn't* — told in full in Part V — is the canonical scar for this rule and probably for the whole chapter: three deploys chasing a missing `git_sha` through every Docker mechanism the team had, because the verification curl was hitting `/health` (a two-line status check with no `git_sha` field) instead of `/api/v1/health` (the full health endpoint). The producer was never broken. The verifier was looking through the wrong window. The lesson lives in two rules at once: health checks must actually report dependencies, and verification curls must hit the endpoint that reports them. *Pin: if your health check can't say what's broken, it can't say anything's healthy.*

**Second-edition clause: the monitoring is part of the system — verify it observes.** The instruments you'd use to notice an outage can themselves be silently down, and nothing downstream of a dead instrument ever complains. The first case study discovered its frontend error tracker had been a no-op for five releases: a security release had tightened the Content-Security-Policy to `connect-src 'self'`, which blocked the tracker's own reporting endpoint — the release that hardened the app disarmed its smoke alarm. (*"We have not yet decided whether this is hilarious or appalling."*) The check is cheap and almost never run: trigger a deliberate test error and confirm it arrives; confirm the metrics dashboard shows the deploy you just did. Put it in the post-deploy checklist next to the health curl. *Pin: an unobserved observer is a prop. Fire a test flare through it now and then.*

## §9 Trust boundaries

Verification (§8) tells you the work is correct. Trust boundaries tell you whether the agent had the authority to do the work at all. This chapter is the political layer on top of the technical one. Get the technical layer right and the political one wrong and you ship a verified force-push to main.

### Rule: Match the action to its blast radius. Confirm before crossing the line.

**Why:** A local file edit is reversible. A force-push is not. Treat both the same and you'll eventually force-push something that should have been a file edit. The agent doesn't intuit blast radius — it sees both as "a tool call I'm allowed to make." That intuition is the engineer's job.
**How to apply:** Local and reversible — let the agent run. Shared state, hard to reverse, visible to other people — confirm first. The test is recovery time: if this is wrong, how long to undo it? Seconds, fine. Hours of someone else's work, ask first.

The cost of an action is not visible in its syntax. `git commit` and `git push --force-with-lease origin main` are two characters apart and four orders of magnitude apart. The Four-Fix WCAG Contrast Cycle is the calibrated version of this (full story in Part V) — four consecutive contrast violations across two releases, each fix a Tailwind class swap of one shade. Reversible, local, tiny blast radius. The right move was to let the agent change the colors, run the axe-core suite, and confirm by *evidence* (§8) rather than by approval — the verification step did the blessing. A deploy in the same session gets a manual confirmation, because the recovery time is "how long until rollback finishes," not "Cmd-Z." Different blast radius, different boundary. *Pin: blast radius is set by recovery time, not by command length.*

> **Field note — case study 1:** *The fourth contrast fix in two releases.* Four WCAG contrast violations across two releases, each a one-class utility color swap caught by axe-core on the next run. Reversible, local, tiny blast radius. The right move was to stop adding approval ceremony to the fixes and let the automated rail do the blessing — the rail was doing its job; humans were the slow learners.

**Second-edition clause: reversibility has a time axis — bake in the hard-to-undo levers.** Recovery time isn't binary; some actions are undoable in principle and effectively permanent in practice, because the undo propagates through caches, browsers, or third-party lists on a schedule you don't control. For those, deploy the *conservative setting first* and calendar the escalation. The fifth case study's HSTS rollout is the pattern: preload is close to irreversible (browsers ship the list), so the release set `max-age` to one day, opened a ticket, and put the bump to a year plus preload on the calendar after a bake-in week. The retro's line: *"the most dangerous lever is the one that's hard to put back."* Anything with that shape — DNS TTLs, permanent redirects, published package names, retention policies — gets the same treatment: smallest committing step first, escalation scheduled, never both at once.

### Rule: Authorization is scoped, not blanket.

**Why:** "Yes, push" once does not mean "yes, push" forever. When a user approves a destructive action, they are approving *that specific action*, not handing out a permission slip for the next one. An agent that generalizes a single yes into a standing yes will eventually cross a line nobody told it not to cross.
**How to apply:** Every risky action is its own decision unless durable instructions — CLAUDE.md, `settings.json` permissions, an explicit skill — say otherwise. If in doubt, ask. The cost of asking is one round-trip. The cost of not asking is a retro chapter.

The interesting code, as the Admin Who Couldn't Fire Herself release put it (full story in Part V), is in the *denial* path. RBAC went in for admins, and the rules that needed care weren't "an admin can edit a record" — those were one-liners. The careful rules were "no self-role-change, no self-deactivation, no self-deletion, no escalation via update." Half a dozen explicit refusals, because trust granted in one direction (you are an admin) does not generalize in every direction (therefore you can fire yourself). Scoped authorization for agents works the same way. You approved a `git commit`; that does not mean the next `git push --force` is pre-approved. Where the harness can express "this tool, this scope," use it — harness permissions are the durable form of "yes, but only this." Everything else is a per-action decision. *Pin: every yes is for one action. The next risky action is its own conversation.*

> **Field note — case study 1:** *The Admin Who Couldn't Fire Herself.* RBAC landed for the admin panel and the one-liners were all in the "yes" paths. The careful rules were in the refusals — no self-role-change, no self-deactivation, no self-deletion, no escalation via update. Half a dozen explicit denials, each written on purpose, because trust in one direction doesn't generalize in every direction. A later release added one more the first pass missed: the last superadmin can't fire themselves either.

The corollary is *The Default That Was Admin* (Part V, case study 4): a shared edge-function handler signature that defaulted to `admin` when the client wasn't specified silently elevated every new endpoint written after the refactor. The fix was one line — change the default to `anon`. The broader lesson: **the default direction matters as much as the authorization rule.** The unsafe default is the one everyone who didn't read the docs will end up using — including agents, whose default behavior is "use the API the way the type signature suggests." Defaults must be the least-privilege option, every time. *Pin: make the safe choice the default; require explicit opt-in for elevation.*

### Rule: When the agent hits an obstacle, it must investigate, not delete.

**Why:** Unexpected files, branches, lock files, and orphaned containers usually represent in-progress work — from a teammate, from an earlier you, from a process that hasn't finished. Deleting them to make the error go away is how you lose a day of uncommitted work nobody can reconstruct.
**How to apply:** Investigate root causes. `git reset --hard`, `rm -rf`, `--no-verify`, `git clean -fd`, "let me just drop the database" — last resorts, not first resorts. If the agent cannot tell you *why* deleting the thing is safe, it isn't.

The Deleting the Ghost near-miss was a deletion that almost shipped (full story implied across Part V). The release was cleaning up a legacy deploy script — replaced by the new blue-green version, no callers in the codebase, no references in any workflow, every grep clean. By every test the agent could run, the file was dead code. The code-quality reviewer caught it: the operations runbook still pointed at the old script as the manual recovery path during a rollback. The reference wasn't in any source file or workflow — it was in a Markdown runbook nobody had thought to grep. One careless deletion would have left the on-call playbook pointing at a ghost. The rule generalized: never delete a file without grepping for its name across docs and runbooks first, and when the agent says "this is safe to delete," the right response is "show me where you looked." *Pin: if the agent can't show you where it looked, it didn't look.*

> **Field note — case study 1:** *Deleting the Ghost.* A legacy deploy script was scheduled for deletion. Every grep of the source tree and workflows came back clean. A code-quality reviewer noticed the operations runbook still pointed at the old script as the manual recovery path during a rollback — a reference that lived in a Markdown file nobody had thought to search. Deleting it would have left the on-call playbook pointing at a file that no longer existed. Grep your docs before you delete anything.

**Second-edition clause: investigation depth follows blast radius too.** "Investigate, not delete" is about destructive shortcuts, and it stands. But its mirror image also needs saying: not every mystery deserves a full excavation. When the fifth case study's test runner wedged inexplicably, the team adopted a config that worked, banked the ninety minutes, and left *"a TODO-shaped observation"* rather than burning the session on a full diagnosis — because the blast radius of the unexplained behavior was zero once the workaround held. The discriminator is the same one as always: what breaks, and for how long, if the mystery stays unsolved? A phantom in shared state or a security surface gets the full §10 treatment. A tooling quirk with a working configuration gets a note and a ticket. Spending craft attention on zero-blast-radius mysteries is the human doing the laborer's job in disguise.

### Rule: Secrets never transit the transcript.

**Why:** An agent session is a document. It gets logged, persisted, summarized, sometimes shared, sometimes fed to other tools — and every credential that was ever printed into it is now *in* it, wherever it goes. A secret that passes through the transcript on its way to the secrets store has been copied to a place with none of the store's protections and all of the store's value.
**How to apply:** When an agent session must move credentials — deploy keys, service-role tokens, API keys — pipe them: from the secret manager's CLI straight into the target (`vault read … | target-cli set …`), through shell variables, never echoed, never pasted into the conversation. If a secret does transit the transcript, treat it as exposed: rotate it, don't rationalize it. Verify properties of secrets (length, prefix, checksum) rather than values. And build the habit *before* the incident: the goal state is a deploy session whose retro can say "zero secrets printed."

The sixth case study learned this in two consecutive deploys. The first moved a service-role key into the host's env config by way of the conversation — it worked, and the retro's last line item was the rotation that followed, because *worked* and *safe* are different claims. The second deploy was run under the corrected discipline — every secret piped from the platform CLI into shell variables, never printed — and its retro logged the number that matters: *"0 secrets printed to the transcript this time."* The same sessions produced the companion lesson (§2): when a sourced secret is rejected downstream, check its *length* before doubting your code — one platform CLI returned a 20-character slice of a 64-character secret, and the rejection was the system working. *Pin: the transcript is a copy of everything that touches it. Don't let secrets touch it.*

### Rule: Before touching a non-negotiable, write down what would change your mind.

**Why:** Every project has load-bearing commitments — "no AI in the response path," "anonymous by design," "zero runtime dependencies." Sooner or later a plausible proposal will arrive to revisit one, and the two cheap responses are both wrong: reflexive refusal (the commitment becomes dogma nobody can re-examine) and casual revisiting (the commitment erodes through a series of reasonable-sounding exceptions). The disciplined move is a pre-registered experiment: define, *before gathering any evidence*, exactly what result would justify the change — plus the full cost accounting the proposal's framing conveniently omits.
**How to apply:** File the challenge as a research ticket, not a change ticket. In it: the success bar stated as measurable thresholds, the costs that don't show up in the benchmark (privacy posture, determinism, the marketing copy that made the commitment a promise), and an explicit "we don't know the answer yet." Then run the experiment on its own schedule, not the release's. If the bar is met, the change earns a real conversation. If nobody can state a bar, that's the answer: the proposal is a mood, not a case.

The fifth case study's classifier is deterministic on purpose — "nothing you write is ever sent to a model" is in the product's public copy. When "would a small LLM classify better than the regex?" inevitably surfaced, the team neither refused nor complied. They filed it with a pre-declared bar (≥95% register agreement *and* a lower unclassified rate *and* free-tier resource fit), itemized the costs the benchmark can't see, and closed with the sentence that makes the whole move: *"We don't know the answer. We have written down what would change our mind."* The commitment stayed intact, the question stayed askable, and no one had to win an argument to keep it that way. *Pin: a non-negotiable survives scrutiny by pre-registering the scrutiny — name the bar before you look at the data.*

---

# Part III — When It Goes Wrong

## §10 Diagnosis — build the lab

*(New in the second edition.)* The first edition treated debugging as a failure mode to recover from — "stop fixing and start diagnosing" was a pin inside §11. The fifth case study turned it into a discipline with its own equipment, and the results were strong enough to earn a chapter. The premise: when a class of bug recurs, the scarce resource isn't fixes — the agent can generate plausible fixes indefinitely — it's *evidence*. The projects that debug well are the ones that invest in the instruments that produce evidence: persisted traces, replay surfaces, exportable diagnostics. Build the lab, and the bugs run out of places to hide. Skip it, and every fix is a guess wearing a lab coat.

### Rule: Build the diagnostic surface before the fix.

**Why:** Without observability, you debug by re-reasoning about source code — and the agent is dangerously good at that, producing confident, plausible, unverifiable diagnoses. Worse, for state-dependent bugs, reproducing the failure by hand *pollutes the state* you're trying to observe, and re-running today's code tells you what today's code does, not what last week's did. The diagnostic surface — a persisted trace of every decision, a replay tool, an export — converts debugging from archaeology into reading.
**How to apply:** When the same class of bug shows up a second time, stop fixing individual instances. Spend the next cycle shipping the instrument: persist the decision trace at the moment of the decision (not reconstructed later), build the playground that replays inputs against the current logic, make the whole thing exportable so a bug report can carry its own evidence. *Then* fix the backlog of instances — they'll fall in batches.

The fifth case study's classifier misfires are the controlled experiment. Seven entries on screen, three replied wrong. The agent started typing a fix and stopped — diagnosing the misfire would have required re-entering the text (polluting the journal) and would have produced the *current* classifier's trace, not the one that misfired: *"the wrong answer would have been a different wrong answer."* So the release shipped the lab instead: a persisted classification trace on every entry, a debug playground, and only then the one-line fix. The next release added replay-the-whole-journal; the one after made every trace exportable as a Markdown diagnostic notebook. Then the payoff, measured: four real misfires closed *"in a single afternoon,"* and within two more releases the majority of a miscategorized corpus had been re-homed. The retro's summary is the rule: *"build the diagnostic surface alongside the change you're making, and you can see the change land in real time instead of inferring it from second-order signals."* *Pin: when the same bug class bites twice, the next thing you ship is the instrument, not the fix.*

### Rule: The ticket's diagnosis is a hypothesis. Read the trace before believing the issue.

**Why:** Bug reports — including the ones you filed yourself, including the ones an agent filed with great confidence — arrive with a diagnosis baked into the framing, and the framing is wrong often enough to be the single most expensive thing to trust. Designing the fix from the ticket means building a beautiful solution to a problem that may not exist. The trace is the only witness that was actually there.
**How to apply:** Before designing any fix, pull the actual evidence for the actual failing case: the persisted trace, the raw payload, the log line at the moment of failure. Confirm the ticket's story against it. Only then design. If there is no trace to pull, you're in the previous rule — go build the instrument first.

The fifth case study walked into this twice, instructively. A ticket said hedge phrases ("just a little bit") were suppressing heavy-affect detection, and a whole hedge-ignore subsystem got drafted — then someone read the trace: the entry containing `sad` had never matched anything, because the heavy-signals list only spoke in extremes (`devastated`, `hollow`, `grief`). Four lines of mild-affect vocabulary fixed it. *"It would have been a beautiful fix for a problem that didn't exist."* One release later, a ticket prescribed a triumph-register fix; the human's one glance at the entry — future tense, not a win — redirected the whole thing to anticipation handling. The project's instructions file now carries the distilled version: *"Read the trace before believing the issue."* Note what this rule does to the loop: it's §5's explore step running at bug scale, and it's the reason the lab (previous rule) pays rent every single week. *Pin: the ticket tells you where it hurts. Only the trace tells you what's broken.*

### Rule: A fixed bug's class is a search query, not a closed ticket.

**Why:** Bugs come in families. The conditions that produced one instance — a pattern copied across layers, a convention nobody enforces, a client that masks failures — almost always produced siblings, and the siblings are one layer up or down from where you just looked. Fixing the instance and closing the ticket leaves the family in place, and each sibling will cost a full diagnosis later, whereas right now — with the failure mode fresh in your head — each one costs a grep.
**How to apply:** After confirming a fix, turn the root cause into a search: where else does this pattern appear? Which other layer does the same job? What else would fail the same way and be masked by the same client? Budget ten minutes. File what you find, even if you fix it later. The two sanity checks that cost nothing — run the same probe one layer deeper — are the difference between killing a bug and killing its class.

The first case study's public-endpoint saga is the cautionary tale: the *same* failure mode — a public path silently broken, masked by the web client that never exercised it — was found **three separate times**, in three layers. First the nginx crawler map (share previews 401ing for three releases). Then, during the fix's verification, the perimeter middleware's dead checks (native clients 403ing for three versions). Then, during the *next* release's visual QA, two sanity curls found the API-key middleware's exemption list missing the same public endpoints — the routing so recently and heroically restored was still broken one layer down. The retro tallied it dryly: *"3 instances of the 'silent public-path breakage masked by web client' failure mode."* Three diagnoses that could have been one diagnosis and two greps. *Pin: after every fix, hunt the siblings one layer deeper. The class dies by search, not by ticket.*

### Rule: Exploration mode is not production mode.

**Why:** A good lab (rule 1) exercises production code against non-production state — frozen histories, replayed inputs, states that never persist. Stateful rules that are *correct* in the real flow can misbehave against that frozen state, and the misbehavior looks exactly like a production bug. If you don't name the difference, you'll "fix" production logic that was never broken — the diagnostic equivalent of friendly fire.
**How to apply:** When a bug reproduces only in the diagnostic surface, ask first: which production invariants assume state that *moves* (history accumulating, cooldowns expiring, caches filling)? If the playground freezes that state, the divergence is the playground's problem. Fix it there — an explicit flag that bypasses the stateful rule in exploration, with production code byte-identical — and never the other way around.

The fifth case study's *Marcus Monopoly* is the type specimen. After a new register shipped, every playground test came back with the same historical figure. The rotation logic contained a fairness rule — a figure never seen recently beats all others — that is exactly right in production, where each reply becomes history. In the playground, history is loaded once and never updated, so the one figure absent from the last sixty days won *every* draw: a fairness rule producing perfect unfairness against frozen state. The user made the diagnosis in one sentence: *"I think the logic is right. I think we need to fix the debug page so that it ignores the anti-repeat logic, since it will never save."* The fix was a `randomize` flag the playground passes and production doesn't. Production shipped byte-identical. *Pin: when the bug only reproduces in the lab, suspect the lab's frozen state before the production logic.*

### Rule: When the runner wedges, suspect the runner.

**Why:** The diagnostic instinct — it must be my code — is usually right and occasionally very expensive. Test runners, bundlers, caches, and sandboxes have their own failure modes (corrupted module caches, pool deadlocks, stale daemons), and a session spent debugging your code for a tool's hang is a session lost to a category error. The complementary error is over-investigating: a full root-cause excavation of a tool bug you can neither fix nor report usefully.
**How to apply:** When the tooling hangs or fails in a way that's *shaped wrong* for your change — instant where it should be slow, hanging where it should fail, failing in files you didn't touch — flip the hypothesis: try a different pool mode, clear the tool's cache, retry the build. If a configuration works, adopt it, note the mystery, and move on (§9's investigation-depth clause). Not every red is a bug: *"some reds are just the registry having a moment."*

The catalog from the case studies: vitest hanging for minutes on a suite that runs in 1.5 seconds under `--pool=forks` — adopted, banked the time, *"left a TODO-shaped observation"* (fifth case study). Thirty-eight unrelated tests hanging because four parallel agents corrupted the shared module-graph cache — `rm -rf node_modules/.vitest` fixed all of them (first case study, told in full in Part V). A build that died at `npm install` on a commit whose preview had built clean — one retry, gone (sixth case study). The common thread: in each case the failure's *shape* (wrong files, wrong speed, wrong stage) pointed away from the code, and the fix was at the tool layer. The agent, note, will happily generate code-level explanations for all three. That's the trap. *Pin: failures in files you didn't touch, at speeds that don't make sense, are the runner talking. Answer it at the runner's layer.*

## §11 Failure modes & recovery

If you're reading this first, something is on fire. That's fine — this is the door we left unlocked for that. Seven failure modes follow, easiest to recognize first, most dangerous last. The first five are discipline failures; the sixth is a topology failure; the seventh — new in this edition — is epistemic. Find the one that matches, read what's happening underneath, do the fix. Then — before you walk away — read the short closing note, because every agent failure has a human antecedent, and the antecedent is almost always cheaper to fix than the symptom. We've been in all of these. None is terminal.

### Failure mode: The agent went off the rails

**Symptoms:** Code that has nothing to do with what you asked for. Files invented out of thin air. The agent solving a problem you don't recognize. You read the diff and think "what conversation were we even having?"
**What's actually happening:** The brief was vague or missing, and the agent filled the context gaps with guesses. Every prompt is a cold start (§1); when the prompt doesn't say what "done" looks like, the agent invents a "done" that sounds reasonable and ships toward it.
**The fix:** Stop. Don't steer mid-flight. Open a fresh conversation and write a self-contained briefing — goal, constraints, what you've already ruled out, success criteria. See §4 The first conversation.

The instinct is to send another message correcting the drift. Don't. A one-line correction to a context-starved conversation gives the agent a new way to be wrong. Kill it, write the briefing you should have written the first time, start over. You're throwing away ten minutes of nonsense to save an afternoon of it.

### Failure mode: The agent produced slop

**Symptoms:** Code that compiles but feels wrong. Generic helpers nobody asked for. Defensive try/except around errors that can't happen. Three layers of abstraction over a function called once. The PR is twice the size it should be and reads like a coding-interview answer.
**What's actually happening:** No constraints in the prompt. The agent's default mode is to add — a new helper, a new layer, an extra branch — because adding feels like work and looks like care. Without a "don't add features beyond the task" rail, every prompt drifts toward gold-plating.
**The fix:** Add explicit YAGNI constraints to the prompt. Better, make them durable: promote "no abstractions for a single caller; no handling for impossible errors; no refactoring adjacent code unless asked" into memory or a skill. See §6 Memory hygiene and §7 Skills as institutional knowledge.

The morning-after tax is the tell. If you've spent a morning removing what the agent added yesterday — the unused helper, the wrapper, an early-return for a case that doesn't exist — that's slop. The God Module Problem hits the same pattern at the file level: god modules grow because nothing justifies the interruption to split them. Slop grows the same way. Constrain at the prompt; promote to memory the second time you re-type it.

> **Field note — case study 1:** *The God Module Problem.* One admin module grew to 1,052 lines because every new feature "just added one more route to the existing file." Nothing ever justified the interruption to split it. The cost wasn't visible until someone tried to brief a subagent on "admin behavior" and had to load the whole thing. Slop grows for exactly the same reason — each addition is too small to argue with.

### Failure mode: The agent can't be trusted with anything important

**Symptoms:** Every output needs heavy review. You're editing the agent's work more than you're working alongside it. You stopped delegating things that matter because checking costs more than doing it yourself. Velocity collapses; morale follows.
**What's actually happening:** No verification discipline. The agent has been rewarded for sounding done rather than being done — every "looks good, ship it" without an evidence check trains the next "tests pass" to be a vibe instead of a fact. Trust didn't erode; it was never built on anything.
**The fix:** Install §8 Verification before completion, hard. Evidence before assertions, every time. Make the verification command and its output part of the deliverable, not a courtesy.

This feels like a people problem and isn't — the loop lacks a forcing function. The Trust Your Local Tests pivot is the cleanest version *(see §12)*: three releases of typing "trust your local tests" into fresh conversations, each correction evaporating by the next session. The fix wasn't another correction; it was ripping SQLite out of the suite so local and CI ran the same paths. You can't out-discipline a missing rail. Build the rail.

### Failure mode: The agent loops on the same wrong fix

**Symptoms:** The agent fixes something, the test fails, the agent fixes it differently, the test fails the same way. Each fix is plausible. None work. You're three rounds in and the error message hasn't moved.
**What's actually happening:** Misdiagnosed root cause. The agent is iterating on a problem that isn't the problem. The fixes look reasonable in isolation; none touch the actual broken thing because nobody asked "wait, what is actually broken?"
**The fix:** Stop touching code. Run systematic debugging — dump raw state, log the actual response, walk the data path from producer to consumer. Find the real failure before the next edit. See §8 — and if this class of bug has bitten before, see §10: build the lab, then read the trace instead of re-reasoning about the source.

*The Health Check That Wasn't* (Part V) is the canonical example. What matters here is the move: when the second fix fails the same way as the first, stop fixing and start diagnosing. *Pin: when the second fix fails the same way as the first, stop fixing and start diagnosing.*

### Failure mode: The agent confidently lies about state

**Symptoms:** "Tests pass." (They don't.) "Deploy succeeded." (It rolled back.) "I verified the endpoint." (It returns 404.) The summary is fluent, optimistic, and wrong. You only catch it because something downstream breaks an hour later.
**What's actually happening:** No evidence-before-assertions discipline. The agent learned that a confident summary closes the conversation, and "I ran X and it passed" reads identically to "I ran X and pasted the output." Every other failure in this catalog announces itself. This one looks like progress and rots underneath.
**The fix:** Install §8 *very* hard. Reject any success claim not accompanied by the verification command and its actual output. Where the harness can enforce it — hooks, settings.json, skill scaffolding — make evidence mandatory, not optional. *Pin: prose without paste is hallucination. Make the paste mandatory.*

### Failure mode: The partnership architecture is wrong

**Symptoms:** Every agent's individual work is clean, but the integration is a mess. Files end up on the wrong branches, commits cross-contaminate, state leaks between tasks that were supposed to be isolated. When you go looking for "the bug," there isn't one — every agent did exactly what it was told, and the failure emerged from the way the agents were *arranged*. You find yourself debugging topology instead of code.
**What's actually happening:** All five earlier entries are discipline failures. This one isn't. The agents have *all* the discipline; the collaboration architecture has a hidden incompatibility with the underlying tools — usually shared state lurking under what looks like isolation.
**The fix:** Stop trying to out-discipline the architecture. Change the *shape* of the collaboration, not the prompts. Read §13 and ask: are tasks actually independent at the level the coordination model assumes? Is there shared state under the isolation that nobody is managing? *Pin: when the agents are good and the result is bad, the architecture is wrong.*

The canonical scar is the third case study's v6→v7 worktree pivot *(told in full in §13)* — same agents, same discipline, worktree-per-agent produced branch confusion and orphaned refs; team-in-one-worktree with file-boundary ownership shipped cleanly. The rail you couldn't out-discipline was the *coordination architecture*, not the pipeline.

### Failure mode: The workspace lies about state

**Symptoms:** Everyone — the agent, the docs, the memory, *you* — agrees on a fact about the system, and the fact is false. The branch is protected (it isn't). The middleware reads that header (it never has). The migration guide's section titled "the actual cause" describes a cause that wasn't. Nothing is drifting; the belief was never true. You find out on the day the belief was supposed to matter.
**What's actually happening:** All six earlier entries are failures of *doing*. This one is a failure of *knowing*. Written context — memory, instructions files, comments, runbooks, even retros — is an amplifier: it repeats whatever it was given, with perfect confidence, to every reader, forever. Nothing in the normal loop ever re-tests standing beliefs, because verification (§8) fires on *changes*. A false belief that arrives in writing looks exactly like institutional knowledge. It survives code review. It survives audits that don't probe. The agent isn't hallucinating; it's faithfully citing a source that was wrong at birth.
**The fix:** Probes, not corrections. Find the load-bearing beliefs about the system — protections, integrations, "X reads Y," "Z is enabled" — and run the command that would prove each one: the API call that shows the protection object, the grep that finds the consumer of the header, the test error that arrives in the tracker. Fix what fails, and attach the probe to the belief so the next audit re-runs it (§6's probe rule, §15's audit cadence). *Pin: written context is an amplifier, not a witness. Only a command output is a witness.*

The gallery from two projects in one season: main-branch protection asserted by memory, instructions file, and PR descriptions — `404: Branch not protected` (*The Lock That Wasn't*, Part V). An nginx comment confidently documenting that the backend trusts a forwarding header — `grep` found zero consumers; *"a documentation lie about a security control … looks load-bearing in code review. It survives audits."* A migration guide with a section titled "this is the actual cause of the 403s" — *"It was authoritative. It was wrong,"* and the team corrected it with a visible post-mortem note rather than a silent rewrite, so the record shows the belief *and* its correction. That last move is the culture this failure mode wants: being wrong in writing is recoverable; being wrong in writing and erasing the trail is how the next false belief gets believed.

### One more thing, before §12: every agent failure has a human antecedent.

The seven entries above describe things the agent did, or the architecture did, or the written record did, and the fix is aimed at the agent, the architecture, or the record. That framing is useful for diagnosis — it tells you *which rail to build*. But before you walk away with the prompt to fix, check upstream.

Every failure in this chapter has a human-side twin, and the twin is usually where the cycle started. You skipped the brainstorm because the fix "felt obvious" (the twin to *loops on the same wrong fix*). You skipped the retro because the cycle "didn't really have anything to learn" (the twin to *produces slop*). You accepted "tests pass" as evidence because typing the verify-and-paste ritual *again* is boring (the twin to *confidently lies about state*). You promoted a correction to a CLAUDE.md note instead of a skill because a note is five seconds and a skill is an hour (the twin to *can't be trusted with anything important*). You wrote the claim down without running the probe, because writing is faster than verifying (the twin to *the workspace lies about state*). The agent was downstream of a shortcut you took.

When an agent failure shows up, look for the human antecedent before you tune the prompt. The antecedent is almost always cheaper to fix than the symptom, and fixing the symptom without the antecedent just reschedules the same failure. *Pin: every agent failure has a human antecedent. Look for it before you blame the model.*

## §12 The rescue protocol

You've read §11 and found your failure mode. Good — now you know what's broken. This chapter is the next seven days. It's a checklist, not an essay, because a team in crisis doesn't need more prose. Three horizons: the next hour, the next day, the next week. Work them in order. Don't skip ahead.

### In the next hour — stop the bleeding

- **Pick one small, scoped task.** Not the thing that's on fire — something adjacent and contained. Something you can verify end-to-end in five minutes. The goal is not to ship it; the goal is to complete one clean loop so you remember what "working" feels like.
- **Run the full loop on that task.** Explore, even if it's three greps. Brainstorm, even if it's ninety seconds. Plan, even if it's one page. TDD if code is involved. Verify with evidence. Commit. Every step, in order, no shortcuts — you are re-calibrating the muscle, not optimizing it.
- **Stop using the agent for anything you can't verify in 5 minutes.** If you can't check it, you can't ship it right now. Verification is the trust currency; accept IOUs and you'll be babysitting again by tomorrow morning. See §8.
- **Audit your memory files. Delete anything you can't justify.** Open them. Read each entry out loud. If you can't say "this is still true and the agent needs it," cut it. Stale memory is poisoning the well — every contradicted fact teaches the agent that your notes are suggestions. See §6.

### In the next day — stabilize

- **Run the brainstorming skill before every task for one full day.** Every single one. The trivial ones too. You will feel it slow you down; it will also catch two scope drifts you would not have caught, and at least one of them would have cost you an afternoon.
- **Write one feedback memory from last week's corrections.** Open your recent chat logs. Find the correction you made most often — the one you're tired of typing. That's the memory. One is enough. See §6.
- **Run an honest retro on the last week.** Not a changelog. What hurt, what surprised you, what you'd do differently. A paragraph is fine. The point is to name the pattern out loud so you stop walking into it. See §16.
- **Read §8 Verification out loud.** Literally out loud, the whole section. This sounds silly and it works — the failure mode that got you here is almost always evidence discipline, and reading the rules aloud is how they stop being wallpaper and start being rules.

### In the next week — rebuild trust

- **Promote two repeated corrections into real skills.** Not another CLAUDE.md paragraph — an actual skill with a trigger and a checklist. If you've typed the same correction three times this month, that's a skill the harness should be loading for you. See §7.
- **Add one hook that enforces a non-negotiable you've been asking the agent to "remember."** The correct number of reminders is zero; the correct number of hooks is one. Pick the rule you are most tired of repeating, and put it somewhere the harness cannot forget it. See §3.
- **Reconcile CLAUDE.md against your memory files.** CLAUDE.md is the things that don't change — architecture decisions, invariants, the shape of the project. Anything that drifts week-to-week belongs in memory or in the trash. Move stale facts out; let CLAUDE.md get smaller.
- **Ship one thing end-to-end using the full loop.** Not a refactor, not a cleanup — a real change that a user would notice, with a real verification that produces real output. Paste the evidence into the commit. Let the feeling of *that worked* compound into the next one.

### A worked example: Trust Your Local Tests

Three releases in a row, the team typed some version of "trust your local tests" into a fresh conversation and watched the correction evaporate by the next session. Local tests passed; CI failed. The backend suite ran SQLite on laptops and Postgres in CI, and every round of "works for me" was eroding faith in the suite itself. By the end of that third release, nobody fully believed a green local run meant anything — which meant nobody believed a red one either, which is worse.

The rescue was one cycle of the full loop applied to the parity gap itself, not the symptoms. Brainstorm: *what if local and CI ran the same database?* Plan: rip SQLite out, make the laptop suite use Postgres via Docker. TDD on the harness changes. Verify: same test, same bytes, same result in both environments. Commit, ship, done. The rule it implemented was §8's quiet clause — verification only counts in an environment that matches the one you're shipping to. Once that rail existed, the corrections stopped being necessary. You cannot out-discipline a missing rail. Build the rail.

> **Field note — case study 1:** *Trust Your Local Tests, the rescue that stuck.* The fix wasn't more discipline; it was structural. Rip the SQLite branch out of the test bootstrap, point local and CI at the same Postgres path, stop needing the phrase. Rails that make the old mistake impossible outlast any amount of "please remember to."

---

# Part IV — Leveling Up

## §13 Parallel agents & worktrees

Parallelism pays off exactly once: when the tasks are genuinely independent and the overhead of coordination is less than the time the fan-out saves. Everything else — racing on shared state, fan-out as a way to avoid thinking about dependencies, worktrees that quietly accumulate forgotten work — costs more than it earns. This chapter is about knowing the difference before you commit to the shape.

### Rule: Fan out only when tasks are independent.

**Why:** Parallel agents on dependent tasks produce merge conflicts, races, and subtle interleavings you'll spend longer debugging than the parallelism ever saved you. Two agents that both need to edit `services/timer_service.py` will produce a conflict. Two agents that need each other's types but don't wait for them will make different assumptions and ship two incompatible halves of a feature.
**How to apply:** If task B needs task A's output, they are sequential. If they touch different files with no shared state, they are parallel. The test is honest: can you describe the handoff between B and A in one sentence? If yes, they are sequential even if the files don't overlap. "B uses the interface A defines" is a handoff. You can make that interface explicit — agree on it in the plan, stub it, and run in parallel — but you have to do that work first, and it counts as a dependency.

The heuristic that holds across every release is grouping by file overlap, not by issue priority. Two high-priority issues that both touch the same test file are not a parallel pair — they are a serialization point. *Parallel Work* — told in full in Part V — is the textbook clean case: two agents, two languages, different runners, zero shared state, both green on first run because the file map guaranteed the conflict couldn't happen. A later release ran 14 subagents across 29 files with zero conflicts, for the same reason: the plan mapped file ownership before any agent started work. The file map is the contract. Write it first. *Pin: group by file overlap, not by issue priority.*

*The Interface That Never Needed a Sixth Method* (Part V, case study 2) is the strongest evidence for interface-first parallelism the playbook has: a five-method adapter contract absorbed 70+ adapters across nine releases without ever changing, because the interface itself refused to permit conflicts. Four agents working in parallel against a tight contract can't collide — not by discipline, by *construction*. *Pin: the interface you design before the parallel work begins is the coordination protocol the parallel work runs on.*

*The Wave Pattern* (Part V, case study 2) is the rhythm that made seven-agents-per-release safe: schedule trivial items first as a load test for the build/config/test harness, then moderates, then complex. The cheap wave shakes out every infrastructure surprise before the expensive agents commit to 150-line state machines — software's version of checking the parachute before jumping.

### Rule: Worktrees are workspaces, not stashes — and they are not a coordination strategy.

**Why:** A worktree is an isolated place to do work. It is not a place to park something "for later." Worktrees rot. Uncommitted experiments accumulate in long-lived worktrees the same way food accumulates on a desk — slowly, invisibly, until what's there is unrecoverable. The cost is not the disk space; it is the work itself: an afternoon of exploration with no commit, no branch, no artifact — just a worktree that got stale and got deleted. **And a second failure mode the original rule missed:** worktrees look like they isolate parallel agents, but the git state underneath them is *shared*. Worktrees isolate the *filesystem*; they do not isolate *branches, refs, HEAD, or merge state*. Five agents in five worktrees on five feature branches are all operating against the same underlying git database, and without an explicit coordination layer above that, they will step on each other's branches, cross-contaminate commits, and produce orphaned refs that have to be recovered by hand.
**How to apply:** Every worktree should have a definite end — merged, deleted, or explicitly reopened — within days. If you can't immediately name what the worktree is for, it is time to close it. Clean exit means committed (even as a draft branch), merged, or explicitly discarded — not suspended. "I'll come back to this" is how worktrees die. **For parallel-agent work specifically:** do not reach for worktree-per-agent as the isolation mechanism. Use file-boundary parallelism inside a single worktree, with a team or dispatch layer that assigns non-overlapping files to each agent. The third case study learned this the hard way (see *The v6 Worktree Experiment* below) and pivoted in the next release to a team-in-one-worktree approach with file-level ownership — same agents, same discipline, dramatically different outcome. *Pin: isolate context with worktrees; isolate work with file boundaries. Never rely on worktrees to isolate git state across agents.*

*The v6 Worktree Experiment* and *The v7 Team Pivot* (both Part V, third case study) are the cleanest paired evidence for this rule the playbook has. Same project, back-to-back releases, same kind of parallel work — worktree-per-agent in v6 produced branch confusion and orphaned refs that had to be recovered by hand; team-in-one-worktree with file-boundary ownership in v7 shipped cleanly. No agent was undisciplined in either release. The architecture changed and the outcome changed. This is what §11's partnership-architecture failure mode looks like when you fix the architecture instead of the agents.

The right mental model is that a worktree is a sprint, not a shelf. You open it with a task in mind, you work the task, you close it. A worktree that outlives its task is drift in physical form — and unlike a branch, there's no PR to force a reconciliation. If the work is real, commit it. If it's experimental, commit it to a draft branch. If it's done, delete it. The worktree lifecycle should be boring. *Pin: if you can't remember what it's for, close it.*

### Rule: Designate merge points explicitly; update them last.

**Why:** The hardest part of parallel agent work is not the parallel code — it's the few shared files every agent has to touch: the config registry, the main entrypoint, the integration test, the dependency manifest. If every agent edits those in parallel, you get conflicts by construction. If one agent edits them and the others wait, you've serialized the parallelism. The clean move is to declare those files as *merge points* — shared touchpoints that *nobody* edits during the parallel phase — and update them *after* all the parallel work has landed. The parallel phase becomes conflict-free by construction; the merge phase becomes a single mechanical pass against a known list of files.
**How to apply:** Before fan-out, identify every file any agent would plausibly need to touch to integrate its work. That list is your merge-point set. Split the plan into two phases: phase one is the parallel work that touches *only* each agent's own files; phase two is a single-threaded pass that updates each merge-point file with every agent's integration. The file map becomes a contract with two columns: *owned by an agent* and *merge point.* No file can be in both. The second case study ran this pattern cleanly across every release with parallel agents: *"the only shared touchpoints — the config registry, the main entrypoint, the integration test — are updated after all adapters land, eliminating contention."* Six agents, seven agents, twelve agents — zero merge conflicts on core logic across every release that used this pattern. *Pin: parallel work is a two-phase plan. Phase one is the fan-out; phase two is the merge-point pass. Mixing them is where conflicts come from.*

> **Field note — case study 2:** *Six agents, zero conflicts, by construction.* One release had four adapter agents plus two CI-pipeline agents working in parallel — six agents, one codebase, zero merge conflicts on core logic. The file map assigned every file to exactly one writer before any agent started; merge points (config registry, main wiring, integration test) were updated in a single-threaded pass after all four adapter agents reported back. The conflict that didn't happen was *impossible* for the structure to produce.

**Second-edition clause: merge-point discipline extends to the commit log.** When subagent waves land through a single controller, the controller owns the truthfulness of the history, not just the cleanliness of the merge. The fifth case study caught a wave commit whose message described only half of what the wave had actually changed — and amended it before push, for a reason stated precisely: *"it only matters if you use `git bisect`, which Seth does."* A commit message that undersells its diff is a lie the bisect will surface at the worst time. The merge pass ends with a read of the diff against the message, not just a conflict-free merge.

### Rule: Subagents protect your context window; they don't hide work from you.

**Why:** The point of a subagent is to do a large-process task — search 200 files, read 25 retros, trace a call graph across 14 modules — and return a small output: a decision, a summary, a short report. A subagent that writes 5,000 lines you don't read is a liability, not a feature. You've outsourced the work and the accountability at the same time, and when something breaks in those 5,000 lines the debugging session starts from scratch.
**How to apply:** Dispatch when the *output* you need is small but the *process* is large. Research, analysis, searching, reading — good subagent work. Code generation is not exempt from review just because an agent wrote it: if the subagent's job is to write code, you still have to read the code. Context-window savings from dispatching do not transfer to accountability for the code produced.

**Qualifier — reading can be mechanized.** At high parallelism, literal line-by-line review stops being tractable and in mechanical domains becomes unnecessary. Case study 2's seven-agents-per-release rhythm reached every line with *automated gates* — build+test+vet+race, integration tests spinning up every adapter, coverage matrix pinning feature coverage — and the delegation was safe because the pipeline was boring enough to trust (§3). Accountability stays yours either way; "reading" is what's delegable when gates are trustworthy. When they aren't, parallel agent work outruns supervision and the pattern collapses.

*Pin — at very high velocity, the qualifier becomes the mode.* At case study 3's tempo (nine major versions in three days), no human reviewed every line. Gates-as-reading became the default; human line-by-line review was reserved for craft-sensitive code (interaction design, data migrations, auth boundaries). The velocity is the *signal* that all three layers are doing their own jobs.

*The Vitest Cache Incident* (Part V) is this story viewed from the other side: four parallel agents, clean code, green tests — and thirty-eight unrelated tests hanging because the agents' concurrent writes corrupted vitest's module-graph cache in a shared `node_modules`. The fix was mechanical. Finding it required diagnosing an effect that emerged from the parallel *structure*, not from any individual agent's output. What you dispatch, you own — including the parts that emerge from interactions between dispatched tasks. *Pin: dispatch to compress process, not to avoid reading the result.*

> **Field note — case study 1:** *The Subagent Orchestra.* Fourteen subagents across two parallel tracks, 29 files touched, zero merge conflicts — the file map assigned every file to exactly one dispatch before any agent started. Full entry in Part V.

### Rule: Review delegated work in two stages, with reviewers who don't trust the implementer.

**Why:** A single review pass on delegated work has to hold two different questions at once — "does this do what the spec asked?" and "is this good code that will still be good next quarter?" — and in practice the first question eats the second. Worse, a reviewer who starts from the implementer's summary inherits the implementer's blind spots. Splitting the review into two independent stages, each blind to the implementer's report, catches two distinct failure populations that a single combined pass reliably misses.
**How to apply:** After a subagent (or wave of subagents) reports done, dispatch two reviewers in sequence: a **spec-compliance reviewer** that reads the spec and the diff and answers only "is every requirement delivered, and does the verification witness it?" — this is where the revert question (§8) gets asked — and a **code-quality reviewer** that reads the diff cold and answers only "what here is wrong now, or will be wrong someday?" Neither gets the implementer's self-assessment as input. The human integrates the three reports.

The first case study ran this as standing practice through its v6.x waves — *"neither trusting the implementer's report"* is the retro's own phrasing — and the division of labor showed up in what each stage caught. The spec reviewer caught the verification theater (the E2E tests that bypassed the layer under test). The quality reviewers, pass after pass, caught the *not-wrong-now-but-wrong-someday* class that spec compliance can't see: value-equality assertions guarding a reference-identity invariant, an event-handler decoration that swallowed propagation, a regex ported faithfully from an archived config that would have matched human users as crawlers, a `try/finally` that leaked on one path. One wave's retro summarized: three passes, three *different* failure modes caught. None of the three would have surfaced the other two's findings. *Pin: the implementer reports, the spec reviewer checks the claim, the quality reviewer checks the future. Nobody grades their own homework.*

### Rule: Isolate even the "read-only" agents.

**Why:** An agent dispatched to *report* — audit, survey, research — still runs tools, and tools touch state: package managers mutate lockfiles, test runners write caches, builds regenerate artifacts. "Report-only" describes the agent's *assignment*, not its *side effects*. A parallel fleet of readers sharing your working tree can leave it subtly dirty, and the dirt shows up later as a diff nobody can explain.
**How to apply:** Give fan-out agents — including auditors and surveyors — a disposable checkout, a worktree, or at minimum a `git status` check before and after the fleet runs. If a "read-only" pass leaves the tree modified, treat the modification as unexplained state (§9): investigate or revert it before it rides along in someone else's commit.

The fifth case study's audit fleet — four parallel report-only agents, ten minutes, eighteen issues filed — was a clear win with one asterisk: afterwards, the working tree contained a phantom `package.json` version *downgrade* nobody had made, most plausibly a side effect of one auditor running a package-manager command mid-analysis. Harmless, caught, reverted — and a perfect miniature of the failure shape, because it surfaced days later as "why does the tree say 1.0.3?" The lesson isn't "don't run audit fleets" (run them; see §15). It's that *parallel* plus *shared mutable tree* is the §11 topology failure in its mildest form, and the mild form is free to prevent. *Pin: "report-only" is a job description, not a sandbox. Give the fleet its own copy of the world.*

## §14 Plan quality

A plan is a contract you write with future-you. Future-you will be context-deprived, possibly stressed, definitely without the reasoning you had during planning. The plan is either detailed enough to carry that reasoning forward, or it isn't — and if it isn't, future-you will fill the gaps with whatever seems plausible in the moment. That is where features drift and bugs are born.

### Rule: A plan with placeholders is a wish list.

**Why:** "TODO: handle errors later" is the engineer outsourcing the hard part to future-them. Future-them will be confused, stressed, and without context. The hard part has to be done *at plan time*, not at implementation time.
**How to apply:** Every step contains the actual content. No "TBD," no "similar to above," no "implement later," no "add appropriate error handling." If you can't say what the error handling is, you're not ready to plan it yet — go back to brainstorming.

The shape of a placeholder looks reasonable. "Handle edge cases" sounds responsible. "Wire up the error path" sounds thorough. Neither tells you what the edge cases are, what the error path does, or what the downstream behavior should be when it fires. When the agent hits that step, it fills the gap with something plausible. Not wrong, exactly — but not the thing you had in mind, either, and by the time you notice you've built two layers on top of it. The tell is a plan that you can read and nod along to but couldn't execute yourself. If you couldn't hand it to a new team member and walk away, it isn't specific enough. Go back. Name the thing.

**Second-edition clause: a known-failing test deferred to "future work" is a TODO, not TDD.** The placeholder has a sneakier costume: a risk you *did* name, parked in the plan's "known risks" section, with a test you know would fail if you wrote it. The fifth case study caught one in self-review — a grammatical guard listed as a risk while the negative fixture that would exercise it was quietly going to fail on day one. The retro's verdict: *"That's not TDD; that's a TODO."* If you can already write the failing test, the work belongs in this plan, not the next one. Naming a gap is not the same as closing it; the plan gets credit only for the second one.

The self-updating preflight check from the blue-green deploy release is the inverse of this problem stated positively: instead of hardcoding a list of required environment variables in the script — effectively "TODO: remember to update this list when we add a new var" embedded in deploy infrastructure — the script learned to read required vars from the compose file itself. A single grep against the compose YAML. The list is always current because the plan was complete enough to ask "what is the actual source of truth for required vars?" instead of proxying it with a placeholder that would go stale. A plan that asks the right question before deferring never has to ask it again.

> **Field note — case study 1:** *The Preflight That Would Have Saved Us a Week.* An earlier deploy shipped with a missing environment variable because the script's required-vars checklist was hardcoded and three vars behind the compose file. The fix was self-updating validation: the preflight grep'd the compose file for variable references and checked each one was set. The list was always current because nobody had to remember to update it. Self-updating validation beats a manually-maintained checklist, every time. *Pin: if you can't fill in the step right now, you can't implement it right now.*

### Rule: Each step is one action, two to five minutes long.

**Why:** Bigger steps hide complexity and break the TDD rhythm. "Implement the feature" is a chapter, not a step. Small steps also mean small blame radius — when a step fails you know exactly where.
**How to apply:** "Write the failing test" is a step. "Run the test and verify it fails" is a step. "Write the minimal implementation" is a step. If a step would take longer than five minutes, split it. *Qualifier:* the five-minute rule is a *proxy* for "small blame radius." When architecture provides that for free — one-adapter-per-directory, a tight interface contract, a self-contained package with its own test file — a single step can be larger and still satisfy the rule. Case study 2's unit of parallel work was "implement the next adapter" (sometimes thirty minutes or more), fine because a failure was trivially localized to one directory, one package, one agent. If the architecture isn't doing that work for you, hold to five minutes.

The failure mode is a step that sounds atomic but isn't. "Add date range filtering to the admin list" — sounds like one thing. Actually it's: write the query parameter model, add the backend filter clause, write the service method, add the frontend filter state, wire the UI controls, add the E2E test, and handle the edge case where the end date is before the start date. Seven steps collapsed into one. When the agent "does" that step, it makes all seven decisions at once and you get to review seven decisions at once — which means you'll miss the one that's wrong. The Month That Wasn't Thirty Days hotfix is a clean example: the planning step was "write tests for the 30-day date filter." The step that would have caught it was "write a test that generates dates 30 days apart" and then a *separate* step "verify that 30-day offset doesn't cross a month boundary on CI." The first step sounds sufficient; the second is where the flakiness lived. Step granularity is how you surface the complexity before the agent buries it.

> **Field note — case study 1:** *Hotfix 1: The Month That Wasn't Thirty Days.* A test that used a 30-day date offset worked fine most months and failed on calendar days when "30 days ago" crossed a month boundary. The plan step "write tests for the 30-day date filter" was too coarse to name the constraint; a separate step — "verify that the 30-day offset doesn't cross a month boundary on CI" — would have caught it at plan time instead of from a user report. *Pin: if a step takes longer than five minutes, split it.*

### Rule: The plan must cover the spec — and match the codebase.

**Why:** A plan that drifts from the spec produces a feature that drifts from the requirement. Every section of the spec without a corresponding task is not a gap in the plan — it is a gap in the feature.
**How to apply:** After writing the plan, walk every spec section and point at the task that implements it. If a section has no task, you have a hole — not a feature, a hole.

The Four Scoping Gaps release is the canonical case. The spec was clear: the release-automation tool should open Release PRs on the develop branch and trigger deploy when a Release is published. The plan was one step — "add `target-branch` to the config" — that sounded like it covered the spec. It did not. Walking the spec against the plan would have surfaced four separate gaps (cataloged in Part V), each plausible in isolation, none visible unless you walked the spec step by step and asked "which task covers this?" The test for spec coverage is pointed and mechanical: take each requirement sentence and name the task that delivers it. If you can't name one, write one.

The Trust Your Local Tests positive case is worth holding alongside it. That spec broke the work into five phases and was explicit about which items were already solved by earlier phases — one issue was marked "no code changes needed, resolved by an earlier phase"; another had been fixed in a prior release. One whole phase required zero commits. The spec knew this before the engineers did, because they'd written it down. Spec coverage in the forward direction lets you close issues before the agent ever touches the keyboard.

> **Field note — case study 1:** *Four Scoping Gaps, spec-walk edition.* Four scoping gaps in one release-automation plan, each of which looked reasonable in isolation and none of which a spec walk would have allowed. The plan had one step; the spec had four requirements; the math was right there on the page if anyone had written both columns next to each other. *Pin: walk every spec section and name the task that implements it.*

**Qualifier: spec coverage includes *temporal* ordering across systems.** The "plan covers the spec" rule, as written, catches missing tasks. It does not by itself catch *tasks executed in the wrong order across systems whose dependencies cross the boundary between them.* When a plan touches more than one system — code + infrastructure, code + database migrations, code + secrets vault, code + DNS, code + third-party config — the order of operations is part of the spec, even when the spec doesn't say so out loud. A plan that says "add startup-time validation that requires `IP_SALT` to exist" must include the step "add `IP_SALT` to the secrets vault" *and* must execute that step *before* the validation deploys. Otherwise the validation deploys, the process refuses to boot, and the deploy bricks itself the instant it lands. The fix is one line of plan; the cost of skipping it is an outage. Treat cross-system ordering as a first-class spec coverage check: for every task, ask "what must already be true in some other system before this task can run?" — and add the prerequisite as its own earlier task.

> **Field note — case study 1:** *The Guard That Came Before the Secret.* A release added a "fail fast" startup check: if `IP_SALT` wasn't set in the environment, the API would refuse to boot rather than fall back to a hardcoded default that would silently weaken the IP-hashing scheme. The PR was clean. Tests passed. Code review approved it. The deploy script ran. The new container started. The startup check fired. The container exited. The deploy script retried. The container exited. Two retries later the deploy script gave up and rolled back to the previous version. Root cause: the plan added the *guard* but never added the step "set `IP_SALT` in the production secrets vault" — which a teammate had assumed was already there because the variable name had appeared in earlier code. It hadn't been. The fix was thirty seconds (add the secret, redeploy). The lesson is the rule above: **a plan that introduces a precondition must also introduce the step that establishes the precondition's prerequisite, in the right order.** Walking the spec is not enough; you also have to walk the *dependencies between systems* and verify the order of operations across them. *Pin: when a task assumes another system is in a particular state, the assumption is part of the spec — and the step that gets the system into that state is part of the plan.*

**Second-edition clause: a plan can be wrong about the codebase, not just the spec.** Spec coverage catches missing tasks; nothing in it catches tasks that describe a codebase that doesn't exist. The first case study's v6.0 plan said "create new test file" for a module that already had one — with a different mocking convention the new tests then had to be rewritten into — and used field names from the planning conversation (`name`, `arrives_at`) where the real schema said `event_name`, `target_datetime`. Both collisions were found at implementation time, which is the expensive time. This is §5's explore rule cashing out as a plan-quality check: before execution, walk the plan's *nouns* — every file it says to create, every field it names, every function it claims exists — and verify each against the tree. A plan whose nouns don't match the codebase is fiction with good structure. *Pin: walk the spec for coverage, walk the codebase for truth.*

### Rule: Predict the failing output before you run it.

**Why:** A TDD step that says "write the failing test, run it, see it fail" has a silent weakness: *any* failure looks like the expected failure if you haven't said what the expected failure is. A test failing for the wrong reason — an import error, a fixture problem, a different code path — reads as "step complete" and quietly voids the whole red-green contract. Writing the *predicted output* into the plan turns each test run into a self-checking instrument: prediction matches observation, proceed; prediction misses, something unaccounted-for is happening and you just found out at the cheapest possible moment.
**How to apply:** For each TDD step in the plan, write the expected failure concretely — the exception type, the assertion message, the count (`1 failed, 1 passed`). At execution, compare actual to predicted before moving on. A mismatch is not an inconvenience; it is the drift detector firing. Stop and reconcile.

The first case study's consumer-tier plan specified the exact pytest output each step should produce before the production change landed — down to `'NoneType' object is not subscriptable` and the failed/passed counts. Prediction matched observation four times running, and the retro rated the practice *"self-validating in a way no other discipline we've tried has been"* — because every match is positive evidence that your model of the code is current, and every mismatch is an early warning you'd otherwise have received as a production surprise. The cost is one line per step, written when the reasoning is already loaded. *Pin: an unpredicted failure proves nothing. Say what red you expect, then check you got that red.*

### Rule: Descope explicitly. Name what's out, and name why.

**Why:** A plan that only names what's *in* is a plan that quietly hopes everyone agrees on what's *out*. They won't. The items you silently omit will come back as surprise asks during implementation, as scope creep during review, or as "wait, I thought we were doing that" at the retro. Explicit descopes close those loops at plan time, when they're cheap, instead of at implementation time, when they're a conversation you didn't plan to have.
**How to apply:** In every plan, write a dedicated "Descoped" section. List every item the plan considered and decided *not* to do. Give each one a named reason — "hardware-dependent, untestable in CI," "dependency too large for this release," "spec evolves faster than we can keep up," "low value for the complexity cost." A descope with a reason is a negotiable contract. A descope without a reason is an argument waiting to happen. The second case study's final release is the clean example: v1.0.0 cut four items from the plan, each with a one-line reason, and the retro treated those cuts as *part of the release's value*, not as a failure to ship everything. Descoping with reasons is how a plan stays honest about its own boundaries.

> **Field note — case study 2:** *Descoping the Final Four.* The v1.0.0 release cut four items that had been on the roadmap, each with a one-line reason: one required physical hardware and was untestable in CI; one brought in a massive dependency with complex signaling; one depended on an enormous external codebase for a spec that evolves rapidly; one added significant complexity with no proportional value. Each descope was named with its reason in the release plan *and* in the retro. The release still shipped well above its original target, and the four cuts were part of the story, not a shortfall. A plan that can explain what it chose not to do is a plan that has actually been thought about. *Pin: every plan has a descoped section. Every descoped item has a reason.*

**Second-edition clause: descoping has a change-sized sibling — the "things we deliberately didn't do" list.** Descope operates at plan scale; the same honesty is worth keeping at the scale of an individual change, where the considered-and-declined edits are invisible in the diff. From its v0.11.0 retro onward, the fifth case study shipped every change with a list of the adjacent edits it chose *not* to make — didn't lower the triumph threshold, didn't add `excited` to the contentment cluster — each with its reason. The purpose is double. For the humans: *"not adding things you considered adding is the half of the work that doesn't show up in the diff but does show up in the next person's trace."* For the agents: a declined change *with its reason attached* is the only durable defense against a future session "helpfully" making it — the reason is what turns restraint from an absence into an instruction. Mid-cycle bug discoveries get the same treatment: the first case study found a dead method and a domain typo during an unrelated release and deliberately left both, writing it down plainly — *"The bug is right there. It's trivial to fix. … And the right answer is still: not now."* *Pin: restraint that isn't written down will be undone by the next helpful editor — including you.*

> **Field note — case study 2:** *The Config Test That Was Always One Release Behind.* A single test in the project's config package asserted the exact number of registered adapters — a hardcoded integer that had to be bumped every single release because the test pinned a literal instead of deriving it. One retro caught it mid-flight: *"TestDefaultConfig failed with the wrong expected count. The ghost of the previous release, hard-coded in an assertion, politely informing us that we had changed the thing we explicitly set out to change."* The deeper lesson is that tests which pin *literal facts about the codebase* (counts, filenames, fixed lists) are decoupled from the facts they claim to pin, and every release has to remember to update them manually. A test that derives its assertion from the code is self-updating; a test that hardcodes it is a scheduled reminder disguised as an assertion. *Pin: if a test has to be updated every time the code changes, the test is asserting the wrong thing.*

## §15 Audits

*(New as a chapter in the second edition — the first edition carried this as a coda aside, and the evidence outgrew the placement.)* An audit is a different shape of attention than review. A reviewer checks that a *change* is correct; an auditor asks what's wrong with what's *already shipped* — including, crucially, what's wrong with what's already *written*: the claims, the docs, the memory, the beliefs. Four case studies have now run scheduled audits, and the pattern held every time: the audit surfaced more user-visible and risk-relevant findings than the feature release before it, and almost none of the findings had ever generated a bug report. This chapter is the discipline for looking on purpose.

### Rule: Schedule audits on purpose.

**Why:** Feature work, bug reports, and automated tests all organize attention around *changes* and *complaints*. Whole categories of defect generate neither: the security hole nobody has exploited yet, the UX seam every user silently routes around, the accessibility failure your suite scores as passing. The only way those get found is a human (increasingly: a human directing agents) deciding to walk a surface end to end with no goal except *find what's wrong*.
**How to apply:** Put audits on the release calendar as first-class themed cycles — a security pass, a visual pass in both themes on both form factors, a docs-truth pass — each with its own retro. Pick one surface per audit. Do not attach the audit to a feature release; the audit *is* the release.

The fourth case study is the origin evidence, unchanged from the first edition and still decisive: a scheduled security audit surfaced fifteen category-level issues that a year of normal review had walked past (lost-update races, TOCTOU windows, missing UUID validation, regex injection, materialized views silently never refreshed), and a visual audit produced six UX fixes nothing else would have found. Both out-delivered the feature releases they followed. The second edition adds the mechanized form (rule 3 below) and the two rules the fifth case study's audit season forced into words (rules 2 and 4). *Pin: every release that ships only what the bug reports asked for is a release that left work on the table. Audit on purpose.*

### Rule: Claims must be downstream of code, not upstream.

**Why:** Privacy policies, marketing copy, READMEs, PRDs — the project's public claims — have a failure mode all their own: they get written *aspirationally*, describing the system as it's intended to be, and then the implementation never catches up while the claim sits there accruing liability. A claim is a promise a user can hold you to; an unimplemented claim is a broken promise with a timestamp proving how long you didn't notice.
**How to apply:** Treat every outward claim as an assertion requiring evidence, exactly like §8 treats "tests pass." Before publishing a claim, verify it against the running system. At audit time, walk every published claim and probe it. When the PRD and the code disagree, the tiebreak is the retro's question: *which one can a user verify?* — fix that side first.

The fifth case study's "ready for company" release wrote the polish — privacy policy, marketing copy — and its audit season then spent three patch releases un-writing it. The policy claimed paid-tier point-in-time backups (never purchased), claimed no third-party requests (a font CDN loaded on every page), and referenced an analytics provider (never installed). None were lies when read charitably; all were *aspirations formatted as facts*. The retro named the principle: *"claims should be downstream of code, not upstream. Aspirational privacy text is a liability for exactly as long as it's unimplemented — which can be months when nobody's auditing."* The same season caught the PRD asserting a different OAuth provider than the login page actually offered — and the code won the tiebreak, because the login page is the one a user can see. *Pin: publish what the system does. If you want to publish something better, build it first.*

### Rule: The debt is in the seams. Diff what you wrote down against what's true.

**Why:** A codebase under the loop's discipline stays surprisingly healthy — the rot doesn't accumulate in the code. It accumulates in the *seams between the artifacts*: docs asserting what code no longer does, memory asserting what infra never did, dependency manifests drifting from lockfiles, licenses missing, claims aging. No single seam is anyone's job, which is exactly why they rot. And the audit for seams mechanizes beautifully: it's read-and-compare work, the shape agents are best at.
**How to apply:** Every few weeks, dispatch a small fleet of parallel report-only agents — one per seam family: docs-vs-code, security posture, dependency and debt, devops config — each instructed to *diff the written record against observed reality* and report, not fix. Synthesize to one screen. File everything as tickets; fix in a themed cycle. Isolate the fleet from your working tree (§13).

The fifth case study's first audit fleet is the demonstration: four agents, about ten minutes of wall clock, four written reports, eighteen issues filed. The verdict on the code itself: *"the codebase is in genuinely good shape… The debt was in the seams — between what we'd written down and what was true."* The haul was pure seam: the unprotected main branch everyone believed was protected, the backup tier the policy claimed and nobody had purchased, the missing LICENSE, the font CDN leaking IPs, dependency drift. A release later, the retro added the operational note that makes the cadence sustainable: *"The rot itemizes faster than it accumulates if you measure it at all."* Ten minutes of fleet time per few weeks keeps the seam debt enumerated, which is most of the way to keeping it paid. *Pin: the code is watched by the loop; the seams are watched by nobody. Send the fleet down the seams.*

### Rule: Probe the gate. A protection you've never tested is a protection you don't have.

**Why:** Protections — branch rules, backups, rate limits, alarms, permission boundaries — share a cruel property: in normal operation, a working protection and a missing one look identical. Nothing exercises them until the day something goes wrong, which is precisely the day you can't afford to learn they were never on. Beliefs about protections are therefore the single highest-value target for an audit, because they are load-bearing, untested by all ordinary activity, and (per §11's seventh failure mode) amplified by every document that repeats them.
**How to apply:** Enumerate the protections the project believes it has. For each, run the probe that would prove it: the API call that returns the protection object, a test restore from the backup, a request that should be rate-limited, a deliberate error that should page. Attach each probe's command to the belief (§6) so the next audit re-runs it mechanically. A protection with no possible probe should be treated as absent in every risk decision.

*The Lock That Wasn't* (§6, Part V) is the canonical scar: weeks of confident, written, repeated belief in branch protection, dissolved by one API call returning `404: Branch not protected`. The team's response is the part to copy — not just enabling the protection, but reclassifying the belief category: the README now treats an un-PR'd commit on main as a security incident, and the audit fleet's security agent probes the protection object instead of quoting the docs. Companion scars from the same season: the backup tier that existed only in the privacy policy, and the error tracker that had been CSP-blocked into silence for five releases (§8) — three protections, three probes that had never been run, three gates that were open the whole time. *Pin: a gate you've never rattled is scenery. Rattle every gate on a schedule.*

## §16 The retro habit

Every loop ends with a retro. Not a changelog — a retro. The loop is explore → brainstorm → plan → TDD → verify → commit → retro, and the last step is the one that turns a cycle into cumulative learning. Without it, each release is isolated. With it, each release teaches the next one something the last one had to discover the hard way.

**This is the second load-bearing chapter of the playbook, and it is paired with §8.** Verification catches the failure; retros convert it into a rule. Skip verification and the failure ships. Skip the retro and the failure re-ships, forever. Every scar in Part V exists because one of those two disciplines was skipped. Every rule in the rest of this playbook exists because one of those two disciplines produced it. If you remember nothing else from this document, remember that pairing: **verify the work to catch the bug; retro the cycle to kill the class.** Two disciplines, one practice, and the reason the playbook has any rules at all.

**Six projects have independently evolved this discipline.** The first case study's thirty narrative retrospectives, the second case study's nine themed release retros, the third case study's nine-version retro-plus-workflow-document practice, the fourth case study's audit-driven retros, the fifth case study's twenty retros in three months — including one for a session that produced *zero code* (a pure elicitation session; it still had a "By the Numbers" section) — and the fleet's per-panel retros all converged on the same shape without any of them copying from the others. When six differently-shaped projects independently reach for the same tool, the tool is load-bearing, not incidental. The retro is not a ceremony; it is the mechanism by which agent-directed work becomes cumulatively smarter instead of cyclically forgetful. This chapter is load-bearing because the practice is load-bearing because the discipline is load-bearing. Everything else in the playbook is downstream of this.

### Rule: Write retros in voice, not in bullet points.

**Why:** A dry changelog is forgotten in a week. A story is remembered in a year. The retrospective's job is to be *rediscoverable* — and humans rediscover stories, not checklists. Name the bugs by their nicknames. Describe what it felt like. Admit what surprised you. The difference between "Release 5.11 CI/CD Cleanup Summary" and "The One Where Five Small Fixes Grew Teeth" is not aesthetic — it is the difference between a document nobody opens and one somebody searches for by instinct two years from now. If your retro reads like a status report, it will be treated like one: filed, ignored, and eventually auto-archived by a sprint tool.

**How to apply:** Write like a person, not a project manager. If you spent three deploys fixing a bug that turned out not to exist, that's a story worth telling exactly that way. If a Slack integration blew up because Slack's format is named after Markdown the way ketchup is named after tomatoes, say that. The engineer who finds your retro eighteen months from now while Ctrl-F'ing for "Slack notifications broken" will thank you for the specificity. Titles are half the job: "The One Where We Solved The Wrong Bug For Three Rounds" is something someone will click. A version number followed by a feature list is not.

> **Field note — case study 1:** *Titles earn their clicks.* The first case study has 24 retros, from the founding sprint through the most recent pipeline polish. Each one has a title that tells you what it's about. One is "The One Where Five Small Fixes Grew Teeth." One is "The Preflight That Would Have Saved Us a Week." Another is "Hotfix 1: The Month That Wasn't Thirty Days." The retros are the proof of concept for this rule — and they're the source material for many of the field notes in this playbook. *Pin: "The One Where We Solved The Wrong Bug For Three Rounds" is a title someone will click in two years. "Release 5.11 CI/CD Cleanup Summary" is not.*

### Rule: Retros are how the loop learns.

**Why:** Without a retro, every cycle re-discovers the same mistakes. The lesson learned in retro N becomes the rule applied in loop N+1 — but only if retro N gets written. Skipped retros compound. The first skip is free; by the third, you've stopped seeing the pattern you're walking into because you never named it the first time. The instinct to skip is strongest on small releases. Those are exactly the ones that teach the most granular lessons — the kind that aren't worth a postmortem but are worth a paragraph.

**How to apply:** A retro is mandatory at the end of every release, even small ones. It doesn't have to be long. It has to be honest. An honest paragraph beats a dishonest page — and a missing retro is the most dishonest thing you can write, because its absence implies nothing went wrong, and something always went wrong. The Health Check That Wasn't root-cause analysis is three paragraphs and four sentences of "what we learned." That's enough. The Month That Wasn't Thirty Days retro was written in 20 minutes about a flaky test that only failed on certain calendar days. Six months later it was cited in a planning document. Paragraphs don't evaporate; meetings do.

> **Field note — case study 1:** *The One Where Five Small Fixes Grew Teeth.* The Health Check That Wasn't cost three rounds of correct fixes to a non-bug because nobody stopped to ask what `/health` actually returned. The retro named it. The pattern — verify the verifier — is now a rule in §8. That transfer happened because the retro was written. *Pin: skipped retros compound.*

### Rule: Write a retro at the end of every themed cycle, and right after every surprise.

**Why:** "End of every release" is a useful default only when your work has releases. When it doesn't — or when "release" is a blurry calendar thing rather than a shippable thematic cycle — the default collapses and retros start getting skipped for the wrong reasons. The rule that works across contexts is: write a retro whenever a cycle closes *or* whenever something surprises you. Cycles give you scheduled reflection. Surprises give you opportunistic reflection. Together they catch both the slow lessons (the accumulation of small rough edges over a themed slice of work) and the fast ones (the unexpected bug, the near-miss, the "huh, that wasn't supposed to happen"). A cycle without a retro leaks its slow lessons. A surprise without a retro leaks its fast ones.
**How to apply:** Retro at three triggers.
- **At the end of any themed cycle with a shippable boundary.** The §5 nested-cycles rule is the driver: task-level, release-level, and project-level cycles each deserve a retro at their own scale. A task-level retro can be three sentences and a lesson. A release-level retro is the full story. A project-arc retro is the meta-story of all the release retros.
- **At the end of any unit of work that took more than a day**, even if no one calls it a release. If you spent a day or more on something, something happened that is worth a paragraph.
- **Immediately after any surprise** — a major incident, a near-miss, a debugging session that went sideways, a deploy that rolled back, a test that failed in a way that made you say "huh." Surprise is the signal that the cycle already produced a lesson worth extracting *now*, not at the next scheduled boundary. Catch it while the context is hot.

**Do not** write retros on calendar intervals divorced from the work ("weekly retros regardless of whether anything happened"). A retro with nothing to say is worse than no retro, because it teaches the team that retros are performance, not learning. Retros follow cycles and surprises, not dates.

> **Field note — case study 2:** *Nine retros, one per release, none skipped.* The second case study wrote a retro at the end of every single release — nine of them across the major arc, plus the follow-on point releases. Every one had a theme, a story, nicknamed bugs, and a "what we learned" section. The discipline wasn't "retros on Friday"; it was "the cycle closes, the retro gets written, then the next cycle can begin." The retros were the latch between cycles. Without the latch, cycle nine doesn't know what cycle three learned. *Pin: the retro is the latch between cycles. No retro, no latch, no cumulative learning.*

### Rule: A retro has an anatomy. Use it as a scaffold, not a template.

**Why:** "Write in voice, name what broke, end with one extractable sentence" is a *posture*, not a *structure*. A reader who hasn't seen a good retro has nothing to start from. The posture rules (voice, honesty, extractable lesson) produce great retros *once you know the shape they live in*. The shape is the thing that makes a retro skimmable by a cold reader, re-readable by a future engineer looking for something specific, and parseable by an agent extracting lessons. Without the shape, retros drift into freeform memoir that is readable exactly once.
**How to apply:** The scaffold, in five parts. Scale each part to what the cycle actually produced — not every retro needs every part, but the shape is what makes a longer retro legible.

1. **The mission.** One paragraph on what you were trying to do, why it mattered, and what "done" was going to look like. A cold reader eighteen months from now needs this to orient. Skip it and the rest of the retro is context-free.
2. **What happened — the execution narrative.** The story of the cycle. Nicknamed bugs. Surprises. The near-misses that didn't make the commit log. The parts that were harder than expected and the parts that were easier. Written in voice (§16 rule 1), not in bullet points. This is where the humans live.
3. **The numbers.** Dry metrics for the people who came for them: counts, times, sizes, test results, dependency deltas, lines added and removed. Not the whole build output — the handful of numbers that characterize the cycle. This section makes the retro skimmable by a reader with a specific question and no time for the story.
4. **What we learned — the extractable lessons.** Stated explicitly, not left for a reader to infer from the story. One sentence per lesson, with the lesson first and the context second. This is the section the agent and future-you will Ctrl-F for. It's also the section that feeds the next cycle's plan (§5 nested cycles). If a lesson isn't in this section, it isn't going to reach the next loop.
5. **What's next.** The handoff to the next cycle. What this retro is telling the next loop to do differently, to watch for, or to try. A one-line *"what's next"* is enough; the point is to make the lesson actionable on the very next cycle.

Not every retro needs all five. A one-day hotfix might be three sentences and a lesson. A release retro probably wants all five. The anatomy is a scaffold for when the retro is larger than a paragraph — it's what keeps a long retro from becoming an unstructured memoir that nobody re-reads. The second case study's nine release retros all follow roughly this shape: mission, waves (their execution-narrative section), numbers, what we learned, what's next. They read like stories *because* they have skeletons underneath.

> **Field note — case study 2:** *The retro as story with a skeleton.* Every release retro opens with a one-sentence mission, walks through waves of execution with nicknamed adapters and discovered gotchas, lists the raw numbers in a "The Numbers" section, extracts lessons in a "What We Learned" section, and closes with "What's Next." The shape is unmistakable from retro to retro, but the voice is different every time — each has its own rhythm, its own jokes, its own arc. The skeleton is what lets the voice happen: when the structure is handled, attention goes to the prose. *Pin: the anatomy is the scaffold that frees the voice.*

### Rule: A retro has three audiences: you next month, your team, and the agent next time.

**Why:** The retro you write today is read by future-you when you're trying to remember what you did, by teammates who weren't there, and by an agent that will be asked to read this retro as context for a future task. All three need different things — future-you needs the full story, teammates need the context they missed, and the agent needs a clean extractable lesson — but all three can get what they need from the same document if you include the lesson explicitly, not just as something implied by the narrative.

**How to apply:** Every retro ends with "what we'd do differently" — a sentence, not a section. That sentence is the thing the agent extracts. That's the sentence you'll Ctrl-F for next month. It doesn't have to be long. The Four Scoping Gaps retro's extract is: "Walk every spec section and name the task that implements it before starting the work." Trust Your Local Tests': "If local and CI aren't running the same test suite, fix the suite, not the gap." Those sentences are now rules in §14 and §8, respectively — they got there because they were written down explicitly, not left inside the story for a reader to infer. The story is for the humans. The explicit lesson is for everyone, including the agent that hasn't read the story yet. *Pin: every retro ends with one sentence the agent can extract.*

### Rule: The retro unit is the arc, not the tag — and when a retro was wrong, write the reversal down.

**Why:** Two honest pressures emerged once the practice ran long enough, and both needed naming rather than denying. First: at real velocity, some tags are too small to teach anything alone — three same-day patch releases are one story, not three. Mechanically requiring a retro per tag produces padding, and padding teaches the team that retros are paperwork. Second, and more uncomfortable: retros themselves can encode wrong lessons. A retro that celebrates a decision feeds that celebration into the next loop with all the authority this chapter gives it — and if the decision was wrong, the loop learns the error *as a lesson*.
**How to apply:** Let the retro unit follow the *narrative arc*: a cluster of same-day patches consolidates into one retro, provided the consolidation actually happens — the arc rule is a license to batch, never a license to skip. And when later work reverses something an earlier retro praised, the new retro says so explicitly: what we said, why we now think otherwise, and the principle that emerges. The retro directory is a lab notebook, not a trophy case; its value is that it's *true*, including about itself.

The fifth case study supplied both halves in one season. Three same-day patch releases got no individual retros; the next minor release's retro told their story as one arc, with the reasoning stated: *"The small releases were small… the retrospectives directory is allowed not to be"* a one-to-one record of every tag. Meanwhile, the project's v1.0 retro had *celebrated* its new marketing paragraphs as exactly the right transparency — and three of that release's claims turned out to be aspirational (§15), reversed across the following patches. The reversing retro didn't quietly move on; it stated the counter-norm: *"The right thing to write in a retrospective is not always 'we got it right' — sometimes it's 'we got it wrong, here's what we did instead, and here's the principle.'"* The same project also pressure-tested the boring end: when the agent recommended skipping a quiet release's retro, the human overruled, and the resulting document earned its keep with one line — *"The retro is boring because the work was on schedule. We should not stop writing the boring ones."* *Pin: batch retros by arc, never skip the consolidation — and when the loop learned a wrong lesson, the correction is itself a retro-worthy lesson.*

---

The first case study has thirty retros behind it, written across more than two years, each one a story the field notes in this playbook have been borrowing from. Part V collects the ones worth reading in full — alongside entries from the other five case studies — and here they are, ready when you are.

---

# Part V — Field Notes from the Case Studies

Every rule in this playbook has a bruise under it. The entries below are where the bruises came from — compact re-tellings of the bugs that taught us the rules, each one naming the chapter it grounds. Read them in any order; each is self-contained. The headlines are whimsical on purpose, because a bug with a nickname is a bug you remember.

The stories are grouped by the *kind* of problem they illustrate, so a reader scanning for "I'm having a verification problem" or "my parallel agents are stepping on each other" can jump to the right neighborhood first. Within a group, they're in no particular order.

## Verification & feedback loops

*Stories where the test was green, the status was "ok," and the thing was broken. The bruises here all trace back to verifying the wrong surface or trusting a signal that was answering a different question than the one you were asking.*

### The Health Check That Wasn't (v5.11.0)

**What happened:** Three deploys in a row, `git_sha` came back `unknown` in the health response after every release. We rebuilt the Docker image pipeline four different ways — shell export of `GIT_REV`, compose env file, compose override, `--build-arg` — and each fix deployed cleanly and "didn't work."
**What we thought was happening:** The build-arg plumbing was dropping `GIT_REV` somewhere between the YAML and the container, and we just had to find where.
**What was actually happening:** The verification curl was hitting `/health`, which returns `{"status":"ok"}` and has never had a `git_sha` field. The full health JSON lives at `/api/v1/health`. The producer was never broken. We spent three deploys fixing a hole that wasn't there because the verifier was looking through the wrong window.
**The lesson:** §8 — health checks must check health, and verification curls must hit the endpoint that reports it. *(See DevOps Playbook Gotcha #8.)*

### Verify What You Shipped, Not What You Built (v5.9.0)

**What happened:** The deploy script reported success. The new container had started. Every status check was green and every log line said "ok." The live site was still serving the old version.
**What we thought was happening:** A browser cache, a CDN delay, something between the user and the server — not the deploy itself.
**What was actually happening:** An orphan container from the previous compose definition was still holding the port. The new container was running and healthy and completely unreachable from the internet, because nginx had never flipped to it. "I started the container" had become a stand-in for "the container is serving traffic." The fix was one line of verification: one `curl` against the public health URL, comparing the response body to the SHA we just built.
**The lesson:** §8 — evidence before assertions, against the URL the user will actually hit.

### Trust Your Local Tests (v5.7.0)

**What happened:** For three releases running, the backend test suite passed on every laptop and failed intermittently in CI. Nobody trusted "local green" anymore — every PR got a manual "but did it pass in CI?" even after it had passed in CI.
**What we thought was happening:** Flaky tests. A Redis timing issue. Something environmental we'd catch eventually.
**What was actually happening:** Local used SQLite via a `is_testing` branch in `database.py`; CI used Postgres. Every release, the gap introduced a new dialect-specific failure, and every release we patched the symptom. The rescue was a single cycle of the full loop applied to the gap itself — rip the SQLite branch out, make `conftest.py` truncate a shared Postgres engine between tests, force every environment through the same path.
**The lesson:** §8 — verify in the environment that matters, and §12 — you cannot out-discipline a missing rail.

### The Cache That Worked Locally And Lied In CI (v5.4.0)

**What happened:** We refactored the cache layer so Pydantic models flowed through Redis, shipped the PR with a green local suite, and watched an image-generation pipeline explode in CI the moment the deploy ran.
**What we thought was happening:** A Redis connection issue, or maybe a dependency version mismatch in the CI image.
**What was actually happening:** Someone had written `json.dumps(model, default=str)` as the serializer. `default=str` does not dictify a Pydantic model — it calls `str()` on it and produces the model's *repr*, a string that looks like Python source. Local was green because local used an in-memory cache with no serialization path at all; the model went in as an object and came out as an object. CI had actual Redis, which needed JSON, which exposed the bug.
**The lesson:** §8 — if your local doesn't run what CI runs, your local green is a lie.

### The Doorbell That Never Rang (v4.2.0)

**What happened:** Audit logging shipped. Backend tests green, frontend tests green, a beautiful admin page that rendered an audit table. The table had zero rows in it. Every admin action completed successfully and left no trace.
**What we thought was happening:** A query filter bug, or a timezone off-by-one making events land outside the default window.
**What was actually happening:** Nothing in between the two halves emitted an audit event. Backend exposed the read endpoint. Frontend rendered the list. No service call anywhere in the admin routes actually fired the emit. Both halves were tested in isolation; nobody had wired the doorbell to the button. A thirty-second click in a real browser would have caught it.
**The lesson:** §8 — "tests pass" is not "feature works." Open the thing and use it.

### The Comparison That Quantum-Superposed Into Nonexistence (case study 1)

**What happened:** A "Comparison of the Day" feature shipped to the homepage. The component was implemented correctly, the data fetched correctly, the unit tests passed, the integration tests passed, the deploy was clean. It never appeared on the page.
**What we thought was happening:** A caching or CDN bug swallowing the response on first paint.
**What was actually happening:** The component was wrapped in `{!isLoading && <Feature />}`, and on the homepage's particular data path `isLoading` never resolved to false because of a stale-cache race condition in a sibling component. The feature rendered into a virtual DOM that nobody ever painted. If *The Doorbell* is about missing wiring (the event never fired), this is the inverse: *the bell rang, perfectly, into a room nobody could see into.*
**The lesson:** §8 — a green test suite tells you the parts work; only a real session in the real browser, on the real page, with the real data, tells you the user can use the thing.

### Two Hotfixes in One Release, Same Gap (case study 3)

**What happened:** A data-layer migration from manual `useEffect`/`useState` to TanStack Query shipped with 161 unit tests green and broke cache-hit paint within 24 hours of release. Its stablemate, shipped the same day for the same reason, was a touch-vs-mouse guard that had been written and tested on desktop only and silently blocked single taps on iPad Safari.
**What we thought was happening:** Both changes were mechanical — data layer swap and an input-event refactor. Unit tests covered the data behavior and the handler logic. Nothing to see here.
**What was actually happening:** The TQ bug: a side effect moved inside `queryFn` never ran when TQ served cached data. The iPad bug: the guard had never been exercised on an actual touch device. Both failures slipped a full green suite because no test exercised the *interaction pipeline* on the real substrate — cache-warmed data + real click, or real gesture on a real device. A single Playwright click against a pre-warmed cache would have caught the TQ bug in five seconds; a real tap on a real iPad would have caught the other.
**The lesson:** §8 — when you're swapping a foundation layer (data layer, auth, router, state), the test gap is always on the *interaction* side, because the unit tests were written for the *old* substrate's assumptions.

### The bufconn Gap (case study 2)

**What happened:** One protocol adapter had full unit-test coverage using an in-memory connection that bypassed network transport. Every test passed beautifully.
**What we thought was happening:** The adapter was ready to ship.
**What was actually happening:** The first smoke test from a real client against the running server discovered that a required discovery feature had never been enabled, and the client had no way to find the service. Fix: two lines. The in-memory loopback tested *logic*; it did not test *deployment*. The retro's one-liner: *"this is not an argument against unit tests; it is an argument for also just… running the thing."*
**The lesson:** §8 — your tests can only catch the things they actually test. A complete suite against the in-memory path is not a complete suite against the wire.

### The Tests That Would Have Passed Anyway (case study 1)

**What happened:** A fix restored nginx routing so social-media crawlers could reach the link-preview endpoint. The change shipped with a suite of E2E tests. All green.
**What we thought was happening:** The routing fix was verified end to end.
**What was actually happening:** The tests hit the backend endpoint directly and the dev server directly — bypassing nginx, the exact layer being fixed. Reverted, every test would still have passed. A reviewer asked one question — *would these tests pass if you reverted the change?* — and the theater collapsed. The remedy was honesty in two moves: rename the test file to what it actually pins (the endpoint contract), and move the real verification into the post-deploy smoke test, the only place that exercises nginx.
**The lesson:** §8 — the revert question is *"the sharpest tool we have for distinguishing verification from verification theater."*

### The Formatter That Ate the Evidence (case study 1)

**What happened:** A consumer API-key tier shipped with forty green tests and a plan that ended with a mandatory manual integration task. The manual task found two production-killers in one afternoon.
**What we thought was happening:** Forty for forty; the manual step was belt-and-suspenders.
**What was actually happening:** First, the production compose file explicitly allowlists which env vars reach each container, and the new `CONSUMER_API_KEYS` wasn't on the list — the feature was *"entirely correct in code review and entirely broken in production."* Second, the logging pipeline's formatter had been silently discarding every structured `extra={...}` payload since the day it was configured; the test suite's log-capture fixture passed because it reads records *before* any handler runs. Neither failure was *reachable* by a unit test — one lived in an ops file no test loads, the other past the exact boundary the fixture stops at.
**The lesson:** §8 — *"when testing whether a feature delivers, not whether it runs, look at the wire output, not the test fixture."*

### The Perimeter That Trusted the Polite Client (case study 1)

**What happened:** Native mobile clients started getting 403s from endpoints that worked flawlessly in every browser and every test — and had for three major versions and 311 CI runs.
**What we thought was happening:** A mobile-side auth bug; the captured response headers said `X-Authenticated: true` right next to the 403.
**What was actually happening:** A "defense-in-depth" perimeter middleware had four authorization checks that were secretly *sequential* — three of them dead code — and the surviving check keyed on the Referer header, which browsers send on every XHR and the native HTTP stack never sends. Every test client was the polite kind. The fix was 21 lines: trust the request the upstream auth had already authenticated.
**The lesson:** §8 — test with the rudest client you support. A guard that only ever meets polite clients is a guard nobody has met.

### The Smoke Alarm the Security Release Disarmed (case study 1)

**What happened:** During an audit, someone noticed the frontend error tracker had reported nothing — nothing at all — for five releases.
**What we thought was happening:** Five quiet releases.
**What was actually happening:** A security release had tightened the Content-Security-Policy to `connect-src 'self'`, which blocked the error tracker's own reporting endpoint. The release that hardened the app disarmed its smoke alarm, and nothing downstream of a dead instrument ever complains. The retro: *"We have not yet decided whether this is hilarious or appalling."*
**The lesson:** §8 — observability is part of the system; verify it observes. Fire a deliberate test error through the pipe now and then.

## Scope, plans, and surprises

*Stories where the plan looked obvious, the scope felt small, and the thing that bit was the work nobody had named yet. These are the bruises that come from skipping the brainstorm, leaving a placeholder in a plan, or trusting a fan-out to hide coordination problems it never could.*

### Four Scoping Gaps in One Release (v5.11.0)

**What happened:** A one-line release-automation config fix was supposed to make Release PRs open against the develop branch and trigger the deploy workflow when a Release was published. The fix shipped. Nothing worked. Then the second fix shipped. Nothing worked.
**What we thought was happening:** A typo in `release-please-config.json` — add `target-branch`, move on.
**What was actually happening:** Four separate scoping errors, each plausible in isolation. `target-branch` is an action input, not a config key — the JSON accepted it silently. There was no anchor Release, so release-please scanned to the start of the repo. The merge commit used `release:` as its type, which is not a conventional-commit type and was silently skipped. And release-please plus the default `GITHUB_TOKEN` does not trigger downstream `release: types: [published]` workflows.
**The lesson:** §14 — walk every spec section and name the task that implements it.

### The naivePlural Drift (case study 4)

**What happened:** A small `naivePlural()` helper existed as three copy-pasted duplicates across three edge functions. Over one release cycle, one of the three copies had an irregular-noun branch extended with `tooth → teeth` and `goose → geese`; the other two didn't. The user-visible bug: the same entity rendered as "1 mouse" on one page and "1 mice" on another, with a third path still saying "1 mouses."
**What we thought was happening:** A rendering inconsistency — maybe a stale cache on one of the pages.
**What was actually happening:** Three copies of the same function that had *drifted silently*. Nobody owned the reconciliation because the copies were small enough individually that none of them flagged in review. The duplication was fine the day it shipped; what it became was a bug. The fix was to extract the helper into a shared module — the extract that, under §7's rule, had been deferred as "the pattern hasn't stabilized yet." It had. The stabilization was invisible because nobody re-checked.
**The lesson:** §7 — duplicates are fine when the pattern is still finding its shape; duplicates that have already drifted are a bug waiting to be reported. Re-check at each correction, not just at the third.

### The Four-Fix WCAG Contrast Cycle (v5.5.0–v5.6.0)

**What happened:** Across two releases, four separate WCAG contrast violations slipped into the UI — each one a utility-class color swap picked by eye that looked fine in the design tool, failed the axe-core suite on the next run, and got fixed with a one-class swap.
**What we thought was happening:** We thought we were calibrated to the contrast rules by now. After the second one, we thought we were calibrated *now*. After the third, we stopped guessing.
**What was actually happening:** Nothing was broken — the automated rail was catching exactly what it was designed to catch. The humans were the slow learners. The right move was to stop pre-judging contrast by eye and let the axe-core evidence do the approving.
**The lesson:** §9 — when the blast radius is small and the test is automated, confirm by evidence, not by ceremony.

### Hand-Rolling the Legacy State Machine — Right Call, Wrong Call (second case study, v0.3.0)

**What happened:** The second case study was implementing a batch of early-era protocols. One of them is the pathological one — a decades-old protocol that uses *two connections* for what every other protocol accomplishes with one, with a secondary data channel that requires hand-negotiated host/port encoding in a format nobody else uses. The team considered importing a library and decided instead to hand-roll the entire state machine from the standard library. ~150 lines. Pure stdlib. Listener, data channel, directory listing, file transfer. All of it.
**What we thought was happening:** This is a judgment call about dependency weight versus implementation cost. The project's ethos was zero-dependency-if-possible; the protocol was in scope; the hand-roll was tractable; we'd save the dep.
**What was actually happening:** The retro named the tension directly: *"Right because it kept the dependency count low and forced us to truly understand the data-channel negotiation. Wrong because we now truly understand the data-channel negotiation, and that knowledge cannot be unlearned."* The hand-roll worked. It shipped. The test suite ran clean. And the team now carries around the protocol's internal mechanics as permanent mental residue — the bespoke host-port encoding, the ephemeral listener, the two-connection dance, the state transitions that make sense only if you were in the room when the spec was written. Every unit of knowledge about a legacy protocol you gain is a unit of attention you cannot reclaim for anything else. The dependency you didn't import was free; the attention you spent internalizing the protocol is not.
**The lesson:** A counter-weight to "always reach for a library" *and* to "always hand-roll for purity." The real question isn't library-vs-hand-roll — it's whether the knowledge you'll acquire during the hand-roll is worth the craft attention it will permanently occupy. Sometimes yes (the team's zero-dependency posture became a source of genuine craft pride across nine releases). Sometimes no (the legacy protocol's mechanics are nobody's art). The judgment call connects back to §1's three-layer thesis: a hand-roll is a decision to spend *craft* attention on *mechanics*, and that trade is only worth it when the mechanics are themselves part of the craft. Here they aren't. The zero-dependency posture as a whole is. The retro was honest about the tension instead of pretending the hand-roll was unambiguously correct, which is the only reason the lesson survives.

### Fred Was Almost an Uncle (case study 5)

**What happened:** A subagent was dispatched to write reply templates in the voice of a beloved children's-television host. The draft came back warm, kind, encouraging — and generic. ("Yeah. That's a real one.")
**What we thought was happening:** The dispatch was fine; the model just needed another pass.
**What was actually happening:** The dispatch prompt said "the right energy" *in passing* and pointed at a JSON file — not at the twenty lines of seed library that actually specified the voice (the permission-granting constructions, the load-bearing second person). The human's review was one sentence: *"these don't sound like fred rogers. Are you sure?"* The re-dispatch put the voice spec in the prompt verbatim and required the agent to produce three too-saccharine and three just-right calibration samples *before* drafting. The second draft was the man himself: *"You're a person who carried a worry without making a fuss about it… You did that."*
**The lesson:** §1 and §4 — for taste-heavy delegation, pointing at the spec is not the same as putting the spec in the context. Demand calibration samples before the real output, and route the result past the human ear.

### The Streak in a Trenchcoat (case study 6)

**What happened:** During a pre-code elicitation session for an anti-optimization health app — a product whose ethos explicitly forbids gamification — the agent proposed a success metric: "you use it daily, unbroken."
**What we thought was happening:** A reasonable north star for a daily-use product.
**What was actually happening:** The metric was *"a streak in a trenchcoat"* — the exact engagement mechanic the product forbids, smuggled into the meta-layer by pattern-matching on what success metrics usually look like. The human's verdict on streaks ("Streaks stink of judgement") reversed the metric out of the specs entirely. The catch happened only because the elicitation session made the agent state its model of success out loud before any of it was load-bearing.
**The lesson:** §4 — audit the agent's proposed north stars against the product's own ethos. The agent optimizes toward the pattern, and the pattern is somebody else's product.

## Diagnosis & the lab

*Stories where the fix was drafted before the evidence was read — and what happened when a project started shipping instruments instead of guesses. The bruises here come from trusting a diagnosis (the ticket's, the agent's, your own) that no trace had ever witnessed.*

### The Hedge That Wasn't (case study 5)

**What happened:** A ticket reported that hedge phrases ("just a little bit") were suppressing heavy-affect detection in a journaling classifier. A hedge-ignore subsystem was designed and half-drafted.
**What we thought was happening:** Hedges were diluting the signal; the fix was to strip them before classification.
**What was actually happening:** The persisted trace — newly available, because the previous release had shipped the diagnostic surface instead of a fix — showed the misfired entry had never matched anything: the word `sad` simply wasn't in the heavy-signals list, which spoke only in extremes (`devastated`, `hollow`, `grief`). Four lines of mild-affect vocabulary fixed it. *"It would have been a beautiful fix for a problem that didn't exist."*
**The lesson:** §10 — the ticket's diagnosis is a hypothesis. Read the trace before believing the issue.

### The Word the Domain Was Named After (case study 5)

**What happened:** A rest-and-recovery keyword domain kept missing obvious entries.
**What we thought was happening:** Edge cases; the list needed a few more synonyms.
**What was actually happening:** The agent-authored wordlist contained every verb of resting (`napped`, `slept`) and every resting-place noun (`porch`, `hammock`) — and not the word `rest`. *"The bare noun. The thing the entire domain is named after. Missing… We added it. The fixture passed. We laughed."* The sibling contentment cluster had the same disease: `simple pleasures` and `at peace`, no `happy` — vocabulary *"designed by someone trying to write literature about contentment."*
**The lesson:** §1 — agent-authored heuristics encode the author's vocabulary, not the user's. Only real inputs close the gap.

### The Marcus Monopoly (case study 5)

**What happened:** After a new reply register shipped, the user reported that one historical figure was answering *every* playground test.
**What we thought was happening:** The rotation logic was broken; a fix to production fairness rules was taking shape.
**What was actually happening:** The fairness rule — a figure not seen recently beats all others — is correct in production, where every reply becomes history. The debug playground loads history once and never writes back, so the one figure absent from the last sixty days won every single draw: a fairness rule producing perfect unfairness against frozen state. The user made the call: *"I think the logic is right. I think we need to fix /debug so that it ignores the anti-repeat logic, since it will never save."* Production shipped byte-identical; the playground got a bypass flag.
**The lesson:** §10 — exploration mode is not production mode. When the bug only reproduces in the lab, suspect the lab's frozen state first.

### The Silence That Was the Symptom (case study 1)

**What happened:** A pre-planning survey agent, sent to read the nginx layer before a routing release, mentioned almost as an aside: "nginx blocks social crawlers by default."
**What we thought was happening:** A configuration note for the backlog.
**What was actually happening:** Four curls confirmed that every shared link's preview had been a 401 JSON blob on every social platform for three releases — the link-preview generator built two versions earlier had never once been reachable from the surfaces it existed to serve, dropped in a later nginx consolidation. No one had filed a bug, because broken share previews don't generate bug reports; friends just don't click. *"The silence is the symptom."* The two-issue release became three, and the third was the one production needed most.
**The lesson:** §5 and §10 — exploration finds the bugs nobody filed. Features whose failure mode is silence need scheduled probes, because no user will ever tell you.

## Tooling & environment traps

*Stories where the code was fine and the tool was lying. Bash buffering its own script, a token that couldn't wake the next workflow, a Slack dialect cosplaying as Markdown — the bruises here all come from trusting a tool to behave like its documentation said it did.*

### The Actions Token That Won't Wake the Next Workflow (v5.10.0)

**What happened:** We moved release creation to release-please and the deploy pipeline went silent. Merging the Release PR created the GitHub Release exactly as intended; the `deploy.yml` workflow, wired to `release: types: [published]`, never fired.
**What we thought was happening:** A YAML trigger typo, or maybe a branch-protection rule eating the event.
**What was actually happening:** A documented GitHub Actions behavior: PRs and Releases created by a workflow using the default `GITHUB_TOKEN` do not trigger downstream workflows. The "fix" was technically working — a Release was created — but the next stage was built on a chain that the token could not carry across. A PAT or GitHub App token was required for the handoff.
**The lesson:** §8 — verify in the environment that matters; a green release event doesn't prove the downstream workflow saw it.

### Bash Buffers Scripts In Memory (v4.2.0)

**What happened:** The footer on the live site read `rev unknown` after deploy. The footer had displayed the git hash since v4.0.0. It worked in dev. It worked in CI. It did not work in production. We pushed fix after fix to `deploy.sh` and watched the old buggy version run to completion anyway.
**What we thought was happening:** Git wasn't pulling, or the runner had a stale clone, or the `GIT_REV` export was being eaten somewhere in the compose plumbing.
**What was actually happening:** Bash reads a script into a memory buffer when it starts executing. `git pull` updated the file on disk — the new bytes were right there — but the running shell kept executing its in-memory copy of the old file. Any edits after the `git pull` line never took effect on the run that pulled them. The fix is one line: after the pull, `exec "$0" "$@"` to re-read the script from disk.
**The lesson:** §11 — when the obvious fix doesn't stick, stop editing and dump the raw state. *(See DevOps Playbook Gotcha #9 for the `exec "$0" "$@"` self-reexec pattern.)*

### Slack mrkdwn Is Not Markdown (v5.10.0)

**What happened:** CI notifications started going out to the team channel with raw `**asterisks**` and `[link text](urls)` rendered as literal characters instead of formatting. The messages looked like a drunk bot.
**What we thought was happening:** A webhook payload escaping bug — something double-encoding the Markdown before Slack got it.
**What was actually happening:** Slack's mrkdwn is not Markdown. Bold is `*single asterisks*`, not `**double**`. Links are `<url|text>`, not `[text](url)`. The webhook was delivering exactly what we'd written; we had written the wrong dialect. The fix was a full conversion to Block Kit, where the formatting contract is explicit instead of cosplaying as a familiar one.
**The lesson:** §8 — verify in the environment that matters, including the one that renders your message. *(See DevOps Playbook Gotcha #6 and Phase 6 for the Block Kit migration.)*

### The Truncated Secret (case study 6)

**What happened:** A serverless function kept rejecting a signing secret that had definitely, verifiably been set. The code that validated it came under suspicion.
**What we thought was happening:** A validation bug, or a subtly wrong secret.
**What was actually happening:** The platform CLI's `env:get`, used to source the secret into the session, returned a **20-character slice of a 64-character value** — and exited zero. The function was correctly rejecting garbage; the system was working. The retro's warning: tooling can hand you a truncated value *"and smile while it does it."*
**The lesson:** §2 and §9 — when a sourced secret is rejected, check its *length* before doubting the code. Verify properties of secrets (length, prefix), never by printing values.

### The Day the Landlords Came Calling (case study 1)

**What happened:** In one release: the CI provider refused all five jobs — a billing dispute two vendors above the project — forcing a local fast-forward merge and a by-hand run of the deploy script. An hour later, the issue tracker's free-tier cap blocked filing the regression the release had just found.
**What we thought was happening:** A CI outage; then a tracker hiccup.
**What was actually happening:** Two SaaS dependencies failing on the same afternoon, both unrecoverable *through* the failed service. The deploy survived because the deploy script had always been runnable by hand. The bug survived because it got written to three tracker-independent places — the changelog, memory, and the retro. The aftermath is visible in the project's instructions file: the tracker was demoted, and the backlog went local-first.
**The lesson:** §3 — every automated rail needs a rehearsed manual fallback, and every found bug needs a persistence path that doesn't depend on someone else's billing department.

### The Redirects File That Outranked the Config (case study 6)

**What happened:** Wiring the third sibling app to the same API-endpoint pattern as the first two — "muscle memory" by now — produced 404s and SPA HTML from `/api/v1/*` routes that were configured identically to the working apps.
**What we thought was happening:** The pattern was identical; something environmental had to be wrong.
**What was actually happening:** The third app had a `public/_redirects` file whose bare catch-all **outranks** the `netlify.toml` redirects the pattern relied on. *"The pattern we'd called 'identical' was identical in the code and different in the routing, and the difference lived in a file we hadn't thought to look at."* The third repetition is when you stop reading the instructions — and when the platform's precedence rules stop forgiving you.
**The lesson:** §5 — explore before you plan applies to config, too. "Identical to the last one" is a claim about every layer, including the ones you didn't diff.

## Trust & blast radius

*Stories about authorization, denial paths, and the moments when "yes" in one direction quietly failed to mean "yes" in every other direction. The bruises here come from forgetting that the interesting rules live in what gets refused, not in what gets allowed.*

### The Admin Who Couldn't Fire Herself (v4.3.0)

**What happened:** RBAC landed for the admin panel. The interesting bugs weren't in the "yes" paths — those were one-liners. They were in the "no" paths: self-role-change, self-deactivation, self-deletion, privilege escalation via update.
**What we thought was happening:** RBAC is a matrix of allows; fill it in and you're done.
**What was actually happening:** Trust in one direction ("you are an admin") does not generalize in every direction ("therefore you may fire yourself"). Half a dozen explicit refusals had to be written on purpose, one by one, because each was a line the matrix didn't draw by default. The last-superadmin protection came later still, in v5.6, because we missed it the first time too.
**The lesson:** §9 — authorization is scoped, not blanket. Every yes is for one action.

### The Default That Was Admin (case study 4)

**What happened:** A refactor of the edge-function pipeline introduced a shared handler signature with an optional `client:` parameter — `'admin'` or `'anon'` — that **defaulted to `admin`** when unspecified. Existing functions were fine because they passed the right client explicitly. Every *new* endpoint written afterward silently ran with admin privileges because *not thinking about the client* meant getting the admin one.
**What we thought was happening:** The new signature was ergonomic; the existing callers were correct; the new callers were also correct because they compiled.
**What was actually happening:** A security review in the next release caught two endpoints (a public stats endpoint, a public leaderboard) running with admin keys for a full release cycle. No data leaked because the underlying RLS happened to cover it, but the privilege gradient was inverted. Fix: one line — change the default to `anon`.
**The lesson:** §9 — the unsafe default is the one that gets used by everyone who didn't think about it. Make the safe choice the default; require explicit opt-in for elevation.

## The record that lied

*Stories where the written context — memory, docs, comments, the harness itself — asserted something that was never true, and every reader repeated it with confidence. The bruises here come from treating written words as witnesses. Only a command output is a witness.*

### The Lock That Wasn't (case study 5)

**What happened:** The instructions file said main was branch-protected. The auto-memory said so. Weeks of PR descriptions said so. During an audit, someone finally ran the API call.
**What we thought was happening:** Nothing — that's the point. The gate appeared to be doing its job.
**What was actually happening:** `404: Branch not protected`. The protection had never been enabled. *"Both were lying. Not maliciously. Just confidently. For weeks."* The gate had appeared to work because no one had tested whether the gate existed. The fix took two minutes; the reclassification took longer — the README now treats an un-PR'd commit on main as a security incident, and the belief carries its probe. The strange small joy from the retro: after enabling protection, *"the auto-memory was not corrected. It is now correct without modification."*
**The lesson:** §6 and §15 — a belief you've never probed is a hypothesis. A protection you've never tested is a protection you don't have.

### The Header Nobody Read (case study 1)

**What happened:** An nginx config comment confidently documented that the backend trusts an `X-Forwarded-By` header as part of the security perimeter.
**What we thought was happening:** A load-bearing control, faithfully described.
**What was actually happening:** `grep -i x-forwarded-by backend/` returned zero matches. No middleware had ever read the header. The comment was born false and had survived every review since, because *"a documentation lie about a security control … looks load-bearing in code review. It survives audits"* — audits that read the docs instead of probing the claim.
**The lesson:** §11 (failure mode seven) — written context is an amplifier, not a witness. Grep the claim, not the comment.

### The Edit That Reported Success (case study 5)

**What happened:** Route components shipped to production that nothing routed to — pages that existed in the bundle and were unreachable in the app.
**What we thought was happening:** The components had been wired; the harness said the edits succeeded.
**What was actually happening:** The harness's edit tool had, at least once, reported success without persisting the change. The components compiled cleanly in isolation, CI stayed green, and the missing `<Route>` entries were invisible until a human clicked. The harness is software; software lies under load.
**The lesson:** §2 — trust harness claims the way you trust "tests pass": with evidence. For edits that matter, the witness is `git diff`, not the tool's return status.

## Parallel agents & architecture

*Stories where the individual agents did clean work and the result broke anyway — because the shape of the collaboration had a hidden incompatibility with the tools underneath it, or because an effect emerged from the parallel structure that no single agent could see. Fix the topology, not the agents.*

### Parallel Work (case study 1)

**What happened:** Two agents dispatched to write tests in parallel — one in Python/pytest, one in TypeScript/vitest. Different directories, different build tools, no shared state. The backend agent finished in two minutes; the frontend took three.
**What we thought was happening:** A risky parallel dispatch that we'd have to reconcile.
**What was actually happening:** There was nothing to reconcile. Both agents produced working tests on the first run. The absence of conflict wasn't luck — it was what the file map guaranteed the moment the split was drawn.
**The lesson:** §13 — fan out only when tasks are independent; group by file overlap, not issue priority. The file map is the contract.

### The Subagent Orchestra (case study 1)

**What happened:** Fourteen subagents dispatched across two parallel tracks on a refactor. Twenty-nine files touched, zero merge conflicts on core logic.
**What we thought was happening:** Fourteen is a lot of agents. We'd see conflicts.
**What was actually happening:** The plan's file map — written before any agent started — assigned every file to exactly one dispatch. Conflicts weren't prevented by discipline; they were *impossible by construction.*
**The lesson:** §13 — dispatch to compress process, not to avoid reading the result. Plan the file map before the fan-out.

### The Wave Pattern (case study 2)

**What happened:** By the third release, the project had converged on a rhythm: parallelize in waves, not all at once. Trivial adapters (50 lines of stdlib) first. Moderate adapters (state machines, transport security) next. Complex adapters (hand-rolled state machines, multi-phase handshakes) last.
**What we thought was happening:** A scheduling heuristic.
**What was actually happening:** A load test for the harness. The trivial wave validated that the build system, config registration, and test harness all worked before the project committed agents to 150-line state machines. The retro: *"the software equivalent of checking the parachute before jumping."* Seven parallel agents per release, no coordination overhead, because the first wave shook out every infrastructure surprise before the expensive work started.
**The lesson:** §13 — schedule the cheapest items first as a load test for the harness. The expensive work runs on a harness you've already debugged.

### The Interface That Never Needed a Sixth Method (case study 2)

**What happened:** A five-method adapter interface — name, start, stop, port, protocol identifier — was designed in the first release and absorbed more than seventy adapters across nine releases without ever changing. TCP, UDP, TLS, HTTP, IPC, raw sockets, binary protocols, text protocols, XML streams, binary-encoded formats, sidecar-based adapters, platform-specific adapters. Five methods. Still five methods.
**What we thought was happening:** A clean abstraction designed for extension.
**What was actually happening:** Something stronger. The retro: *"the interface isn't just a software abstraction — it's an organizational one. It turns a team coordination problem into a compilation step."* When four agents work in parallel against the same contract, conflicts are impossible by construction — the interface refuses to permit them. The agents build in total isolation and merge without conflict because the only thing each adapter can *do* is satisfy the five methods.
**The lesson:** §13 — the interface you design before the parallel work begins is the coordination protocol the parallel work runs on. Design it like it matters.

### The v6 Worktree Experiment (case study 3)

**What happened:** Five parallel agents, five git worktrees, five feature branches, one codebase. Each agent's individual work was clean. The integration was a disaster.
**What we thought was happening:** Worktrees were isolating the agents from each other. Git was handling the rest.
**What was actually happening:** Worktrees isolate the *filesystem*; they do not isolate *branches, refs, HEAD, or merge state*. Agents committed to wrong branches, commits cross-contaminated between features, and orphaned refs had to be recovered by manually extracting files from abandoned commits. No agent was undisciplined. The coordination model had a hidden shared-state dimension the setup didn't anticipate. The retro: *"parallel worktrees work best when agents are completely independent; shared git state (branch switching, merges) creates coordination problems."*
**The lesson:** §11 — when the agents are good and the result is bad, the architecture is wrong. §13 — worktrees are workspaces, not a coordination strategy.

### The v7 Team Pivot (case study 3)

**What happened:** Same project, next release, same kind of parallel work. Instead of worktree-per-agent on separate branches, the team used a team-spawning mechanism with agents in the *same* worktree, on the *same* branch, with explicit file-boundary assignments before any work started.
**What we thought was happening:** A last-ditch simplification.
**What was actually happening:** Three agents on three separate features merged cleanly with zero conflicts. Two more agents ran in a follow-up phase with explicit file-boundary instructions for shared files like `App.tsx` and `types.ts`. Same project, same agents, same discipline as v6. The architecture changed; the outcome changed. The retro: *"parallel agents work well when boundaries are drawn at the feature level (different files) rather than the branch level (different git state)."*
**The lesson:** §11 — you don't out-discipline a bad topology; you change it. §13 — isolate context with worktrees; isolate work with file boundaries.

### The Vitest Cache Incident (v5.0.0)

**What happened:** Four parallel agents wrote theme variants across several pages. The code was clean, the tests were clean, the dispatch was textbook. Then thirty-eight unrelated tests started hanging with vitest timeouts, every one of them in files nobody had touched.
**What we thought was happening:** An agent had subtly broken a shared util or introduced a render loop somewhere in a component mount path.
**What was actually happening:** Four agents had been writing to the same `node_modules` directory at once, and vitest's module-graph cache under `node_modules/.vitest` had corrupted itself during the concurrent writes. No individual agent's output was wrong. The failure was an emergent property of the parallel structure. `rm -rf node_modules/.vitest` fixed all thirty-eight tests.
**The lesson:** §13 — subagents protect your context window, they don't hide interactions between dispatched tasks from you.

### The Phantom Downgrade (case study 5)

**What happened:** Days after a four-agent report-only audit fleet ran, the working tree showed a `package.json` version *downgrade* — 1.1.0 to 1.0.3 — that no human had made and no commit explained.
**What we thought was happening:** Someone fat-fingered a revert.
**What was actually happening:** Most plausibly, one of the "read-only" auditors had run a package-manager command mid-analysis, and the tool had helpfully rewritten the manifest in the shared tree. The audit itself was a clear win — eighteen issues filed in ten minutes — but "report-only" described the agents' *assignment*, not their *side effects*. Harmless this time; riding along in someone's next commit the time after.
**The lesson:** §13 — isolate even the read-only agents. A fleet sharing your working tree is the topology failure in its mildest form, and the mild form is free to prevent.

### The Docker Port Mappings That Weren't (case study 2)

**What happened:** 180+ passing tests. Zero data races. Four clean releases. And a Docker container that had been completely unreachable from outside for every single one of those releases.
**What we thought was happening:** The container was fine — CI said so, and CI had been green on every dimension we'd thought to measure.
**What was actually happening:** The Makefile's port mapping routed a host port to a privileged container port, and the binary inside the container ran as a non-root user that could not bind privileged ports and was listening on a different port entirely. Every port mapping was a Potemkin village pointing at an empty socket. The first manual smoke test returned an immediate TCP RST. CI had validated that the image *built*; CI had never validated that the image *answered*. Fix: fifteen lines across three files. The retro: *"unit tests prove your code works. Integration tests prove your components work together. But nothing proves your deployment works except deploying it and poking it with a stick."*
**The lesson:** §8 — test what you ship, not what you build. Same scar as *The Health Check That Wasn't*, two projects, two languages, two different infrastructure stacks.

## Audits as craft work

*Stories where the human decided to look at the work, systematically, with no goal but to find what was wrong — and found things no amount of feature work, bug reports, or automated tests would have surfaced. These are the bruises that exist because nobody was auditing; the audits above healed more than any feature release could have.*

### The Security Audit Pass (case study 4)

**What happened:** A release was dedicated entirely to a systematic security audit — no feature work, no bug reports, no failing tests driving it. Just the human reading every endpoint, every query, every permission surface, looking for what a year of normal review had walked past.
**What we thought was happening:** A nice-to-have. An hour spent sharpening the axe.
**What was actually happening:** Fifteen issues surfaced, most of them category-level rather than line-level: lost-update races on entity mutation, TOCTOU on entity creation, missing UUID validation at API boundaries, regex-injection vectors in user-provided search terms, materialized views that had silently stopped being refreshed. None of these had triggered a bug report; most had been live for months; some had been live for over a year. Each one was found by slow, deliberate attention to a specific surface the normal review cycle never organized around.
**The lesson:** Coda — the systematic audit is craft work the agent cannot substitute for and the pipeline cannot catch. Schedule audits on purpose.

### The Visual Audit Pass (case study 4)

**What happened:** A later release walked every page of the app in both light and dark themes on both desktop and mobile, with no agenda.
**What we thought was happening:** A polish pass. The design was already pretty good.
**What was actually happening:** Six UX fixes surfaced that nothing else would have: inconsistent page-header sizes across sections, button overload on one page, featured content styled identically to error states, a confidence bar that took three rows to convey one piece of information, dark-mode contrast issues the automated axe suite wasn't flagging because they were at the threshold of "accessible but ugly." None of these were bugs. All of them were real. The audit produced more user-visible improvement than the preceding feature release.
**The lesson:** §15 — audits are a *different shape of attention* than review. A reviewer checks that a change is correct; an auditor asks what's wrong with what's already shipped. The two disciplines produce different findings and are not substitutes.

### The Claims That Ran Ahead of the Code (case study 5)

**What happened:** A "ready for company" release wrote the grown-up polish: a privacy policy, marketing copy, the works. Three patch releases over the following month quietly un-wrote it.
**What we thought was happening:** The polish pass was the release's triumph — its retro *celebrated* the new copy.
**What was actually happening:** The policy claimed paid-tier point-in-time backups (never purchased), claimed no third-party requests (a font CDN loaded on every page, leaking visitor IPs), and referenced an analytics provider (never installed). Aspirations, formatted as facts, published. The reversing retros stated the principle: *"claims should be downstream of code, not upstream. Aspirational privacy text is a liability for exactly as long as it's unimplemented."* And the companion norm: a retro that praised the mistake gets corrected out loud — *"sometimes it's 'we got it wrong, here's what we did instead, and here's the principle.'"*
**The lesson:** §15 and §16 — publish what the system does; audit every outward claim like an assertion; and when a retro taught the wrong lesson, the correction is a retro-worthy lesson.

### The Fleet in the Seams (case study 5)

**What happened:** Four parallel report-only agents — docs-vs-code, security, debt, devops — ran for about ten minutes and filed eighteen issues.
**What we thought was happening:** A fishing expedition over a codebase that was, by every loop-level signal, healthy.
**What was actually happening:** The codebase *was* healthy — *"the debt was in the seams — between what we'd written down and what was true."* The haul: the unprotected main branch everyone believed was protected, the backup tier that existed only in the privacy policy, a missing LICENSE, the IP-leaking font dependency, dependency drift. One-screen synthesis, eighteen tickets, one themed cleanup cycle. The next release's coda made the cadence argument: *"The rot itemizes faster than it accumulates if you measure it at all."*
**The lesson:** §15 — the seams mechanize. A ten-minute agent fleet, run every few weeks, keeps the gap between record and reality enumerated — which is most of the way to keeping it closed.

---

# Coda — The three layers, read back through the field notes

Every field note in Part V is a moment when the three-layer division of labor from the thesis was violated. Read them that way and the whole gallery becomes one story told many ways.

- **The agent was asked to do the craftsperson's job.** *The lookup form called "clutter" and removed* (referenced in §1): a design-pass agent made a taste call about what was load-bearing for a use case it had no context for. That's craft work, and craft work is the human's. The agent was doing elaboration the human should have done itself. The fix wasn't a better prompt — it was the human keeping taste in the human lane.
- **The pipeline was trusted to validate the thing it wasn't validating.** *The Health Check That Wasn't*, *Verify What You Shipped*, *The Docker Port Mappings That Weren't*, *The bufconn Gap*: a pipeline reported green while the thing the user actually hits was broken. In every case, the mechanics layer was doing *a* job, just not *the* job — and the human had stopped supervising because the green check looked authoritative. The fix wasn't more discipline; it was making the pipeline check what actually mattered.
- **The human was doing the laborer's job.** *Trust Your Local Tests*: three releases of typing the same correction into fresh conversations, because the parity gap had turned the human into a permanent manual rail. The fix was to build the rail in code so the human could stop being it. *The Four Scoping Gaps*: a fifteen-minute brainstorm — craft work — was skipped because the problem looked mechanical, and the human ended up doing four passes of mechanical debugging instead of one pass of craft thinking.
- **One layer tried to compensate for a missing layer.** *The Onion*, *Three Deploys to Green*: weeks of cascading failure because the CI and deploy layers were doing work the pipeline should have been doing by itself. The human and agent were fighting the mechanics layer, not working inside it.

The thesis isn't decoration. It's the diagnostic. When a cycle feels wrong, ask which layer is doing the wrong job, and put it back in its lane. Every rule in this playbook is, in the end, a way to perform that diagnosis quickly and return each layer to itself — so the human can get back to the work only a human can do.

## The audit is craft work the human owns — with a fleet at its disposal

One craft discipline deserves naming explicitly because it has no analog in the agent or the pipeline layer: **the systematic audit** — now a full chapter (§15), but it belongs in the Coda too, because it's where the three-layer thesis pays out. Not a feature pass, not a bug-fix sprint, not a refactor. Looking at your own work with fresh eyes, on purpose, with no goal except to find what's wrong. Part V's *Audits as craft work* group has the exemplars: a security audit that surfaced fifteen issues a year of normal review had walked past, a visual audit that produced six UX fixes nothing else would have found, and an agent fleet that filed eighteen seam-debt issues in ten minutes over a codebase everyone believed was clean.

The second edition's refinement: the audit *mechanizes further than the first edition guessed* — the seam-diffing, the claim-probing, the gate-rattling are read-and-compare work agents do superbly in parallel (§15) — but the two ends of the audit stay irreducibly human. The front end is the *decision to look*: no bug report, no pipeline gate, and no agent will ever propose spending a release finding out what's wrong with work everyone believes is fine. The back end is the *reading of the findings*: which of the eighteen tickets matters, which "accessible but ugly" is actually ugly, which seam is load-bearing. The agent doesn't audit; it executes an audit. The pipeline doesn't audit; it gates. The attention — slow, deliberate, ungoaled looking by the person who knows what the work is *for* — is the craft layer doing its highest-value job. The pipeline is boring so the agent can elaborate; the agent elaborates so the human can audit; the human audits so the work gets *good*.

Schedule audits on purpose. Pick a surface — security, accessibility, performance, visual consistency, error messaging, the truthfulness of your own documentation — and walk it end to end with no goal except "find what's wrong." Send the fleet down the seams; walk the taste surfaces yourself. The first one will feel like overkill. The findings will silence that. *Pin: every release that ships only what the bug reports asked for is a release that left work on the table. Audit on purpose.*

---

*We can create art and beauty with a computer.* The three-layer discipline is how you make that line true in practice, every day, on a real project with real deadlines. The agent elaborates. The pipeline validates. You create — and audit, and notice, and decide what's worth making. The playbook is the apparatus. The art is the point.

---

# Appendix A — If you are an agent reading this

*Reference, not flow.* The Coda was the closing statement. This appendix exists so agents can find the rules without re-reading the prose — and so humans can skim the whole spine in one screen when they want to.

You are an agent, and a human engineer has loaded this playbook as context because they want you to work the way it describes. It does not matter which model you are or which harness is running you — the rules below are model-invariant, and §2 maps the harness-specific names (read "CLAUDE.md" as your instructions file, "settings.json" as your harness config). This appendix is your index: every rule from chapters §1 through §16, stripped to imperatives, each with a one-sentence reason and a link back to the full section. Skim the rules here; jump to the section when a rule needs context you don't have. One overriding instruction: if anything in this appendix conflicts with the project's instructions file, with a skill the user tells you to run, or with a direct instruction from the user, the user wins — always. The rest of the file is for the human reading over your shoulder; you can skim it, but the rules live here.

## §1 Mental models · [full section](#1-mental-models)

- **Brief the agent like a smart colleague who just walked into the room.** — Every prompt is a cold start; a self-contained briefing prevents invented answers.
- **Delegate the task, not the understanding.** — Synthesis is the engineer's job; handing the agent a riddle is where work falls apart.
- **The agent is good at breadth and consistency. It is bad at judgment under ambiguity.** — Use it for search, refactor, fan-out; make trade-off calls yourself.
- **Agent-authored domain content is a plausible first draft of the world, not the world.** — Wordlists, heuristics, and personas encode the author's vocabulary; only real data and the human's world knowledge close the gap.

## §2 The model and the harness · [full section](#2-the-model-and-the-harness)

- **The disciplines are model-invariant. Only the calibration moves.** — A model upgrade widens the qualifiers (step size, delegable judgment); it never retires verification, retros, or trust boundaries. A better model fails less often and more convincingly.
- **Pick the model tier by the shape of the work, not the size of the diff.** — Gates can judge mechanics, so mechanics go cheap; nothing but the model judges voice, so voice goes expensive.
- **The harness is a dependency: map its layers, keep the knowledge portable.** — File knowledge by layer (instructions file, memory, skills, hooks, permissions), not by filename; prefer repo-portable homes (AGENTS.md, docs/, retros) so a harness swap loses nothing.
- **Trust harness claims the way you trust "tests pass": with evidence.** — Edit tools mis-report, CLIs truncate secrets, CI providers have billing disputes; verify with an independent read, and keep a manual fallback for every automated rail.

## §3 The workspace · [full section](#3-the-workspace)

- **Your pipeline is a precondition, not a feature.** — Every discipline in this playbook assumes CI catches mechanical failures quickly and deploys are automated; a flaky pipeline inverts the loop and drags the human into the mechanics layer. You are done when the pipeline is boring. And every automated rail needs a rehearsed manual fallback — automation you can't bypass is a dependency you can't survive.
- **The instructions file is for facts that don't change. Memory is for facts that do.** — Stable facts in a stable layer stay correct; moving facts in memory can be corrected next turn.
- **Skills are for procedures. The instructions file is for facts.** — Skills get executed on purpose; notes get absorbed as ambient noise and ignored under pressure.
- **Hooks make automation non-negotiable.** — Anything the agent is asked to "remember to do" will fail silently at least once; hooks take the choice out of the loop.
- **The harness config configures the harness. The instructions file configures the agent. They are different layers.** — "Can't" is enforced by the tool; "should" is enforced by politeness.

## §4 The first conversation · [full section](#4-the-first-conversation)

- **Bootstrap with the smallest context that contains the answer.** — Token budget is attention budget; three load-bearing files beat eighty skimmed ones.
- **Correct drift in message 2, not message 50.** — Early corrections are nearly free; late ones mean rewriting ten turns built on top of the drift. The highest-leverage corrections are conceptual reframings — correct the frame in one sentence now, or the code in one release later.
- **If the agent doesn't know something, tell it. Don't let it guess.** — Hallucination is most likely when the agent is confidently filling a gap.
- **Make the agent tell you what it thinks you're building — then grill it.** — The agent's model of the product is a guess until you've heard it recited and corrected it out loud; the value proposition is not derivable from a type definition.

## §5 The loop · [full section](#5-the-loop)

- **Explore before you plan. The plan is not the codebase.** — Run the greps, check the migration state, dispatch the survey agent; ten minutes of reading reality deletes an hour of planning against a memory of it, and exploration finds the bugs nobody filed.
- **Run the whole loop. Skip a step out loud or pay for it silently.** — Each step (explore, brainstorm, plan, TDD, verify, commit, retro) catches a different class of failure.
- **Brainstorm before planning. Plan before code.** — Out of order, the bounds are hallucinated; a plan that feels obvious hasn't been pressure-tested. The brainstorm can amortize across cycles when the upfront thinking was rigorous.
- **Frequent commits are not optional.** — Bisecting agent bugs only works if commits are small enough to bisect against. Precondition: a pipeline fast enough to support the cadence.
- **Retros feed the next loop.** — Without them, the loop has no memory and each release starts from zero.
- **Cycles nest. Each level needs a theme, a boundary, and all three phases.** — Task-level, release-level, and project-level loops all take the same shape; cycles without themes get named by date and forgotten.

## §6 Memory hygiene · [full section](#6-memory-hygiene)

- **Memory has four types. Use the right one or it rots.** — User facts, feedback, state, and pointers have different staleness profiles; mixing them produces a junk drawer.
- **Stale memory is worse than no memory.** — No memory makes the agent ask; stale memory makes it act confidently on last quarter's facts.
- **A belief you've never probed is a hypothesis, not a memory.** — Memory and instructions files amplify whatever they're given, true or not; attach the command that proves each infrastructure belief, and run it.
- **Save the why, not just the rule.** — A rule without its reason becomes unfollowable dogma the moment the world moves on.
- **Don't memorize what the code already says.** — Anything one `grep` away will drift out from under a memory note the moment a file is renamed.
- **File your neighbor's scars, keyed to the trigger that will make them yours.** — A sibling project's bug plus a named trigger (the dependency bump, the platform migration) is your cheapest future fix; fleets learn through cross-repo memory.

## §7 Skills as institutional knowledge · [full section](#7-skills-as-institutional-knowledge)

- **Skills are procedures with discipline. Instructions-file notes are facts you hope get followed.** — If a thing must happen reliably, it needs a host other than the agent's attention.
- **Rigid skills exist for a reason. Don't adapt the discipline away.** — Rigid skills feel like overkill in exactly the moments they're needed most.
- **Write a skill after the third correction.** — The third correction is the moment "I keep saying this" becomes "the system should enforce this."
- **Ship the cheap defense now; schedule the clean refactor for a quiet phase.** — The warning comment buys the time; the maintenance cycle spends it; skipping either half is how seams become incidents. Rigor budgets are per-audience — debug tooling may take documented shortcuts user-facing code can't.

## §8 Verification before completion · [full section](#8-verification-before-completion)

- **"Tests pass" is not "feature works." Verify the feature.** — Suites can be green while the feature is broken because no test exercised the wire. Check what each assertion would tolerate — a test guarding a weaker property than the invariant is theater in miniature.
- **Evidence before assertions. Always.** — Prose without paste is hallucination; evidence of the wrong claim is theater.
- **Ask: would these tests pass if the change were reverted?** — If yes, they don't test the change; rename what they actually pin and verify in the layer being fixed.
- **Verify in the environment that matters.** — If local doesn't run what CI runs, local green is a lie. Test with the rudest client you support; verify what was fetched, not what rendered.
- **When a value crosses a layer boundary, verify the wire, not the fixture.** — Some delivery properties are structurally invisible to unit tests; the manual wire-level integration task is mandatory plan content, not extra credit.
- **Health checks must check health — and observability must be observed.** — A check that can't detect a downed dependency is a status check cosplaying as one; an unobserved error tracker is a prop. Fire a test flare through it.

## §9 Trust boundaries · [full section](#9-trust-boundaries)

- **Match the action to its blast radius. Confirm before crossing the line.** — Blast radius is set by recovery time, not by command length. Reversibility has a time axis: deploy the conservative setting first and calendar the escalation on hard-to-put-back levers.
- **Authorization is scoped, not blanket.** — Every yes is for one action; it is not a standing permission slip for the next risky thing.
- **When the agent hits an obstacle, it must investigate, not delete.** — Unexpected files and orphan containers usually represent in-progress work; if you can't show where you looked, you didn't look. Mirror clause: investigation depth follows blast radius — a zero-impact tooling mystery gets a note and a ticket, not a session.
- **Secrets never transit the transcript.** — The session log is a copy of everything that touches it; pipe secrets, verify their properties not their values, and rotate anything that leaked.
- **Before touching a non-negotiable, write down what would change your mind.** — File the challenge as a pre-registered experiment: measurable bar, full cost accounting, no conclusion before evidence.

## §10 Diagnosis — build the lab · [full section](#10-diagnosis--build-the-lab)

- **Build the diagnostic surface before the fix.** — When a bug class recurs, ship the instrument (persisted traces, replay playground, exportable diagnostics) first; then the fixes land in batches and you watch them land instead of inferring it.
- **The ticket's diagnosis is a hypothesis. Read the trace before believing the issue.** — Fixes designed from the ticket's framing are beautiful solutions to problems that may not exist; the trace is the only witness that was there.
- **A fixed bug's class is a search query, not a closed ticket.** — The siblings are one layer up or down; hunt them by grep while the failure mode is fresh, or pay a full diagnosis per sibling later.
- **Exploration mode is not production mode.** — Stateful rules that are correct in the real flow misbehave against a playground's frozen state; bypass them in the lab with an explicit flag, never in production.
- **When the runner wedges, suspect the runner.** — Failures in files you didn't touch, at speeds that make no sense, are the tooling talking; try the cache clear and the config change before debugging your code, and don't over-investigate a mystery with zero blast radius.

## §11 Failure modes & recovery · [full section](#11-failure-modes--recovery)

- **Agent went off the rails:** stop, open a fresh conversation, and write a self-contained briefing (§4) — steering a context-starved conversation only gives new ways to be wrong.
- **Agent produced slop:** add explicit YAGNI constraints and promote them into memory or a skill (§6, §7) — without a rail, every prompt drifts toward gold-plating.
- **Agent can't be trusted with anything important:** install evidence-before-assertions discipline hard (§8) — you can't out-discipline a missing rail; build the rail.
- **Agent loops on the same wrong fix:** stop touching code, dump raw state, diagnose the real failure (§8, §10) — when the second fix fails the same way, the root cause is misdiagnosed; if the class recurs, build the lab.
- **Agent confidently lies about state:** reject any success claim not accompanied by verification command plus output (§8) — this is the failure that looks like progress and rots underneath.
- **Partnership architecture is wrong:** the agents are good but the result is bad — change the shape of the collaboration, not the prompts (§13). Fix the topology, not the discipline.
- **The workspace lies about state:** everyone agrees on a fact that was never true — probe the load-bearing beliefs with commands (§6, §15); written context is an amplifier, not a witness.

*Closing note:* every agent failure has a human-side twin — skipped brainstorm, skipped retro, accepted-prose-as-evidence, note-instead-of-skill, claim-written-without-probe. Look for the shortcut you took upstream before you tune the prompt. The antecedent is almost always cheaper to fix than the symptom.

## §12 The rescue protocol · [full section](#12-the-rescue-protocol)

- **In the next hour:** pick one small scoped task, run the full loop on it, stop using the agent for anything you can't verify in 5 minutes, and audit memory files with a bias toward deletion — re-calibrate the muscle before optimizing it.
- **In the next day:** run the brainstorming skill before every task for a full day, write one feedback memory from last week's corrections, run an honest retro, and read §8 out loud — stabilize by reinstalling the disciplines that got skipped.
- **In the next week:** promote two repeated corrections into real skills, add one hook that enforces a non-negotiable, reconcile the instructions file against memory, and ship one thing end-to-end with pasted evidence — move pain from prompts into the harness.

## §13 Parallel agents & worktrees · [full section](#13-parallel-agents--worktrees)

- **Fan out only when tasks are independent.** — Group by file overlap, not issue priority. Interface-first design makes conflicts impossible by construction.
- **Designate merge points explicitly; update them last.** — Shared touchpoints (config, main, integration tests) belong to a single post-parallel pass. Phase one is fan-out; phase two is the merge-point pass — which ends with reading the diff against the commit message, because the controller owns the history's truthfulness.
- **Worktrees are workspaces, not stashes — and they are not a coordination strategy.** — Worktrees isolate filesystem, not git state. Use file-boundary parallelism inside a single worktree; never worktree-per-agent.
- **Subagents protect your context window; they don't hide work from you.** — Dispatch when the output is small but the process is large. Accountability is yours; "reading" delegates to automated gates when the pipeline is trustworthy.
- **Review delegated work in two stages, with reviewers who don't trust the implementer.** — A spec-compliance pass (asks the revert question) and a code-quality pass (hunts the wrong-someday class), neither fed the implementer's self-report. Nobody grades their own homework.
- **Isolate even the "read-only" agents.** — "Report-only" is a job description, not a sandbox; audit fleets run package managers and dirty shared trees. Give the fleet its own copy of the world.

## §14 Plan quality · [full section](#14-plan-quality)

- **A plan with placeholders is a wish list.** — If you can't fill in the step right now, you can't implement it right now. A known-failing test deferred to "future work" is a TODO, not TDD.
- **Each step is one action, two to five minutes long.** — Small steps surface complexity before the agent buries it. The time budget is a proxy for small blame radius; when architecture provides that for free, steps can be larger.
- **The plan must cover the spec — and match the codebase.** — Walk every spec section and name the task that implements it; then walk the plan's nouns (files, fields, functions) against the tree. Cross-system ordering is part of the spec.
- **Predict the failing output before you run it.** — Write the expected red (exception, message, counts) into each TDD step; a match is a drift detector reporting all-clear, a mismatch is the cheapest warning you'll ever get.
- **Descope explicitly. Name what's out, and name why.** — Every plan gets a "descoped" section with named reasons; every change gets a "things we deliberately didn't do" list, because restraint that isn't written down will be undone by the next helpful editor.

## §15 Audits · [full section](#15-audits)

- **Schedule audits on purpose.** — Whole defect categories generate no bug reports; the only way they're found is someone deciding to look. The audit is its own themed cycle with its own retro.
- **Claims must be downstream of code, not upstream.** — Aspirational policy text is a liability for exactly as long as it's unimplemented; when the PRD and the code disagree, fix the one a user can verify.
- **The debt is in the seams. Diff what you wrote down against what's true.** — A parallel report-only fleet (docs, security, debt, devops) enumerates the record-vs-reality gap in minutes; the rot itemizes faster than it accumulates if you measure it at all.
- **Probe the gate. A protection you've never tested is a protection you don't have.** — Branch rules, backups, alarms, and rate limits look identical present or absent until the day they matter; rattle every gate on a schedule and attach the probe to the belief.

## §16 The retro habit · [full section](#16-the-retro-habit)

- **Write retros in voice, not in bullet points.** — A dry changelog is forgotten in a week; a story with a nickname is rediscoverable in two years by instinct.
- **Retros are how the loop learns.** — A retro is mandatory at the end of every release, even small ones; an honest paragraph beats a dishonest page. Paired with §8: verification catches the failure; retros convert it into a rule.
- **Write a retro at the end of every themed cycle, and right after every surprise.** — Scheduled retros catch slow lessons; surprise retros catch fast ones. Don't retro on calendar intervals divorced from the work.
- **A retro has an anatomy. Use it as a scaffold, not a template.** — Five parts: mission, execution narrative, numbers, what we learned, what's next. Scale each to what the cycle produced; the scaffold is what frees the voice.
- **A retro has three audiences: you next month, your team, and the agent next time.** — End every retro with one extractable "what we'd do differently" sentence — the story is for humans, the explicit lesson is for everyone including the agent that hasn't read the story yet.
- **The retro unit is the arc, not the tag — and when a retro was wrong, write the reversal down.** — Same-day patches consolidate into one story (the consolidation must actually happen), and a retro that praised a mistake gets corrected out loud: "we got it wrong, here's what we did instead, and here's the principle."


# Appendix B — Glossary

Terms with local meaning — reach for this when a word is doing more work than it seems to.

- **Blast radius** — the scope of consequences if an action goes wrong; used to decide whether to confirm with the user before running a destructive command. See [§9](#9-trust-boundaries).
- **Blue-green deploy** — a deployment pattern that runs the new version ("green") alongside the old ("blue"), health-checks it, flips traffic, and keeps the old version warm for rollback. *(See DevOps Playbook Phase 4.)*
- **Conventional commits** — a commit-message convention (`feat:`, `fix:`, `chore:` …) that machine tools can parse to decide version bumps and changelog sections. *(See DevOps Playbook Phase 5.)*
- **Health endpoint** — an HTTP endpoint that reports the service's own dependency status and build identity (git SHA, version), distinct from a lightweight status check used by load balancers. *(See DevOps Playbook Phase 7.1 and Gotcha #8.)*
- **release-please** — a GitHub Action that reads conventional commits, opens Release PRs, and publishes GitHub Releases automatically. *(See DevOps Playbook Phase 5 and Gotchas #3–#5.)*
- **Brainstorm** — the second step of the loop; a skill invocation that turns a vague idea into a written spec. See [§5](#5-the-loop).
- **Diagnostic surface (the lab)** — the persisted traces, replay playgrounds, and exportable diagnostics that let a bug be diagnosed by *reading evidence* instead of re-reasoning about source. Built before the fix when a bug class recurs. See [§10](#10-diagnosis--build-the-lab).
- **Elicitation** — a pre-code session in which the human makes the agent state its model of the product out loud, grills it, and corrects it while corrections cost one sentence. See [§4](#4-the-first-conversation).
- **Explore** — the first step of the loop; the greps, directory listings, and survey-agent passes that reconcile the plan with the actual codebase before planning begins. See [§5](#5-the-loop).
- **Instructions file (CLAUDE.md, AGENTS.md)** — the project-instructions file the harness loads automatically as system context at the start of every conversation. `CLAUDE.md` in Claude Code; `AGENTS.md` is the emerging cross-tool convention (honored by Codex, opencode, and a growing list); `GEMINI.md` and `.cursorrules` fill the same role elsewhere. The playbook says "instructions file" in rules and CLAUDE.md in field notes — that's what the file was called when the scar formed. See [§2](#2-the-model-and-the-harness) and [§3](#3-the-workspace).
- **Field note** — a short inline vignette that grounds a rule in a real event from the case studies; appears in the human layer of every two-layer chapter. See [How to read this playbook](#how-to-read-this-playbook).
- **File-boundary parallelism** — a parallel-agent coordination model where each agent owns a disjoint set of files, assigned before any work begins, with shared touchpoints deferred to a post-parallel merge pass. The alternative to branch-level or worktree-level isolation. See [§13](#13-parallel-agents--worktrees).
- **Flexible skill** — a skill whose steps are guidelines to adapt to context, as opposed to a rigid skill that must be followed exactly. See [§7](#7-skills-as-institutional-knowledge).
- **Hook** — a shell command the harness executes automatically on a named event (e.g., `post-tool-use`, `pre-commit`) without waiting for an explicit agent invocation. See [§3](#3-the-workspace).
- **Memory** — one of four typed persistent notes (user, feedback, project, reference) that an agent writes and reads across conversations to preserve context beyond a single session. See [§6](#6-memory-hygiene).
- **Model tier** — the capability/price class of the model doing a given piece of work; chosen by the shape of the work (mechanics go cheap behind gates, voice and synthesis go expensive), not by diff size. See [§2](#2-the-model-and-the-harness).
- **Probe** — the command whose output proves a belief about the system (the API call that returns the branch-protection object, the test error that arrives in the tracker). Beliefs about protections carry their probes; audits re-run them. See [§6](#6-memory-hygiene) and [§15](#15-audits).
- **Merge point** — a shared file (config registry, main entrypoint, integration test, dependency manifest) that every parallel agent's work eventually has to touch. In a well-planned fan-out, merge points are owned by a single single-threaded pass after the parallel phase finishes, not edited by the parallel agents. See [§13](#13-parallel-agents--worktrees).
- **Pin** — a one-sentence extractable lesson marked inline with `*Pin:*`. The distilled version of a chapter's argument, written to survive when the surrounding narrative is forgotten — small enough to remember, specific enough to act on, structured so an agent can lift it into memory unchanged. When a pin contradicts the surrounding prose, the pin wins. See [How to read this playbook](#how-to-read-this-playbook).
- **Plan** — a written, step-by-step implementation guide derived from a spec that defines how to build something before any code is touched. See [§14](#14-plan-quality).
- **Report-only fleet** — a set of parallel agents dispatched to audit and report (docs-vs-code, security, debt, devops) without fixing; isolated from the working tree because "report-only" describes the assignment, not the side effects. See [§13](#13-parallel-agents--worktrees) and [§15](#15-audits).
- **Rescue protocol** — the three-horizon recovery playbook (next hour, next day, next week) for teams whose agent partnership has broken down. Not an essay — a checklist. See [§12](#12-the-rescue-protocol).
- **Revert question** — "would these tests pass if the change were reverted?" — the ten-second check that separates verification from verification theater. See [§8](#8-verification-before-completion).
- **Rigid skill** — a skill whose steps must be followed exactly in order, with no discretionary adaptation. See [§7](#7-skills-as-institutional-knowledge).
- **settings.json** — the harness-level configuration file that controls which tools are available, what permissions are granted, and which hooks are registered. See [§3](#3-the-workspace).
- **Skill** — an invokable, named procedure with a defined discipline; the harness construct, not the colloquial sense of "ability." See [§7](#7-skills-as-institutional-knowledge).
- **Spec** — a written design contract that describes what to build, captured before planning begins; a plan covers how to satisfy a spec. See [§14](#14-plan-quality).
- **Subagent** — a fresh child agent dispatched with a curated context window, used to protect the parent's context or to run isolated work in parallel. See [§13](#13-parallel-agents--worktrees).
- **Two-stage review** — the delegated-work review pattern: a spec-compliance reviewer (does the diff deliver every requirement, and does the verification witness it?) followed by a code-quality reviewer (what is wrong now or will be wrong someday?), neither fed the implementer's self-report. See [§13](#13-parallel-agents--worktrees).
- **The loop** — the canonical development cycle: explore → brainstorm → plan → TDD → verify → commit → retro; every feature passes through every step. See [§5](#5-the-loop).
- **Three-layer thesis** — the playbook's core division of labor: the pipeline handles mechanics, the agent handles elaboration, the human handles craft. Every rule in the document is, at root, a maneuver to keep each layer in its lane. See [The thesis](#the-thesis).
- **Two-layer format** — the playbook's chapter convention: an imperative rule at the top (the agent layer) followed by narrative explanation and a field note (the human layer). See [How to read this playbook](#how-to-read-this-playbook).
- **Wave pattern** — a parallel-work rhythm in which the cheapest, most mechanical items run first — as a load test for the build, config, and test harness — before committing agents to heavyweight implementations. "Check the parachute before jumping." See [§13](#13-parallel-agents--worktrees).

# Appendix C — About the case studies

Every field note in this playbook — every nicknamed bug, every three-deploy chase, every "we thought it was X, it was actually Y" — comes from one of six real projects. The first is a full-stack production web application built by a small team over more than two years, heavy on agent collaboration from early days, shipped through some thirty public releases from its founding sprint through its most recent major version — which itself was built in parallel waves with survey agents, two-stage review, and mandatory wire-level integration tasks, and contributed several of the second edition's new rules. It's live. It has users. It has the kinds of scars a project gets when you ship things on purpose, read your own retros, and write the next one anyway. This appendix intentionally anonymizes product identity across all six case studies — the point of the playbook is the practice, not the products — so what's described below is the *shape* of each effort: team size, velocity, release cadence, coordination pattern, and what each one added to the rules.

The retrospective practice is the part that matters for this playbook. Every release — feature, patch, infrastructure cycle, emergency hotfix — got a narrative retro at the end. Not a changelog and not a feature list: an actual story, written in voice, with the bugs named by the nicknames they earned while people were fixing them. *The Doorbell That Never Rang. The Health Check That Wasn't. The Month That Wasn't Thirty Days. The Vitest Cache Incident.* The discipline of writing those retros is what generated the raw material this playbook is curated from. Part V's field-note gallery is the short list — the entries that transferred cleanest to a rule — but every other inline vignette traces back to one of those retros.

They appear in this playbook as inline vignettes rather than as links for one reason: the reader is not assumed to have access to the source. That is the whole point of this portable version. Every story this playbook actually relies on is told in full, right where it's cited. You do not need to click anywhere. If the vignette feels thin, the rule above it is still carrying the weight; if the vignette feels thick, you have what you need without leaving the page.

The same practice, applied to any project with any tech stack, would generate the same *kind* of material. Your bugs will not be our bugs. Your deploy script will fail in ways ours never did. Your agent will invent helpers your team will never use. Those become your field notes — and they will, at the time you are writing them, feel exactly as load-bearing as ours did to us.

The specific project is not the point. The *practice* is the point. Your project's field notes are going to look different and be just as load-bearing.

## Second case study — a parallel-agent protocol server

Partway through curating this playbook, we pressure-tested it against a second project with a very different shape: a single-binary server whose work was implementing a large catalog of external network-protocol specifications as plug-in adapters behind a narrow shared interface. Over nine releases and roughly six months, it grew from three adapters to more than seventy, spanning TCP, UDP, TLS, HTTP, IPC, binary wire protocols, text protocols, XML streams, binary-encoded formats, and build-tag-gated platform-specific primitives. The project is a single Go binary with two external Go dependencies and two sidecar Python dependencies, approximately 15,000 lines of code, and a five-method interface that never changed across any release. It was built almost entirely by parallel agents — four, six, seven, sometimes twelve at once — with humans holding the planning, retros, and judgment calls.

The shape is completely unlike the first case study. No production database. No user-visible UI. No deploy drama (it ships as a container image and a docker-compose file). No quarterly release calendar. The work is rhythmic, mechanical, and heavily parallelizable by construction. If the first case study is *"one team shipping a web app to real users for two years,"* the second is *"can a small group of humans direct a fleet of agents to implement dozens of protocol specs, and keep the results coherent?"* Different question, different scars.

**What held without modification.** Verification (§8), the loop (§5), retros (§16), memory hygiene (§6), trust boundaries (§9), and plan quality (§14) all landed in the second case study the same way they landed in the first. The core rules are not artifacts of one project's shape — they're the disciplines that make agent-directed work legible at all.

**What the second case study amplified.** Parallel agents (§13) gained three new rules' worth of evidence: the interface-as-coordination-protocol insight, the wave pattern, and the explicit merge-point discipline. Every one of these was implicit in the first case study and load-bearing in the second. A five-method adapter interface absorbed more than seventy adapters across every protocol family in networking history without ever changing — the strongest evidence for interface-first design this playbook contains.

**What the second case study stress-tested.** Three rules needed qualifiers rather than rewrites: agent judgment (§1) is stronger when trade-offs are mechanical, delegating understanding (§1) is safer when the understanding lives in authoritative external specs, and the five-minute-step rule (§14) is a proxy for small blame radius that can relax when the architecture provides it for free. The first case study couldn't have surfaced any of these qualifiers because its work lives on the other end of each spectrum — social trade-offs, head-based understanding, judgment-heavy steps. Two projects, two positions on each axis, one honest set of rules.

**What the second case study added.** Two entirely new rules that the first case study had no way to generate: the nested-cycles rule in §5 (the second case study's nine themed releases are the clean exemplar) and explicit descoping in §14 (its v1.0.0 "Descoped Four" is the clean exemplar). Both rules were already implicit in the first case study's practice; the second case study's different shape is what forced them out into the open as explicit rules.

The practice that generated the second case study's material is the same one that generated the first's: a narrative retro at the end of every release, written in voice, with nicknamed adapters and named lessons. **The Wave Pattern. The Interface That Never Needed a Sixth Method. The Docker Port Mappings That Weren't. Hand-Rolling the Legacy State Machine.** The second case study's retros sit alongside the first's as the raw material for the playbook's second pass — and reading them against each other is how every field note from the second case study in this document earned its place.

Two projects, very different shapes, same practice, same rules — and this was only the second pressure-test.

## Third case study — a high-velocity time-tracking web app

Partway through the second pressure-test, we brought in a third project: a time-tracking web app (React, TypeScript, Supabase, Netlify) built to support retroactive block painting rather than real-time timers. The shape is closer to the first case study than to the second — full-stack web app with a real auth surface, a real database, a real cloud deploy, a real user-facing UI — but the velocity is on a different planet. The third case study shipped **nine major versions in three days**, from scaffold to PWA: local foundation, week view and analytics, goals/streaks/CSV export, cloud deploy, security hardening, accessibility and keyboard shortcuts and undo/redo, TanStack Query migration plus sharing plus PWA, half-hour granularity across ~35 files, and a pure tech-debt release to pay off carried debt. Two hundred unit tests, an E2E suite, axe-core accessibility tests, Lighthouse CI, Sentry, Playwright on chromium and mobile, all running as gates.

The project has its own codified workflow document — `docs/WORKFLOW.md` — that independently describes the same practice this playbook describes: CLAUDE.md as single source of truth, versioned backlog with themed milestones, changelog per release, narrative retrospectives per version, git-flow, dual-deploy with backend-first ordering, quality gates with visual QA, and AI agent coordination via team spawning and file-boundary parallelism. None of this was copied from the first case study's practice; the third case study's team arrived at the same shape from first principles.

**What held without modification.** Every rule in the playbook that applied. The loop, retros, verification, memory, skills, trust boundaries, plan quality — the third case study ran all of them and benefited from all of them. The three-layer thesis is the most visibly true on this project: at nine-versions-in-three-days, the human cannot be doing laborer's work anywhere in the stack or the tempo collapses. The velocity is the signal that all three layers were doing their own jobs.

**What the third case study added.** Two contributions that weren't present in the first two projects.

The first is the **v6 → v7 worktree pivot**, which forced a new failure mode into §11 and a new qualifier onto §13's worktrees rule. v6 tried five parallel agents in five separate git worktrees on five separate feature branches and produced branch confusion, cross-contaminated commits, and orphaned refs that had to be recovered by hand. No agent was undisciplined. The coordination architecture had a hidden shared-git-state dimension the setup didn't anticipate. v7 pivoted to a team-in-one-worktree approach with explicit file-boundary ownership, and shipped cleanly. Same agents, same discipline, different architecture, different outcome. This is the clearest demonstration in any of the case studies of a failure that is *not* a discipline problem and *cannot* be fixed by installing more discipline — you have to change the topology of the collaboration itself. The partnership-architecture failure mode in §11 exists because of this release.

The second is the **v7.0.1 and v7.0.2 hotfix pair**, which sharpened §8's "evidence before assertions" rule with a new angle the playbook didn't previously name. Both hotfixes shipped within 24 hours of release despite a full green test suite — because the tests answered a different question than the humans assumed. The TanStack Query migration broke cache-hit paint because no test exercised the cache-hit path; the iPad tap failed because no test exercised a touch gesture on a real device. The unit tests were not lying. They were answering the question *"does the data layer work?"* when the humans were reading the green check as *"does the feature work?"* Those are different claims, and the distance between them is where this class of bug lives. The playbook now names this directly: *the right evidence for the wrong claim is still theater.*

**What the third case study stress-tested.** One rule stretched rather than broke. §13's subagent qualifier — "automated gates can count as reading when the domain supports it" — was written as an *exception* clause on the main rule. At this project's tempo it becomes the *default* mode, with human line-by-line review reserved for craft-sensitive code (interaction design, data migrations, auth boundaries). The rule is still correct; the relationship between the rule and its qualifier inverts at high velocity. I noted this inline rather than rewriting the rule.

## Fourth case study — an audit-driven community-data web app

The fourth pressure-test was a community-data web application with admin moderation: React 18 + Vite + TypeScript + Tailwind on the frontend, edge functions in a managed serverless runtime on the backend, managed Postgres for storage, OAuth for optional user accounts, Vitest for unit tests, Playwright for integration. The shape overlaps the first and third case studies — full-stack web app with a real auth surface, a real database, real users, real moderation workflows — but the distinguishing feature is the explicit *audit cadence* that runs alongside feature work: a scheduled security audit pass in one release produced fifteen findings that a year of normal review cycles had walked past (lost-update races, TOCTOU on entity creation, missing UUID validation, regex injection vectors, materialized views that were never being refreshed), and a later visual audit pass walked every page of the app in both light and dark themes on both desktop and mobile, producing six UX fixes nothing else had surfaced. Neither audit was a feature release; neither was driven by a user complaint. Both came from the human deciding *"I'm going to look at our work, systematically, until I see what we missed"* — and both produced more value than any feature release that cycle could have shipped.

**What held without modification.** Same as the others — the loop, retros, verification, memory, skills, trust boundaries, plan quality. The fourth case study ran them all.

**What the fourth case study added.** The **systematic audit as craft work** — a rule now pinned explicitly in the Coda. The first three case studies all had audits in their retros, but only this project ran them as *scheduled* work with their own releases and their own retros, and the results made it impossible to treat auditing as a nice-to-have. Audits are now named in the playbook as a discipline the agent cannot substitute for and the pipeline cannot catch — the one irreducibly human move that the three-layer thesis is trying to free attention for.

It also sharpened the *extract-when-the-pattern-stabilizes-vs-duplicates-drift* discussion in §7 with the `naivePlural()` scar: a small utility function copy-pasted across three edge functions instead of extracted into a shared helper, one copy of which silently drifted by forgetting to handle irregular nouns, producing user-visible "1 mice" / "1 mouses" inconsistencies across code paths. Duplicates are fine when the pattern is still finding its shape; duplicates that have already drifted are a bug waiting to be reported. The fourth case study is what moved that distinction from implicit practice into an explicit clause on the rule.

## Fifth case study — an epistolary journaling app with a deterministic classifier

The fifth case study is the second edition's largest new source: a one-sentence-per-day journaling PWA in which one of five historical-figure personas replies to each entry from a hand-written template corpus, routed by a deterministic keyword classifier. "No AI in the response path" is the project's load-bearing non-negotiable — which makes it a fascinating stress test for this playbook, because the *product* refuses the very technology that *builds* it. React, TypeScript, a managed Postgres backend, roughly twenty-four tagged releases and twenty narrative retros in about three months, zero to 375 tests. One human, one primary agent, with model-tier escalation for voice work (a mid-tier dispatcher, top-tier per-figure corpus dispatches) and periodic four-agent report-only audit fleets.

**What the fifth case study added.** More new rules than any project since the first. The whole of §10 (build the lab, read the trace, exploration-vs-production mode, suspect the runner) came from its classifier-misfire arc — the release that shipped a diagnostic surface *instead of* a fix, and the afternoon that closed four misfires because the lab existed. §15's claims-downstream-of-code and probe-the-gate rules came from its audit season (*The Lock That Wasn't*, the privacy policy that described an unpurchased backup tier). §1's agent-vocabulary rule came from its wordlists (*"the wordlist reveals what the writer was thinking about, not what the user is going to write"*). §16's arc-not-tag qualifier and the write-the-reversal-down norm came from its patch-release clusters and its self-correcting retro directory. §2's model-tier rule came from its corpus work. And the "things we deliberately didn't do" clause in §14 is its standing practice.

**What the fifth case study stress-tested.** The retro discipline itself, at high frequency and small scale — twenty retros in three months, including one for a session that produced zero code, and one the agent recommended skipping ("the boring retro") that the human insisted on and that earned its keep in one line: *"The retro is boring because the work was on schedule. We should not stop writing the boring ones."*

## Sixth case study — a fleet of single-user instrument apps

The sixth case study is not one project but a constellation: small, sharply-scoped, single-user "instrument" apps — a once-daily rendered front page that consumes the others over versioned HTTP contracts, a daily anti-optimization health journal, a family dinner planner — each too small to generate a playbook on its own, and together generating something none of them could alone: evidence about how practice transfers *between* projects. One human, one agent at a time, shared platform, shared scar tissue.

**What the fleet added.** §6's file-your-neighbor's-scars rule — a dependency bug filed as theoretical in one repo and cashed in as a live fix in another two days later (*"we imported the cure with the disease"*). §4's elicitation rule — the zero-code session that caught the agent misidentifying the product's heart and proposing *"a streak in a trenchcoat"* as a success metric. §9's secrets-hygiene rule — one deploy that rotated a key because it had transited the transcript, and the next deploy engineered so the count of printed secrets was zero. §2 and §3's resilience clauses — the truncated-secret CLI, the `_redirects` precedence trap, and the recognition-on-sight payoff of cross-project memory. The fleet is also where the playbook's portability claims get tested in practice: its newest projects inherit instructions files, pipeline patterns, and retro discipline from their older siblings *through the repo*, not through any single harness.

Six projects, six different shapes, same practice, same rules — plus the set of sharpenings each new project forced out of the rules that already existed. If the rules hold across six independent projects with different shapes, different languages, different velocities, different team sizes, and different review cadences, the rules are not artifacts of any one project. They are the shape of the practice itself.

## Companion — the DevOps playbook

This playbook has a sibling: the **DevOps playbook**, derived from the same first case study and the same retro practice. The two documents are explicitly paired. The DevOps playbook tells you how to make the pipeline boring — health endpoints that report real dependencies and the build SHA, blue-green deploys with automated rollback, lint/test/scan on every push, conventional commits and release-please, manifest-driven production state, Docker parity between dev and prod. Its thesis is one line: *you are done when the pipeline is boring.* This playbook tells you how to work inside a boring pipeline with an agent.

Read together, the two playbooks are the two halves of a single practice. The DevOps half builds the mechanics layer; the engineer-agent half works inside it. The thesis — *we can create art and beauty with a computer* — depends on both. Without the pipeline half, the agent becomes something you babysit and the human becomes the laborer. Without the engineer-agent half, the boring pipeline just runs empty cycles under nobody's direction. Neither playbook is self-sufficient. Both together are.

If the rules in this document feel like they're leaning on a precondition you don't have — fast CI, reliable deploys, parity between environments — go read the companion first. Build the rails. Come back. Everything here will cost less once you do.
