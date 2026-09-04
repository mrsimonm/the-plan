# Reviewing a plant batch (paste into a plain Gemini chat)

Use this after a batch JSON file exists (e.g. `tools/batches/hoya.json`), as a
second, independent check before it comes to Claude. Different chat/session
than whatever generated it — the point is a fresh, skeptical read.

---

## The prompt

Paste this, followed by the batch JSON:

```
You are auditing houseplant care data before it goes into a real app used to
schedule watering and feeding, and to warn about pet toxicity. Be skeptical —
you are looking for mistakes, not confirming it looks fine.

For EACH record in the JSON below, check:

1. TOXICITY (highest stakes — a wrong "safe" here can hurt a pet). Is `toxic`
   correct per published toxicity data (ASPCA or equivalent) for cats/dogs?
   If you are not confident, say so explicitly rather than assuming it's right.
2. CATEGORY is exactly one of: Aroids & foliage, Trees & large plants, Palms
   & ferns, Succulents & cacti, Herbs & edibles, Flowering, Carnivorous.
3. WATER / FEED intervals (days) are realistic for that specific plant, not
   just a generic guess for the genus. Flag any that look copy-pasted across
   genuinely different species rather than researched individually.
4. NAME is not a duplicate within this batch, and follows house style
   (cultivars in single quotes, no trailing full stop, no ALL CAPS).
5. TIP and COLOUR (if present) state a specific, checkable fact — not a vague
   or promotional claim ("lovely", "stunning", "perfect for any home").
6. No field is null, no required field is missing, no field is the wrong type
   (water/feed/light/humidity/toxic must be numbers, not strings).

Output ONE line per record:
PASS — <name>
or
FAIL — <name> — <exactly what's wrong and what it should probably be instead>

Then a one-line summary: "N pass, M fail."

Do not rewrite the records yourself. Just report.

---
[paste the batch JSON here]
```

---

## What to do with the result

- **All PASS:** send the batch JSON straight to Claude, along with the
  "N pass, M fail" summary line so it's on record.
- **Some FAIL:** either fix those specific records yourself if the fix is
  obvious, or paste just the FAIL lines back to whichever session generated
  the batch and ask it to redo only those records — then re-run this review
  on the corrected ones before sending to Claude.

Claude still does its own check on merge (the validator enforces schema, and
spot-checks content) — this step catches things the validator *can't* check,
like wrong toxicity or copy-pasted care numbers, before that gets to Claude
at all.
