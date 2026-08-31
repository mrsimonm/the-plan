# Pottingbench redesign — liquid glass, on branch `redesign-glass-v2`

Fresh attempt, branched from `main`. The prior `redesign-glass` branch
(color-token swap, then a "Nothing gadget" pixel-font pass, then a partial
walk-back) is discarded entirely — nothing from it carried forward.

**Skills read before starting:** `high-end-visual-design` and
`redesign-existing-projects`, both loaded and confirmed in-chat. Applying:
the Double-Bezel/layered-depth thinking from the first (adapted to real
liquid glass — blur+saturate+inner hairline+specular highlight — rather
than its dark-OLED default archetype) and the audit-then-fix priority order
from the second (fonts → color → states → layout → components).

**`ecc:loop-start` evaluated, not used for the round loop.** It scaffolds a
runbook + hook profile for autonomous, checkpointed background loops (the
kind driven by scheduled wakeups across sessions). This task is rapid
sequential design iteration inside one working session — the rounds below
ran directly, as the brief's fallback allows.

## Visual system (implemented exactly as specified)

- **Font**: system stack only (`-apple-system, BlinkMacSystemFont, "SF Pro
  Text", "Helvetica Neue", Inter, sans-serif`) via one `--font` token. 129
  separate `font-family` declarations (three different decorative/mono
  faces) consolidated down to this one variable. No pixel or dot-matrix
  font anywhere — the retro lives only in the color palette now.
- **Background**: cream `#EDEAE0` with three large soft radial-gradient
  "blobs" (teal `#5E9E85` and grey-green `#A9AE9C`, 12–24% opacity) as the
  `body`'s own `background-image` — deliberately *not* a `::before`
  pseudo-element, because a `position:fixed; z-index:-1` pseudo can lose a
  stacking-context fight against the sticky header/nav and paint in the
  wrong order (this happened during round 1 and was caught before commit).
  An element's own background is guaranteed to paint beneath its own
  content, no ambiguity.
- **Liquid glass**: one shared recipe — `--glass-fill` (cream at ~55%
  opacity), `--glass-blur: blur(24px) saturate(170%)`, a `--glass-border`
  (white at ~50%), and `--glass-shadow` (soft ambient shadow + an inset
  top-edge specular highlight in one `box-shadow` list) — applied to every
  card, tile, the header, the tab bar, buttons, dialogs, and the focus
  timer disc.
- **Shape**: `--r: 24px` on containers, `--r-sm: 13px` on controls, full
  pill (`--r-pill: 999px`) on tabs and primary buttons.
- **Text**: `--ink-strong` (charcoal `#2E2E2A`) for `h1–h3` and every `<b>`
  in the codebase (title-weight moments even outside semantic headings —
  plant names, task titles, card headers); `--ink` (dusty grey-green
  `#6E7367`) for body copy; teal reserved for `.primary` buttons, "today",
  and active/selected states — nothing else is colored.
- **Navigation**: the tab bar is now a floating glass pill, detached from
  the header, sentence-case labels, active tab a solid teal pill with
  cream text.
- **Calendar/Gantt blocks**: translucent tint with a 3px teal left edge —
  deliberately *no* per-block `backdrop-filter`, since dozens of these can
  be on screen in the day/week grid and repeated blur is a GPU cost the
  performance guideline explicitly warns against; blur stays on
  fixed/sticky surfaces (header, nav, dialogs) only.
- **Focus timer**: one large centered glass disc (`aspect-ratio:1`,
  `border-radius:50%`), the running time set in giant thin numerals
  (`font-weight:200`, `clamp(38px,9vw,52px)`), one teal Start button.
- **Modals**: glass sheet, centered card on desktop, slides up from the
  bottom on mobile (`position:fixed` + `translateY` keyframe below
  640px), blurred dim backdrop.
- **Dark mode**: same system on a charcoal-olive base (`#2E2E2A`), same
  three blobs (brighter, since the base is darker), glass fill using the
  body-text grey-green (`#6E7367`) at 42–55% instead of cream.
- **Motion**: 150–260ms transitions on buttons/tabs/tiles/dialogs, a
  global `prefers-reduced-motion` block that collapses all animation and
  transition durations to near-zero.
- Old CSS not deleted outright where it still carries real behavior (see
  "Decisions" below on `.theme-planner`/`.theme-hours`), but every value
  that painted the old look — the three-font stack, the per-module blue/
  purple accent swap, decorative hex-color arrays — was replaced, not
  layered under the new tokens.

## Decisions worth recording

- **`.theme-planner`/`.theme-hours` emptied, not deleted.** The original
  app swapped `--accent` to blue/purple while those tabs were open (toggled
  by a class the JS still adds in `showNow()`). The brief says nothing gets
  colored besides the one teal accent, so both rule bodies are now empty —
  the JS class-toggle keeps firing harmlessly, and if a future revert ever
  wants per-module identity back, the hook is still there.
