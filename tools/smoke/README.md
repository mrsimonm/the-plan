# Smoke gate (beta checklist gate 10 — refs R4/R7)

One command, from anywhere in the repo:

```bash
tools/smoke/smoke.sh
```

Exit code 0 = PASS, non-zero = FAIL. Run it before every push to `main` while
the beta release train is live.

## What it does

1. **Syntax gate** — `extract-inline-js.mjs` pulls every inline `<script>` out
   of `index.html` (the whole app lives in one) and runs `node --check` on it.
   Catches the "call shipped without its definition" class of breakage before
   a browser ever loads.
2. **Browser gate** — serves the repo on `127.0.0.1:8137` (`SMOKE_PORT` to
   override), boots the app with the repo's existing `playwright-cli` tooling
   in a **fresh in-memory profile** at a **360×732** viewport (the beta phone
   size), then opens every app/view by making the same calls the real tab and
   app-menu buttons make:

   Potting Bench tabs Garden/Bench/Grow/Diary/Library/Stats · Library
   sub-views plants/academy/shelf/log · Planner · Hours · TeachBench ·
   TeachBench student portal · Notes · Settings.

   It **fails** on any console error, uncaught exception, unhandled promise
   rejection, or failed same-origin request, and verifies each view actually
   became visible.

## Output

A per-view table, then the verdict:

```
VIEW                 SHOWN  NEW-ERRORS
boot                 yes    0
bench:garden         yes    0
…
network(same-origin) -      0
RESULT: PASS
```

On FAIL it also prints the captured console/error messages and any failed
same-origin requests, and exits 1.

## Requirements (all already on this machine / in this repo)

- `node` (used for extraction + `--check`)
- `python3` (localhost static server)
- `playwright-cli` (already used throughout this repo — snapshots and logs
  land in `.playwright-cli/` as usual; the gate uses its own named session
  `smoke`, so it won't disturb an interactive session)

No packages are installed; nothing in the app is modified.
