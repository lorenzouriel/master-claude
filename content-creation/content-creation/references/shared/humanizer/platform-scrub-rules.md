# Platform scrub rules

Applied after the universal patterns in `humanizer.md`. Each block adds the
tells specific to one platform's culture and algorithm. The regex lists are
detection aids: flag the match, then rewrite by judgment. Never auto-substitute,
because keeping the meaning needs a human-quality rewrite.

Global rule for every platform: Lorenzo uses **no emojis, ever**, and **no em or
en dashes**. Those two never pass, whatever a platform's culture tolerates.

---

## LinkedIn

### Negative parallelism (hard ban, always on)

Rewrite every form as two plain declaratives.

```python
LINKEDIN_NEG_PARALLEL = [
    r"It's not just (\w+(?:\s+\w+){0,5}), it's (\w+(?:\s+\w+){0,5})",
    r"(\w[\w\s]{0,20}) isn't (\w[\w\s]{0,20}), it's (\w[\w\s]{0,20})",
    r"Not (\w[\w\s]{0,20}), but (\w[\w\s]{0,20})",
    r"It's not about (\w[\w\s]{0,20}), it's about (\w[\w\s]{0,20})",
    r"The question isn't (\w[\w\s]{0,20}), it's (\w[\w\s]{0,20})",
    r"This isn't (\w[\w\s]{0,20})\. This is (\w[\w\s]{0,20})",
    r"The real (\w+) isn't (\w[\w\s]{0,20}), it's (\w[\w\s]{0,20})",
]
# Rewrite as: "nobody's playing for unit economics. they're playing to own distribution."
```

### Engagement bait (delete or replace)

```python
LINKEDIN_ENGAGEMENT_BAIT = [
    r"What do you think\??",
    r"Thoughts\?",
    r"Agree or disagree\?",
    r"Let me know (in the comments|below|your thoughts)[!.]?",
    r"Tag someone who needs (this|to hear this)[!.]?",
    r"Drop a comment below[!.]?",
    r"Share your thoughts[!.]?",
    r"I'd love to hear (from you|your thoughts)[!.]?",
]
# Replace: end on the strongest line, or ask a specific question that expects a real answer.
```

### Announcement openers (rewrite)

```python
LINKEDIN_ANNOUNCEMENTS = [
    r"I'm (so )?(excited|thrilled|delighted) to (announce|share|reveal)[^.]*\.",
    r"I'm (honored|humbled|proud) to (be|announce|share)[^.]*\.",
    r"Excited to share[^.]*\.",
    r"Big (news|announcement)[^.]*\.",
]
# Lead with the concrete moment or result, not the feeling about it.
# Bad:  "I'm excited to announce we raised $2M."
# Good: "We raised $2M. Here's what we're building:"
```

### CTA closers (rewrite)

```python
LINKEDIN_CTAS = [
    r"Save this (post )?for later[!.]?",
    r"Repost this if[^.]*\.",
    r"Like if you (agree|found this helpful)[!.]?",
]
# Keep: a specific PS with a reason ("PS: full breakdown in the first comment.")
# Remove: generic save/like/repost asks.
```

### Algorithm tells (flag)

- External link in the body: move it to the first comment.
- 3+ hashtags: trim to 0-2 at the end.
- All-caps first line: rewrite.

---

## X

### Engagement bait (delete or replace)

```python
X_ENGAGEMENT_BAIT = [
    r"RT if you agree[!.]?",
    r"Retweet if you (agree|relate)[!.]?",
    r"Follow me for more (content|tweets) like this[!.]?",
    r"Like and retweet if[^.]*\.",
    r"What do you think\?$",
    r"Thoughts\?$",
    r"Agree\?$",
]
# End on the strongest line, or a specific open question with a real answer expected.
```

### Hedge openers (commit to the claim)

```python
X_HEDGE_OPENERS = [
    r"^I (think|feel|believe) (maybe|perhaps|possibly)",
    r"^Some might (argue|say|suggest)",
    r"^It could be argued that",
    r"^One might say that",
    r"^In my (humble|personal) opinion,?",
]
# X rewards conviction. Hedged takes die.
```

### Thread tells (flag)

- Numbered tweets (`1/`, `2/`) everywhere: drop the numbers; each tweet stands alone.
- A filler tweet that only says "Let's break it down" or "Here's why:": delete it.
- The thread emoji or "A thread" with no promise: replace with the actual promise.
- Every tweet the same length: vary.

### Algorithm tells (flag)

- External link in the tweet body: move to the first reply (or the last thread tweet).
- 2+ hashtags: remove (0-1 max, none by default).
- All-caps words: rewrite.

---

## Instagram

### Captions: engagement bait (delete or replace)

