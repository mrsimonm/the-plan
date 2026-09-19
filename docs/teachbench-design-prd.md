# Teachbench — Design Quality PRD

Written 14 Sep 2026, before any code. Scope: the Teachbench teacher side
(`#view-teachbench`, the `TB` module) and the student portal
(`#view-teachbench-student`, `TBS_UI`). Potting Bench and the planners are out
of scope for this document.

## 1. Goal

Make Teachbench look and feel like a product a real design team shipped, not a
generated one. Judged by three people: Margo (teacher, uses it daily on a
laptop and a phone), her students (children and teenagers, phone only), and
Simon (owner). Margo's own brief in `docs/teachbench-student-spec.md` asks for
"visually clean, calm, and a bit luxurious" and "quick to scan, visual, and
well structured". That is the target.

## 2. What is wrong today — evidence, not opinion

Measured on 14 Sep against build v1.0.112 at 1024×768 and 375×812.

1. **Every block is the same card.** The student page stacks seven identical
   bordered, rounded, equally-tinted cards (header, At a glance, Notes, Tasks,
   Student portal, Lessons and payment, Can do). Nothing on the page is more
   important than anything else. Forms sit inside cards inside cards (Tasks,
   Lessons). The app stylesheet has 72 occurrences of `border:1px solid
   var(--line)` — the "grey 1px border on every card" tell.
2. **One purple does every job.** Primary buttons, the selected sidebar item,
   focus rings, segmented tabs, chips and the timer are all the same lavender
   on near-black. Three filled purple buttons are visible in one scroll of the
   student page (Add tasks, Connect to the portal, Record payment), so none of
   them reads as *the* action. Dark-by-default purple is the single most
   recognised AI-generated look.
3. **Typography has no system.** The stylesheet uses 31 distinct `font-size`
   values (8 px to 38 px, including 9.5, 10.5, 11.5, 12.5, 13.5, 14.5).
   Headings are corrected with inline styles (`<h2 style="font-size:17px">`,
   `font-size:15px`). Tracked ALL-CAPS labels are used as decoration on data
   ("ATTENDED", "NO-SHOWS", "CONTENT — ONE WORD OR PHRASE PER LINE").
4. **Forms come before content.** Students opens with an add-student form
   above the roster. Tasks opens with a six-field form above an empty library.
   Words opens with three stacked forms (add word, new list, paste a list)
   before a single word is shown. The rarest action sits above the commonest.
5. **Two navigation paradigms on one screen.** A hamburger-style scope menu
   ("Students ▾") next to filled segmented tabs (Library / By student; Bank /
   By student / Review), inside a 15-item app sidebar.
6. **Empty states are a grey sentence.** "No tasks yet — add one above.",
   "Nothing scheduled" seven times down the Week view.
7. **Emoji as icons** (📷 Photo, 🔊 Hear it, 🐢 Slower, 🎤 Say it) beside the
   app's own line-icon set.
8. **Phone defects.** In Can do, the checkbox and its sentence overflow the
   right edge of the screen at 375 px. The version pill sits over controls in
   the bottom corner. (The ADHD Planner has the same pill-over-Done problem;
   it is a shell issue, not a Teachbench one.)
9. **Seven skins, no identity.** `data-palette` offers amethyst, citrine,
   emerald, frosted, monolith, obsidian and sapphire. Variants of one generic
   look are themselves a tell; Simon has already said token-only redesigns
   read as "all the same".

## 3. Principles adopted, and where they come from

- **Clarity, deference, depth, consistency** — Apple HIG's four. Content first,
  chrome recedes, layers show hierarchy, familiar patterns.
- **Hierarchy through space before lines.** Polaris: spacing achieves grouping
  and hierarchy; larger, heavier, contrasting elements attract attention.
  Polaris also admits Card is its most-overridden component. Default to
  borderless groups; a card is a deliberate choice, never the default.
- **60-30-10 colour.** Neutral surfaces carry ~60 %, a secondary tone ~30 %,
  the accent ≤10 % and it means one thing: "act here". Semantic colours
  (success / warning / danger / info) stay separate from the brand hue.
- **One type family, one scale, three weights.** A ratio-based scale
  (Material's five roles; Apple's text styles); two or three styles per
  screen; weight and size do the work, colour only assists.
- **8-pt spacing.** Carbon, Polaris, Primer, Fluent all use it: a fixed
  vocabulary of 4/8/12/16/24/32/48 and nothing else.
