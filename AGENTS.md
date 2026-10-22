# AGENTS.md: read this first

This repo is the memory and runner for a multi-model remote coding setup.
Any AI or human picking this up in a fresh chat should start here.

## Reading order
1. `STATE.md`: where things stand right now (short, always current)
2. `DECISIONS.md`: what was decided and why
3. `ERRORS.md`: problems hit and their fixes
4. `history/INDEX.md`: one line per completed stage
5. `history/stage-NN/`: full detail for a stage, only when needed

## Rules
- NEVER write tokens, keys, or secrets into this repo, logs, or chats.
  Secrets live in Modal Secrets only. Scan before every push.
- Update `STATE.md` and `DECISIONS.md` before ending any work session.
- Log every error and its fix in `ERRORS.md`.
- Do not mark anything "working" in STATE.md unless it was actually run.
  Use the Verified / Unverified split.
- Agents never read other models' branches or the current stage's verdict.
- Only the human merges to a stage branch or `main`.

## Layout
- `modal/run_agent.py`: spawns Modal sandboxes that run OpenCode headless
- `history/`: prompts, results and verdicts per stage
- `history/RUBRIC.md`: how the judge ranks branches
