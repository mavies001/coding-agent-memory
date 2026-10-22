# STATE (last updated 2026-10-22)

## Goal
Run a coding agent in the cloud while the PC/phone is off. Five open models each
write code for a stage on their own branch; a judge ranks them, the human approves
the best, and the winner becomes the base for the next stage.

## Accounts and repos
- Modal workspace `ayokemi`; GitHub `mavies001`; control device: Termux on Android
- `coding-agent-memory`: this repo (runner + memory), private
- `agent-sandbox-test`: throwaway smoke-test target, private
- `modal-hosting-cookbook`: earlier Modal experiments, reference only
- Modal Secrets: `github-agent-test` (GITHUB_TOKEN, fine-grained, test repo only),
  `modal-proxy` (MODAL_PROXY_TOKEN_ID / _SECRET)

## Verified (actually run)
- All 6 Modal endpoints answer /v1/models; GLM chat completion works
- Runner end to end for glm, kimi, deepseek, inkling, muse: sandbox clones the
  repo, OpenCode edits README.md headless, runner commits, pushes
  `stage-test/<model>-<ts>` and opens a PR (#1-#5 on agent-sandbox-test)
- OpenCode custom provider `modalep` works with `-m modalep/<model id>` (ids with
  a slash are fine); edit/bash permissions allow, no approval prompts
- Raw logs are pushed to branch `agent-logs`, file `runs/<branch>.log`, redacted

## Unverified (do not assume)
- Whether a detached job survives closing Termux (not deliberately tested)
- `--model all`: Modal keeps only the last spawned function alive when the
  client disconnects, so it is unreliable until an orchestrator function exists
- qwen (spare) never run through the runner
- Behavior of the five models on real, multi-file tasks; cost of 5 parallel runs
- Test sandbox (runs tests on every branch) does not exist yet
- Branch protection on private repos may need a paid GitHub plan
- Real project repo not chosen yet

## Next steps
1. Build an orchestrator so `--model all` is reliable after detach
2. Add the test sandbox (no GitHub token, no write access)
3. Pick a real target repo, extend/make a fine-grained token for it
4. Run stage 1, paste summaries to the judge, log the verdict in history/
