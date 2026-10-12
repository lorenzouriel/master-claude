# IG Reel Script Formats

> Voice rules from `references/shared/memory/preferences.md` apply to every
> spoken line and on-screen text: no emojis, no em dashes, no guru vocabulary.

Five Reel script structures for Instagram. Each includes timing, on-screen text cues, and spoken lines.

---

## Format 1: Tutorial / How-To

**Length:** 30-60 seconds  
**Use when:** Step-by-step guides, workflows, "here's exactly how I do X"

**Structure:**
```
[0:00-0:03] HOOK
  On-screen: "How to [specific result] in [timeframe]"
  Spoken: "If you're [target situation], here's exactly what I do:"
  Visual: [Start already doing the thing, not talking about doing it]

[0:03-0:08] WHY IT MATTERS
  Spoken: "[One sentence on why this matters / what breaks without it]"
  On-screen: optional reinforcement of the pain point

[0:08-0:40] STEPS (5-8 seconds per step)
  Step 1:
    On-screen: "1. [Step name]"
    Spoken: "[What you do. What you get. 1-2 sentences max.]"

  Step 2:
    On-screen: "2. [Step name]"
    Spoken: "[Same. Vary sentence length from step 1.]"

  Step 3+: [Same pattern]

[0:40-0:55] CTA
  On-screen: "Save this / Comment [word]"
  Spoken: "Save this for the next time you need it." or "Comment [word] and I'll send you [specific resource]."
```

**Worked example (30 sec):**
```
[0:00-0:03]
On-screen: "dbt incremental model in 3 steps"
Spoken: "Most data engineers rebuild their full table every run. Here's how to stop doing that:"

[0:03-0:07]
Spoken: "At scale, full refreshes take hours. Incremental cuts that to minutes."

[0:07-0:18]
On-screen: "1. Add materialized='incremental'"
Spoken: "Change the config to incremental. This tells dbt to only process new rows."

[0:18-0:28]
On-screen: "2. Set your is_incremental() filter"
Spoken: "Wrap your WHERE clause in is_incremental(). dbt handles the rest."

[0:28-0:30]
On-screen: "Save this"
Spoken: "Save this. You'll need it."
```

---

## Format 2: Story (Narrative)

**Length:** 30-60 seconds  
**Use when:** Personal experience, turning points, lessons from real events

**Structure:**
```
[0:00-0:03] HOOK (the ending, not the beginning)
  On-screen: "[The result or tension that makes them want to watch]"
  Spoken: "[Where you ended up, the resolution or the stakes]"

[0:03-0:12] SETUP
  Spoken: "[Who you were / what the situation was before it changed]"
  On-screen: "[Optional: key context in 3-5 words]"

[0:12-0:35] THE STORY
  Beat 1: [What happened. Specific.]
  Beat 2: [What changed / the moment it shifted]
  Beat 3: [What it cost or what you gained]
  (Each beat: 5-8 seconds, 1-2 spoken sentences)

[0:35-0:50] THE LESSON
  Spoken: "[One sentence. The thing you'd tell someone in the setup situation.]"
  On-screen: "[The lesson as a short phrase]"

[0:50-0:60] CTA
  Spoken: "[One action: comment, save, or just end on the strongest line]"
```

**Hook rule for Story format:** Start at the END, not the beginning. "The pipeline lost 2 days of orders" is a better hook than "Let me tell you about the migration."

---

## Format 3: Listicle

**Length:** 20-45 seconds  
**Use when:** "N things/tools/mistakes about X", fast-paced, high-energy

**Structure:**
```
[0:00-0:03] HOOK
  On-screen: "[N] [things/mistakes/tools] [audience] [doesn't know / needs]"
  Spoken: "Here are [N] [things]. Let's go:"
  Visual: [Fast cut energy. Signal this will be quick and dense]

[0:03 onwards] ITEMS (3-5 seconds per item)
  Each item:
    On-screen: "[Number]. [Item name]"
    Spoken: "[One sentence max. The most surprising thing about this item.]"

[Last 5 sec] CTA
  On-screen: "Save this list"
  Spoken: "Save this for later."
```

**Rules:**
- Move FAST. 3-5 seconds per item max.
- Most counterintuitive item goes second-to-last, not last (drop-off is highest at end)
- Spoken lines must be different from on-screen text (if they're the same, one is redundant)
- Start with the most accessible/recognizable item; end with the most surprising

---

## Format 4: Opinion / Contrarian

**Length:** 30-60 seconds  
**Use when:** Hot takes, industry pushback, "here's why the consensus is wrong"

**Structure:**
```
[0:00-0:03] HOOK (the bold claim)
  On-screen: "[Specific contrarian claim]"
  Spoken: "[State it directly. No setup. No "some people think..."]"

[0:03-0:15] STEELMAN (the other side)
  Spoken: "[The strongest version of the opposing view. Be fair. One sentence.]"
  On-screen: optional, "The case for [opposing view]:"

[0:15-0:40] YOUR ARGUMENT
  Point 1: [Evidence, experience, or logical step. Specific.]
  Point 2: [Same.]
  (Optional) Point 3: [The most surprising piece of evidence.]

[0:40-0:55] REFRAME
  Spoken: "[New way to think about it. The mental model shift.]"
  On-screen: "[The key phrase from the reframe]"

[0:55-0:60] CLOSE (no CTA needed for opinion Reels; end on the strongest line)
```

**Rules:**
- The steelman is NOT optional. Skipping it reads as bad faith.
- End on your strongest point, not a restatement of the hook
- Don't soften the conclusion. If you believe it, commit to it.

---

## Format 5: Behind-the-Scenes / Reveal

**Length:** 20-45 seconds  
**Use when:** Process reveals, "a day in my work", unexpected context, myth-busting

**Structure:**
```
[0:00-0:03] HOOK (the surprising thing they're about to see)
  On-screen: "[What you're showing / the reveal]"
  Spoken: "[One line that makes them curious, the unexpected angle]"
  Visual: [Show the thing. Don't just talk about showing it]

[0:03-0:15] THE REVEAL
  Spoken: "[Walk through what they're seeing. Narrate with context they don't have.]"
  On-screen: [Labels, arrows, context as needed]

[0:15-0:35] WHY IT MATTERS
  Spoken: "[What this changes / what they should think about their own situation now]"
  On-screen: optional key takeaway

[0:35-0:45] CTA
  "Comment if you want to see more of this." or end on the strongest observation.
```

---

## Shared rules for all formats

### Hook rules (0:00-0:03)
- **On-screen text** must make sense with the sound off
- **Spoken line** must make sense with the screen off
- Both together must be more compelling than either alone
- Never start with: "Hey guys", "So today", "Welcome back", "In this video I'm going to"
- Always start: mid-sentence, mid-action, or at the point of maximum tension

### Pacing rules
- Read the script aloud. Time it. Cut anything over your target length by 20%.
- Vary spoken sentence length. Short. Then a longer sentence for contrast. Then short again.
- Silences between beats are fine. Don't rush to fill every second

### CTA rules
- One CTA per Reel. Never two.
- Best CTA for reach: "Share this with [specific person]"
- Best CTA for saves: "Save this for the next time you [specific situation]"
- Best CTA for comments: "Comment [specific word] and I'll DM you [specific resource]"
- Worst CTA: "Follow me for more content like this!"
