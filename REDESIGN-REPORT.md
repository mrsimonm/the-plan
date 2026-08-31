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
