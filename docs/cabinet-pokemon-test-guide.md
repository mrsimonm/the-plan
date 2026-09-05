# Cabinet — Pokémon cards: phone test guide

Build: **v1.0.62** (bump commit `…`; feature commits `3298655` template + `4116b94` set completion).
Scope: the new **"Pokémon cards"** Cabinet collection type and its set-completion panel.

## Tap-by-tap

1. **Update / version** — if the "reload for the new version" toast appears, tap reload. The version chip (bottom-left) should read **v1.0.62**.
2. **Create the collection** — Cabinet → **+ New collection** → choose **Pokémon cards** from the type list. The maker label should read **Set** (it will say **Sada** once you switch to Czech). Save.
3. **Add an owned card** — open the collection → **+ add item**:
   - Title: `Charizard`
   - **Set** (the maker field): start typing `Base` — a dropdown of the real set names appears (autocomplete); pick **Base**. If you prefer, type `Base Set` instead — both must land on the same set.
   - Card number: `4/102`
   - Status: leave **Owned** (default). Save.
4. **Add a wanted card from the same set** — **+ add item**, Set = **Base**, title `Pikachu`, card number `58/102`, and set **status = Wanted**. Save.
5. **The completion panel** — back on the collection page you should now see, above the item list, a **Base** panel:
   - progress bar with **1 / 102** (owned over the set's printed total),
   - an owned line and the **Missing** list containing your wanted Pikachu,
   - a per-set value tally (the owned card's `worth`, or `paid` if worth is empty).
6. **Check it persists** — reload the page: the panel and both cards are still there.
7. **Czech** — switch EN → CZ. The type name shows **Pokémonové karty**, the maker field label **Sada**, and field labels/options are Czech (Card number → Číslo karty, Rarity → Vzácnost, Wanted → Chtěná/Wanted status label, etc.). The **Set completion** heading reads **Dokončení sad** and **Missing** reads **Chybí**.
8. **A pseudo-set degrades gracefully** — add an item whose Set is e.g. `my binder` (free text, not a real set): it appears in the item list but draws **no** progress panel — nothing breaks.

## What "owned" means for the bar

Owned = items with status *not* Sold/Gifted/Wanted/Ordered (the same convention the rest of Cabinet uses). Each distinct card counts as one, regardless of `qty`. Sold/given-away items are excluded from the numerator and the value tally.
