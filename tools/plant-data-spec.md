# Pottingbench — plant data spec

Reference for generating plant records. Attach this to Gemini along with
`existing-names.txt`. Ready-to-paste prompts are in `gemini-prompts.md`.

---

## Only eight fields are required

The app degrades gracefully. A plant with just the required fields is fully
functional — searchable, schedulable, with correct care reminders and tag pills.
The optional fields add depth to its care sheet, and can be filled in later
without regenerating anything.

**Required — every record, always:**

| Field | Type | Notes |
|---|---|---|
| `name` | string | Unique. The primary key. |
| `category` | string | One of the seven below. |
| `water` | number | Days between waterings. |
| `feed` | number | Days between feeds. `0` means never. |
| `light` | number | Index 0–4. |
| `humidity` | number | Index 0–2. |
| `toxic` | number | `0` or `1`, for cats and dogs. |
| `tip` | string | The one practical thing. |

**Optional — omit rather than invent:**

| Field | Type | If omitted |
|---|---|---|
| `colour` | string | Colour row hidden. Worth filling for cultivars. |
| `tags` | array | Only the tags derived from the numbers show. |
| `size` | string | Size row hidden. |
| `propagation` | string | "More of it" row hidden. |
| `picto` | string | Gets its category's icon automatically. |
| `lore` | 3 strings | The "about" card is hidden entirely. |

Unknown fields (`sources`, `notes`, `confidence`) are ignored and dropped at
merge, so add them freely for your own checking.

---

## Output format

Return **one JSON object**, nothing else. No prose, no markdown fence, no
trailing commas.

```json
{ "plants": [ { …record… }, { …record… } ] }
```

A minimal record — this is the right shape for bulk cultivar work:

```json
{
  "name": "Philodendron 'Pink Princess'",
  "category": "Aroids & foliage",
  "water": 7, "feed": 14, "light": 2, "humidity": 1, "toxic": 1,
  "tip": "The pink only holds in bright light. Cut back to a variegated node if it reverts.",
  "colour": "Dark green with pink variegation"
}
```

A full record, for headline species worth the extra depth:

```json
{
  "name": "Calathea orbifolia",
  "category": "Aroids & foliage",
  "water": 4, "feed": 21, "light": 3, "humidity": 2, "toxic": 0,
  "tip": "Distilled or rain water only — tap water burns the leaf edges brown.",
  "colour": "Silver-banded mid green",
  "tags": ["fussy", "tapwater"],
  "size": "50–70 cm",
  "propagation": "Division",
  "picto": "prayer",
  "lore": [
    "A striped-leaf prayer plant from eastern Brazil, with round leaves far larger than most of its relatives.",
    "It is the water that kills it, not the light — anything but distilled or rain water scorches the margins within weeks.",
    "The leaves rise and fall on a daily cycle, driven by hinged joints at the leaf base called pulvini that pump water to change the angle."
  ]
}
```

Aim for **40 records per batch**. Smaller batches are more accurate, and each
one validates independently.

---

## Field detail

### `name` — unique, exact
The primary key across four internal structures, so it must be unique against
`existing-names.txt` and within the batch. House style:

- Common name where that is what people say: `Snake plant`, `ZZ plant`
- Botanical where that is what people say: `Monstera deliciosa`
- Cultivars in single quotes: `Epipremnum 'Marble Queen'`, `Philodendron 'Pink Princess'`
- Disambiguate in brackets: `Philodendron (heartleaf)`, `Pitcher plant (Sarracenia)`
- No trailing full stop, no ALL CAPS, no ™ or ®

### `category` — exactly one of
```
Aroids & foliage        Trees & large plants      Palms & ferns
Succulents & cacti      Herbs & edibles           Flowering
Carnivorous
```
Never invent one — an unrecognised category is rejected. If a plant fits none,
leave it out and say so in your reply.

### `water` / `feed` — integer days
Realistic indoor averages for a mature plant in a normal room, spring/summer.
Existing library spans water **2–45** and feed **0–120**. `feed: 0` means never
feed and is a real answer — carnivores, and anything the seed carries.

### `light` — 0–4 · `humidity` — 0–2
```
light                              humidity
0  Full sun (hours of direct)      0  Dry air is fine
1  Bright, some direct             1  Average
2  Bright, indirect                2  Likes humidity
3  Medium
4  Low
```