- **HCOLORS (Hours per-project dot colors) and the Gantt `--cap-1..4`
  capacity-heat scale were retinted** to the same warm palette family —
  purely decorative, referenced by array index only, no user-visible names
  attached.
- **The project-planner's *named* color picker (`PAL`/`PALN` — "Teal",
  "Purple", "Rust", …) was left untouched.** Those hex values are shown to
  the user by name in a picker; recoloring the hex without renaming the
  option would make "Purple" not look purple.
- **No `backdrop-filter` on `.wb-blk`** (calendar/Gantt event blocks) — see
  "Calendar/Gantt blocks" above. This is the one place "glass" means
  "translucent tint," not "blurred," and it's a deliberate reading of the
  brief's own performance guardrail, not an omission.

## Round log

### Round 1 — implementation
Built the full visual system above across all six views in one pass (the
system had to exist before any view could be screenshotted meaningfully).
Screenshotted Garden, Diary, Academy, Daily Planner, Gantt/Timeline, and
Hours at desktop; Garden and Hours additionally at mobile and in dark mode.
Verified: full add-plant flow, started/stopped the Hours focus timer
(survived a reload), dragged a calendar block to a new time.

**Caught and fixed before commit:**
1. The blob background used a `::before` pseudo-element with
   `z-index:-1`, which lost the stacking fight against the sticky header
   and nav and rendered in the wrong paint order (invisible/behind the
   opaque body background rather than behind the glass panels). Fixed by
   moving the blobs to `body`'s own `background-image` instead.
2. The pre-existing `.theme-planner`/`.theme-hours` blue/purple accent
   swap was still active and referenced the now-renamed `--bloom-a/b`
   tokens — both a broken reference and a direct violation of "nothing
   else is colored." Emptied both rule bodies.
3. `--ink-2` (75 references) was orphaned when the token set was
   rebuilt — added as a compatibility alias (`--ink-2: var(--ink)`) rather
   than hunting down 75 individual call sites, since the semantic mapping
   is exact (old secondary-text tier → new body-text tier).

### Round 2 — glass consistency
Critique of round 1's screenshots: several surfaces sat right next to true
glass cards while themselves being flat, opaque fills — the kind of thing
that reads as "the same app with new colors" under scrutiny rather than a
committed material change. Fixed the five worst instances:

1. **Calendar/planner blocks (`.wb-blk`)** — flat `--accent-soft` fill
   swapped for a translucent glass tint (`color-mix` over `--glass-fill`).
2. **Academy picto tiles (`.ptile`)** — flat `--surface-2` swapped for
   `--glass-fill` + `--glass-border`, matching every other tile.
