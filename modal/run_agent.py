"""
Remote coding-agent runner (first test). STATUS: UNTESTED, see ERRORS.md.

From Termux:
  modal run --detach modal/run_agent.py --model glm --task "Add a line to README.md"
  modal run --detach modal/run_agent.py --model all --stage 1 --task "..."

A spawned Modal Function creates a Sandbox, clones the repo, runs OpenCode
headless against one Modal endpoint, then commits, pushes a branch and opens a PR.
Results: check the PR on GitHub, or the Modal logs dashboard.

Secrets needed (Modal Secrets):
  github-agent-test -> GITHUB_TOKEN (fine-grained, one repo)
  modal-proxy       -> MODAL_PROXY_TOKEN_ID, MODAL_PROXY_TOKEN_SECRET
"""
import json
import shlex
import time

import modal

APP_NAME = "coding-agent"
WORKSPACE = "ayokemi"
app = modal.App(APP_NAME)

# name -> (endpoint slug, model id returned by /v1/models)
MODELS = {
    "glm": ("glm-5-3", "zai-org/GLM-5.3"),
    "kimi": ("kimi", "moonshotai/Kimi-K3"),
    "deepseek": ("deepseek-v4-1-flash", "deepseek-ai/DeepSeek-V4.1-Flash"),
    "inkling": ("inkling-nvfp4", "thinkingmachines/Inkling-NVFP4"),
    "muse": ("muse-spark-open-816b-a42b", "meta-models/Muse-Spark-Open-816B-A42B"),
    "qwen": ("qwen3-8-2-4t-a95b", "Qwen/Qwen3.8-2.4T-A95B"),
}
CONTESTANTS = ["glm", "kimi", "deepseek", "inkling", "muse"]

agent_image = (
    modal.Image.from_registry("node:22-slim", add_python="3.12")
    .apt_install("git", "curl", "ca-certificates")
    .run_commands("npm install -g opencode-ai")
)

AGENT_SECRETS = [
    modal.Secret.from_name("github-agent-test"),
    modal.Secret.from_name("modal-proxy"),
]

PREAMBLE = (
    "You are working in a git repository already checked out on your own branch. "
    "Complete the task below, run any tests you can, then stop. "
    "Do not run git commit or git push; the runner does that.\n\nTASK:\n"
)


def endpoint_url(slug: str) -> str:
    return f"https://{WORKSPACE}--ep-{slug}-server.us-west.modal.direct/v1"


def opencode_config(base_url: str, model_id: str, mcp: bool = False) -> dict:
    cfg = {
        "$schema": "https://opencode.ai/config.json",
        "provider": {
            "modalep": {
                "npm": "@ai-sdk/openai-compatible",
                "name": "Modal endpoint",
                "options": {"baseURL": base_url, "apiKey": "{env:MODAL_PROXY_TOKEN}"},
                "models": {model_id: {"name": model_id}},
            }
        },
        "permission": {"edit": "allow", "bash": "allow"},
    }
    if mcp:
        cfg["mcp"] = {
            "context7": {"type": "remote", "url": "https://mcp.context7.com/mcp", "enabled": True}
        }
    return cfg


