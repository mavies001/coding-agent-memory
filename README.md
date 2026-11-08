# coding-agent-memory

Runner and memory for a multi-model remote coding setup. Five open models get the same
prompt for a "stage", each builds it on its own GitHub branch and PR, a judge ranks the
results, and a human approves the best one. Everything runs in the cloud (Modal), so the
phone or PC can be off. This repo is also the memory: any new chat or agent continues from here.

## Start here
Read in this order: `AGENTS.md`, `STATE.md`, `DECISIONS.md`, `ERRORS.md`, `history/INDEX.md`.
Open `history/stage-<name>/` only when you need detail on one stage.

- `STATE.md` says what works, what is unverified, and the next steps. It is the source of
  truth for status. This README only explains how to do things.
- Values that change (timeouts, per-model settings) are not repeated here. Read them from the
  code with the `grep` commands shown below.

## How a run works
1. From Termux: `modal run --detach modal/run_agent.py ...` starts a Modal function and returns.
2. The function creates a Sandbox (Node image with OpenCode installed) and clones the target repo.
3. OpenCode runs headless against one model's Modal endpoint, with its stdin closed and a timeout.
   The GitHub token is removed from the agent's environment. The agent edits files but does not commit.
4. The runner commits, pushes branch `stage-<stage>/<model>-<timestamp>`, and opens a PR.
5. A log is pushed to branch `agent-logs` of the target repo as `runs/<branch with / as _>.log`.
   Modal tokens in the log are redacted; other secrets are not, so read it before sharing.
6. A log file on `agent-logs` means the run has ended. It does not mean it succeeded.

## Repo layout
| path | purpose |
|---|---|
| `AGENTS.md` | reading order and rules for any agent |
| `STATE.md`, `DECISIONS.md`, `ERRORS.md` | current status, decisions with reasons, errors with fixes |
| `history/INDEX.md` | one line per stage |
| `history/RUBRIC.md`, `history/VERDICT_TEMPLATE.md` | how judges rank, verdict format |
| `history/stage-<name>/` | `prompt.md`, `results.md`, `verdict.md` for a stage (as they exist) |
| `modal/run_agent.py` | the runner |
| `modal/glm_probe.py` | diagnostic: calls the GLM endpoint from inside Modal using the stored secret |
| `tools/view_results.sh` | downloads each model's newest branch, builds an index page, serves it on localhost |

## Runner reference
~~~
modal run --detach modal/run_agent.py --model <name> --task "<text>" [--repo <owner/repo>] [--stage <name>] [--mcp <list>] [--skills]
~~~
| flag | meaning |
|---|---|
| `--model` | `glm`, `kimi`, `deepseek`, `inkling`, `muse`, `qwen` (spare), or `all` |
| `--task` | the task text; the runner adds a short preamble in front of it |
| `--repo` | target repo, default is set in the `main` function |
| `--stage` | label used in the branch name (`stage-<stage>/...`) |
| `--mcp` | comma-separated MCP servers: `inspo`, `context7`, `thinking` (off by default) |
| `--skills` | install the test skill into the sandbox (off by default) |

Check the real defaults and settings in your copy:
~~~
grep -n "def main" -A 8 modal/run_agent.py
grep -n "timeout" modal/run_agent.py
grep -n "MODEL_EXTRA\|OUTPUT_TOKEN_MAX" modal/run_agent.py
~~~
Do not use `--model all` for real runs: Modal keeps only the last spawned function alive after
you disconnect. Start each model as its own command (loop shown below).

## Models and endpoints
Endpoint pattern: `https://ayokemi--ep-<slug>-server.us-west.modal.direct/v1`

| name | slug | model id |
|---|---|---|
| glm | glm-5-3 | zai-org/GLM-5.3 |
| kimi | kimi | moonshotai/Kimi-K3 |
| deepseek | deepseek-v4-1-flash | deepseek-ai/DeepSeek-V4.1-Flash |
| inkling | inkling-nvfp4 | thinkingmachines/Inkling-NVFP4 |
| muse | muse-spark-open-816b-a42b | meta-models/Muse-Spark-Open-816B-A42B |
| qwen (spare) | qwen3-8-2-4t-a95b | Qwen/Qwen3.8-2.4T-A95B |

