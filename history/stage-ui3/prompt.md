Deliver the design brief below as ONE file: index.html (HTML, CSS and JS inline). It is a clickable prototype, not a design-tool file. No network: no CDNs, web fonts or remote images. Use inline SVG icons and sample data. Light and dark themes. Phone screens are designed for 390px width, lecturer screens for desktop.

The brief is large. Do as much of it as you can, and use your own judgment on what to cut. In NOTES.md list every screen and deliverable in the brief as done, partial or skipped, with a one-line reason for each skip. Follow the brief's language rules exactly (no red flags, no banned words).

Definition of done: run `node --check` on your JavaScript and fix every error. NOTES.md also lists how you checked each item and known bugs. Never claim a check you did not run.

THE BRIEF:UI Design Prompt: Process-Transparent Assessment Platform
Paste everything below the line into the design model. Attach or reference the Lovable project brief if the tool accepts it.
Your role
You are a senior product designer. Design the complete UI for a web platform that lets lecturers run quizzes, exams and research assignments, and shows them a clear record of how each student worked. Produce a small design system first, then every screen listed below, each in desktop and mobile versions where stated.
What the product is
Students complete assessments inside our workspace. The platform records activity (typing, pastes and where they came from, materials viewed, leaving the page, time per question, answer changes). The lecturer reviews a timeline of that evidence and decides what it means. We never lock students out and never declare anyone guilty.
Two audiences, two feels:
• Students: calm, reassuring, focused. They must feel supported, not watched. Mobile-first.
• Lecturers: clear, dense, trustworthy. They review many students quickly and must understand every flag at a glance. Desktop-first.
Many users are in markets with slow, expensive data and mid-range phones, so the UI must be light: no heavy imagery, minimal animation, small assets.
Design principles
1. Evidence, not accusation. Never use red for a flag. Never use the words "cheating", "cheater", "caught", "suspicious" or "guilty" in the UI. Use "flagged event", "unusual activity", "rule broken", "needs review".
2. Fact versus pattern. Every flag shows whether it is a recorded fact ("Pasted 200 words from Lesson 3, page 2") or an observed pattern ("300 words typed in 90 seconds after leaving the page for 4 minutes"). Give them different visual treatments.
3. Honest limits. Limited-tracking sessions (mobile, browser-only) carry a visible badge so an empty log is never mistaken for clean behavior.
4. Transparency to students. Before starting they see exactly what is recorded. Afterward they can view their own log.
5. Never lose work. Autosave status and connection status are always visible during an assessment.
6. Plain language. Short sentences. No jargon in student screens.
Visual style
• Calm, academic, trustworthy. Lots of whitespace on student screens, tighter density on lecturer screens.
• Palette: a muted deep blue or teal as primary; neutral greys; amber for flags; green for confirmations; red reserved for real errors only (failed upload, connection lost). Suggest exact hex values and a dark mode.
• Type: one clean sans-serif family (Inter or similar). Define a scale (display, heading, body, small, caption). Use a monospace face only for hashes and file names.
• Rounded corners (8 to 12 px), subtle borders over heavy shadows, 8 px spacing grid.
• Icons: one consistent line-icon set.
• Accessibility: WCAG AA contrast, color never the only signal (pair color with icon and text), visible focus states, keyboard navigation, tap targets at least 44 px.
Design system to produce first
Colors and tokens, typography, spacing, buttons (primary, secondary, quiet, destructive), form fields, selects, toggles, tabs, cards, tables, badges and chips (including the Limited tracking, Student-supplied, Fact, Pattern and Flag variants), toasts, dialogs, drawers, progress bars, timers, empty states, skeleton loaders, and the timeline marker component used in the review screen.
Student screens (mobile-first, with a desktop version)
1. Home / my courses. Upcoming and past assessments as cards with status (open, in progress, submitted), due time and type.
2. Pre-assessment consent. Plain-language list of what is recorded, who can see it, how long it is kept, and what is not recorded. Security level shown as a simple label with a one-line description. Checkbox and a clear "Start" button. Link to "Need an accommodation?"
3. Quiz / exam screen. Sticky top bar with a countdown timer (calm, turns amber in the last minutes), question progress, autosave indicator ("Saved") and a connection indicator. One question at a time with large answer options, and a question navigator the student can open as a drawer. Gentle, non-accusatory notice if the student leaves the page ("You left for 20 seconds. This is recorded for your lecturer.").
4. Offline / reconnecting state. Work keeps saving locally, with a banner explaining it will sync when back online.
5. Writing workspace (assignments and research). Desktop: split layout with a materials panel (PDF and DOCX viewer, tabbed) on one side and the rich-text editor on the other, with a draggable divider and a swap-sides toggle. Mobile: the editor full screen, with materials in a bottom or side drawer. Show allowed and not-allowed actions near the editor (for example, a small "Pasting from Lesson materials is allowed" hint). Student-supplied sources appear in a separate tab labeled Student-supplied, with an upload control that respects the lecturer's setting (off, before start only, any time).
6. Submit confirmation. A summary (answered, unanswered, time used) and a final confirm step. Then a success screen with a link to "View my activity".
7. My activity. A simple, readable list or timeline of what was recorded in the student's session, in plain language, with no flags language aimed at the student.
Lecturer screens (desktop-first, with a usable tablet version)
1. Dashboard home. Courses, upcoming assessments, and a "needs review" queue showing sessions with flagged events.
2. Course page. Students, assessments, materials.
3. Assessment builder. A step flow: Basics, Questions, Materials, Security and rules, Review and publish. Include question types (multiple choice, short answer, long answer), question bank with random draw, order randomization, time limit, open-book or closed-book.
4. Security level picker. Three preset cards: Basic (activity log), Standard (log plus identity check), Strict (desktop app plus camera, marked "Coming soon" and disabled). Each card lists in plain language exactly what is recorded. An "Advanced" expander reveals individual settings.
5. Rule builder. Each rule is a readable sentence with controls, for example When a student pastes text from [lecturer material v] → [allow v], When a student leaves the page for more than [30] seconds → [flag v]. Add rule, reorder, preset templates ("Open book", "Closed book", "Research project"), and a small preview of what would be flagged.
6. Materials manager. Upload PDF and DOCX, set each as "allowed to quote", "must cite" or "view only", with file size and type limits shown.
7. Class review list. Table of students with columns: name, status, session type (with the Limited tracking badge where relevant), number of flagged events, time spent, submitted time. Sort and filter by flag count and flag type. Row click opens the session.
8. Session review (the most important screen). Design this with the most care.
    ◦ Header: student, assessment, session type badge, total time, flag count.
    ◦ Timeline: a horizontal timeline of the whole session with colored markers for events (pastes, page leaves, file additions, long idle gaps, question changes). Hovering a marker shows a short tooltip, and clicking opens a flag detail drawer with the surrounding context (text before and after, source material and page, durations).
    ◦ Each flag in the drawer shows its Fact or Pattern label, the rule it broke, and what the lecturer's setting was.
    ◦ Replay: play, pause and scrub the writing back from the stored text changes, with the timeline synchronized.
    ◦ Sources panel: lecturer materials used, plus student-supplied files with the time each was added.
    ◦ Summary strip: neutral context lines such as "12 of 15 paragraphs have no related source activity", never presented as a verdict.
    ◦ Decision and notes: the lecturer's outcome (no concern, needs follow-up, referred) and a notes field.
9. Probe workflow. A focused view that lists the questions or passages with the most unusual activity for one student, with space to write follow-up questions to ask orally, record the student's response, and mark the outcome.
10. Settings. Retention period, upload quotas, and consent text.
States to design for every key screen
Empty, loading (skeletons), error, offline, long content, a very long timeline with many events, a student with zero flags, and a session marked Limited tracking.
Copy tone
Neutral and respectful. Examples of the right voice: "This was recorded for your lecturer." / "Pasted 200 words from Lesson 3." / "Needs review." Examples of the wrong voice: "Cheating detected." / "Suspicious behavior." / "You were caught leaving the page."
Deliverables
1. Design system board (tokens and components).
2. Student screens in mobile and desktop.
3. Lecturer screens in desktop (and tablet for the review list and session review).
4. A clickable flow for: student takes a quiz on a phone, loses connection, reconnects and submits; and lecturer opens a flagged session, inspects a flag, and records a probe outcome.
5. A short notes page listing component names and states so the designs can be handed to developers working in React and Tailwind.

