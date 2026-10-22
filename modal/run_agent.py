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


def opencode_config(base_url: str, model_id: str) -> dict:
    return {
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


def build_script(repo, branch, model, model_id, base_url, task) -> str:
    cfg = json.dumps(opencode_config(base_url, model_id), indent=2)
    prompt = PREAMBLE + task
    commit_msg = f"agent({model}): {task[:60]}"
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
echo "== agent start: {model} ({model_id})"
set +e
env -u GITHUB_TOKEN opencode run -m modalep/{model_id} {shlex.quote(prompt)}
AGENT_RC=$?
set -e
echo "== agent exit code: $AGENT_RC"
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
def run_task(model: str, repo: str, task: str, stage: str):
    slug, model_id = MODELS[model]
    branch = f"stage-{stage}/{model}-{int(time.time())}"
    script = build_script(repo, branch, model, model_id, endpoint_url(slug), task)

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
):
    names = CONTESTANTS if model == "all" else [model]
    for name in names:
        if name not in MODELS:
            raise SystemExit(f"unknown model {name}; choose from {list(MODELS)} or 'all'")
        call = run_task.spawn(name, repo, task, stage)
        print(f"started {name}: call {call.object_id}")
    print("Jobs are running in the cloud. Check the PRs on GitHub or the Modal logs.")
