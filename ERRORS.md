# ERRORS (cause -> fix)

| date | problem | cause | fix |
|---|---|---|---|
| 2026-10-22 | GLM reply had empty `content`, `finish_reason: length` | Reasoning model spent all 50 max_tokens thinking (`reasoning_content`) | Use large max_tokens (1000+); agents must not cap output low; set reasoning effort consistently |
| 2026-10-22 | Wrong endpoint/token format assumed | Earlier guess used `inference.us-west.modal.direct` and `ID.SECRET` | Use own endpoint URLs and `Authorization: Bearer wk-<id>.ws-<secret>` |

## Likely first-run failures in modal/run_agent.py (untested)
- `opencode: command not found`: npm global bin not on PATH in the image
- Config invalid: remove the `permission` block from the generated opencode.json
- Model not found: `-m modalep/<id>` may not parse ids containing `/`; try the Modal built-in provider
- Agent hangs waiting for approval: permissions not auto-allowed in headless mode
- `Secret not found`: create `modal-proxy` first
- Sandbox create fails inside the function: pass the app differently (see Modal sandbox docs)

## Log, 2026-10-22 session
| problem | cause | fix |
|---|---|---|
| First GLM run stalled after "agent start", no output | Most likely stdin held open and OpenCode waiting (not proven) | `< /dev/null` plus `timeout 1800`; later runs completed |
| `modal run --detach` note: only the last triggered function stays alive | Modal behavior for local entrypoints | Run models as separate commands; build an orchestrator function |
| `modal-proxy` secret created with an empty secret | Pressed Enter at the hidden prompt without pasting | Recreate with `--force`, paste the ws- secret |
| "Timed out waiting for final app logs" at the end of a run | Client closes before logs arrive | Harmless; read logs with `modal app logs <app id>` or the agent-logs branch |
