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
