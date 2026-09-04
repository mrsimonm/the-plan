# Potting Bench — plant database expansion (hand this whole file to the other AI)

You are generating houseplant care data for an existing app called Potting Bench.
Follow this spec exactly. Everything you need is in this one file.

**Boundaries — read first:**
- Confirm your current working directory before doing anything.
- The ONLY thing you may create or change is one new file:
  `tools/batches/<genus>.json` (see filename rule below).
- Do NOT open, read for editing, or modify `index.html` or any other file in
  this project. You are not implementing a feature — you are producing one
  data file. A separate, human-run script merges it in later.
- Do NOT install packages, run other scripts, or touch git.
- If any of this is unclear, stop and ask rather than improvising.

---

## The task

Generate records for **every {{GENUS}} cultivar and variety in general
commercial cultivation**, including named cultivars, variegated forms and
common trade names.

Required fields only, plus `colour` — do not write `lore`, `size`,
`propagation`, `tags` or `picto` for this batch.

Fill `colour` carefully for every record — it is what distinguishes one
cultivar from another, so be specific and descriptive rather than promotional.

Exclude any name that appears in the "Already in the app" list below.

Where cultivars genuinely share care requirements, give them the same numbers
rather than inventing spurious variation between them.

If you are not confident about a plant's toxicity, leave that plant out
entirely rather than guessing.

Aim for **40 records**. Fewer accurate records beats more invented ones.

**When done:** write the JSON to `tools/batches/{{genus-lowercase-hyphenated}}.json`
— for example, for Philodendron: `tools/batches/philodendron.json`. Then tell
the user it's ready; do not attempt to merge or validate it yourself.

Replace `{{GENUS}}` above with whatever genus you're asked to do next.

---

## Already in the app — never repeat these names

Adenium (desert rose), Aeonium, African violet, Agave, Aglaonema, Alocasia,
Aloe vera, Amaryllis, Anthurium, Anthurium clarinervium, Areca palm, Asparagus
fern, Aspidistra (cast iron plant), Astrophytum, Avocado, Bamboo (Fargesia),
Bamboo (Phyllostachys), Banana (Musa), Basil, Bay laurel, Begonia, Begonia
rex, Bird of Paradise, Bird's nest fern, Blue star fern, Boston fern,
Bougainvillea, Bromeliad, Burro's tail, Butterwort (Pinguicula), Button fern,
Caladium, Calathea / Goeppertia, Cattleya orchid, Chilli, Chives, Christmas
cactus, Citrus (lemon), Clivia, Coffee plant, Coleus, Colocasia, Coriander,
Crassula 'Gollum', Crocodile fern, Croton, Crown of thorns, Ctenanthe,
Cyclamen, Dendrobium orchid, Desert cactus, Dieffenbachia, Dill, Dracaena
fragrans, Dracaena marginata, Dracaena reflexa (Song of India), Dracaena
sanderiana (lucky bamboo), Echeveria, Epiphyllum (orchid cactus), Epipremnum
'Marble Queen', Euphorbia trigona, Fatsia japonica, Ficus benjamina, Ficus
ginseng (microcarpa), Fiddle Leaf Fig, Fittonia (nerve plant), Gardenia,
Gasteria, Geranium (Pelargonium), Ginger, Goldfish plant, Haworthia, Hibiscus,
Homalomena, Hoya, Hypoestes (polka dot), Ivy (Hedera), Jade plant, Jasmine,
Kalanchoe, Kentia palm, Kimberly Queen fern, Lavender, Lemon balm, Lemongrass,
Lettuce, Lipstick plant, Lithops, Maidenhair fern, Majesty palm, Mammillaria,
Maranta (prayer plant), Ming aralia, Mint, Money tree (Pachira), Monstera
adansonii, Monstera deliciosa, Nepenthes (tropical pitcher), Norfolk Island
pine, Olive tree, Oncidium orchid, Opuntia (prickly pear), Orchid
(Phalaenopsis), Oregano, Oxalis triangularis, Pandanus (screw pine), Parlour
palm, Parsley, Pea shoots, Peace lily, Peace lily 'Sensation', Peperomia,
Philodendron (heartleaf), Philodendron Birkin, Philodendron Brasil,
Philodendron Micans, Pilea peperomioides, Pitcher plant (Sarracenia),
Poinsettia, Ponytail palm, Portulacaria afra, Pothos / Epipremnum, Rabbit's
foot fern, Rhaphidophora tetrasperma, Rhapis (lady palm), Rhipsalis, Rocket
(arugula), Rosemary, Rubber plant (Ficus elastica), Sage, Sago palm (Cycas),
Schefflera, Scindapsus pictus, Sempervivum (houseleek), Snake plant, Spider
plant, Spring onion, Staghorn fern, Strawberry, Strelitzia nicolai,
Streptocarpus, String of dolphins, String of hearts, String of pearls, String
of turtles, Stromanthe, Sundew (Drosera), Syngonium, Tarragon, Thaumatophyllum
(Selloum), Thyme, Tomato, Tradescantia, Turmeric, Venus flytrap, Yucca, ZZ
plant, Zebra haworthia.