All are reasoning models. GLM-5.3 needs special settings (low reasoning effort, large output
budget) to finish big prompts; see `DECISIONS.md` and `MODEL_EXTRA` in the runner. Reasoning on
GLM cannot be turned off, only lowered. OpenCode caps output at 32,000 tokens per request unless
`OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX` is set.

## One-time setup (human, in Termux)
Prerequisites: `gh auth status` shows you logged in, `modal profile current` prints the workspace,
and this repo is cloned at `~/coding-agent-repo`.

Placeholders look like `<THIS>`: replace the whole thing including the angle brackets. Never
type a literal `wk-...` or paste real tokens into a chat or into this repo.

**1. Target repo** (where the agents work; needs a `main` branch with a README):
~~~
gh repo create <OWNER>/<REPO> --private --add-readme
~~~

**2. Repo-scoped GitHub token.** GitHub, Settings, Developer settings, Personal access tokens,
Fine-grained. Only the target repo. Permissions: Contents (read and write) and Pull requests
(read and write), nothing else. Short expiry. Store it (paste at the hidden prompt, then Enter):
~~~
read -s GH_FINE
modal secret create github-agent-test GITHUB_TOKEN="$GH_FINE" --force
unset GH_FINE
~~~
The runner always reads the secret named `github-agent-test`, so a different target repo needs a
token for that repo stored under this name. Check scope (expect your repo's name, then a 404 for another repo):
~~~
read -s T
curl -s -H "Authorization: Bearer $T" https://api.github.com/repos/<OWNER>/<REPO> | grep -E '"full_name"|"private"'
curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $T" https://api.github.com/repos/<OWNER>/<OTHER_REPO>
unset T
~~~

**3. Modal endpoint token.** Create it, then store the ID (starts `wk-`) and secret (starts `ws-`).
Run the `read` lines one at a time, because pasting several lines can make `read -s` swallow the next one:
~~~
modal workspace proxy-tokens create
read -p "Token ID: " PID
read -s PS
modal secret create modal-proxy MODAL_PROXY_TOKEN_ID="$PID" MODAL_PROXY_TOKEN_SECRET="$PS" --force
unset PID PS
~~~
Check: `modal secret list` shows `github-agent-test` and `modal-proxy`. Only these two are attached to
agent sandboxes. Other secrets in the workspace must stay unattached.

## Smoke test (one model, trivial task)
~~~
cd ~/coding-agent-repo
modal run --detach modal/run_agent.py --model glm --repo <OWNER>/<REPO> --stage test --task "Append one line to README.md that says hello from the agent."
~~~
Expected within minutes: a PR titled `[glm] ...`, a branch `stage-test/glm-<timestamp>`, and a log
on `agent-logs`. If all three appear, the whole chain works.

## Run a stage (same prompt, all five models)
1. Write `history/stage-<name>/prompt.md`: a concrete product, numbered requirements that can be
   checked on a phone, constraints (single file, no network, works at 390px wide), an instruction to
   run `node --check` on its JavaScript, and a required `NOTES.md` listing each requirement as done,
   partial or skipped plus known bugs. Do not mention tools or skills unless the stage tests them.
2. Commit and push the prompt. Note your Modal credit before and after.
3. Start each model:
~~~
cd ~/coding-agent-repo
for m in glm kimi deepseek inkling muse; do
  modal run --detach modal/run_agent.py --model $m --repo <OWNER>/<REPO> --stage <name> --task "$(cat history/stage-<name>/prompt.md)"
done
~~~
Add `--mcp` or `--skills` only when the stage tests them, and give every model the same flags.

## Check progress and results
List finished runs and read each exit code (line 3 of each log):
~~~
for f in $(gh api "repos/<OWNER>/<REPO>/contents/runs?ref=agent-logs" --jq '.[].name' | grep stage-<name>); do
  echo "$f: $(gh api "repos/<OWNER>/<REPO>/contents/runs/$f?ref=agent-logs" --jq .content | base64 -d | sed -n '3p')"
done
gh pr list -R <OWNER>/<REPO> --state open
modal app list
~~~
- Exit code 0 is a normal end and 124 is the agent timeout. Exit 0 does not prove it worked: a log
  with no tool output and `NO_CHANGES` means the model produced nothing.
- `modal app list` should show no leftover `coding-agent` tasks once everything has finished.
- A job still running after about an hour is suspect; check the Modal dashboard.

## View and judge
~~~
bash ~/coding-agent-repo/tools/view_results.sh <name> 8000
~~~
Open `http://localhost:8000/` on the phone, test each page by hand, and compare it with its own
`NOTES.md`. Use `<stage1>,<stage2>` to combine a rerun with an earlier stage (newest branch per model wins).
Rank with `history/RUBRIC.md`. Then write `history/stage-<name>/verdict.md`, add a line to
`history/INDEX.md`, update `STATE.md`, and push:
~~~
git add -A && git commit -m "Stage <name> verdict" && git push
~~~
Before pushing, scan for secrets:
~~~
grep -rnE "github_pat_[A-Za-z0-9_]{20}|gho_[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20}|ws-[A-Za-z0-9]{10,}" . --include="*.md" --include="*.py" --include="*.sh" || echo clean
~~~

## MCP and skills
- MCP gives the agent tools. Skills give it written instructions. Both are off unless you pass the flag.
- Give every model the same MCP and skills in a comparison; shared tools also make outputs converge.
- `inspo` (UI references) and `context7` (library docs) are remote servers that need no login and
  receive the agent's queries. `thinking` is a local server installed in the image.
- Do not add write-capable MCP servers such as GitHub MCP: they need a token the agent could use.

## Security rules
- Tokens live only in Modal Secrets. Never in this repo, logs, prompts or chats.
- The agent token is fine-grained, one repo, short expiry. It has no Workflows permission, so agents
  cannot push CI files.
- The broad `gho_` login used by `gh` stays on Termux only.
- Only the human merges. Test PRs are closed, not merged: `gh pr close <NUMBER> -R <OWNER>/<REPO>`.

## Troubleshooting
| symptom | cause | fix |
|---|---|---|
| patch fails with "not found exactly once" | an earlier patch was never applied | apply earlier patches first; compare with `grep` on the names it mentions |
| 401 from an endpoint | a placeholder or half-pasted secret was used | store the token with `modal-proxy` and probe from inside Modal |
| `gh api .../runs/$f` gives 404 | the run has not finished, so there is no log yet | wait, or poll until the log name appears |
| run ends with exit 0, no files, `NO_CHANGES` | model returned nothing (seen with GLM on a big prompt) | read the log after `--- opencode logs`; check reasoning settings and output limits |
| "Timed out waiting for final app logs" | client exited before Modal finished sending logs | harmless; read `modal app logs <id>` or the `agent-logs` branch |
| `BrokenPipeError` from `python -m http.server` | browser cancelled a request | harmless |
| `modal secret create` says it exists | secret already created | add `--force` |
| viewer port in use | an old server is running | Ctrl+C it or pass another port |

## Not built yet
A reliable "run all five" orchestrator, a test sandbox that runs the same tests on every branch,
and automated tests on the target repo (for example a GitHub Actions workflow that the human adds
to `main`). `STATE.md` lists what is unverified.

## Rules for an AI agent working with this repo
- You cannot run commands on the human's accounts. Write the commands, ask the human to run them,
  and ask for the output.
- Never ask for tokens or secrets. Never put them in files.
- Do not mark anything verified unless the human ran it. Keep Verified and Unverified separate in `STATE.md`.
- Log decisions in `DECISIONS.md` and errors in `ERRORS.md` before ending a session.
