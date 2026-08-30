# Overnight notes — 30 Aug 2026

Branch: **`overnight-polish`**, branched from `main` at `956eff5`. `main` untouched,
nothing force-pushed, no branches deleted.

The previous overnight run's notes are preserved in git history (`git show
956eff5:OVERNIGHT_NOTES.md`).

---

## Part 1 — Bug re-checks: all three were already fixed

You asked me to verify before fixing. I did, with real gestures in the browser,
and **none of the three still reproduces.** No code was changed for Part 1.

| # | Report | Verified result |
|---|---|---|
| 1 | Plachta has no up/down drag at all | **Works.** Body-drag 10:00→13:00 with duration kept; S-handle 2h→4h; N-handle to 11:00/6h |
| 2 | Up/down resize flaky on his device | **No bug found.** Resize lands on every drag from 5px upward |
| 3 | Empty-slot click-to-add missing in some views | **Works in all four.** Day, Week, Month and Plachta each open the dialog on the right day with a prefilled time |

On #2 specifically, I swept drag distances rather than trying it a few times:

```
3px → no change     (below the 4px arm threshold — correct, stops a click resizing)
4px → no change     (at the threshold — correct)
5,6,8,9px → +0.25h
13,17px   → +0.5h
26px      → +0.75h
34px      → +1h
```

Monotonic, no dead zone. An earlier code review had suspected a 4–8px band where
a drag registers but changes nothing; that does **not** reproduce.

### Why his device behaved differently — worth your attention

These reports almost certainly predate the Wave 1 fixes, and the reason they
survived on *his* laptop specifically is the service-worker bug: the app was
cache-first on the shell, so a device that had loaded the site once kept that
build forever. Twenty-five builds shipped under one cache name. **Before
concluding anything is broken on his machine again, have him tap the version
badge (bottom-right).** If it does not match the deployed build, nothing else
he reports can be trusted.

---

## Part 2 — Mobile performance: what was actually slow

Profiled before changing anything, as asked. Two real causes, both fixed.

### 1. Every edit rewrote the entire store, photos included

`touch()` ran a synchronous `JSON.stringify(S)` plus `localStorage.setItem` on
**every mutation**. `S` includes `S.photos` — base64 images. Dragging a calendar
block never touches a photo, but rewrote all of them anyway.

Measured on this desktop, which is several times faster than a phone:

| Store | `touch()` |
|---|---|
| 10 KB, no photos | 0.1 ms |
| 1.9 MB, 12 photos | **4.5 ms** (45×) |

**Fix:** the write is coalesced onto the next timer tick. Callers are unchanged
and the bytes written are identical — one write happens instead of several.
Measured after: 20 mutations on a 1.9 MB store produce **0 writes during the
burst and exactly 1 after**.

`setTimeout`, not `requestAnimationFrame` — rAF is paused outright in a hidden
tab, so a background mutation would sit unwritten until you looked at the tab
again. `visibilitychange`, `pagehide` and `beforeunload` all flush
synchronously, so a pending write can never outlive the session. Verified the
case that matters: a drag committed and the page reloaded **in the same tick**
still persisted.

### 2. Work sessions were rescanned for every column

`pItemsFor` walked the whole session list for each day it was asked about,
building a `Date` and formatting it every time. A Month board asks 31 times, so a
year of tracked work meant tens of thousands of date conversions to find a
handful of matches.

**Fix:** sessions are bucketed by day once per render pass, cleared exactly where
`pCareCache` already is.

| 900 sessions, 31 days | |
|---|---|
| rescan per day | 8.4 ms |
| indexed | **1.7 ms** (~5×) |
| index build | 0.2 ms |

### Honest caveat

Both wins are real and measured, but they were measured on a desktop with
*synthetic* data. I could not reproduce your dad's phone. The photo finding is
the one I would bet on, because it scales with exactly the thing a plant app
accumulates — and it is invisible until the library gets big.

**Not done, deliberately:** photos still live in the same `localStorage` key as
everything else, so a very large library keeps the whole store heavy. Splitting
photos into their own key (or IndexedDB) is the real fix, and it is a storage
change I was not willing to make unattended overnight.

---

## Part 3 — Visual redesign: the plan

Written before implementing, as you asked.

### Direction

The current look reads generic because it is **tinted green throughout** — the
neutrals themselves carry a hue, so every surface is faintly green and the
saturated accent (`#22C55E`) sits on top of it. That combination is what makes
it feel "like a Google".

The change: **neutral, untinted greys as the system, with one restrained accent
used sparingly.** Nothing's discipline is that the interface is monochrome and
the accent is an event, not a background condition. Dark mode becomes a true
near-black rather than a dark green.

### Palette

**Light**

| Token | Value | Note |
|---|---|---|
| `--bg` | `#F4F4F2` | warm neutral paper, no hue |
| `--surface` | `#FFFFFF` | |
| `--surface-2` | `#FAFAF9` | |
| `--sunk` | `#ECECEA` | |
| `--line` | `#E2E2DF` | |
| `--line-strong` | `#C9C9C4` | |
| `--ink` | `#16181A` | near-black, faintly cool |
| `--ink-2` | `#5C6166` | |
| `--ink-3` | `#8E9499` | |
| `--accent` | `#3F6B54` | muted forest — the subject acknowledged, not shouted |
| `--accent-soft` | `#E8EEEA` | |

**Dark**

| Token | Value | Note |
|---|---|---|
| `--bg` | `#0B0C0C` | true near-black, untinted |
| `--surface` | `#141616` | |
| `--surface-2` | `#1A1D1D` | |
| `--line` | `#262A29` | |
| `--line-strong` | `#3A403E` | |
| `--ink` | `#ECEEED` | |
| `--ink-2` | `#9AA1A0` | |
| `--accent` | `#7FA890` | muted sage — calm, deliberately not neon |
| `--accent-soft` | `#17241D` | |