```python
IG_ENGAGEMENT_BAIT = [
    r"Double tap if you agree[!.]?",
    r"(Like|Save) this post[!.]?",
    r"(Comment|Let me know) (below|in the comments)[^.]*\.",
    r"Tag (a friend|someone) who (needs this|would love this)[!.]?",
    r"Share this with[^.]*\.",
    r"Smash that like button[!.]?",
]
# Replace with a CTA that gives a reason:
# "Save this for the next time your pipeline fails at 3 AM."
# "Full lab on Medium, link in bio."
```

### Caption openers (rewrite)

```python
IG_OPENER_TELLS = [
    r"^Here (I am|we are) at [^.]*\.",      # describes the image
    r"^In today's post, I('m| am) sharing",
    r"^So excited to share",
    r"^I'm thrilled to (announce|share)",
    r"^Welcome back to my (page|feed|account)",
    r"^Today I want to talk about",
]
```

### Weak vocabulary (replace)

```python
IG_VOCAB_REPLACE = {
    "curated": "selected / chosen / built",
    "authentic": "[remove; show it instead]",
    "aesthetic": "[name the actual look]",
    "vibe": "feel",
    "intentional": "deliberate",
    "passionate": "[remove; show the work]",
    "journey": "process / path",
    "content creator": "[say what you actually make]",
}
```

### Links (rewrite)

```python
IG_LINK_BAIT = [
    r"Link in bio!?$",
    r"Check (the|my) link in (my )?bio[!.]?",
    r"More in (the )?bio[!.]?",
]
# Replace: "Full lab on Medium, link in bio." Say what is there.
```

### Carousel tells (flag)

- Every slide the same word count: vary.
- Bullet lists inside one slide: one idea per slide, short paragraph.
- "Swipe for more" on every slide: cover only, if at all.
- A slide with a title and no body: add content or merge.

### Reel scripts (spoken)

```python
REEL_PRESENTER_OPENERS = [
    r"Hey (guys|everyone),?",
    r"Welcome back( to my (channel|page))?[!.]?",
    r"So today I (want to|wanted to|am going to) (talk about|show you|cover)",
    r"In this (video|reel),? I (will|am going to|want to)",
    r"(So,? )?[Ww]ithout further ado",
    r"[Ll]et's (get into it|dive in|get started)[!.]?",
]
# The hook starts at word 1, mid-action or mid-statement.

REEL_FILLERS = [
    r"[Ss]o basically",
    r"[Yy]ou know what I mean\??",
    r"[Ss]o yeah,? that's (pretty much )?it",
    r"[Ii] hope that (makes sense|was helpful)",
    r"[Dd]oes that make sense\??",
]

REEL_WRONG_PLATFORM_CTAS = [
    r"[Dd]on't forget to (like and )?subscribe[!.]?",
    r"[Hh]it that (follow|subscribe|like) button[!.]?",
    r"[Ss]ubscribe for more content like this[!.]?",
]
# Replace with one specific CTA ("Save this for your next incident review.") or none.
```

- Uniform rhythm (every sentence 12-18 words): break one in three into a punch under 6 words.
- List-reading voice ("Step 1: ...", "Step 2: ..." with identical shape): vary each item.
- Scripted transitions ("Moving on to our next point", "As I mentioned earlier"): cut, just start the next point.

---

## Medium

### Openers and closers (rewrite)

```python
MEDIUM_TELLS = [
    r"In this article,? (we|I) will (explore|discuss|cover|look at)",
    r"^In today's (fast-paced|data-driven|ever-evolving)",
    r"^## (Conclusion|Final Thoughts|Wrapping Up)$",   # the skeleton uses "## Overview"
    r"I hope (this|you) (helps|found this)",
    r"Happy (coding|learning)!?",
]
```

### Structure tells (flag)

- Generic best-practice bullet lists with no measurement: replace with the
  measured version or cut (medium-tech-article non-negotiable 2).
- Technique with no price stated: add "The price: ...".
- Statement headers on lab or playbook sections ("## Blocking Analysis"):
  rewrite as the reader's question in quotes.
- Paragraphs over 4 lines: split.

### Do NOT scrub on Medium

These are part of Lorenzo's fixed article skeleton, even though they look like
universal-pattern hits (section 28, signposting):

- The `Let's [verb]?` transition into the body.
- The closer: "What about the next steps?" / "Save the content here, ... It is
  the best way to learn!"
- "Not a medium member? Read here!" at the top.
- `(check here!)` cross-link markers.

---

## Never scrub (all platforms)

These are signs of a real person writing:

- Specific, unusual, hard-to-fabricate details (exact amounts, real tools,
  precise dates, a lab table name).
- Mixed feelings left unresolved ("mostly right, but it still bothers me").
- Lowercase sentence openings in comments and replies (house style).
- `..` as a soft pause in comments and replies (house style, replaces em dashes).
- Deliberate fragments ("Worth it." "Every time.").
- Genuine asides and self-corrections.
- Contractions.
- Specific numbers and named entities: add more, never remove.
