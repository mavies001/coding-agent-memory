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

## Log, 2026-10-23 to 24
| problem | cause | fix |
|---|---|---|
| Patch assertion "MCP_SERVERS not found" | The earlier multi-MCP patch was never applied | Apply the combined patch; patches now check their anchors |
| 401 from a probe in Termux | Pasted `wk-...` placeholder overwrote the real ID, and `read -s` can swallow the next pasted line | Run probes inside Modal with the `modal-proxy` secret |
| `gh api ... contents/runs/$f` returned 404 | `$f` was empty because the log is only pushed when the run ends | Wait for the log, or poll until it appears |
| `BrokenPipeError` from python http.server | Browser cancelled a request | Harmless |
| "Timed out waiting for final app logs" | Client exits before logs arrive | Harmless; read `modal app logs <id>` or the agent-logs branch |
| Inkling skipped the skill | Not found/loaded unprompted (1 run) | Retest; consider a skill hint in the shared preamble |

### GLM-5.3 silent failure on the ui1 prompt (3 runs, exit 0, no output, no files)
- OpenCode log: request sent, nothing returned, process ended about 59 s later. Config loaded fine.
- Direct probes (inside Modal): reasoning is always on (Modal: reasoning parser 'glm45'
  cannot be disabled; `thinking` disabled via Anthropic API -> HTTP 400; `enable_thinking:false`
  and Z.ai-style `thinking` disabled in chat were ignored).
- Default effort: ~115k chars of reasoning and no answer in 32k tokens. `reasoning_effort: low`
  is honored: answer starts after ~97k chars (353 s) but was cut by the 32k cap.
- Speed about 75 tokens/s (one 4k-token call took 529 s, unexplained).
- OpenCode clamps max_tokens to 32,000 unless OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX is set
  (GitHub issues; unverified in 1.19.4). The ~59 s early end is still unexplained.
- Fix being tested: GLM-only low effort + 200k output + env override + 45 min timeout.
- Gap: a run with exit 0 and no output/changes looks like success; needs a guard.

### GLM fix result (stage ui1d, 2026-10-24)
GLM completed the ui1 prompt: index.html + NOTES.md (888 lines), PR #26, exit 0. Settings used:
reasoningEffort low, limit.output 200000, OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX=200000, agent
timeout 2700. Several settings changed together; which one was decisive is unknown. GLM's claims
(node --check, 8/8 done) are self-reported until the page is tested.