- **One primary action per view.** Carbon and Polaris both cap it; Polaris
  says no more than two filled buttons in a card. Primary = filled,
  secondary = outlined/tonal, tertiary = text.
- **Laws of UX.** Hick (fewer choices per screen), Fitts (44 px targets),
  Miller (chunk into ≤7), Jakob (behave like apps people already know),
  aesthetic-usability (polish buys forgiveness for the rest).
- **Empty states** (Carbon): a short headline, one line, one action; tertiary
  buttons when several empty states can show at once.
- **Microcopy.** Verb first, two to four words, name the outcome ("Send
  homework", not "Submit").
- **Anti-generic rules** from the 2026 "AI design slop" literature: lock tokens
  in a design file, cap the palette, pick a real type pairing, no gradient
  hero, no glass glow, no bounce easing, no uniform radius, no nested cards,
  no unrequested dark mode, and keep a banned list to review against.

## 4. Requirements

MUST = ships in this project. SHOULD = ships unless it costs disproportionate
effort. Each has an ID for the acceptance checklist.

### A. Direction (the decision everything else hangs on)

- **A1 MUST** One aesthetic direction, chosen before code, from two or three
  structurally different mockups drawn as pictures. Proposed default:
  *calm editorial notebook* — light, warm off-white paper, ink-dark text,
  one restrained accent, generous whitespace, content typeset like a good
  textbook. This matches Margo's "calm, a bit luxurious" and is the opposite
  of the current dark neon.
- **A2 MUST** Teachbench gets its own visual identity, scoped to its two
  sections, independent of the seven app palettes. The app shell (sidebar,
  top bar) stays, but the content area belongs to Teachbench.
- **A3 SHOULD** Light theme by default for both halves; dark remains available
  and is designed, not inverted.

### B. Tokens — the design file

- **B1 MUST** Type scale of six sizes on a 1.2 ratio from a 15 px body:
  12 / 13 / 15 / 18 / 22 / 28. Roles: Label 12, Secondary 13, Body 15,
  Heading 18, Title 22, Display 28 (student portal only). No other
  `font-size` inside Teachbench CSS; no inline `style="font-size"`.
- **B2 MUST** Three weights: 400, 500, 600. Bold (700) only for the Display
  role.
- **B3 SHOULD** A second typeface for headings and the student flashcard
  face, chosen for warmth and Czech diacritics (candidates: Fraunces,
  Newsreader, Source Serif 4, loaded from Google Fonts with the system stack
  as fallback). Body stays on the system stack. Decision for Simon (§8).
- **B4 MUST** Spacing scale 4 / 8 / 12 / 16 / 24 / 32 / 48. No other margins
  or gaps.
- **B5 MUST** Three radii only: 6 px controls, 12 px containers, pill for
  chips and avatars.
- **B6 MUST** Colour roles: paper (page), surface (raised group), ink, ink-2
  (secondary), ink-3 (labels), line (dividers, used sparingly), accent,
  accent-soft, and four semantics — success, warning, danger, info. The eight
  student colours remain the only other hues.
- **B7 MUST** Elevation: groups are separated by spacing and a surface tone,
  not by borders. Exactly one shadow token, used only for things that float
  (menus, dialogs, the sticky action bar).
- **B8 MUST** Motion: 150–200 ms ease-out for state changes; no bounce,
  elastic or spring easing anywhere; `prefers-reduced-motion` respected (the
  app already has the switch).
- **B9 MUST** Contrast: 4.5:1 for body text, 3:1 for large text and control
  outlines, in both themes, checked with a tool rather than by eye.

### C. Structure — teacher side

This is the redesign. A palette swap alone does not satisfy this section.

- **C1 MUST Students.** The roster is the first thing on the page: a plain
  list (colour dot, name, level, next lesson, one status word), no card per
  row. One primary button, "Add student", opens an inline row. Backup moves
  to an overflow menu (⋯) in the header; it is important, not frequent.
- **C2 MUST Student page.** A header (name, colour, level, next lesson, one
  primary action) and a compact summary strip, then sections as headed groups
  separated by spacing: Overview, Words, Tasks, Lessons & payment, Notes,
  Can do. On desktop the sections may be side-by-side in two columns; on a
  phone they stack. Zero cards-in-cards.
- **C3 MUST Tasks and Words.** Library first. "Add" is one primary button that
  reveals the form; "Paste a list" and "New list" are secondary actions
  inside that form, not separate stacked forms.
- **C4 MUST Week.** Today is the only highlighted day. Empty days are one
  quiet line; the seven-times-repeated "Nothing scheduled" goes.
- **C5 MUST Navigation.** One paradigm. Sections (Students / Week / Tasks /
  Words / Messages) become underlined text tabs on desktop and the existing
  menu button on phones; sub-sections (Library / By student, Bank / By
  student / Review) become the same tab style one level down, never filled
  segments.
- **C6 MUST Search** stays beside the section tabs and searches the section
  you are in, as now.
- **C7 MUST** Every Teachbench dialog fits a 375×812 screen with its footer
  visible; already true, must stay true.

### D. Structure — student portal

Highest visibility, most contained (it hides the app shell entirely), so it
ships first.

- **D1 MUST Today.** Greeting, one large number (cards due), one primary
  button "Start reviewing". Streak, points and best are one line of text
  under it, not three tiles. Recap and "words that keep beating you" are
  headed groups further down.
- **D2 MUST Review.** The card fills the screen; the word is set in the
  Display role, centred, with the prompt above it in Secondary. Reveal is the
  only button until the answer shows. Grading is one row: Again (quiet
  danger), Hard (secondary), Good (primary), Easy (secondary). No emoji; the
  speak/slow/say controls use the app's SVG icons.
- **D3 MUST Words, Calendar, Homework, Chat** follow the same rules: list
  first, one primary, headed groups.
- **D4 MUST Access-code screen.** One field, one button, the code typeset
  large and monospaced. It is the first thing a child sees.
- **D5 SHOULD** Per-student accent colour (from the eight) tints the primary
  button and the Today number, which is the "small personalised touch" Margo
  asked for.

### E. Components

- **E1 MUST** One primary (filled) button per view. Secondary = tonal or
  outlined. Tertiary = text. Destructive = quiet outline red, filled only in
  a confirmation dialog.
- **E2 MUST** Labels are verb-first and 2–4 words. "Record payment", "Send
  homework", "Copy statement". No "OK", no "Submit".
- **E3 MUST** Eyebrow (small caps) labels only as group headings in dense
  desktop layouts; never on data values (ATTENDED → Attended).
- **E4 MUST** Icons come from the app's existing SVG set; emoji are removed
  from every control.
- **E5 MUST** Empty states: headline (Body, 500), one sentence (Secondary),
  one tertiary action. Example: "No students yet" / "Add the first one and
  their lessons, words and homework live here." / "Add student".
- **E6 MUST** Tap targets ≥ 44 × 44 px on phones; desktop density may be
  tighter.

### F. Phone

- **F1 MUST** No horizontal page overflow at 375 px on any Teachbench screen
  (fixes the Can do defect).
- **F2 MUST** The version pill never overlaps a control on any view; it
  hides while a sticky action bar is on screen.
- **F3 MUST** The top bar names the section you are in.

### G. Language and consistency

- **G1 MUST** Every new or changed string has a Czech entry; user-entered
  data (names, words, card faces) is never translated.
- **G2 MUST** The same treatment across teacher side and student portal — one
  button set, one type scale, one spacing scale. No re-defaulting between
  screens.
- **G3 MUST** A banned list, checked before each ship: purple-to-blue
  gradients, glass blur with glow, bounce easing, nested cards, three-or-six
  identical cards in a row, uniform radius on everything, ALL-CAPS data,
  emoji icons, inline font sizes, a second accent.

## 5. Non-goals

- No new framework, build step, or dependency beyond an optional web font.
- No change to the `TB` or `TBS` data models, Firestore rules, or sync.
- No change to Potting Bench, the Daily Planner or the ADHD Planner (they get
  their own PRD if this one works).
- No new palettes. The seven existing ones are untouched for the rest of the
  app and simply do not apply inside Teachbench.
- No redesign of the app shell (sidebar, top bar) beyond F2 and F3.

## 6. Acceptance criteria — measured, not eyeballed

1. `grep` of Teachbench CSS finds ≤ 6 `font-size` values and 0 inline
   `style="font-size"`.
2. ≤ 1 filled primary button per screen, counted on every screen and
   sub-tab.
3. 0 elements matching card-inside-card in `#view-teachbench` and
   `#view-teachbench-student`.
4. 0 horizontal overflow at 375 × 812, 390 × 844, 844 × 390 and 1440 × 900
   on all screens, including every dialog.
5. All text passes WCAG AA contrast in both themes (tool-checked).
6. Every tap target ≥ 44 px on the phone layout.
7. Every string resolves in EN and CS; 0 orphaned CS keys.
8. Smoke gate (`qa-home.yml`, 360 × 732 boot of every view) passes; 0
   console errors.
9. Margo says it is calmer and faster to scan than before. Simon signs off
   on the mockup before code, and on each phase before it is pushed.

## 7. Delivery plan

Each phase is its own build (version bump) and a hand-test at
`http://localhost:8955/index.html` before it is pushed to `main`, which is
the deploy.

- **Phase 0 — Direction (no code).** Two or three mockups of the student
  Today + Review screens and the teacher Students + Student page, as pictures
  on a canvas, structurally different from each other. Simon picks one.
- **Phase 1 — Tokens + student portal.** Sections B, D, E, F. The portal is
  self-contained, so this is the safest first ship and the one students see.
- **Phase 2 — Teacher: Students and Student page.** C1, C2, C5–C7, F1.
- **Phase 3 — Teacher: Tasks, Words, Week, Messages.** C3, C4.
- **Phase 4 — Audit.** Run §6 in full; fix what fails; update `HANDOFF.md`.

All edits to `index.html` are string-anchored, appended at block ends, and
committed via a private index — the working rules in `HANDOFF.md` apply.

## 8. Decisions needed from Simon

1. Light-by-default for Teachbench (A3)? Recommendation: yes.
2. A second typeface for headings and flashcards (B3)? Recommendation: yes,
   one serif, loaded from Google Fonts with a system fallback.
3. Should Margo see the Phase 0 mockups before you choose, or after?
4. Is "calm editorial notebook" the right direction to draw first, or do you
   want one of the alternatives to be deliberately bolder?

## Sources

Apple HIG principles — [HIG summary](https://gist.github.com/eonist/f4ba31012815731284d867232f6c70e4), [Apple design system breakdown](https://superdesign.dev/blog/apple-design-system), [Liquid Glass: hierarchy, harmony, consistency](https://www.createwithswift.com/liquid-glass-redefining-design-through-hierarchy-harmony-and-consistency/).
AI-generated look and fixes — [The Purple Gradient Problem](https://dev.to/james_anderson_h/the-purple-gradient-problem-why-ai-ui-all-looks-alike-and-how-to-fix-it-3j65), [AI Design Slop (SmoothUI)](https://smoothui.dev/blog/ai-design-slop), [AI slop design tells (925 Studios)](https://www.925studios.co/blog/ai-slop-design-tells), [Design systems for AI coding](https://www.braingrid.ai/blog/design-system-optimized-for-ai-coding).
Typography — [Type scales in UI](https://medium.com/design-bootcamp/typographic-hierarchy-made-easy-understanding-type-scales-in-ui-24a694f1e0e8), [Typography hierarchy and usability](https://raw.studio/blog/how-typography-hierarchy-boosts-ui-usability/), [Semantic type tokens](https://uxdesign.cc/mastering-typography-in-design-systems-with-semantic-tokens-and-responsive-scaling-6ccd598d9f21).
Spacing — [Carbon spacing](https://carbondesignsystem.com/elements/spacing/overview/), [8pt grid](https://medium.com/design-bootcamp/designing-in-the-8pt-grid-system-f3c1183ea6e8), [Spacing best practices](https://cieden.com/book/sub-atomic/spacing/spacing-best-practices).
Colour — [60-30-10 rule (UX Planet)](https://uxplanet.org/the-60-30-10-rule-a-foolproof-way-to-choose-colors-for-your-ui-design-d15625e56d25), [Choosing a UI palette (UXPin)](https://www.uxpin.com/studio/blog/choose-color-pallete/), [60-30-10 for developers](https://www.sixtythirtyten.co/blog/60-30-10-rule-complete-guide).
Laws of UX — [All 21 laws (UX Design Institute)](https://www.uxdesigninstitute.com/blog/laws-of-ux/), [UX laws reference](https://www.parallelhq.com/blog/ux-laws-design-principles).
Cards and buttons — [Polaris card layout](https://polaris-react.shopify.com/patterns/card-layout), [Polaris common actions](https://polaris-react.shopify.com/patterns/common-actions/best-practices), [Polaris Card discussion](https://github.com/Shopify/polaris-react/discussions/6458), [Button hierarchy](https://cieden.com/book/atoms/button/how-to-create-button-hierarchy), [Button states (NN/g)](https://www.nngroup.com/articles/button-states-communicate-interaction/).
Empty states and copy — [Carbon empty states](https://carbondesignsystem.com/patterns/empty-states-pattern/), [UX microcopy guide](https://kompassify.com/blog/ux-microcopy-guide).