Dark mode is designed as its own thing rather than an inversion: the accent is
*lighter and less saturated* than its light-mode counterpart, because a
saturated colour on near-black glares.

### Typography

- **Display / headings: Space Grotesk** replaces Bricolage Grotesque. Bricolage
  is a lively, organic variable face; Space Grotesk is drawn from a
  proto-geometric skeleton with squared terminals — engineered rather than
  friendly, which is the register asked for.
- **Body: Manrope**, kept. Clean, geometric, and not the default-system look
  that reads as generic.
- **Numerals: JetBrains Mono**, kept and already used in 70 places. Tabular,
  technical, and central to the engineered feel — the strongest existing asset.

### Shape and noise

- Radii tighten: `--r` 18→12, `--r-sm` 12→8, `--r-xs` 9→5. Rounded, but
  precise rather than soft.
- Shadows flatten hard. The current two-layer 48px blooms are the main source of
  visual noise; separation comes from 1px hairlines instead.
- Decorative `--bloom-*` gradients dropped to near-nothing.

### Scope

Applied at the token layer, so it lands across Garden, Bench, Grow, Diary,
Library, Stats, Hours and the Daily Planner at once rather than section by
section.

### What was actually built — and one thing the plan missed

Implemented as its own pass, after the bug and performance work, in `fc541c1`.
42 token replacements across the three theme blocks, plus 46 typography
declarations.

The plan missed something I found while verifying: **the Planner and Hours each
override `--accent` with their own identity colour**, and both were loud — a
saturated blue `#1D4ED8` and purple `#6D28D9`. Changing only the base palette
would have left two of the most-used sections still looking like the old app.
They are now muted into the same system:

| Section | Was | Now (light / dark) |
|---|---|---|
| Garden and the rest | `#15803D` green | `#3F6B54` / `#7FA890` |
| Daily Planner | `#1D4ED8` blue | `#40566E` / `#8FA6BF` |
| Hours | `#6D28D9` purple | `#5B5470` / `#8E86A6` |

Section identity is kept, because it is a good idea — it just needed to stop
shouting.

**Contrast, measured across both themes and all three identities:** body text
17.8:1 light and 15.6:1 dark, secondary text 6.3 and 6.9, lowest accent 5.29:1.
Every value clears the 4.5 body threshold, not merely the 3.0 for UI.

**Verified it did not break anything.** All eight views render with no console
errors, and after the CSS changed I re-ran the gestures rather than assuming
radii and shadows were cosmetic: body-drag moved 10:00→13:00, S-handle resized
2h→4h, and a tap opened the editor on the right record, with `pBoardBusy` never
latching.

---

## What needs your attention

1. **Wave 2 is on `main` and on GitHub, untested by you.** You asked me to merge
   it anyway and I did (`72f47b2`). Tonight's branch sits on top of it. If Wave 2
   turns out to have problems, `main`'s pre-Wave-2 tip is `07eb0de`.
2. **The photo storage question** above — the remaining performance ceiling.
3. **GitHub Pages is not enabled yet.** It needs a click in Settings → Pages, or
   `gh auth login` so I can do it.

## Decisions made on your behalf

- **Part 1: changed nothing.** All three reports verified as already fixed. Given
  your instruction to verify first and only fix what is broken, writing code
  would have meant inventing a problem.
- **Coalesced writes rather than splitting photos out.** The bigger win is moving
  photos to their own key, but that is a storage-layout change, and doing it
  unattended against a store that holds your real data is not a risk worth
  taking overnight. The safe fix captures most of the benefit.
- **Kept Manrope and JetBrains Mono**, replaced only the display face. A full
  three-family swap would have been a larger, more disruptive change for less
  gain — the mono is already doing the engineered work.
- **Muted the Planner and Hours identity accents rather than removing them.**
  Deleting them would have been simpler and more uniform, but the sections
  reading as distinct is genuinely useful; the problem was saturation, not the
  idea.

## Commits, in order

```
2f09d00  Notes: Part 1 verification, Part 2 measurements, Part 3 design plan
dfda354  Perf: coalesce the store write instead of paying it per mutation
c1e4c28  Perf: bucket tracked-work sessions by day instead of rescanning
fc541c1  Design: neutral palette, engineered type, flatter surfaces
```

Part 1 produced no commit, because nothing was broken.

## How to check my work quickly

1. Tap the version badge — everything below assumes you are on this build.
2. **Look**, in both light and dark. Dark mode is the bigger change; it should
   feel like a considered near-black, not a dark green.
3. Planner and Hours should still feel like their own places, in slate and plum
   rather than blue and purple.
4. Drag a block up and down, resize it, and tap it. Those three are what I
   re-checked after the CSS changed.
5. If the phone still feels slow with a big photo library, that is the storage
   split I deliberately did not do — see Part 2.

## Testing honesty

Everything above was exercised in a real browser, not read. Two caveats worth
stating plainly:

- The performance work was measured with **synthetic** data on a desktop. The
  mechanisms are real and the numbers are real, but I could not reproduce your
  dad's phone, so I cannot promise the felt improvement matches the measured
  one.
- I drove gestures with dispatched pointer events rather than physical input.
  That exercises the same handlers a mouse does, and it caught real bugs during
  Waves 1 and 2 — but it is not identical to a finger on glass, and the touch
  path is the one I have tested least.

Test fixtures created during the night were cleaned out of `localStorage`
afterwards; the store on `localhost:8934` is back to 3 KB. Your real data lives
on a different origin and was never touched.
