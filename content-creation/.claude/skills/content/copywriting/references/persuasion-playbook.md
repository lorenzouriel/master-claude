# Persuasion Playbook

Distilled from the owner's study notes (Cashvertising, Cialdini's *Influence*,
"Confissões do Escritor Milionário", the PAAD creator course, Schwartz's
awareness levels, hook-psychology and funnel notes). Already covered elsewhere,
so not repeated here: AIDA, PAS, PASTOR, SUCCESs, Cialdini's six principles
(`newsletter-humana/references/frameworks.md`); headline formulas
(`copy-frameworks.md`); platform hook formulas (`linkedin-post`, `x-post`).

Filter for this brand: the tone and avoid-list in `context/preferences.md`.
Examples below come from a tech niche; translate them to the owner's audience
(`context/company.md`) before reusing any of them. Every technique
below is tagged **use**, **careful**, or **off-brand**. Persuading means
helping the reader see the action fits their own goals. If a line only works
because the reader doesn't notice it, cut it.

## Contents

1. One idea, one emotion, one action
2. Awareness levels: how direct to be
3. What people actually want (attention drivers)
4. The curiosity loop (hooks)
5. Ten attention patterns for posts
6. The four-block short-form script
7. Endings: PS over begging CTAs
8. Recurring series
9. Distribution habits
10. Off-brand list

## 1. One idea, one emotion, one action

Every piece revolves around a single idea that is big, easy to grasp, useful,
and convincing at first read. One dominant emotion. One action at the end.

Structure: headline (the most important part) → lead (the big idea, under
~600 characters) → body.

Check before drafting: can you say the idea in one sentence a junior engineer
would repeat to a colleague? If not, the piece has two ideas. Split it.

Pyramid principle for the body: answer first, then 3+ supporting arguments,
then facts, data, anecdotes, or quotes under each.

## 2. Awareness levels: how direct to be

Match the opening to what the reader already knows (Schwartz).

| Level | Reader state | Lead with | Example (tech niche) |
|---|---|---|---|
| Unaware | Doesn't see the problem | The pain, made visible | "Your pipeline passed every test last night. It still shipped wrong numbers." |
| Problem-aware | Feels it, no fix | The cost of the pain | "Every rerun of that DAG duplicates 2% of rows. Here's what that does to month-end." |
| Solution-aware | Knows fixes exist | Practical, applicable advice | "Idempotent writes in 3 patterns, with the SQL." |
| Product-aware | Knows a method/system exists | The owner's specific way of doing it | "How I structure every Fabric lakehouse I build." |
| Most aware | 80-90% convinced | The last push: a sharper metaphor, a detail from their reality, a clearer explanation | Lab repo, a before/after metric, the consulting page |

The more aware the reader, the more direct the copy. Go indirect when the
reader doesn't trust results yet, doesn't believe the problem has a fix, or
doesn't see the need. Indirect never means vague or slow.

## 3. What people actually want (attention drivers)

People care about themselves, not about the author or the tool. Anchor every
hook to one driver, then make it concrete enough to picture ("mental movie":
specific, visual, filmable words instead of "improve", "optimize",
"leverage").

| Driver | Status | How it shows up (tech example) |
|---|---|---|
| Avoid loss, pain, risk | **use** | Silent data bugs, wasted compute spend, on-call pages, the outage nobody saw coming. Loss weighs more than gain. |
| Less effort, shortcuts | **use** | "The 20-line pattern that replaced our 400-line framework." Simple path to a hard result. |
| Curiosity, hidden information | **use** | A gap between what the reader knows and what they want to know. Must be paid off in the piece. |
| Competence and status | **careful** | "What senior engineers check first." Fine when it's about skill; off-brand when it's "be in the top 1%". |
| Belonging, in-group | **careful** | "If you've debugged a skewed join, you know." Not "this isn't for everyone". |
| Authority and certainty | **use** | State the rule plainly when you've earned it ("Funciona assim"). See pattern 4 below. |
| Care for others (team, users) | **use** | Protecting the downstream team, the analyst who trusts the dashboard. |
| Fear, survival, attraction | **off-brand** | Doom framing and appearance/attraction appeals don't fit a technical audience. |

## 4. The curiosity loop (hooks)