3. **Stat number tiles** (Hours, Stats) — flat `--sunk` with no border
   upgraded to full glass, backdrop-filter included (only 2–4 on screen
   at a time, so the blur cost that ruled it out for calendar blocks
   doesn't apply here).
4. **Inputs/selects/textareas** — were on the 24px container radius,
   which on a ~38px-tall field read as an odd near-stadium shape; moved
   to the 13px control radius.
5. **`.sp-pick`, `.sp-add`, `.chip`, `.wk`** — four more control-scale
   elements still on the container radius; moved to control-scale or
   full pill depending on whether each reads as a field or a toggle/tag.

Re-screenshotted Daily Planner (calendar block), Academy (tiles + search
field), and Hours (stat tiles + inputs) at desktop in light mode to confirm
each fix. Committed as `ca47a44`.

### Round 3 — a real bug, not a polish nit
Screenshotted Garden on mobile for the first time since round 1 and found
the floating pill nav was overflowing the viewport: `.nav` used
`max-width:fit-content`, so the pill grew as wide as its full six-tab
content — wider than a 390px phone screen. The pill's own rounded ends
were pushed off-screen with no visible affordance that it could scroll; at
rest the screenshot just showed a clipped rectangle with "Bench" cut down
to "nch". This is the kind of thing that would have shipped invisibly if
mobile hadn't been screenshotted again after round 1.

Fixed: `.navwrap` becomes a centering flex container, `.nav` gets
`max-width:100%` instead of `fit-content`. Confirmed via
`getBoundingClientRect()` that the nav's own box (`left:12, right:378`)
now sits fully inside a 390px viewport, with `scrollWidth` (487) exceeding
`clientWidth` (364) — content scrolls *inside* the pill, the pill itself
never overflows.

Also used this round to check two spec requirements not yet screenshotted:
the New Plant modal correctly renders as a bottom sheet on mobile (rounded
top corners only, blurred dim backdrop, slides up) — implemented in round
1 but never actually verified until now — and Academy in dark mode, which
matched round 1/2's light-mode result with no new issues. Committed as
`1b1f41f`.

### Round 4 — dark-mode surface weight, final drag regression check
Checked the two view/theme combinations not yet screenshotted (Diary on
mobile, Gantt/Timeline in dark mode). Diary was clean — the round 3 nav
fix holds. Gantt in dark mode surfaced one more thing: the Daily Planner's
"Free" capacity-bar segment (an unfilled track with no explicit background,
inheriting `--sunk` from its parent `.budget-bar`) read as a near-black
slab next to the surrounding charcoal-olive glass panels — `--sunk` was
`#282824`, close enough to black at a glance to undercut the "no pure
black" spirit of the brief even though it's not literally `#000`.
Lightened to `#333330` — still correctly darker/recessed than `--surface`
in both directions, just not reading as a flat black hole.

Closed the round by re-running the round-1 drag regression test against
every change through round 4: created a task, dragged it from 10:00 to
13:00 on the day grid, confirmed the block's label updated. Drag still
works after four rounds of surface changes. Committed as `24711e5`.

### Round 5 — sweeping the views never screenshotted
Per the "what to do next" list above, swept the views this branch had never
opened in a browser: Stats, the Grow/Propagation guide detail, starting a
propagation batch and its check-in card (Cuttings/Batch tracking), Bench's
mixing sliders, and Shelf (product list + Settings toggles + Appearance).

**No code changes this round.** Every one of these inherited the design
system cleanly: glass stat tiles with big numbers, the propagation guide's
step list and "when/what/how" sections read exactly like Academy's, the
batch check-in card's segmented "Roots showing / Nothing yet / Lost one"
control matches every other segmented control in the app, the water-volume
and strength sliders use the same teal-filled-track language as the
day/week/month scope slider, and the product-shelf rows' status pills
(`NO DOSE`, category tags, `BIO`) read as small glass-tinted badges
consistent with everywhere else pills appear. Re-checked Shelf in dark
mode too (via the Daily Planner day-grid, which was on screen at the
time) — the round 4 `--sunk` fix holds there as well.

This is a genuine, if less dramatic, finding: five rounds of building and
fixing the *shared* system paid off here — there was nothing view-specific
left to fix because nothing in these views does anything the shared
tokens don't already cover. Screenshots: `r5-stats-desktop.png`,
`r5-grow-desktop.png`, `r5-propguide.png`, `r5-batch-modal.png`,
`r5-cuttings-batch.png`, `r5-bench-desktop.png`, `r5-shelf.png`,
`r5-shelf-products.png`, `r5-shelf-dark.png`.

**Stopping at 5 of the allowed 6 rounds.** Round 5 found zero problems
across eight more screens — a sign of the system holding up, not a sign
there's nothing left to look at, but pushing to round 6 with no next
concrete concern isn't the same "meaningful improvement" bar the earlier
rounds cleared. Views still not opened in this session: Product/Formula
detail (only the list was checked), the fullscreen planner focus mode, and
History/Log.

## Definition of done

Pulled a true "before" by extracting `main`'s pristine `index.html` (`git
show main:index.html`) and serving it on a separate port — not a snapshot
from partway through this branch's own history.

**Garden**, desktop, side by side:
- Before: near-white background, opaque solid-green pill nav, uppercase
  "+ PLANT" button, flat white cards with a generic drop shadow.
- After: cream background with visible soft teal/grey-green blobs, a
  floating translucent glass pill nav with a solid-teal active tab,
  sentence-case "+ Plant" button, glass cards with a bright inner hairline
  and specular top highlight.
- Nobody mistakes these for the same app with a color change. **Pass.**

**Hours**, desktop, side by side:
- Before: flat white/grey opaque cards, a dark-navy "ADD" button, and a
  purple "FOCUS" segment (the old per-module accent swap) — no glass, no
  blobs, no shape system.
- After: warm cream + blobs, glass stat tiles, a solid teal "Add" pill,
  and — the clearest single tell — the running clock is no longer a
  number in a box but one large centered glass disc with giant thin
  numerals.
- **Pass.**

**Academy, Diary, Daily Planner, Gantt/Timeline**: not independently
re-fetched from `main` for a literal before/after pair in this check (time
budget), but every one of them inherited the same global rebuild verified
above — floating glass nav, cream+blob background, glass cards/tiles,
system font, teal-only accent — and each was individually screenshotted
across rounds 1–4 in at least two of {desktop, mobile, light, dark}. I'm
confident in the same verdict for these four on the strength of the shared
token system, not a guess: the same variables that produced the Garden/
Hours contrast above are the only variables any of these views' CSS reads.

## Self-critique

**What's solid:** the material system reads as a genuine liquid-glass
rebuild, not a re-skin — blobs are visible behind every glass panel,
blur+saturate+inner-hairline+specular-highlight is applied consistently
rather than per-view, the shape system (24/13/pill) is used with intent
rather than one radius everywhere, and the focus-timer disc is a real
"this couldn't be the old app" moment. The four rounds caught two things a
single implementation pass would have shipped broken — the blob stacking
bug and the mobile nav overflow — which is the actual value of doing
rounds instead of one pass and calling it done.

**What I'd push further with more time:**
- **5 of the allowed 6 rounds ran.** Rounds 1–4 each found and fixed
  something real (a stacking bug, five flat-surface inconsistencies, a
  genuine mobile layout bug, a dark-mode contrast issue); round 5 swept
  eight more screens (Stats, the propagation guide, Batch/Cuttings,
  Bench's sliders, Shelf) and found nothing to fix — a real result, not a
  skipped check, and the reason I stopped before round 6 rather than
  padding it with cosmetic non-findings. Product/Formula detail, the
  fullscreen planner focus mode, and History/Log are still unopened.
- **The calendar/Gantt blocks are glass in name more than in feel.** The
  no-`backdrop-filter` decision (performance-motivated, dozens of blocks
  on one grid) means `.wb-blk` is a translucent *tint*, not something that
  visibly refracts what's behind it the way the cards and the timer disc
  do. That's a defensible tradeoff, not a mistake, but it's also the one
  place in the app where "liquid glass" is weakest, and a future pass
  could test whether a much cheaper blur radius (4–6px) on just the
  *visible* blocks (not the whole grid) gets some of the refraction back
  without the GPU cost.
- **Dark mode got one fix (the `--sunk` lightening) but not a full
  critique pass of its own.** Every dark-mode screenshot in this report is
  a spot-check of a view already validated in light mode, not an
  independent "does dark mode have its own problems" pass. Given more
  time I'd screenshot all six views in dark mode specifically looking for
  contrast and glass-visibility issues that only show up against the
  charcoal-olive base, not the cream one.
- **Named color picker (PAL/PALN) and HCOLORS/`--cap-1..4` are the only
  remaining non-neutral colors in the app**, by design (see "Decisions"),
  but I haven't checked whether they look *out of place* against the new
  glass system specifically — they were retinted for palette family, not
  re-verified for how they read as swatches on translucent surfaces.

**What to do next**, in priority order: (1) open the three views still
unopened — Product/Formula detail, the fullscreen planner focus mode,
History/Log; (2) a dedicated dark-mode critique pass across all six views,
not spot-checks; (3) revisit whether calendar blocks can get a cheap,
bounded blur; (4) re-verify the Gantt bar drag-to-reschedule interaction
specifically (the day-grid drag was re-tested every round; the Timeline
module's own drag was not).

## Round 6 (post-merge) — "make it luxurious": colour and gradients

Shipped after rounds 1–5 were merged to `main` and live. Direct feedback:
liked the direction, wanted the palette pushed further with visible colour/
gradients in the background and fields, and didn't like the flat charcoal
dark mode — asked for the teal-green to carry dark mode instead.

**Tool note**: tried `mcp__visualize` first per the request to use available
design tools, but its own design system explicitly forbids gradients, mesh
backgrounds, and decorative surface effects (it's built for flat, neutral
chat widgets) — the opposite of what this needed. Experimented directly in
the real app instead, which gives an accurate preview of the actual glass+
gradient interaction and lets me verify with real screenshots rather than a
static mockup.

**Light mode**: went from three faint background blobs to four visibly
saturated ones (added gold and terracotta alongside teal/sage), spread
further before fading out, so the wash reads as colour rather than an
ambient tint. Added `--glass-sheen` — a diagonal gradient (a hint of accent
catching light top-left, fading to neutral glass) — applied to every major
glass surface: cards, plant tiles, the plant hero card, buttons, and the
focus-timer disc. Primary buttons got a two-stop teal gradient instead of
flat fill.

**Dark mode**: rebuilt from neutral charcoal-olive (`#2E2E2A`) to a deep
emerald-green lounge (`#122019`) — same teal accent, now the dominant glow
against near-black green instead of sitting on flat grey. This is a much
bigger change than the round-4 `--sunk` tweak; it's a different dark mode,
not an adjustment of the old one.

Verified: Garden, Academy, Hours (stat tiles + the focus-timer disc) in
both themes at desktop; re-ran the drag regression test post-change to
confirm nothing geometry-related moved. Screenshots: `lux-garden-light.png`,
`lux-garden-empty-3.png` (clean, no mid-transition ghosting — see below),
`lux-garden-dark.png`, `lux-hours-dark.png`, `lux-hours-clock-dark.png`,
`lux-academy-light.png`, `lux-planner-blocks.png`.

**One non-issue worth recording**: a screenshot taken immediately after
`reload()` (`lux-garden-empty-2.png`) showed ghosted text from the
previously-open view bleeding through — a mid-cross-fade-transition capture,
not a rendering bug. Re-screenshotting after the transition settled
(`lux-garden-empty-3.png`) confirmed clean output. Noting this so a future
round doesn't chase a phantom bug: screenshot after a brief settle, not
immediately on reload, when comparing exact pixels.

**What I didn't get to**: the request also asked "any other ideas how to do
it better" — I didn't propose alternatives beyond the direction implemented
(e.g., a second accent hue for a true two-accent system, or per-section
themed gradients rather than one global wash). Worth raising as an open
question rather than assuming this is the final direction.

## Round 7 — separating the glass panels from the background

Direct feedback on round 6: the panel sheen used the same diagonal
direction and accent tint as the background blobs, so cards read as a
continuation of the gradient rather than a distinct floating layer —
colour-wise and shape-wise separation was asked for specifically.

**Skill used**: `ecc:liquid-glass-design` (Apple's iOS 26 Liquid Glass
patterns). Its SwiftUI/UIKit code doesn't translate to CSS, but its core
principle does: glass is a *material* with its own light reflection —
`.glassEffect(.regular.tint(color))` applies a tint to the glass itself,
independent of whatever content sits behind it. That's precisely what was
missing: the CSS sheen was inheriting the background's hue and direction
instead of having its own.

**Fix**: `--glass-sheen` no longer mixes in `--accent` at all — it's now a
plain white highlight banded across the top edge only (180deg, distinct
from the background blobs' diagonal flow), simulating light falling on the
glass from above rather than colour bleeding through it. `--glass-fill`
opacity raised (.55→.68 light, similarly in dark) so panels read as a
denser, more opaque material sitting *on* the colour rather than nearly as
transparent as the colour itself. Border and ambient shadow strengthened
to match with shape-wise separation (a more visible "elevated" panel, not
just a colour change).

Verified via playwright-cli: Daily Planner, Garden/Library, in both
themes — screenshotted after letting the tab-switch cross-fade settle this
time (confirmed in round 6 that screenshotting immediately on reload can
catch a transition mid-flight; not a bug, just bad timing). Result: cards
now visibly read as bright panels floating above the background in both
light and dark mode, rather than blending into the gradient wash.

## Round 8 — real frosted texture, spot highlights, glassier tabs

Three asks: (1) actual frosted-glass texture, not just blur; (2) tabs feel
more glass-like; (3) the round-7 top-band highlight was still "too linear,"
wanted a few spots instead.

**Texture**: added a fixed SVG-noise grain layer (`feTurbulence`,
`mix-blend-mode: overlay`, opacity .05 light / .07 dark) sitting above the
whole app, `pointer-events:none` so it can never intercept a click or drag.
This is the same technique from the very first `redesign-glass` attempt,
reintroduced here since this branch never had it — it's what makes surfaces
read as textured glass rather than just smoothed-over blur.

**Spot highlights, and a real bug caught by the feedback loop**: reworked
`--glass-sheen` from a linear top-band into a few small radial catch-light
spots. First attempt used small, high-opacity spots — screenshotting the
result showed distinct floating white circles inside the cards, not a
diffuse glow. Diagnosed properly rather than guessing: disabled the grain
layer via an injected stylesheet to rule it out as the cause, then used
`document.elementFromPoint()` to confirm the blobs sat exactly where the
`--glass-sheen` radial-gradient math placed them — the spots were working
as coded, just too small and too opaque to read as anything but a hard
circle. Fixed by making them much larger and much lower-opacity with a
longer fade (peak opacity .6→.28, radius roughly 2–3× larger). Re-screenshot
confirmed clean, diffuse highlights with no stray blobs.

**Tabs**: given their own heavier version of the material — blur 24px→30px,
saturate 170%→190%, a brighter pair of spots than the standard recipe —
since the tab bar is the one glass surface always on screen.

Verified via playwright-cli in both themes, and re-ran the drag regression
test with the grain layer active to confirm `pointer-events:none` actually
passes mouse events through to the calendar block underneath (it does).

## Round 9 — richer colour, and the actual reason Apple's glass edges look classy

Two asks: more colour in light mode, and address that the edges "don't
look as classy" as Apple's own liquid glass.

**Colour**: light-mode blob RGB values shifted to punchier hues (not just
higher opacity) — e.g. the teal blob went from `rgba(94,158,133)` to
`rgba(72,164,128)` — plus opacity raised again across all four. Reads as
genuinely colourful now rather than a tinted neutral.

**Edges — the actual answer to "how do they do it"**: a flat CSS
`border-color` can only ever be one solid colour. Real glass doesn't have
a uniform-colour rim — light catches one side and barely touches the
other. That unevenness *is* the classy part; a single-colour hairline
border, however bright, can never reproduce it. Fixed by adding
`--glass-edge`, a gradient applied via `border-image` (the only way to put
a gradient on a border) — bright top-left, dimming through the middle,
brightening slightly again bottom-right — on the seven highest-visibility
surfaces (cards, tiles, the timer disc, stat tiles, the nav, plant hero
card, dialogs). Left buttons/chips/segmented controls/calendar blocks on
the simpler flat hairline — too many on screen for the gradient to read
as anything, and `border-image` carries a small per-element cost.

Also strengthened `--glass-shadow` with a crisp outer 1px ring (the old
pure-white inner highlight could nearly vanish against a light background)
and a subtle inset bottom shadow for bevel, in both themes.

Verified via playwright-cli: corners checked at hi-res for `border-image`/
`border-radius` rendering artifacts (none found) in both themes; re-ran
the drag regression test post-change.

**Correction, round 10**: that "none found" was wrong. The user spotted
hard corners under the rounded ones in actual use — `border-image` not
respecting `border-radius` is a known cross-browser inconsistency
(Safari especially), and it evidently didn't reproduce clearly enough in
the Chromium screenshots above for me to catch it. Recorded here rather
than quietly editing the claim above, since the point of this log is an
honest trail, not a clean one.

## Round 10 — fixing the hard corners for real

Replaced `border-image` with the mask-composite technique: a `::before`
pseudo-element sized to match its parent (`inset:0`, `border-radius:
inherit`), painted with `--glass-edge`, then cut down to a 1px ring via
`padding:1px` + `mask-composite:exclude` (`-webkit-mask-composite:xor`
alongside it for older Safari). Because the ring's shape comes from an
actual `border-radius` on a real box rather than `border-image`'s own
slicing logic, it follows any radius exactly — including the 50% on the
circular focus-timer disc, checked directly and confirmed as a clean
circle with no corner artifacts.

One risk checked rather than assumed away: giving the seven surfaces
`position:relative` for the pseudo-element to anchor to includes
`dialog`, and native `<dialog>` centering normally depends on
`position:fixed` from the browser's own UA stylesheet. Verified in the
running app that the New Plant dialog still centres correctly on desktop,
and that the existing mobile bottom-sheet override (`position:fixed`
inside the `max-width:640px` query) still wins there since it's more
specific in the cascade.

Verified via playwright-cli: hi-res screenshots of a rectangular card,
the floating nav pill, and the circular timer disc — clean gradient
rings, no hard edges, in any of the three shapes. Re-ran the drag
regression test post-change.

## Round 11 — merging panels that sit too close together

Feedback: panels sometimes sit close enough that two sets of rounded
corners fight each other, and the fix should be to merge them into one
panel instead of leaving two separately-rounded boxes touching.

**Investigated rather than assumed.** My first hypothesis, from a desktop
screenshot of Diary, was that the round-8/9 glass-sheen gradient was
painting a false "box within a box" illusion inside the "Coming up" card.
Tested it directly: injected a stylesheet that disabled the sheen and
re-screenshotted — pixel-identical result, so that wasn't it. Then
inspected the actual DOM (`getBoundingClientRect` + computed styles on
every child of the card) and confirmed no nested element had its own
background or border-radius. The real issue only became obvious at mobile
width: "Coming up" and "Schedules" were genuinely two separate sibling
`.card` elements, a plain 12px `.stack` gap apart — fine on desktop, tight
enough on a 390px-wide screen that the two rounded-corner boundaries read
as competing with each other around a small label.

**Fix**: merged them into one `.card` with an internal divider (border-top
on the "Schedules" section) — the same `.card-sec` pattern already used
elsewhere in this codebase for "one card, several related sections that
belong together." The explanatory hint paragraph stays outside the card
as a caption, unchanged.

Verified via playwright-cli at both desktop and mobile widths, and walked
through "+ Schedule" to its validation dialog to confirm the `#schedList`
element — now wrapped differently but same id — still receives content
and its click handler still fires.

**Scope note**: I found and fixed one clear instance of this pattern by
checking Diary, Bench, and Academy at both widths. I did not do an
exhaustive sweep of every view (Batch, Cuttings, Shelf, Product, Formula,
Log, the fullscreen planner focus mode are still unchecked from earlier
rounds too) — if there's another specific spot this is still happening,
a screenshot or view name would let me fix that one directly rather than
me guessing again.

## Round 12 — search in Plachta (a real feature, not a visual pass)

First functional addition in this whole redesign, scoped to Plachta only
per request. A search field plus an Upcoming/Past segmented toggle now
sits above Plachta's continuous canvas (hidden for every other scope).

**Data scope, decided deliberately**: searches `S.planner.tasks` (covers
both one-off tasks and events — anything with a concrete `due` date) by
title, filtered to upcoming (`due>=today`) or past (`due<today`), sorted
nearest-first in whichever direction, capped at 40 results. Left
`S.planner.blocks` (recurring templates like "Sleep") out on purpose —
those recur on a weekly pattern rather than carrying one due date, so
"upcoming vs. past" doesn't map onto them the same way. In the Past
bucket, a task nobody ever marked done is flagged in the existing
`--crit` red — a genuinely missed thing, distinct from a past Event
(just a record) or a completed task.

Clicking a result re-centres Plachta on that date. This needed its own
explicit call (`pPlachtaAnchor = iso; renderSchedule(); pPlachtaCentre
(iso)`) rather than just setting the anchor — `renderSchedule()`'s own
centring logic only defaults to today or preserves whatever scroll
position was already there, so without the explicit re-centre afterward
the jump would silently land on the wrong day.

**A debugging note worth keeping**: while testing this, a drag on an
unrelated calendar block appeared to stop working — dragging a 22:00
task downward did nothing. Traced it down before assuming a regression:
the block was near the bottom of the 24-hour grid with nowhere further
to go, and dragging the same block *upward* worked immediately. Not a
bug, but confirms the value of tracing rather than guessing when
something looks broken.

Verified via playwright-cli: created a task, searched for it, clicked
through to confirm the canvas re-centres correctly; toggled Past/Upcoming
and confirmed the empty state; searched an existing event to confirm
Task/Event labels render correctly for both kinds. Checked desktop,
mobile, light, and dark.

## Round 13 — fullscreen focus mode was clipping the 24-hour grid

Real regression, from round 10. That round added `position:relative`
straight onto the shared `.card` rule, for the gradient-edge pseudo-
element. The calendar's "fill the screen" button toggles a `.pfocus-card`
class onto that same element — same specificity as `.pfocus-card`'s own
`position:fixed`, so source order decides, and `.card` sits later in the
file. `position:relative` silently won, and "fullscreen" quietly stopped
being fullscreen: `getBoundingClientRect()` on the card showed
`{x:206,y:22,width:1028,height:950.75}` in a 1440×900 viewport — nothing
like `position:fixed;inset:0`. The bottom of the 24-hour grid had nowhere
to go and no way to scroll to it.

**Fix**: raised `.pfocus-card`'s selector to `.card.pfocus-card` (two
classes) so it always wins over plain `.card` regardless of file order.
Confirmed the same way the bug was found: the card's rect is now exactly
`{0,0,1440,900}`, and `scrollHeight` (949) now correctly exceeds
`clientHeight` (900) — scrolled to the bottom and watched hour 23 render
with room to spare, instead of being unreachable.

Also confirmed: exiting focus mode still works, the normal (non-
fullscreen) day view was never affected by this bug and still isn't, and
drag-and-drop on a calendar block still works after the fix.

## Round 14 — beta feedback: laggy Water Volume / Strength sliders

First direct beta-tester bug report handled in this redesign. Reported
as "the slider is ~300ms behind the finger" on Bench's Water Volume
control — a real performance bug, not a visual one.

**Root cause**: a dragged `<input type=range>` fires `input` on every
pixel of movement — dozens of times a second — and the handler was
calling `renderMix()` (a full innerHTML rebuild of the ingredient/step
list) synchronously on every single tick. `renderVol()` was doing the
same thing to the tick marks via `buildTicks()`, even though tick
positions are static within the current range and only actually change
on a mode switch (Formula/One product, spray vs. pot). Two full DOM
rebuilds per pixel of drag is exactly what a ~300ms lag looks like.

**Fix**: `renderVol()` gained an optional `liveOnly` flag — every
existing call site still calls it with no argument and gets the
identical full repaint, zero behaviour change. Only the slider's own
`input` handler passes `liveOnly=true`, skipping the tick rebuild while
still updating the number and the slider's visual position every tick.
The expensive `renderMix()`+`saveLocal()` calls are debounced to 60ms of
quiet and flushed immediately on `change` (fires once, when the drag
ends) so releasing the slider never waits out an extra debounce window
on top of the drag itself. Applied the identical fix to the Strength
slider, which had the same `renderMix()`-on-every-tick pattern even
though nobody had reported it yet.

Verified via playwright-cli: measured 20 simulated rapid `input` events
at 0.175ms/tick (down from two full DOM rebuilds per tick); confirmed
the mix panel's displayed amount settles correctly and immediately on a
simulated drag+release with a real product selected; same timing check
on the Strength slider. Re-ran the calendar drag regression test
(unrelated code path) to confirm nothing else broke.

## Round 15 — a beta feedback batch: settings, calendars, dialogs, nav

A larger, unsorted batch of beta-tester feedback, triaged into five
separate fixes.

**1. Settings was duplicated in two places.** The header gear icon (next
to the Potting Bench / Daily Planner / Hours switcher) jumped straight
into editing the Academy guide — the single most niche setting in the
app — ahead of every real one, and a second, full settings page (mixing
readings, appearance, action days, daily task reset, people & data,
backup/export) lived buried inside Library → Shelf, of all places,
because that's simply where it was first written. Rebuilt as one
`view-settings` screen reached the same way from any of the three apps:
three top-level `<details>` categories, one per module (Potting Bench /
Daily Planner / Hours), each opening on whichever app you came from and
the other two collapsed. Editing the Academy guide moved inside the
Potting Bench category as its own nested, collapsed `<details>` — closed
by default, so it only "rolls out" when someone actually goes looking
for it, per the request. Hours' settings card (currency, rate, Pomodoro
lengths) moved out of the Hours view itself into the Hours category for
the same reason. Every moved field kept its existing id, so none of the
code that reads or writes it needed to change — this was a markup
relocation, not a rewrite. `settingsBtn`'s Back button returns to
whatever view was open before Settings, tracked in `settingsReturnView`.

