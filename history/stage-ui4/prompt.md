Build the homepage of "Lumen", an LMS where lecturers run quizzes, exams and research assignments and see a clear record of how each student worked. Deliver ONE file: index.html (HTML, CSS and JS inline). It must be a dynamic site, not a static mock: content is rendered by JavaScript from data arrays, and every control works. No network: no CDNs, web fonts or remote images. Use inline SVG icons and sample data. Audience: students and lecturers, many on slow data and mid-range phones, so keep it light. Design for 390px width and usable up to desktop.

Theme: blue. Define a palette as CSS variables (a deep blue primary, lighter blue tints, neutral greys). Amber is for flags, green for confirmations, red only for real errors. Provide light and dark themes with a toggle, and respect prefers-color-scheme on first load.

Requirements (report each in NOTES.md as done, partial or skipped):
1. Sticky header with logo, nav links that smooth-scroll to sections and highlight the current one, theme toggle, and a mobile menu drawer.
2. Role switch (Student / Lecturer) near the top. It changes the hero headline, supporting text and the featured benefits, with a smooth transition.
3. Hero with a clear headline, a primary button and a secondary button, and a live demo: a session timeline with at least 10 markers (pastes, page leaves, file added, idle gaps, question changes). Tapping or hovering a marker opens a detail card that is labeled Fact (recorded) or Pattern (observed) with different visual treatments.
4. Features section rendered from data, with filter tabs (All, For students, For lecturers, Integrity, Offline) that filter the cards with a count.
5. Course and assessment catalog of at least 10 items rendered from data, with search, filter chips by type (Quiz, Exam, Research), a sort control, an empty state, and a visible result count. Each card shows status, due date and type.
6. How-it-works stepper with 3 to 4 steps. Next and previous buttons and tappable step markers update the content and progress.
7. FAQ accordion with at least 6 questions (keyboard accessible, one open at a time).
8. "Request a demo" modal with name, email and role fields, inline validation, a success state, and a way to close it with the Escape key or by tapping outside.
9. Footer with links and language/region selector (it may only change displayed labels).
10. Language rules: never use the words cheating, cheater, caught, suspicious or guilty. Never use red for a flag. Say "flagged event", "unusual activity", "needs review". Short, plain sentences.
11. Quality: consistent 8px spacing, one type family from the system font stack, clear type scale, 44px minimum tap targets, visible focus states, WCAG AA contrast, colour never the only signal, animations under 300ms, prefers-reduced-motion respected, no horizontal scroll at 390px, total file under 150 KB.

Definition of done: run node --check on your JavaScript and fix every error. NOTES.md lists the 11 requirements with status, how you checked each, and known bugs. Never claim a check you did not run.