def build_script(repo, branch, model, model_id, base_url, task, mcp=False) -> str:
    cfg = json.dumps(opencode_config(base_url, model_id, mcp), indent=2)
    prompt = PREAMBLE + task
    commit_msg = f"agent({model}): {task[:60]}"
    safe_branch = branch.replace("/", "_")
    pr = json.dumps(
        {
            "title": f"[{model}] {task[:60]}",
            "head": branch,
            "base": "__BASE__",
            "body": (
                f"Automated run.\n\nModel: {model} ({model_id})\n"
                f"Branch: {branch}\n\nTask:\n{task}\n"
            ),
        }
    )
    return f"""exec 2>&1
set -eu
git config --global user.name "agent-{model}"
git config --global user.email "agent-{model}@users.noreply.github.com"
AUTH="Authorization: Basic $(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64 -w0)"
mkdir -p /work && cd /work
git -c http.extraheader="$AUTH" clone https://github.com/{repo}.git repo
cd repo
BASE=$(git symbolic-ref --short refs/remotes/origin/HEAD | sed 's#origin/##')
git checkout -b {branch}
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/opencode.json <<'JSON'
{cfg}
JSON
export MODAL_PROXY_TOKEN="$MODAL_PROXY_TOKEN_ID.$MODAL_PROXY_TOKEN_SECRET"
echo "== agent start: {model} ({model_id}) mcp={mcp}"
set +e
opencode mcp list 2>&1 | head -20
timeout 1800 env -u GITHUB_TOKEN opencode run -m modalep/{model_id} {shlex.quote(prompt)} < /dev/null 2>&1 | tee /tmp/agent.log
AGENT_RC=${{PIPESTATUS[0]}}
echo "== agent exit code: $AGENT_RC (124 means timed out)"
cd /work
rm -rf logs
git -c http.extraheader="$AUTH" clone --no-checkout https://github.com/{repo}.git logs
cd logs
if git -c http.extraheader="$AUTH" fetch origin agent-logs 2>/dev/null; then
  git checkout -q -B agent-logs FETCH_HEAD
else
  git checkout -q --orphan agent-logs
  git rm -rfq . 2>/dev/null
fi
mkdir -p runs
{{ echo "model: {model} ({model_id})"; echo "branch: {branch}"; echo "agent exit code: $AGENT_RC"; echo "-----"; sed -E 's/(wk|ws)-[A-Za-z0-9._-]+/[REDACTED]/g' /tmp/agent.log | tail -n 400; }} > "runs/{safe_branch}.log"
git add runs
git commit -qm "log: {branch}"
for i in 1 2 3; do
  git -c http.extraheader="$AUTH" push -q origin agent-logs && break
  git -c http.extraheader="$AUTH" pull -q --rebase origin agent-logs
done
echo "== log pushed to branch agent-logs: runs/{safe_branch}.log"
cd /work/repo
set -e
git add -A
if git diff --cached --quiet; then echo "NO_CHANGES"; exit 0; fi
git commit -m {shlex.quote(commit_msg)}
git -c http.extraheader="$AUTH" push origin {branch}
cat > /tmp/pr.json <<'JSON'
{pr}
JSON
sed -i "s#__BASE__#$BASE#" /tmp/pr.json
curl -sS -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \\
  -H "Accept: application/vnd.github+json" \\
  https://api.github.com/repos/{repo}/pulls -d @/tmp/pr.json \\
  | grep -o '"html_url": *"https://github.com/[^"]*/pull/[0-9]*"' | head -1
echo "== done"
"""


@app.function(timeout=60 * 60 * 3)
def run_task(model: str, repo: str, task: str, stage: str, mcp: bool = False):
    slug, model_id = MODELS[model]
    branch = f"stage-{stage}/{model}-{int(time.time())}"
    script = build_script(repo, branch, model, model_id, endpoint_url(slug), task, mcp)

    sb_app = modal.App.lookup(APP_NAME + "-sandboxes", create_if_missing=True)
    sb = modal.Sandbox.create(
        app=sb_app, image=agent_image, secrets=AGENT_SECRETS, timeout=60 * 60 * 2
    )
    rc = -1
    try:
        p = sb.exec("bash", "-c", script)
        for line in p.stdout:
            print(f"[{model}] {line}", end="")
        p.wait()
        rc = p.returncode
    finally:
        sb.terminate(wait=True)
    print(f"[{model}] sandbox exit code {rc}, branch {branch}")
    return {"model": model, "branch": branch, "returncode": rc}


@app.local_entrypoint()
def main(
    model: str = "glm",
    task: str = "Append one line to README.md that says hello from the agent.",
    repo: str = "mavies001/agent-sandbox-test",
    stage: str = "test",
    mcp: bool = False,
):
    names = CONTESTANTS if model == "all" else [model]
    for name in names:
        if name not in MODELS:
            raise SystemExit(f"unknown model {name}; choose from {list(MODELS)} or 'all'")
        call = run_task.spawn(name, repo, task, stage, mcp)
        print(f"started {name}: call {call.object_id}")
    print("Jobs are running in the cloud. Check the PRs on GitHub or the Modal logs.")
