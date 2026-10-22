# STATE (last updated 2026-10-22)

## Goal
Run a coding agent in the cloud while the PC/phone is off. Five open models
each write code for a stage on their own branch; a judge ranks them, the human
approves the best, and the winner becomes the base for the next stage.

## Accounts
- Modal workspace: `ayokemi`
- GitHub account: `mavies001` (gh logged in on Termux; token is broad, keep it on the phone only)
- Control device: Termux on Android (Modal client already set up)

## Verified (actually run)
- `modal profile current` -> ayokemi
- Modal Secret `github-agent-test` exists (key GITHUB_TOKEN, fine-grained, one repo)
- Proxy token works with `Authorization: Bearer wk-<id>.ws-<secret>`
- `/v1/models` answers on all 6 endpoints (see DECISIONS.md for IDs)
- GLM chat completion works: 4.5 s, needs a large max_tokens (reasoning model)

## Unverified (do not assume)
- Chat completions on kimi, deepseek, inkling, muse, qwen
- Secret `modal-proxy` (MODAL_PROXY_TOKEN_ID / _SECRET): created? run `modal secret list`
- Test repo `mavies001/agent-sandbox-test` exists and the token can reach only it
- `modal/run_agent.py` has never been run
- OpenCode install via npm, custom provider config, `-m provider/model-with-slash`,
  headless permissions, and whether it commits/behaves with these models
- Whether a spawned job survives closing Termux (`modal run --detach`)
- Cold-start behavior and credit burn with 5 agents at once

## Next steps
1. `modal secret create modal-proxy ...` (see DECISIONS.md)
2. Create the throwaway repo and confirm token scope
3. `modal run --detach modal/run_agent.py --model glm --task "..."`
4. Fix whatever breaks, log it in ERRORS.md
5. Only then `--model all` for a real stage
