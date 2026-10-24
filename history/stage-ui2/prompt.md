Build "Loop", a social media app UI, as ONE file: index.html (HTML, CSS and JS inline).
No network: no CDNs, web fonts or remote images. Generate avatars and photos with CSS or inline SVG. Audience: phone users, designed for 390px width, usable up to desktop.

Requirements (report each in NOTES.md as done, partial or skipped):
1. Home feed of at least 8 posts (avatar, name, handle, time, text, optional image, like/comment/share counts).
2. Stories row at the top: horizontally scrollable, tapping one opens a full-screen viewer that auto-advances and can be closed.
3. Like button with a visible animation; counts update.
4. Comments bottom sheet: open from a post, add a comment, close by swipe-down or tap outside.
5. Compose: a button opens a modal; posting adds the post to the top of the feed.
6. Bottom nav with Home, Explore, Alerts, Profile. All four screens work. Explore has search that filters posts. Alerts has a list with unread badges that clear when opened. Profile shows stats and a grid of posts.
7. Light and dark themes, with a toggle. Respect prefers-color-scheme at first load.
8. Visual quality: one accent colour, a consistent spacing scale, clear type hierarchy, 44px minimum tap targets, animations under 300ms, and prefers-reduced-motion respected.
9. No horizontal scroll at 390px. State may live in memory.

Definition of done: run `node --check` on the JavaScript and fix every error. NOTES.md lists the 9 requirements with status, how you checked each, and known bugs. Never claim a check you did not run.
