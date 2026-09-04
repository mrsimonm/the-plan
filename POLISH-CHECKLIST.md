# Polish pass — definition of done

Branch: `polish-pass`. The loop works down this file and stops when every box
is ticked. Anything found that is not on the list gets added to it rather than
fixed silently, so the scope stays visible.

## Layout targets (three, not four)

Laptop portrait is deliberately out of scope — it must simply work in a
resizable landscape window.

- **P** phone portrait — 390x844
- **L** phone landscape — 844x390
- **W** laptop landscape — tested at 1024, 1280, 1440, 1920 wide

## 1 · Every view, in every target

For each: nothing overlaps, nothing is clipped, no sideways page scroll, no
text cut mid-word, every control reachable and >=44px on touch.

| View | P | L | W |
|---|---|---|---|
| garden | ☐ | ☐ | ☐ |
| mix | ☐ | ☐ | ☐ |
| cuttings | ☐ | ☐ | ☐ |
| batch | ☐ | ☐ | ☐ |
| plan | ☐ | ☐ | ☐ |
| sched | ☐ | ☐ | ☐ |
| library | ☐ | ☐ | ☐ |
| plants | ☐ | ☐ | ☐ |
| plant | ☐ | ☐ | ☐ |
| product | ☐ | ☐ | ☐ |
| formula | ☐ | ☐ | ☐ |
| shelf | ☐ | ☐ | ☐ |
| log | ☐ | ☐ | ☐ |
| academy | ☐ | ☐ | ☐ |
| acadedit | ☐ | ☐ | ☐ |
| stats | ☐ | ☐ | ☐ |
| settings | ☐ | ☐ | ☐ |
| planner | ☐ | ☐ | ☐ |
| hours | ☐ | ☐ | ☐ |
| hproject | ☐ | ☐ | ☐ |
| teachbench | ☐ | ☐ | ☐ |
| teachbench-student | ☐ | ☐ | ☐ |
| notes | ☐ | ☐ | ☐ |
| note | ☐ | ☐ | ☐ |

## 2 · Bug classes to sweep

- ☐ `[hidden]` vs `display:` — a class that sets display beats the user agent's
  `[hidden]{display:none}`. Four known so far (.navwrap, .field, .dlg-foot
  guarded; .psel-bar found and fixed). Find the rest.
- ☐ Console clean on boot and on every view, in all three targets
- ☐ Anything that renders late, flashes, or shows stale content after a switch
- ☐ Strings with no Czech, and attributes not passed through `t()`
- ☐ Dialogs: reachable, dismissible, not taller than a phone screen

## 3 · Motion

- ☐ Press feedback on every button and chip — one shared rule, not per-component
- ☐ View changes: one considered transition, not several competing ones
- ☐ Lists: items settle in rather than appearing hard, where it costs nothing
- ☐ Every one of the above off under `prefers-reduced-motion`
- ☐ Nothing animates a property that forces layout; no stutter on a phone

## 4 · Performance

- ☐ `backdrop-filter` audit — it is the most expensive thing in the file and
  the prime suspect for jerk
- ☐ Planner render cost (the board redraws in full on every change)
- ☐ Long lists: garden, plants, log, notes
- ☐ Boot: time to first meaningful paint

## Rules for the loop

1. Work on `polish-pass`. Never commit to `main`.
2. One commit per finished item, message says what and why.
3. Verify in the browser at the actual size before ticking. No box is ticked
   on the strength of reading the code.
4. Anything ambiguous or that changes what the app DOES rather than how it
   looks: leave it, write it under "Ask Simon" below.
5. Stop when every box is ticked, or when "Ask Simon" has enough in it that
   continuing without answers would be guessing.

## Ask Simon

_(empty)_