1. **Tight context.** The reader knows the topic in the first line.
2. **Open the loop** with one of: common ground ("We've all shipped a
   `SELECT *` to prod"), a benefit or a pain, a metaphor that simplifies a
   complex idea, or something genuinely surprising.
3. **The twist.** Flip the expectation ("...and that wasn't the bug").

Supporting rules:
- People want more of what they already care about. Hook into a topic they
  already follow (the names in the topic radar, `context/pillars.md`), not a
  brand-new concept.
- Borrowed credibility: a known tool, paper, company, or person lowers the
  "new = risky" filter.
- Reels: the hook lands in three channels at once, spoken line + movement +
  on-screen text (see `ig-reel-script`).
- On LinkedIn the hook is what shows before "see more": 2-3 lines for text
  posts, only 1-2 when there's an image.

## 5. Ten attention patterns for posts

From the PAAD course, ranked by fit for the owner.

| # | Pattern | Status | Note |
|---|---|---|---|
| 1 | Specific or odd numbers | **use** | "37 minutes to 4" beats "much faster". Never invent them. |
| 2 | Break the feed's pattern | **use** | Unusual format, a code block as the hook, a one-line post among walls of text. |
| 3 | Negative framing for a positive point | **use** | "Stop adding indexes" to teach indexing well. |
| 4 | Speak with authority | **use** | Drop "I think" when the claim is backed by work ("You don't need a statistics degree to work in data"). Expect pushback. |
| 5 | Contrarian take | **use** | When everyone says X, show where X fails. Expert language, real evidence. |
| 6 | Repeat the same idea | **use** | Say the core lessons many times, in different shapes and channels. |
| 7 | "If this, then that" | **use** | Lets the reader self-identify ("If your DAG has 40 tasks, you need..."). |
| 8 | Lists | **use** | Lists work. Keep items parallel and specific. |
| 9 | How it is vs. how it should be (before/after) | **use** | Strong for diagrams and carousels. |
| 10 | Social proof from experience | **use** | Years of hands-on work, projects delivered, client results. Combine with the others. |

## 6. The four-block short-form script

For Reels, short videos, and short LinkedIn/X posts that point to a deeper
piece.

1. **Hook.** Short, direct, impossible to scroll past.
2. **Belief break.** "You were told X. Here's where X breaks." The brain likes
   a course correction.
3. **Unique mechanism.** His explanation of why, the key that changes how the
   reader sees the problem.
4. **Direction.** A CTA, direct or indirect, always present (the article, the
   lab repo, the profile).

Every piece that should move people needs pain (why stop scrolling), desire
(why watch to the end), and direction (where to go next). Most posts have none
of the three.

## 7. Endings: PS over begging CTAs

"What do you think? Tell me in the comments" reads as hungry for engagement
and costs authority over time. Prefer:

- A PS with an unexpected detail or a bonus benefit that invites the comment
  or click on its own merit.
- A specific question only the owner could ask ("Which of these three broke first
  for you?").
- Use action verbs in CTAs ("Clone the lab", "Read the full breakdown").

## 8. Recurring series

Repetition turns audience into community: exposure → familiarity → positive
association → habit → loyalty. A fixed series gives people a reason to come
back even when the algorithm doesn't deliver.

Series recipe: a short, repeatable name; the thing shown in use, not static; a
micro-story for context; why it matters; one action. The weekly slot map in
`context/pillars.md` is this idea in practice; name the series explicitly when proposing new ones.

## 9. Distribution habits

- Short-form is the entry point; long-form makes people know them well. Every
  short piece should point to a long one ("short content makes you known,
  long content makes you known well").
- Curate and remix validated ideas: the best threads and quotes on a theme,
  turned into a carousel or thread with their take on top.
- Reply to big accounts for reach and to small ones to build the tribe
  (`linkedin-comment-drafter`, `x-reply-drafter`).
- Own the audience: an email list beats any platform's algorithm.
- Write for their past self: who they were two years ago.

## 10. Off-brand list

Present in the source notes, never used here (they break
`context/preferences.md`):

- Fake or artificial scarcity and urgency ("last spots", countdowns, "only
  today").
- Doom or fear framing ("the silent mistake that will destroy your career").
- "Not everyone can handle this" exclusivity, "top 1%" status bait.
- Appearance, attraction, or lifestyle appeals.
- Hype vocabulary: secret, little-known, game-changer, "nobody told you".
  Curiosity is fine; its clichés are not.
- Launch-funnel pressure tactics. When there is an offer, state it plainly.