Also exclude any name already used in a previous batch you or another
session produced this run, if you're shown one.

---

## Schema

### Only eight fields are required

The app degrades gracefully. A plant with just the required fields is fully
functional. Optional fields add depth and can be filled in later.

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

Unknown fields are dropped at merge — fine to add for your own checking.

### Output format

Return **one JSON object**, nothing else, as the content of the file. No
prose, no markdown fence, no trailing commas.

```json
{ "plants": [ { "...": "one record" }, { "...": "another record" } ] }
```

Minimal record — the right shape for this bulk cultivar batch:

```json
{
  "name": "Philodendron 'Pink Princess'",
  "category": "Aroids & foliage",
  "water": 7, "feed": 14, "light": 2, "humidity": 1, "toxic": 1,
  "tip": "The pink only holds in bright light. Cut back to a variegated node if it reverts.",
  "colour": "Dark green with pink variegation"
}
```

### `name` — unique, exact
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
Never invent one. If a plant fits none, leave it out and say so.

### `water` / `feed` — integer days
Realistic indoor averages, mature plant, normal room, spring/summer. Existing
library spans water **2–45** and feed **0–120**. `feed: 0` is a real answer
(carnivores, and anything the seed carries).

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
`1` if eating it can make a cat or dog ill, per published toxicity lists. When
genuinely unsure use `1` — a false reassurance is the worse error. This is the
one field where an unsourced guess is not acceptable.

### `tip` — 30–160 characters
The single thing that decides whether it lives. Not a description.
- Good: `Rot is the only real risk. When unsure, wait another week.`
- Bad: `A lovely popular houseplant that brightens any room!`

### `colour` — short phrase
What the foliage or flower actually looks like.
- `Dark green with pink variegation`
- `Cream and mid-green marbling`
- `Silver-spotted, purple underside`

### Voice
- **British English.** *colour, metre, realise, grey.*
- **Plain and declarative.** No exclamation marks, ever. Nothing is
  *stunning*, *gorgeous* or *perfect for any home*.
- **Specific over general.** Not "needs good light" but "reverts to plain
  green in a dim corner, and reverted growth never comes back".
- Facts must be checkable. Never invent an etymology, a date or a pollinator.
  If you cannot verify it, write something else.

### Rules
1. Never duplicate a name already in the app or within your own batch.
2. Never emit `null`. Omit an optional field rather than nulling it.
3. `water`, `feed`, `light`, `humidity`, `toxic` are numbers, not strings.
4. If unsure about a plant's toxicity or care numbers, leave the plant out.
   A short accurate batch beats a long invented one.

---

## What genus to do

**{{GENUS}}** — replace this line with the actual genus each time you're asked
for a new batch, e.g. "Do Hoya next."