### `toxic` — 0 or 1
`1` if eating it can make a cat or dog ill. Use published toxicity lists. When
genuinely unsure use `1` — the app's warning is mild and proportionate, and a
false reassurance is much the worse error. This is the one field where an
unsourced guess is not acceptable.

### `tip` — 30–160 characters
The single thing that decides whether it lives. Not a description.
- Good: `Rot is the only real risk. When unsure, wait another week.`
- Bad: `A lovely popular houseplant that brightens any room!`

### `colour` — short phrase
What the foliage or flower actually looks like. This is what makes cultivars
distinguishable from one another, so fill it in whenever a plant is a named
cultivar. Describe, don't sell.
- `Dark green with pink variegation`
- `Cream and mid-green marbling`
- `Silver-spotted, purple underside`
- `Deep burgundy, matt`

### `tags` — from this list only
```
easy   fussy   edible   flowers   tapwater   climbing   trailing
fast   slow    big      propagate pests      sap        nomove     dormant
```
Do **not** emit `toxic`, `safe`, `sun`, `lowlight`, `drought`, `thirsty` or
`humid` — the app derives those from the numbers automatically.

Easily confused: `tapwater` = needs filtered or rain water · `nomove` = drops
leaves when conditions change · `dormant` = genuinely rests part of the year ·
`sap` = irritant sap · `propagate` = cuttings root readily.

### `size` · `propagation` — short strings
`30–60 cm`, `1–2 m`, `Trails 1–2 m`, `Varies hugely` — en-dashes in ranges.
`Cutting in water`, `Division`, `Offsets`, `Leaf cutting`, `Seed — cuttings rarely work`.

### `picto` — optional
Omit it and the plant gets its category's icon, which looks right in almost
every case. Only name one when a plant has a distinctive silhouette:
```
leaves      monstera swiss split heart arrow spathe oval prayer nerve begonia
            oxalis peperomia pilea croton ivy selloum aspidistra
trailing    trail stringheart hoya pearls rhipsalis spider asparagus
uprights    snake zz strap needle luckybamboo bamboo conifer pandanus
trees       fiddle ficus dracaena yucca umbrella pachira olive citrus coffee
            avocado fatsia aralia strelitzia banana
palms/ferns palm fanpalm cycad ponytail fern staghorn birdsnest
succulents  rosette aloe gasteria jade agave adenium kalanchoe lithops
cacti       barrel column opuntia mammillaria epiphyllum
flowers     orchid bloom trumpet bromeliad violet star
carnivores  flytrap pitcher      edibles  herb fruit      generic  broadleaf
```

### `lore` — exactly 3 strings, or omit entirely
Expensive to do well, so reserve it for species worth the depth. Three separate
things in this order, each one or two sentences, each under ~210 characters:

1. **What it is and where it comes from.**
2. **The one thing that matters once it is in your room** — more specific than the tip.
3. **The fact worth knowing for its own sake** — genuinely surprising, and true.

For a cultivar, do not repeat the parent species' lore. Either omit it, or make
all three lines specifically about that cultivar.

---

## Voice

The existing copy is consistent and new plants must not read as bolted on.

- **British English.** *colour, metre, realise, grey.*
- **Plain and declarative.** No exclamation marks, ever. Nothing is *stunning*,
  *gorgeous* or *perfect for any home*.
- **Specific over general.** Not *"needs good light"* but *"reverts to plain
  green in a dim corner, and reverted growth never comes back"*.
- **En-dashes (–) in ranges, em-dashes (—) in asides.**
- **Don't hedge.** State the thing.
- Facts must be checkable. Never invent an etymology, a date or a pollinator.
  If you cannot verify it, write something else.

---

## Rules

1. Never duplicate a name in `existing-names.txt` or within the batch.
2. Never emit `null`. Omit an optional field rather than nulling it.
3. `water`, `feed`, `light`, `humidity`, `toxic` are numbers, not strings.
4. `lore` is exactly 3 entries or absent. Never 1, 2 or 4.
5. If unsure about a plant's toxicity or care numbers, leave the plant out.
   A short accurate batch beats a long invented one.
