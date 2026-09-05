# Cabinet: a Pokémon TCG template + set-completion tracking

Status: research complete. Read-only task — no code was changed; this is a
proposal for a future edit to `index.html`.

## 0. Task

Add a prefilled `pokemon` entry to `CB_TYPES` (index.html, ~line 32965) in
Cabinet, the app's generic collections tracker, and design a small,
offline-friendly set-completion feature so a card collector can see
owned/total per set and a "still needed" list. Cabinet is a localStorage PWA
with no backend, so nothing here may depend on a live price or card API —
values are entered by hand, exactly like every other Cabinet template.

## 1. Competitor landscape

| App / source | What it is | Relevant to this design |
|---|---|---|
| [Collectr](https://getcollectr.com/) ([App Store](https://apps.apple.com/us/app/collectr-tcg-collector-app/id1603892248)) | Portfolio tracker across 25+ TCGs (Pokémon, Magic, Yu-Gi-Oh!, One Piece…). Scans a card and auto-fills set/number/variant. Tracks raw, graded and sealed items separately, daily market valuation. | Confirms raw/graded/sealed as the three states worth distinguishing, and that grading is usually stored as **one** field (company + grade), not subgrades — "every other app treats grading as a single field… shallow (overall grade only, no subgrades)". That's the right depth for Cabinet too. |
| [Pokellector](https://www.pokellector.com/) ([Play Store](https://play.google.com/store/apps/details?id=air.com.pokellector.mobile)) | Free, checklist-first: "My collection" lets you check cards off **by set**, catalogues English and Japanese sets including alt-arts and secret rares, and finds missing cards with filters for rarity/set/release date. Supports CSV/JSON bulk import mapped to set + card number. | The clearest precedent for a lightweight **owned/total per set + missing-card filter** UX — no live pricing needed, it's fundamentally a checklist app. This is the closest model for what Cabinet can do offline. |
| [TCG Collector](https://www.tcgcollector.com/) | "The most detailed Pokémon card collection tracker" — filters by set, variant, rarity, language, condition; shows market price *by finish* (normal/holo/reverse); lets you log which binder and slot a card lives in, including custom grid sizes. | Confirms the field set the task already named (variant, rarity, language, condition) is the real-world standard, and that "binder + slot" is a commonly tracked location detail — Cabinet's existing universal `location` field already covers this without a new type-specific field. |
| [TCGplayer](https://help.tcgplayer.com/hc/en-us/articles/221430307-Card-Conditioning-Overview) / [Card Conditioning Standards PDF](https://mktg-assets.tcgplayer.com/web/seller/guides/Card-Conditioning-Standards.pdf) | The de-facto North American condition scale: **Near Mint, Lightly Played, Moderately Played, Heavily Played, Damaged** (NM/LP/MP/HP/DMG). | This is the condition ladder to use — it's what every US marketplace and most tracker apps key off. |
| [Cardmarket](https://help.cardmarket.com/en/CardCondition) | The EU scale is more granular at the top (Mint, Near Mint, Excellent…) — Cardmarket's "Excellent" maps to TCGplayer's "Lightly Played". | Confirms NM/LP/MP/HP/DMG is the safer international default (it's the coarser, more universally understood scale); a "Mint" tier above NM is worth keeping for factory-fresh raw cards, matching what Cabinet's own `music` template already does (`Mint (M)`, `Near mint (NM)`). |
| [PSA Set Registry](https://www.psacard.com/psasetregistry/faq) / [rules](https://www.psacard.com/psasetregistry/rules) | The reference implementation of "set completion" for graded collectors: completion % = owned ÷ total; a **weighted GPA** additionally weights each card 1–10 by rarity/value and averages the *grades* of owned cards against that weight. | The weighted-GPA machinery is real but heavy (needs a per-card weight table) — worth naming as the "gold standard" but explicitly **out of scope** for a v1: Cabinet should do the simple owned/total %, not weighted grade-point averaging. See §6. |
| [pokemontcg.io](https://docs.pokemontcg.io/) (the API used for `tools/pokemon/sets.json`) | Free, keyless (for low volume) REST API. The **set** object has exactly the shape needed: `id` (a short code like `base1`), `name`, `series`, `releaseDate`, `total`, `printedTotal` (the number printed on the card, which can be lower than `total` when secret rares exist beyond the printed run). The **card** object additionally carries `rarity`, `number`, `artist`, and per-finish TCGplayer prices (`normal`, `holofoil`, `reverseHolofoil`, `1stEditionHolofoil`, …). | This is the source for `tools/pokemon/sets.json`. Its card-level data (rarity/number/artist per card) is the same shape Cabinet's own item fields should hold, confirming the field list below rather than inventing one. |
| Bulbapedia set lists | Human-curated, matches pokemontcg.io closely; occasionally uses fuller names (e.g. "Base Set" rather than the API's "Base"). | Named as fallback source; not used here since the API returned a clean, complete, current dataset (see §7). |
| Dex, PriceCharting, TCGplayer app | General price-comparison and portfolio tools, all live-price-dependent. | Confirm the "no live price API" boundary is a real simplification the market otherwise doesn't make — Cabinet's existing hand-entered `worth`/`paid` model is consistent with how Simon already treats every other Cabinet collection (coins, art), so no new mechanism is needed, just the field names below. |

## 2. Field / metric matrix

What the tools above track, mapped onto what Cabinet already has (universal:
`title, maker, year, acquired, status, condition, location, qty, paid, worth,
tags, notes, photos`) versus what needs a new type-specific `x` field:

| Metric | Covered by | Notes |
|---|---|---|
| Set | **`maker`** (relabelled "Set") | See §3 for why. |
| Card name | universal `title` | e.g. "Charizard ex". |
| Card number / set total | new `x.no` | e.g. `025/102`. Essential — this is the join key against `tools/pokemon/sets.json` for progress, and the thing a checklist app sorts by. |
| Rarity (incl. modern tiers) | new `x.rarity` (select) | Illustration Rare / Special Illustration Rare / Hyper Rare / ACE SPEC confirmed current (2025–26) top-tier rarities — see [rarity guide](https://mintvandal.com/guides/rarity-guide/), [ACE SPEC explainer](https://poke.rip/rarity-guide/). |
| Variant / finish | new `x.variant` (select) | normal / holo / reverse holo / 1st edition / shadowless / promo / stamped — task's list matches TCG Collector's filter set exactly. |
| Language | new `x.lang` (select) | Matters a lot to value — a Japanese 1st-print alt-art is a different card, price-wise, from its English reprint. |
| Condition (raw) | universal `condition`, new ladder | NM/LP/MP/HP/DMG, see §1 and §5 for the "Mint" collision. |
| Grading company + grade | new `x.grader` (select) + `x.grade` (text) | Collectr's finding that even dedicated apps keep this to one field per axis (company, grade) rather than PSA-style subgrades is the right depth for a general collections app. |
| Cert / slab number | new `x.cert` | Lets the owner look the card up on PSA/CGC/BGS/ACE's public cert lookup later — doesn't need to *be* a link, just recorded. |
| Illustrator | new `x.illus` | Optional but real — some collectors specifically chase an artist across sets (e.g. Mitsuhiro Arita cards); pokemontcg.io exposes this per card too. |
| Where it is | universal `location` | Binder/slot/box — already free text, TCG Collector's "binder + slot" need is already met. |
| Value / cost | universal `paid`/`worth` | Hand-entered, as elsewhere in Cabinet — no live pricing. |
| Set completion (owned/total) | **new feature**, not a field | See §4. |
| Missing-card checklist | **new feature**, reuses existing `status:"wanted"` | See §4. |
| Weighted grade-point average (PSA-style) | **not recommended** | See §6. |

## 3. Recommended `CB_TYPES` entry

```js
{id:"pokemon", name:"Pokémon cards", maker:"Set",
 cond:["Mint (M)","Near mint (NM)","Lightly played (LP)","Moderately played (MP)",
       "Heavily played (HP)","Damaged"],
 fields:[{k:"no",l:"Card number",ph:"025/102"},
         {k:"rarity",l:"Rarity",opts:["Common","Uncommon","Rare","Double Rare","Ultra Rare",
                 "Illustration Rare","Special Illustration Rare","Hyper Rare","ACE SPEC Rare",
                 "Rare Holo","Rare Secret","Promo"]},
         {k:"variant",l:"Variant",opts:["Normal","Holo","Reverse holo","1st edition",
                 "Shadowless","Promo","Stamped"]},
         {k:"lang",l:"Language",opts:["English","Japanese","Korean","Chinese",
                 "German","French","Italian","Spanish","Portuguese","Other"]},
         {k:"grader",l:"Grading",opts:["Raw (ungraded)","PSA","CGC","BGS","ACE","Other"]},
         {k:"grade",l:"Grade",ph:"PSA 10, BGS 9.5…"},
         {k:"cert",l:"Cert number",ph:"12345678"},
         {k:"illus",l:"Illustrator",ph:"Mitsuhiro Arita"}]}
```

8 type-specific fields — inside the "max ~12" budget, and roughly the same
shape as the other templates (6 fields each) plus two extra because trading
cards genuinely carry more independently-varying metadata (rarity, variant,
grading are all different axes, where e.g. coins fold "grade" into one
`cert` field already). None need `wide:true` — nothing here is long-form text
the way `prov` (art) or the notes field already are.

**Why `maker` → "Set", not "Illustrator":** `maker` is Cabinet's one
universal grouping field — the whole point of the design (see the comment
block at index.html:32943) is that "By maker" grouping and CSV columns work
for free, for every template, with no new code. For a painter that's the
artist; for a card collector it is unambiguously the **set** — "show me all
my Prismatic Evolutions cards" is the single most common way a Pokémon
collector actually organises a collection, it's how Pokellector, TCG
Collector and the PSA Set Registry all group by default, and — critically —
it's also the exact grouping the set-completion feature in §4 needs to
compute owned/total. Making `maker` do double duty as "the set" means
progress tracking reuses the grouping-by-maker code path Cabinet already
has, instead of inventing a second, parallel notion of "which set is this
in". Illustrator is real information collectors want (confirmed by
pokemontcg.io exposing it per-card) but it fragments a collection into
one-bucket-per-artist, which is not how anyone browses their own binder — so
it becomes its own field (`x.illus`) instead.

**Recommended default `maker` value at collection-creation time**: leave it
free text as usual (matching how `models`/`coins` already work), but see §4
for offering a datalist of set names sourced from `tools/pokemon/sets.json`
so what the owner types matches a real set closely enough for progress
tracking to find it.

## 4. Set-completion feature spec

Kept deliberately small and 100% offline — no card-level master database
(that would be ~19,500+ individual cards across 174 sets, megabytes of data,
a different order of magnitude from every other file in this repo), just the
174-row *set* list already in `tools/pokemon/sets.json` (~26 KB).

1. **Bundle the set list.** Add `tools/pokemon/sets.json`'s contents as a
   small `const CB_PKMN_SETS=[...]` near `CB_TYPES` (or lazy-load it once per
   session) — 174 rows of `{code,name,series,releaseDate,total,printedTotal}`
   is a rounding error next to index.html's existing size.
2. **Autocomplete on the Set field.** When the collection's template is
   `pokemon`, back the maker input with a `<datalist>` built from
   `CB_PKMN_SETS.map(s=>s.name)`, so what gets typed matches a real set
   without forcing an exact-match dropdown (a collector should still be able
   to type "my binder" as a pseudo-set if they want to, exactly as `maker` is
   free text everywhere else in Cabinet).
3. **Progress panel.** On the collection page, when the template is
   `pokemon`, group existing items by `maker` as already happens for "By
   maker" (index.html:34346), and for every group whose name matches a
   `CB_PKMN_SETS` entry (case-insensitive), show a small bar: `owned / total`
   using that set's `printedTotal` as the denominator and a count of items in
   that group with `status` not in `CB_GONE` (i.e. not sold/given away — the
   existing convention, see index.html:33015-33018) as the numerator. Groups
   that don't match any known set (custom binders, "Misc") simply show no bar
   — this degrades gracefully rather than blocking on an exact name match.
4. **Missing-card list, without a card database.** Rather than a checklist
   pre-populated with 102 named cards (which needs the card-level data this
   design deliberately excludes), reuse the **existing `status` field**:
   marking an item `wanted` or `ordered` already means "not owned yet, but
   tracked" everywhere else in Cabinet. A per-set filtered view — "this set,
   status = wanted or ordered" — is the missing-card list, with zero new data
   model. The owner creates a row for a card they want (title + card number +
   set) before they own it, same as they'd do for a `wanted` painting or
   record today.
5. **Per-set value tally.** Sum `worth` (falling back to `paid`) across
   owned items in a matched group — this is the same aggregate Cabinet
   likely already needs for "collection is worth" totals elsewhere, just
   scoped to one `maker` group instead of the whole collection.
6. **What this explicitly does not do:** it does not know which 40 of 102
   cards in a set are still unowned when the owner hasn't created rows for
   them (that needs per-card master data — see §6), and it does not compute
   a PSA-style weighted grade average (needs a per-card rarity weight, which
   this dataset doesn't carry). Both are namable v2 ideas, not blockers for
   v1.

## 5. Czech labels

Cabinet's `CS` dictionary is one flat, global, exact-string map (`t(str)`
looks up the literal English source string), so **existing keys were reused
wherever the exact string already matches** rather than being retranslated —
this avoids duplicate entries and, in one case (see the `"Mint"` collision
below), avoids reintroducing a real bug.

New template name:

```
"Pokémon cards":"Pokémonové karty",
```

New field labels (`l:` values) — reusing `"Language":"Jazyk"` which already
exists (index.html:22959, from Settings) since it's the exact same string:

```
"Set":"Set",                 /* kept as the loanword Czech collectors already
                                 use; "Sada" is the literal alternative if
                                 Simon prefers it */
"Card number":"Číslo karty",
"Rarity":"Vzácnost",
"Variant":"Varianta",
"Grading":"Ohodnocení",
"Grade":"Známka",
"Cert number":"Číslo certifikátu",
"Illustrator":"Ilustrátor",
```

New condition-ladder entries — **reusing** `"Mint (M)"` and
`"Near mint (NM)"` from the `music` template (index.html:34395) and
`"Damaged"` (index.html:34391), which are exact matches already translated:

```
"Lightly played (LP)":"Lehce hraná (LP)",
"Moderately played (MP)":"Středně hraná (MP)",
"Heavily played (HP)":"Silně hraná (HP)",
```

New rarity options:

```
"Common":"Běžná", "Uncommon":"Neobvyklá", "Rare":"Vzácná",
"Double Rare":"Dvojitě vzácná", "Ultra Rare":"Ultra vzácná",
"Illustration Rare":"Ilustrační vzácná", "Special Illustration Rare":"Speciální ilustrační vzácná",
"Hyper Rare":"Hyper vzácná", "ACE SPEC Rare":"ACE SPEC vzácná",
"Rare Holo":"Vzácná holo", "Rare Secret":"Tajná vzácná",
```

(`"Promo"` is reused — check whether it already exists as a key before
adding; if not, `"Promo":"Promo"` is a fine loanword pass-through, same
reasoning as `"Set"`.)

New variant options:

```
"Normal":"Normální", "Holo":"Holo", "Reverse holo":"Reverse holo",
"1st edition":"1. edice", "Shadowless":"Bez stínu", "Stamped":"S razítkem",
```

New language options — only the ones not already covered by the app's own
UI-language list; `"English"`, `"German"`, `"French"`, `"Italian"`,
`"Spanish"`, `"Portuguese"`, `"Other"` are common enough words to check
against the existing dict first (the app already has language pickers
elsewhere for its own UI):

```
"Japanese":"Japonština", "Korean":"Korejština", "Chinese":"Čínština",
```

New grader options:

```
"Raw (ungraded)":"Nehodnocená",
```

(`"PSA"`, `"CGC"`, `"BGS"`, `"ACE"` are brand names/acronyms and should stay
as-is in both languages, same as `"NGC"`-style certification strings the
`coins` template already leaves untranslated, e.g. `"NGC MS64"` at
index.html:32988.)

**The "Mint" collision** (found while checking for exact-string reuse, not
part of the original task, but directly shaped the recommendation above):
`"Mint"` already exists as a `CS` key mapped to `"Máta"` — the herb, from
Pottingbench's plant database (index.html:23402, `"Mint":"Máta"`). Cabinet's
own `custom` template already uses bare `"Mint"` as a condition value
(index.html:33007), which means **that condition option is silently
mistranslated to "Máta" in the Czech UI today** — a pre-existing bug, not
something introduced here, but worth flagging to Simon since it's a one-line
fix (rename the `custom` template's `cond` entry to `"Mint condition"` or
similar, or add a Cabinet-specific override). It's also exactly why this
proposal uses `"Mint (M)"` for Pokémon rather than bare `"Mint"` — that exact
string is already safely translated (`"Mint (M)":"Mint (M)"`,
index.html:34395) and does not collide.

## 6. Risks / open questions

- **The "Mint" translation collision** above is a real, currently-shipping
  bug in the `custom` template, discovered as a side effect of this
  research. Worth a one-line fix independent of the Pokémon work.
- **Set-name matching is fuzzy by design** (§4 step 3): a collector who types
  "Base Set" won't match pokemontcg.io's set named "Base" without a
  normalising alias table (`"Base Set"→"base1"`, `"Base Set 2"→"base4"`, a
  handful of others differ from Bulbapedia's fuller names — see §7). This is
  small (under a dozen aliases) but is a real implementation detail, not
  covered by this doc, which only supplies raw set data.
- **No card-level database, so no auto-populated 102-card checklist.**
  Decided deliberately (§4.6) to keep this offline and small; if a
  future request wants a true "which named cards am I missing" list, that
  needs pokemontcg.io's *card* endpoint (or a Bulbapedia scrape) bundled
  per-set on demand — likely fetched lazily rather than bundled, which would
  be the first place this module needs network access at all. Flagging for
  Simon's call, not assuming it.
- **PSA-style weighted GPA** is real and is what serious graded-set
  collectors actually compare against each other, but it needs a per-card
  rarity/value weight (1–10) that this dataset doesn't have — recommending
  against it for v1 (§1, §4.6).
- **Language field vs. UI language**: the `lang` option list for the *card*
  (Japanese/Korean/Chinese/…) is unrelated to the app's own EN/CS interface
  language — worth a distinct field name in code (`x.lang`, not reusing any
  app-wide "language" state) so there's no accidental coupling.
- **Rarity/variant lists will drift.** Pokémon TCG has introduced a new
  top-tier rarity roughly every couple of years (Illustration Rare and
  Special Illustration Rare both post-date many existing trackers). The
  `opts` list in §3 is current as of the sets in `tools/pokemon/sets.json`
  (through July 2026's *Pitch Black*) but will eventually need a "something
  else" / free-text escape hatch, or a periodic list refresh — noting this
  rather than solving it, since Cabinet's existing `select` field type
  (`{k,l,opts:[...]}`) doesn't currently support an "other, please specify"
  fallback for any template.

## 7. Data file

`tools/pokemon/sets.json` — 174 English-language Pokémon TCG sets, Base Set
(1999) through the newest 2026 set. Fields: `code` (the pokemontcg.io set
id, e.g. `base1`), `name`, `series`, `releaseDate` (`YYYY/MM/DD`), `total`
(cards in the full print run including secret rares), `printedTotal` (the
number printed on the card itself — the right denominator for "X/Y" progress
displays, since that's the number a collector actually sees on their own
cards).

- **Source:** `https://api.pokemontcg.io/v2/sets?pageSize=300&orderBy=releaseDate`
  (public, no API key needed at this volume), fetched 2026-09-05.
- Sorted oldest→newest. Earliest entry: `base1` "Base" (1999/01/09, the set
  Bulbapedia calls "Base Set" — pokemontcg.io's own name is shorter; noted
  as an aliasing risk in §6). Latest entry at fetch time: `me5` "Pitch
  Black" (2026/07/17, Mega Evolution series).
- Not cross-checked against Bulbapedia line-by-line; the API response was
  internally consistent (monotonic release dates, no gaps in series
  numbering) and is the same source most of the third-party trackers in §1
  build on, so treated as reliable. If a discrepancy ever surfaces (e.g. a
  set renamed after release), Bulbapedia is the fallback source named in the
  task.
