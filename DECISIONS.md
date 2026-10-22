# DECISIONS

## Architecture
- **Modal Sandboxes, not an always-on VM.** No exposed IP needed, pay per second.
  Sandboxes have outbound network by default, 0.34 s create, snapshots available
  (from the modal-hosting-cookbook tests).
- **Agent = OpenCode, headless (`opencode run`).** Documented by Modal for its
  endpoints, no system prompt to write. Fallback: Cline CLI (`cline -y`).
  Same agent for all five models so results compare fairly.
- **Local runtime, no Docker in Modal.** The sandbox is already the isolation.
- **GitHub is the source of truth.** Volumes/snapshots are only cache.
  Volume writes only sync on terminate; one writer per volume (last-write-wins).
- **Termux is only the remote control.** Jobs are spawned with `modal run --detach`.
- **One repo + protected `main`, no second "test" repo.** PR = approval step.
  A staging repo only if a concrete need appears.
- **Branch layout:** `stage-N/<model>-<timestamp>` per model per stage. Human
  merges the winner into a stage branch; all models restart from the winner.
- **Test sandbox is separate:** no GitHub token, no write access, throwaway.
- **Judging:** Claude via the app (no API), human has the final say.
  Rubric in `history/RUBRIC.md`. Verdicts logged in `history/stage-NN/verdict.md`.
- **Logs:** decisions and summaries in git; raw agent transcripts stay in Modal logs.

## Security
- Fine-grained GitHub token, one repo, Contents + Pull requests only, short expiry.
- The broad `gho_` gh token stays on Termux, never in a sandbox.
- Runner removes GITHUB_TOKEN from the agent's environment and avoids storing it in
  `.git/config`. This reduces but does not eliminate risk.
- Proxy token goes only to agent sandboxes, never to test sandboxes.
- Never paste tokens in chats. Clear shell history after inline use.

## Models (Modal endpoints, workspace `ayokemi`)
Base URL pattern: `https://ayokemi--ep-<slug>-server.us-west.modal.direct/v1`

| name | slug | model id (from /v1/models) |
|---|---|---|
| glm | glm-5-3 | zai-org/GLM-5.3 |
| kimi | kimi | moonshotai/Kimi-K3 |
| deepseek | deepseek-v4-1-flash | deepseek-ai/DeepSeek-V4.1-Flash |
| inkling | inkling-nvfp4 | thinkingmachines/Inkling-NVFP4 |
| muse | muse-spark-open-816b-a42b | meta-models/Muse-Spark-Open-816B-A42B |
| qwen (spare) | qwen3-8-2-4t-a95b | Qwen/Qwen3.8-2.4T-A95B |

- All six list `tools` support and ~1M context. Inkling has no JSON mode.
- All are reasoning models. Give every model the same reasoning effort.
- Modal docs also describe `https://inference.us-west.modal.direct` with the model
  set to the endpoint hostname (alternative route, used by OpenCode's built-in
  Modal provider). We use the per-endpoint URLs because those are what we tested.
- Proxy token format: `wk-<id>.ws-<secret>`, created with
  `modal workspace proxy-tokens create`.

## Commands
Create the proxy secret (paste the ws- secret at the hidden prompt):
```
read -s PS; modal secret create modal-proxy MODAL_PROXY_TOKEN_ID="wk-..." MODAL_PROXY_TOKEN_SECRET="$PS"; unset PS
```
Run one model:
```
modal run --detach modal/run_agent.py --model glm --task "Add a line to README.md"
```
Run all five on the same task and stage:
```
modal run --detach modal/run_agent.py --model all --stage 1 --task "..."
```

## Added 2026-10-22
- **Repo layout:** one shared memory+runner repo; one target repo per real project;
  keep `agent-sandbox-test` permanently as a smoke test; cookbook is reference only.
  Verdicts live in the memory repo so agents cannot read other models' results.
- **Logs:** raw run logs go to branch `agent-logs` of the target repo (token already
  reaches it, keeps model-branch diffs clean). Summaries and verdicts go here.
- **Runner hardening:** agent runs with stdin closed (`< /dev/null`) and a 30 min
  `timeout`; output is tee'd and pushed even if the agent times out.
- **Until the orchestrator exists:** start models as separate `modal run --detach`
  commands (one per model), not `--model all`.
