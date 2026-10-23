Build "Signal Garden": one self-contained file index.html (HTML, CSS and JS inline). No external libraries, fonts, images or network requests, and no build step. It must work when served by python -m http.server, on a 360px-wide phone and on desktop.

Concept: a generative night-time botanical garden control room where sound, light and plant growth are linked. Pick a distinctive art direction (clear concept, considered palette, system font stacks). Avoid a generic template look.

Requirements (implement all):
1. A full-width animated canvas scene of growing plants or particles that reacts to pointer and touch.
2. A synth: at least 8 pads that play notes with WebAudio. Audio starts only after a user gesture. Include a mute button.
3. A visualizer driven by an AnalyserNode (bars or rings), visibly animating while notes play.
4. At least 3 floating panels (controls, mixer, log) that can be dragged by mouse and touch and come to front when tapped. On narrow screens they must stack or collapse sensibly.
5. Three themes switchable at runtime using CSS variables, with smooth transitions.
6. Pads playable with keys 1-8, visible focus styles, and prefers-reduced-motion respected.
7. At least 3 distinct polished micro-interactions (for example magnetic buttons, ripples, easing).
8. No console errors and no network dependence.

Before finishing, extract your JavaScript to a temp file and run node --check on it to catch syntax errors.

Also write NOTES.md: for each of the 8 requirements say done, partial or skipped with one line of explanation, plus how to run it. Do not claim done for anything you did not implement.
