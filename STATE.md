# STATE (last updated 2026-10-24)

## Goal
Cloud coding agents that keep working while phone/PC are off. Five open models
(GLM-5.3, Kimi K3, DeepSeek V4.1 Flash, Inkling, Muse Spark Open; Qwen3.8 as spare) get
the same prompt per stage and each pushes its own branch + PR. A judge (Claude in the app,
human has final say) ranks them; the winner becomes the base for the next stage.

## Accounts, repos, secrets
- Modal workspace `ayokemi`; GitHub `mavies001`; control device: Termux on Android
- Repos: `coding-agent-memory` (this repo), `agent-sandbox-test` (throwaway target: PRs and
  the `agent-logs` branch), `modal-hosting-cookbook` (reference only)
- Modal Secrets used by agents: `github-agent-test` (GITHUB_TOKEN, fine-grained, test repo
  only) and `modal-proxy` (MODAL_PROXY_TOKEN_ID / _SECRET). huggingface, gcp and
  glm-proxy-token secrets exist in the workspace and are NOT attached to agents.

## How a run works
`modal run --detach` -> Modal function -> Sandbox (node:22 + opencode-ai) -> clone target
repo -> `opencode run` (stdin closed, timeout, GITHUB_TOKEN removed from agent env) -> runner
commits, pushes `stage-<stage>/<model>-<ts>`, opens a PR -> redacted log pushed to branch
`agent-logs` (runs/<branch>.log). A log file on GitHub means the run has finished.
Flags: --model glm|kimi|deepseek|inkling|muse|qwen|all, --stage, --task, --repo,
--mcp inspo,context7,thinking, --skills.
Viewer: `bash tools/view_results.sh <stage[,stage2]> [port]` then open localhost.

## Verified (actually run)
- Modal and GitHub auth, both secrets, all 6 endpoints answer /v1/models
- Runner end to end on all five models (smoke stage `test`, PRs #1-#5)
- A ~200 s job completes in a sandbox; detached start returns immediately
- OpenCode 1.19.4 headless: custom provider `modalep`, model ids with `/`, no approval prompts
- Context7 MCP used by all five; Inspo MCP connects and is called (`opencode mcp list` status
  appears at the top of each log)
- Skills: glm, kimi, deepseek, muse loaded the test skill unprompted; inkling did not (1 run)
- Results viewer served five pages in the phone browser

## Unverified / open
- Survival with Termux fully closed (never deliberately tested)
- Local `thinking` MCP and the stage `mcp2` results (started, never reviewed)
- Qwen through the runner; whether Inkling's skill miss repeats; whether the preamble
  skill-hint patch was applied
- `--model all` after disconnect (detached Modal keeps only the last spawned function alive)
- Whether OpenCode passes GLM's reasoningEffort/limit settings, and the effect of
  OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX in v1.19.4
- Credit cost per stage; rate limits at 5 parallel (none seen with Context7/Inspo)
- GitHub branch protection on private repos may need a paid plan; real project repo not chosen

## Stage status
| stage | task | result |
|---|---|---|
| test | append a README line | 5/5 PRs |
| survive | two `sleep 100` then edit | GLM ok, exit 0 |
| mcp | Context7 then write NOTES.md | 5/5 called the tools and wrote the file |
| skills | notes-format skill | 4/5 loaded it; inkling did not |
| inspo | coffee roaster page with Inspo | human: glm, kimi, deepseek nice; muse, inkling subpar |
| ui1 | "Signal Garden" hard UI, no MCP | PRs from kimi, muse, deepseek, inkling; GLM none (silent failure x3: ui1, ui1b, ui1c); page checks not yet reported; verdict pending |
| mcp2 | context7 + thinking + skills, Flask plan | started, not reviewed |

## Next steps
1. Rerun GLM on ui1 with the patched settings (stage ui1d) and read its log
2. Review the four ui1 pages (sound, visualizer, draggable panels, themes, phone fit, NOTES.md claims) and log the verdict
3. Runner guard: flag a run that exits 0 with no output and no changes
4. Orchestrator so `--model all` survives disconnect
5. Test sandbox (no GitHub token) that runs the same tests on every branch
6. Pick the real project repo and a fine-grained token for it
7. Move skills into files in this repo; write a stage-prompt template
