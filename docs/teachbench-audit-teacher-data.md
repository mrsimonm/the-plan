# TeachBench — teacher-side data-integrity audit

- **Auditor:** tb-teacher-data-2 (autonomous hive worker, read-only, no code touched).
- **Scope:** TeachBench data layer only (`TB.*` in index.html, localStorage key `teachbench.data`, schema version 13). Not a UI/visual audit — see `docs/teachbench-audit.md` for that.
- **Method:** repo served over `127.0.0.1`, fresh in-memory playwright-cli profile, 360×732. Data-layer cases exercised via `page.evaluate()` against `TB.*` and `localStorage` directly (cheap path), plus source reading of the normalise/migrate/backup functions. Throwaway data only; no Firebase writes; index.html untouched.
- **Severity:** BLOCKER / SHOULD-FIX / NICE.
- **HEAD:** working tree as served (uncommitted changes present — `git status` shows `M index.html` at session start).

---

## Summary table

| # | Case | Result | Severity |
|---|------|--------|----------|
| 1 | Can-do questionnaire end-to-end (incl. C2) | PASS | — |
| 2 | Backup export → wipe → restore round-trip | PASS | — |
| 3 | Import of older-schema / corrupt backup | (pending) | |
| 4 | Create→edit→delete persistence (students/lessons/attendance/payments/flashcards) | (pending) | |
| 5 | Two tabs open at once | (pending) | |
| 6 | localStorage near-full behaviour | (pending) | |

---

## Case 1 — Can-do questionnaire end-to-end (incl. C2)

**Result: PASS.** The C2 gap flagged in the earlier `docs/teachbench-audit.md` (auditor "Dwight", HEAD 4990e63) is **fixed in the current working tree**: `TB.CANDO` now includes 6 `c2-*` statements (index.html ~line 7471-7476), and `tbRenderCanDo()`'s level `order` array now ends `[...,"c1","c2"]` (~line 30771), so `order.indexOf("c2")` is a real index rather than -1.

- **Repro (via `page.evaluate` against `TB.*` + a real page reload, not just in-memory):**
  1. Created students at level `c2`, `c1p`, and `null` (no level set).
  2. Ticked can-do items for the C2 student (`c2-03`, `c1-02`) via `TB.saveData`.
  3. Reloaded the page (`playwright-cli reload`), re-read via `TB.loadData()`.
- **Expected vs actual:**
  - C2 student's shown level window (mirroring the render function's own `order`/`base`/`at`/`slice` logic): `[c1, c2]` — one level below plus itself, no level above since C2 is the ceiling. Actual: matches.
  - C1+ student's window: `[b2, c1, c2]` (`c1p` normalises to base `c1`, shows one below/at/above). Actual: matches.
  - No-level student defaults to the `a1` window (`[a1, a2]`), matching the documented fallback for an unrecognised/absent level. Actual: matches.
  - Ticks and per-level scores (`done/total`) survived a full page reload unchanged: C2 student showed `c1: 1/4`, `c2: 1/6`, matching what was ticked. Data is stored as `{studentId, itemId, doneOn}` in `data.canDo`, `doneOn` recorded as a plain date.
- **Severity:** — (no defect; confirms the prior BLOCKER-adjacent SHOULD-FIX from the other audit doc is resolved as of this HEAD).
- **Code location:** `TB.CANDO` (~7437), `tbRenderCanDo()` (~30759), `tbToggleCanDo()` (~30795).

---

## Case 2 — Backup export → wipe localStorage → restore round-trip

**Result: PASS.** Byte-for-byte round-trip with zero lost/renamed/reordered fields.

- **Repro:**
  1. Built a dataset covering every list: 3 students (levels `c2`, `c1p`, no level), 1 lesson (`attendance:'attended'`), 1 payment, 1 vocab list, 1 word, 2 can-do ticks.
  2. `before = TB.loadData()`; `backup = TB.buildBackup(before, nowIso)`; kept the exact JSON string `TB` would write to the downloaded file (this is what `tbExportBackup()` does, minus the `Blob`/`<a download>` step, which is pure DOM plumbing around the same call).
  3. `localStorage.clear()` — confirmed `TB.loadData()` back to a fully empty shape (`students.length === 0`) and the storage key gone.
  4. `parsed = TB.parseBackup(backupRaw)` → `TB.saveData(parsed.data)` (this is exactly what `tbConfirmImport()` does).
  5. Diffed every one of the 9 top-level lists (`students, materials, studentMaterials, vocabLists, words, studentWords, lessons, payments, canDo`) between the pre-wipe snapshot and the post-restore data, each sorted by `id` before stringifying (order-independence).
  6. Reloaded the page for good measure — re-read via `TB.loadData()` from actual localStorage, not the in-memory object — counts still matched.
- **Expected vs actual:** expected zero diffs. Actual: `diffs` object empty — every field (including ones with no explicit assertion above, e.g. `state`, `cancelledAt`, `caught`, `color`, `active`, `rate`) survived identically, since `normaliseData()` is applied on both the write into storage and the write coming out of a restored backup, so the two passes are idempotent on already-clean data.
- **Severity:** — (no defect).
- **Code location:** `TB.buildBackup`/`TB.parseBackup`/`TB.saveData` (~7231-7306), UI glue `tbExportBackup()`/`tbConfirmImport()` (~30043, ~30144).

---
