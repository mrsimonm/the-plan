# Teachbench Student App — Complete Spec for Claude Code

Source: voice interview with the teacher (Simon's wife), organized for direct build handoff.

---

## Project Description

This is a new module inside the existing app suite (alongside Pottingbench and the current Teachbench teacher tools) — a **student-facing companion app** for private English lesson students. It should live in the same project, same stack: vanilla HTML/CSS/JS + localStorage, no new frameworks or build tools, matching the existing file/folder conventions in the project.

The core idea: a personalized, cross-platform app (phone + desktop, always accessible) that extends learning beyond lesson hours through spaced-repetition flashcards, while giving the teacher a dashboard to push content, track progress, assign homework, and generate monthly reviews.

The whole experience should feel visually clean, calm, and a bit luxurious — matching the comfort-focused, natural-conversation tone of the lessons themselves. The teacher is highly organization-oriented and wants everything quick to scan, visual, and well structured, both for herself and for students.

---

## 1. Core Features (Must-Have)

**Spaced repetition flashcards**
Three card types:
- Vocabulary/phrase/idiom cards — front: word or phrase, back: meaning/translation/example sentence.
- Grammar fill-in-the-blank cards — a sentence with a blank, student types or selects an answer, checked automatically, with an explanation shown if wrong. (E.g. present perfect: "I ___ (finish) my homework already.")
- Pronunciation cards — student speaks a target word/phrase; app plays back correct pronunciation via text-to-speech for comparison (speech recognition can come later).

Review timing follows a spaced repetition algorithm (SM-2 style: correct → interval grows, wrong → interval resets/shrinks) to move items into long-term memory. Each flashcard needs: `id`, `type`, `front`, `back`/correct answer, optional `explanation`, `studentId`, `createdAt`, and spaced-repetition metadata (`intervalStage`, `nextReviewDate`, `lastReviewedAt`). Keep the scheduling algorithm in its own function/module so it can be tuned later without touching UI.

**Scheduled review notifications**
Push notifications remind students to review flashcards at the correct spaced intervals. Hitting these windows on time is the actual mechanism that makes spaced repetition work — this isn't just a courtesy reminder, it's core to the feature.

**Teacher → student content sync**
Teacher adds flashcards after a lesson (on her side); they appear automatically in the student's app, triggering a "new words ready" notification. No manual student-side setup needed.

**Per-student progress dashboard (teacher side)**
Shows each student's flashcard and homework progress individually, so the teacher can see what to address in the next lesson. Personalized per student, not aggregate.

**Homework delivery and submission**
Replaces WhatsApp for homework. Teacher sends text, questions, or photos (e.g. screenshots); student replies with text or photo answers, directly in-app.

**Wispr Flow integration**
Teacher already uses Wispr Flow to record and transcribe/summarize her online lessons. The app should connect to Wispr Flow and pull in lesson summaries — either automatically, or via a manual upload option — to build a running per-student learning history (vocabulary and grammar covered, lesson by lesson) without manual re-entry.

**Student visual calendar**
Shows lesson times plus markers for when spaced-repetition reviews are due, so students can see at a glance when to give English some attention.

**Data model notes**
This module needs `Student` and `FlashcardItem` concepts, kept separate from Teachbench's existing `Task`/`Event`/`Project` models — don't overload existing types. Use new, clearly namespaced localStorage keys (e.g. `teachbench_student_*`).

---

## 2. Nice-to-Haves

- **Homework photo annotation** — teacher can draw/write directly on a submitted photo before sending it back
- **Teacher voice notes on flashcards** — real recorded pronunciation/example from the teacher's own voice, instead of (or alongside) text-to-speech
- **Student accent color personalization** — small per-student customization option
- **DeepSeek API integration (teacher side)** — future idea, no defined use case yet

---

## 3. Workflow Improvements

- **Gamification tied to review timing, not daily use** — streak/points system rewards on-time spaced-repetition reviews specifically, with bonus points for extra voluntary practice. Not a generic daily streak — it has to reinforce the actual spaced intervals.
- **Color-coded teacher dashboard** — per-student color coding so the teacher can glance at her full student list and instantly spot who's overdue, on a good streak, or needs attention, without reading text.
- **Monthly auto-generated teacher summary** — end-of-month export/prompt summarizing what was covered for a given student, designed to be pasted into an LLM (e.g. Gemini) to help draft the next month's lesson plan.
- **Monthly student recap** — short visual notice at month-end: what they mastered, what needs more focus, what's next, plus a motivational/inspirational message.
- **"At a glance" student summary** — weekly or monthly view of words learned, homework completed, and streak status.
- **Design polish for "luxurious" feel** — elegant, uncluttered UI; contextual welcome messages; small personalized touches throughout.

---

## 4. Open Questions / Needs Clarifying

- **Wispr Flow integration mechanics**: fully automatic sync, or manual "upload this summary" trigger? Worth deciding which is v1.
- **DeepSeek API use case**: undefined, deferred to later.
- **Gamification scope**: confirmed it should center on spaced-repetition timing rather than raw daily logins — worth defining exact point/streak rules before building.
- **Photo annotation**: nice-to-have, not blocking v1 — confirm if it's in scope for first release or a later pass.

---

## 5. Suggested Build Order (v1 scope)

1. Module scaffold + navigation shell, matching existing project conventions
2. `Student` and `FlashcardItem` data models + localStorage layer
3. Flashcard core (vocab, grammar, pronunciation types) + spaced repetition scheduling function
4. Basic review screen (show due card → answer → reschedule → next)
5. Teacher → student content sync
6. Student calendar (lessons + review due markers)
7. Homework delivery/submission
8. Per-student teacher progress dashboard
9. Wispr Flow integration
10. Gamification, monthly summaries, color coding, and remaining nice-to-haves

**Explicitly not v1**: speech recognition (TTS playback only for now), photo annotation, teacher voice notes, DeepSeek integration — these layer in after the core loop works.

## Working Style

- Small, testable commits — scaffold first, confirm it renders, then data model, then UI.
- Ask before assuming on ambiguous UI details; keep styling simple and consistent with the existing app for now, polish comes later.
- Don't touch existing Pottingbench or Teachbench-teacher-side files/models except to add navigation entry points.