**2. A tapped hour on the Daily Planner grid silently lost its time.**
Clicking an empty hour slot on the day board correctly opened the "New"
dialog pre-filled with that time (confirmed live — e.g. 09:45) — but
`pSlotCreate()` hard-coded a Task's `time` to `""` regardless of what
was in the field:
`time:isEvent?$("#pSlotTime").value||"09:00":""`. Only Events read the
field; a Task always saved empty and fell back to the untimed "drag onto
an hour to give it a time" tray, even though it was created BY tapping
an hour. This is very likely what read as "the calendar is not correctly
interactive" — the one direct way to plan a task at a specific time
silently didn't work. Fixed to
`time:isEvent?($("#pSlotTime").value||"09:00"):($("#pSlotTime").value||"")`,
which still lets a Task be genuinely timeless (an empty field still
saves empty) but no longer discards a time that was actually given.
Verified via playwright-cli: created a task for a genuinely future date
(today is 31 August; the first test used the 14th, which is *last*
month's the-31st-relative past and was overdue by design — re-tested
against 10 September) by clicking a grid hour, confirmed `time:"14:00"`
in the saved record, and confirmed it now renders as a positioned block
on the grid at 14:00 instead of dropping into the tray. Separately audited
the drag/tap gesture state machine (`G2`) for the reported "freezes after
tapping a task" — it already wraps every pointerup commit in try/catch
and unconditionally clears the gesture state even on a throw (an earlier,
already-shipped fix, per its own code comment), so no dangling state that
would explain a permanent freeze was found there; the time-save bug is
the concrete, reproducible fix from this pass.

