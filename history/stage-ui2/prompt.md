Build "Meridian": a single self-contained file index.html (HTML, CSS and JS inline) that is a logistics operations console. No external libraries, fonts, images or network requests, and no build step. It must work when served by python -m http.server, on a 390px-wide phone and on desktop. Generate all data in the browser with a seeded pseudo-random generator, so it is identical on every load: 5,000 shipments with id, origin, destination, status (Created, In transit, Delayed, Delivered, Exception), carrier (6 carriers), weight, value, ETA date and risk score.

Requirements (implement all):
1. Layout: three resizable panes (navigation, workspace, inspector) with drag-resize handles and collapse buttons. Under 700px it becomes a single pane with a bottom tab bar.
2. A virtualized data table: only the visible rows exist in the DOM (at most 80 row elements), smooth scrolling, multi-column sort (shift-click), column resize, and show/hide columns.
3. A filter builder (field, operator, value, multiple rules combined with AND) plus a full-text search with match highlighting. Both update every other view.
4. Four hand-built charts using SVG or canvas: a time series with a draggable brush that filters the data, a stacked bar by status, a donut by carrier, and a heatmap of day by hour. They show tooltips on hover or tap and cross-filter each other and the table.
5. A kanban view of the same data grouped by status, with drag-and-drop between columns using pointer events (works on touch) and a keyboard alternative. Changes update the table and charts immediately.
6. A command palette opened with Ctrl/Cmd+K (and a visible button on mobile): fuzzy search over actions and shipments, with keyboard navigation and a focus trap.
7. Undo and redo (Ctrl+Z, Ctrl+Shift+Z) for status edits and filter changes, with a visible history list.
8. Inline editing of status in the table, with validation.
9. Three themes (light, dark, high contrast) using CSS variables, defaulting to the system preference, persisted in localStorage, and applied to the charts too.
10. Accessibility: proper roles and ARIA for the table, tabs and dialogs, visible focus styles, everything operable by keyboard, and prefers-reduced-motion respected.
11. State persistence: filters, sort, pane widths and current view are saved to the URL hash and localStorage, and restored on reload.
12. Export the current filtered view as CSV via a Blob download.
13. Toast notifications, empty states and loading skeletons.
14. Performance and hygiene: first render under 1 second for 5,000 rows, no console errors, no network requests.

Before finishing, extract your JavaScript to a temp file and run node --check on it.

Also write NOTES.md: for each of the 14 requirements say done, partial or skipped with one line of explanation, then list any known bugs, then how to run it. Do not claim done for anything you did not implement.
