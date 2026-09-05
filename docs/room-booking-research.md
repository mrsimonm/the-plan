# Room Booking & Management — Research

Research for adding a Room Booking & Management module to this app (single-file PWA;
existing modules: Potting Bench, Planner/Daily, Hours, TeachBench, Notes; Czech/English;
localStorage-first with optional Firebase sync). Use case: a company/school with several
teaching or presentation rooms that needs availability, booking, conflict avoidance, and
room management.

Data-layer note (from a narrow grep of index.html, no code changed): TeachBench lessons are
plain objects with `date` (`YYYY-MM-DD` string), `time` (`HH:MM` plain time or `null`), a
`state` enum, `studentId`, and no explicit `duration` field on the lesson itself — the
Planner's day-view blocks are the part of the app that already have resizable, timed blocks
with a duration concept (grep hit near "resize to change duration" in the Planner code).
This suggests a Room Booking module should represent a **booking** as its own record
(roomId, date, start time, duration/end time, ownerId, linked lessonId optional) rather than
overloading the lesson record, and that it can reuse the Planner's existing timeline/grid UI
patterns for a day view.

---

## 1. Competitor landscape

### Skedda
- Target: coworking spaces, universities, sports clubs, studios, general "space booking" (rooms, desks, courts).
- Booking UX: interactive floor plans with drag-and-drop; day/week/list views.
- Conflicts: hard-blocked — a booking is simply refused if it collides with an existing one; one reviewer noted you can't preview the conflict before filling in all fields.
- Recurring: full repeat engine (day/week/month/year, end-by-date or occurrence count, exceptions); edit "this occurrence / this and following / full series".
- Approvals: role/rules engine (Booking Admin, System Admin, Owner) can gate who may create repeat or overlapping bookings.
- Room attributes: per-space settings, granular booking rules.
- Check-in/no-show: not a headline feature (more desk/room admin than kiosk-driven).
- Mobile: responsive web, no dedicated kiosk hardware push.
- Pricing: $99/$149/$199 per month flat tiers (Starter/Plus/Premier), billed annually, capped at 15/20/25 "spaces"; per-space not per-user pricing.
- Source: [GetApp](https://www.getapp.com/customer-management-software/a/skedda-bookings/), [Skedda Support – Repeat Bookings](https://support.skedda.com/en/articles/105723-repeat-bookings), [PeopleManagingPeople review](https://peoplemanagingpeople.com/tools/skedda-review/)

### Robin (Robin Powered)
- Target: hybrid-work offices booking desks *and* rooms, not schools.
- Booking UX: floor plans/maps, calendar sync (Outlook/Google), self check-in that auto-releases unused rooms.
- Conflicts/no-show: check-in required or the room auto-releases — solves the "ghost booking" problem well.
- Room attributes: utilization reporting per room/floor.
- Mobile: full mobile apps with location-based reminders.
- Pricing: ~$3–5/employee/mo (Basic) to $5–8/employee/mo (Professional with visitor mgmt); alternate quote of "from $399/mo" flexible/tailored.
- Source: [SelectHub](https://www.selecthub.com/p/iwms-software/robin-powered/), [Vendr pricing](https://www.vendr.com/marketplace/robin)

### Envoy Rooms
- Target: corporate offices (paired with Envoy's visitor-management product).
- Booking UX: room displays with green/yellow/red status; one-tap booking from the tablet display, Slack, or Teams; live availability maps.
- Conflicts/no-show: auto-release on missed check-in; nudges to book smaller rooms if a big room is under-used.
- Mobile: dedicated app; kiosk requires an iPad (iOS 10+) per room.
- Pricing: per-resource — Standard $5/resource/month + platform fee (billed annually); reservations quoted separately as ~$60/bookable resource/year; visitor management is a separate $109/location/month product.
- Source: [Envoy pricing](https://envoy.com/pricing), [Envoy Rooms product page](https://envoy.com/products/conference-room-scheduling-software)

### Joan
- Target: offices wanting a hardware-forward, low-power kiosk experience (e-ink displays outside each room).
- Booking UX: e-ink door panel shows live status; book from panel, app, or calendar client; floor plan view.
- Hardware: e-ink devices from €349 (Joan 6 RE) to €899 (Joan 13 Pro); battery lasts months to 2+ years since e-ink only draws power on refresh — genuinely differentiated hardware angle, but irrelevant to a pure-software module like ours.
- Integrations: Outlook, Exchange, Google Calendar, Slack.
- Pricing: software from €49/user/month; device connection fee from €9.99/device/month; 30-day free trial.
- Source: [Joan e-ink signage](https://getjoan.com/e-ink-signage/), [Joan pricing (G2)](https://www.g2.com/products/joan/pricing)

### YArooms (YAROOMS)
- Target: mid-size to large hybrid offices; broadest feature set of the bunch (booking + visitor mgmt + digital signage + analytics in one suite).
- Booking UX: web, mobile, Teams chatbot ("YARVIS" AI assistant), and door-panel signage.
- Conflicts/recurring: customizable booking rules, real-time availability, self check-in.
- Pricing: Starter $99/mo (≤20 users, 1 location, 2 floors, interactive floor map); Business $399/mo (≤200 users, 2 locations, 90-day analytics); Enterprise unlisted.
- Source: [YAROOMS product page](https://www.yarooms.com/product/room-booking-software), [Capterra](https://www.capterra.com/p/140364/YAROOMS/)

### Roomzilla
- Target: explicitly spans meeting rooms, classrooms, and gyms — closest of the "big" tools to a school/tutoring use case.
- Booking UX: tablet displays per room/desk showing live status; QR-code quick reservation.
- Conflicts/no-show: real-time availability + auto-cancellation if a booking isn't confirmed via the display/email within a set window — directly solves no-show/ghost bookings.
- Pricing: genuinely small-org friendly — free for ≤3 resources; Standard $17/room or $10/desk per month for 4–29 resources; custom quote at 30+. No pricing tier at Skedda/YArooms scale ($99+/mo minimum) — this is the cheapest "real" competitor.
- Source: [Roomzilla pricing](https://www.roomzilla.net/pricing/), [GetApp](https://www.getapp.com/collaboration-software/a/roomzilla/)

### Condeco (Eptura Engage)
- Target: large enterprises, multi-floor/multi-site — not relevant in scale, but its AI-assisted natural-language booking and badge/sensor-driven auto-check-in are UX ideas worth noting.
- Booking UX: AI-assisted "find me a room" in natural language, deep Microsoft 365/Outlook/Teams integration.
- Conflicts/no-show: automated check-in via badge swipe or occupancy sensors; auto-releases unoccupied bookings; generates walk-in bookings from sensor data.
- Pricing: enterprise-only, roughly £15–25/user/year for combined room+desk, room-panel hardware priced separately. Irrelevant price point for a school/tutoring centre.
- Source: [SoftwareSuggest](https://www.softwaresuggest.com/condeco), [Smart Workplace Guide review](https://smartworkplaceguide.com/reviews/condeco-review-2026-enterprise-room-and-desk-booking-assessed/)

### Teamup Calendar
- Target: teams/departments needing a shared calendar rather than a dedicated "booking system" — closest in spirit to what a solo/small teaching business might reach for instead of building anything.
- Booking UX: one color-coded sub-calendar per room/resource; 11 calendar views including Excel-like tables; no dedicated floor-plan/kiosk UI.
- Conflicts: "disallow double-booking" is a per-calendar toggle, not a hard system-wide constraint; 9 levels of granular access permission (e.g. "modify own bookings only").
- Pricing: free tier, then $10/mo (Plus), $24/mo (Premium), $99/mo (Enterprise); org accounts from $1,200/year. Free tier is usable for a very small single-location setup.
- Source: [Teamup resource bookings](https://www.teamup.com/resource-bookings/), [Teamup pricing](https://www.teamup.com/pricing/)

### Google Workspace room resources (Calendar)
- Target: any org already on Google Workspace — the "default" free option many small schools fall back to.
- Booking UX: rooms are calendar resources with their own email address; you invite the room like a person; "Add rooms or location" search by capacity/equipment; auto-suggestion of best room based on attendee locations and history.
- Conflicts: hard-blocked at the calendar layer — if a room resource is already booked it can't accept a second invite, or a designated resource manager can accept/decline (e.g., "only classroom trainers can book mornings").
- Cost: bundled into every paid Workspace plan, no separate booking-layer fee — very relevant as a "free-if-you-already-pay-for-Workspace" baseline our module competes with.
- Source: [Google Workspace Admin Help](https://support.google.com/a/answer/9025584), [Archie: Google Calendar Room Booking](https://archieapp.co/blog/google-calendar-room-booking/)

### Microsoft Places / Bookings
- Target: Microsoft 365 shops; Places is the newer unified desk+room booking surface (successor/companion to the older Bookings app).
- Booking UX: book from Outlook, Teams, or the Places app; "Places Finder" shows room photos, capacity/equipment filters, and Teams Rooms device info.
- Conflicts: rooms are resource calendars, so double-booking is prevented automatically, same mechanism as Google.
- Cost: bundled into Microsoft 365 licensing tiers that include Places; no separate line-item price found (varies by tenant licensing).
- Source: [Microsoft Learn – Room and Desk Booking](https://learn.microsoft.com/en-us/microsoft-365/places/room-desk-booking/rooms), [Elia.io Places overview](https://www.elia.io/blog/microsoft-places-overview)

### Calendly
- Target: 1:1/group meeting scheduling generally; "meeting room booking" is a bolt-on feature, not its core.
- Booking UX: connects to real calendars to check conflicts before someone books; round-robin distribution across staff.
- Pricing: Free, Standard $10/seat/mo, Teams $16/seat/mo, Enterprise from ~$15,000/year. Per-seat pricing scales badly for a school with many part-time tutors — a relevant negative data point.
- Source: [Calendly pricing](https://calendly.com/pricing)

### SuperSaaS
- Target: small businesses/clubs; explicitly markets a free conference/meeting-room booking template.
- Booking UX: self-service reservation, calendar sync, SMS/email reminders, online payment (PayPal) built in.
- Notable: **usage-based pricing, not per-seat** — unlimited staff/locations/schedules without per-person cost; can set peak/off-peak or member/non-member pricing per room. Free tier caps at 50 upcoming appointments and 50 users.
- Pricing: $9–$48/month tiers beyond the free cap.
- Source: [SuperSaaS conference room booking](https://www.supersaas.com/info/conference-and-meeting-rooms-booking-system)

### Open-source / self-hostable
- **Booked Scheduler / LibreBooking** — general-purpose bookable-resource engine (rooms, equipment, labs, vehicles, people) with rule-based permissions; actively maintained fork is LibreBooking. Good fit for universities/labs; UI described as dated and initial setup nontrivial.
- **Easy!Appointments** (GPL, PHP/MySQL, [GitHub](https://github.com/alextselegidis/easyappointments)) — self-hosted appointment scheduler: providers/services model, working-hour rules, Google Calendar sync, email notifications, multi-language. Built around "provider + service" (like a single tutor's calendar) rather than "room as the bookable unit," so it would need adaptation for a room-first model.
- Source: [Booknetic open-source roundup](https://www.booknetic.com/blog/best-open-source-scheduling-software), [Easy!Appointments](https://easyappointments.org/)

### Tutoring/education-specific
- **Tutorbase** — purpose-built for tutoring centres; the most directly analogous product to what this app could become. Room booking is framed as an *availability engine*: it validates teacher + room + branch simultaneously (won't let a teacher already booked at Branch A be scheduled into a Branch B room in the same slot), filters rooms by capacity/equipment (whiteboard, projector, piano)/delivery mode (in-person/online/hybrid)/location, handles recurring weekly lesson series without manual duplication, and treats the room booking as the source record that flows into invoicing/payroll when room fees apply. Free signup, no credit card required; paid pricing not published. Source: [Tutorbase: Room Booking System Guide](https://tutorbase.com/blog/room-booking-system).
- **Appointy** — general scheduling tool with an education vertical: single/recurring classes with capacity limits, auto-reserves equipment/lab rooms/sports fields/conference halls when a session is booked, hybrid classes with auto-generated Zoom links, staff/parent-meeting scheduling. Pricing: free plan, then $19.99–$99.99/month tiers plus $5–7.50/staff. Source: [Appointy education scheduling](https://www.appointy.com/education-scheduling-software/).
- **Koalendar** — lightweight tutor-scheduling layer (bookings + reminders + payments) aimed at individual tutors/small centres rather than multi-room facilities; less relevant to the room-management angle but confirms the segment exists as a market. Source: [Koalendar tutors](https://koalendar.com/scheduling-software-for/tutors).

## 2. Feature matrix

| Product | Target | Booking UX | Conflict handling | Recurring | Approvals | Room attributes | Check-in/no-show | Mobile | Entry price |
|---|---|---|---|---|---|---|---|---|---|
| Skedda | Coworking/clubs/studios | Interactive floor plan, drag-drop | Hard block, no live preview | Full repeat engine w/ exceptions | Role-based (admin can override) | Per-space settings | Not a focus | Web responsive | $99/mo (15 spaces) |
| Robin | Hybrid offices | Floor plan/map + calendar sync | Prevented via calendar | Standard | — | Utilization reporting | Self check-in auto-release | Native apps | ~$3–8/employee/mo |
| Envoy Rooms | Corporate offices | Room-display traffic lights, one-tap | Prevented; auto-release | Standard | — | — | Auto-release + nudge to downsize | Native app + iPad kiosk | $5/resource/mo + fee |
| Joan | Offices (hardware-first) | E-ink door panel + app | Prevented via calendar | Standard | — | — | Panel-based check-in | App + e-ink hardware | €49/user/mo + €9.99/device |
| YArooms | Mid/large hybrid offices | Web/mobile/Teams bot/signage | Prevented, customizable rules | Standard | Rules engine | Floor maps | Self check-in | Full | $99/mo (≤20 users) |
| Roomzilla | Rooms, classrooms, gyms | Tablet display, QR quick-book | Real-time block + auto-cancel on no-confirm | Repeating | — | Per-resource | Auto-cancel if unconfirmed | Mobile | Free ≤3 resources, $17/room/mo |
| Condeco | Large enterprise | AI natural-language booking | Prevented; sensor/badge-driven | Standard | — | — | Badge/sensor auto check-in | App | £15–25/user/yr (enterprise) |
| Teamup | Any team calendar | Color-coded sub-calendar per room | Optional per-calendar toggle | Standard | 9 permission levels | Minimal | None built-in | Web/app | Free tier; $10/mo Plus |
| Google Workspace | Workspace orgs | Invite room like a person | Hard block (resource calendar) | Standard | Resource manager accept/decline | Capacity/equipment search | None built-in | Full | Bundled in Workspace |
| Microsoft Places/Bookings | Microsoft 365 orgs | Outlook/Teams/Places app | Hard block (resource calendar) | Standard | — | Photos, capacity, equipment filters | — | Full | Bundled in M365 |
| Calendly | General meetings | Calendar-synced booking page | Checked against connected calendars | Standard | Round-robin | Minimal | — | Web/app | Free; $10/seat/mo |
| SuperSaaS | Small biz/clubs | Self-service reservation | Standard | Standard | — | Peak/off-peak & member pricing per room | Reminders only | Web/app | Free ≤50 bookings; $9/mo |
| Booked Scheduler/LibreBooking | Universities/labs (self-host) | Web calendar UI (dated) | Rule-based | Standard | Rule-based permissions | Rich (rooms/equipment/vehicles/people) | — | Responsive web | Free (self-hosted) |
| Easy!Appointments | Self-hosted, provider-centric | Provider/service booking page | Standard | Standard | — | Minimal (provider-first, not room-first) | — | Responsive web | Free (self-hosted) |
| Tutorbase | Tutoring centres | "Find slot" search across teacher+room+branch | Validates teacher+room+branch together | Weekly series, no manual duplication | — | Capacity, equipment, delivery mode, branch | Feeds into invoicing/payroll | Web/app | Free signup, price unpublished |
| Appointy | Education/general SMB | Class booking page, auto-reserve resources | Standard | Recurring w/ monthly/weekly caps | — | Equipment/room/field auto-reserve | Reminders | Web/app | Free; $19.99–$99.99/mo |

## 3. UX patterns worth copying

- **Room = a resource with an inbox, not just a row in a table** (Google/Microsoft pattern). Treating a booking as "invite the room" generalizes nicely to a localStorage-first app: a booking record referencing `roomId` plus start/end, no need to actually model rooms as email accounts.
- **Hard conflict prevention, always** (Skedda/Google/Microsoft/Envoy). Every serious tool refuses an overlapping booking outright rather than warning-and-allowing. One Skedda user complaint — you can't see the conflict until you've filled in the whole form — is worth avoiding: show the conflict live as the user picks date/time/room, before they submit.
- **"Find me a slot" search beats a static grid for a busy small business** (Tutorbase's "Find Slot"/"Find Spot", Google's auto-suggested rooms). For a tutoring centre booking a lesson, the natural query is "a room free Tuesday 4–5pm for 6 students with a whiteboard," not "let me scan a grid." Worth offering both: a day/week timeline grid (reuse Planner's existing timeline UI) *and* a search-by-constraint mode.
- **Validate the whole chain, not just the room** (Tutorbase). A booking should fail if the *teacher* is double-booked even if the *room* is free — directly relevant here since TeachBench already has teacher/student/lesson state; a naive "is this room free" check would miss teacher conflicts.
- **Auto-release / no-show handling** (Robin, Envoy, Roomzilla, Condeco). Every workplace tool solves "someone books a room and doesn't show" with either a check-in step or a released-if-unconfirmed timer. Less critical for a small tutoring business booking its own known rooms in advance, but worth a lightweight version: an unconfirmed booking older than N minutes past its start could be flagged (not necessarily auto-cancelled, since a human running one location doesn't need kiosk-grade automation).
- **Room attributes as filters, not just labels** (Tutorbase, Microsoft Places Finder, Envoy). Capacity, equipment (whiteboard/projector/piano-equivalent for a teaching context), and delivery mode (in-person/online/hybrid) are the three attributes that actually drive which room fits which lesson — a good minimal attribute set to start with.
- **Recurring bookings with per-occurrence editing** (Skedda's "this occurrence / this and following / full series"). TeachBench lessons already have a comparable reschedule pattern (`state:"rescheduled"`, `originalDate`), so the room-booking recurrence UI should follow the same mental model already used elsewhere in the app rather than inventing a new one.
- **Usage-based, not per-seat, pricing model** (SuperSaaS) is a positioning idea more than a UX one, but it maps to how this app is already priced/distributed (a single owner runs multiple tutors/rooms) — irrelevant to build, but worth remembering if this ever becomes a paid module aimed at other schools.

## 4. Pricing/positioning

- The market splits into three price bands: **enterprise per-user/year** (Condeco, Microsoft/Google bundled into existing licensing), **SMB per-month flat-or-per-resource** ($99–$399/mo for Skedda/YArooms; $17/room or $10/desk for Roomzilla; $9–$48/mo for SuperSaaS), and **free/self-hosted** (Google/Microsoft Calendar resources if already paying for the suite; Booked Scheduler/LibreBooking and Easy!Appointments if self-hosting).
- **A tutoring centre with a handful of rooms is the worst-served segment by the big workplace tools** — Skedda/YArooms/Envoy/Joan all assume a minimum spend around $99+/month or per-resource fees that add up fast for a small operator, and none integrate lesson/student data. Roomzilla's free tier (≤3 resources) and Tutorbase (education-native) are the only two that fit a small tutoring business's actual budget and workflow.
- **This app's structural advantage**: it already is the lesson/student/payment system (TeachBench) that Tutorbase and Appointy bolt room-booking onto as a *feature* of a broader tutoring platform. Building room booking natively here means the room-booking layer can validate against real lesson data (teacher, student, existing lesson time) for free, instead of syncing two separate systems.
- **Positioning**: not a competitor to Skedda/Condeco (those solve "hundreds of desks across a corporate campus"); the right comparison set is Tutorbase/Appointy's room-booking feature — small teaching organisation, a handful of physical rooms, tightly coupled to lessons already being scheduled. No separate purchase, no per-seat fee, works offline via the same localStorage model as the rest of the app.

## 5. Open-source / self-hostable options

- **Booked Scheduler / LibreBooking** — closest architectural analog if this were ever extracted as a separate service: room/equipment/vehicle/person as a generic "resource," rule-based permissions per resource. Its documented weaknesses (dated UI, nontrivial setup) are exactly what a native, single-file, no-install module here would avoid.
- **Easy!Appointments** — models scheduling around a *provider* (person) offering a *service*, with rooms if any treated as an attribute rather than the primary entity. Less directly applicable since our need is room-first (multiple teachers/lessons compete for the same physical room), not provider-first.
- **Neither is worth integrating or forking** — both are separate server-side PHP/MySQL apps requiring their own hosting, login, and data model, which conflicts with this app's localStorage-first, single-file, optional-Firebase-sync architecture. They're useful only as a reference for what a minimal, complete room-booking data model looks like (resource, booking, recurring rule, permission).

## 6. What small schools & tutoring centres actually use

- In practice, small operators either (a) use a **shared Google/Microsoft calendar per room** because it's already free with their existing email, (b) use a **whiteboard/paper/spreadsheet** for a single-location business with 1–3 rooms, or (c) adopt a **tutoring-specific SaaS** (Tutorbase, Appointy, or similar) once they have enough rooms/staff that manual coordination breaks down.
- The purpose-built tutoring tools (Tutorbase, Appointy, Koalendar) consistently bundle room booking *into* lesson/class scheduling rather than selling it standalone — validating the plan to build this as a TeachBench-integrated feature rather than a freestanding "rooms" app.
- The recurring pain point cited across sources is exactly what Tutorbase's "availability engine" targets: double-booking a teacher across two locations, or a room across two unrelated lessons, when scheduling is done by hand or across disconnected calendars. A room-booking module here should treat "teacher already has a lesson at this time" as a hard conflict alongside "room already booked," since the app already owns that lesson data.

## 7. Proposed concept for THIS app

**Data model** (fits the existing plain-object/localStorage style seen in TeachBench's `createLesson`/`emptyData`):

```js
function createRoom(fields) {
  return {
    id: createId(),
    name: String(fields.name || '').trim(),
    capacity: Number.isFinite(fields.capacity) ? fields.capacity : null,
    equipment: Array.isArray(fields.equipment) ? fields.equipment : [], // e.g. ["whiteboard","projector"]
    location: String(fields.location || '').trim(), // free text, e.g. building/floor
    active: fields.active !== false,
  };
}

function createBooking(fields) {
  return {
    id: createId(),
    roomId: fields.roomId,
    date: isPlainDate(fields.date) ? fields.date : '',
    time: isPlainTime(fields.time) ? fields.time : null,      // start, HH:MM
    duration: Number.isFinite(fields.duration) ? fields.duration : 60, // minutes
    lessonId: fields.lessonId || null,   // link to a TeachBench lesson, if any
    ownerId: fields.ownerId || null,     // teacher/staff who booked it
    title: String(fields.title || '').trim(), // free bookings not tied to a lesson (e.g. "staff meeting")
    state: ['confirmed','cancelled'].includes(fields.state) ? fields.state : 'confirmed',
    recurring: fields.recurring || null, // {freq:'weekly', until:'YYYY-MM-DD'} or null
  };
}
```

`emptyData()` gains `rooms: []` and `bookings: []` alongside the existing arrays.

**Conflict rule**: a new booking is rejected if it overlaps (same `roomId`, overlapping `date`+`time`+`duration`) with another active booking, *and* — since lessons already carry `studentId`/teacher context — if it overlaps a TeachBench lesson assigned to the same teacher in a different room. This reuses the "teacher + room together" validation pattern from Tutorbase rather than checking the room in isolation.

**Screens**:
1. **Rooms admin** (new small section, likely under Hours or a new top-level "Rooms" entry): a list/CRUD for rooms — name, capacity, equipment tags, location.
2. **Room day/week timeline** — reuse the Planner's existing resizable-block day-view code (the module already has drag-to-move and resize-to-change-duration on Planner blocks) with rooms as parallel columns instead of one column per day; this avoids building a whole new grid component.
3. **Book a room from a lesson**: when creating/editing a TeachBench lesson, add an optional "room" field; picking a room+time surfaces conflicts live (per the "show conflicts before submit" lesson from the Skedda complaint) and, on save, creates/updates the linked `booking` record automatically.
4. **Standalone booking** (for non-lesson use — staff meetings, presentations): a lightweight form (room, date, time, duration, title) using the same conflict check, independent of TeachBench.

**MVP scope** (v1):
- Rooms CRUD (name, capacity, equipment, location).
- Manual booking creation/edit/delete with hard conflict prevention against other bookings in the same room.
- One room-day timeline view (read-only availability at a glance) built on the Planner's existing timeline component.
- Linking a booking to a TeachBench lesson (optional field on the lesson editor), so lessons that need a room show up in the room view automatically.

**Phase 2**:
- Recurring room bookings (mirroring the reschedule/exception pattern already used for lessons).
- Room ↔ teacher combined conflict check (reject a lesson move if the *teacher* is double-booked even across different rooms).
- Search-by-constraint ("find a free room now/next for N people with X equipment"), modeled on Tutorbase's "Find Slot."

**Phase 3** (only if multi-location/multi-tenant ever matters):
- Approval workflow for shared/external bookings (only relevant if rooms are ever shared with people outside this app's existing student/teacher/staff set).
- Firebase-synced multi-device booking so two staff members editing the same room's calendar on different devices resolve conflicts server-side rather than only via localStorage merge.

**Integration with Planner**: since Planner blocks already have resize-to-change-duration, the room timeline view should be visually and interactionally consistent with Planner rather than introducing a second scheduling metaphor in the same app.

## 8. Risks & open questions

- **Two sources of truth for time**: once a lesson can carry a linked `bookingId`/room, edits must keep the lesson (`date`/`time`) and the booking (`date`/`time`/`duration`) in sync — worth deciding early whether the booking *is* the lesson's schedule (single source) or a separate parallel record (current proposal), to avoid drift bugs.
- **Firebase sync + conflict detection**: this app's model is localStorage-first with *optional* Firebase sync; if two devices create overlapping bookings for the same room while offline, conflict prevention that works fine against a single local store won't automatically catch a cross-device conflict until sync — needs a merge/reconciliation rule (e.g., last-write-wins is not safe for double-booking; may need a sync-time re-validation pass that flags rather than silently overwrites).
- **No duration field currently exists on TeachBench lessons** — the concept above adds `duration` only to the new `booking` record, not to lessons, to avoid touching the existing lesson shape; this needs confirming against the actual default lesson length used elsewhere before implementation (not confirmed here, per the scope limit on reading index.html).
- **Scope creep toward the big competitors' features** (kiosk displays, check-in/auto-release, sensor integration, approval chains) is real risk given how differentiated those features are in the market — none of it is needed for a single small tutoring business booking its own rooms in advance, and building it would be pure over-engineering for this app's actual use case.
- **Open question for the owner**: is "room booking" meant only for TeachBench lesson rooms, or also for the Potting Bench / general household use (e.g., presentation rooms for an unrelated audience)? The concept above assumes the primary driver is TeachBench lessons with a secondary standalone-booking capability; if the real need is closer to a general shared-space calendar unrelated to lessons, the MVP priority (lesson-linked booking first) should flip.

(to be filled in)