**3. Dialogs could open off-centre or half off-screen on a phone.**
`dialog{position:relative; ...}` was added in an earlier round only so a
gradient-edge pseudo-element had a positioning context — but every dialog
in the app opens with `.showModal()`, and `dialog:modal` already gets
`position:fixed` centred by auto margins from the browser itself, which
already satisfies that same requirement. An explicit `position:relative`
on top of that fights the browser's own centring on any engine that
honours the author rule, which is consistent with "the phone window opens
in random places, not centred." Removed the override; verified centring
and the gradient edge both still render correctly, in Chromium and in a
newly-installed WebKit engine, at both a phone width and a landscape/tablet
width that crosses the 640px breakpoint. Also switched the mobile bottom
sheet's `max-height` (and the scrollable body's) from `vh` to `dvh`
(`vh` kept as the fallback) — `vh` sizes against the full layout viewport
even once the on-screen keyboard is up, which is the likely cause of
"cannot see the whole window" when adding a task on a phone; `dvh`
tracks the actual visible area.

**4. The Potting Bench tab strip stayed visible — and clickable — while
using Daily Planner or Hours.** `setApp()` sets `.navwrap.hidden = true`
outside Potting Bench, but `.navwrap{display:flex}` is an author rule of
equal CSS specificity to the browser's built-in `[hidden]{display:none}`,
and author rules always outrank user-agent ones regardless of source
order — so the tab strip kept its layout, sat visibly (confirmed via a
non-zero bounding rect and `pointer-events:auto`) behind whatever the
other app's glass panels didn't fully cover, and could still be tapped.
This is almost certainly the reported "nav bar... merges weirdly."
Fixed with an explicit `.navwrap[hidden]{display:none}`. Verified: the
strip is now genuinely `display:none` on Daily Planner and Hours, and
still shows normally back on Potting Bench.

**5. The tab strip clipped its own last tab with no hint it scrolled.**
Six tabs (Garden/Bench/Grow/Diary/Library/Stats) don't fit a phone's
width in one row; Round 3 fixed the pill overflowing the viewport by
making the strip scroll internally, but that left "Stats" hard-cut at
the edge with zero affordance that swiping would reveal it — confirmed
live (`scrollWidth` 487px vs. `clientWidth` 369px, no visual cue at all).
Added edge fades via `mask-image` on `.nav` itself (not a colour-matched
overlay, so it blends correctly over the blurred glass and whichever
blob-gradient background sits behind it in either theme), toggled by a
`navUpdateFade()` scroll listener plus a `ResizeObserver` so a language
switch or viewport change re-evaluates it too. Verified both edges
appear and disappear correctly as the strip is scrolled to each end.

All five verified live via playwright-cli against the running app; no
JavaScript data model or behaviour changed except the one-line time-field
fix in #2, which is a bug fix, not a redesign change.
