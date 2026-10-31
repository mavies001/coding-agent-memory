"""
Hub runner: a Modal Volume ("agent-hub") replaces GitHub. STATUS: UNTESTED.

  modal run --detach modal/run_hub.py --model glm --stage ui2 --task "$(cat history/stage-ui2/prompt.md)"
  modal run --detach modal/run_hub.py --model all --stage ui2 --task "..."
  modal run modal/run_hub.py::promote --bundle runs/ui2/glm-123.bundle
"""
import base64, json, os, re, shlex, subprocess, tempfile, time
import modal

APP_NAME = "coding-agent-hub"
WORKSPACE = "ayokemi"
HUB = "/hub"
app = modal.App(APP_NAME)
hub = modal.Volume.from_name("agent-hub", create_if_missing=True)

ctrl_image = modal.Image.debian_slim(python_version="3.12").apt_install("git")
agent_image = (
    modal.Image.from_registry("node:22-slim", add_python="3.12")
    .apt_install("git", "curl", "ca-certificates")
    .run_commands("npm install -g opencode-ai @modelcontextprotocol/server-sequential-thinking")
)

MODELS = {
    "glm": ("glm-5-3", "zai-org/GLM-5.3"),
    "kimi": ("kimi", "moonshotai/Kimi-K3"),
    "deepseek": ("deepseek-v4-1-flash", "deepseek-ai/DeepSeek-V4.1-Flash"),
    "inkling": ("inkling-nvfp4", "thinkingmachines/Inkling-NVFP4"),
    "muse": ("muse-spark-open-816b-a42b", "meta-models/Muse-Spark-Open-816B-A42B"),
    "qwen": ("qwen3-8-2-4t-a95b", "Qwen/Qwen3.8-2.4T-A95B"),
}
CONTESTANTS = ["glm", "kimi", "deepseek", "inkling", "muse"]
MODEL_EXTRA = {
    "zai-org/GLM-5.3": {"limit": {"context": 1048576, "output": 200000},
                        "options": {"reasoningEffort": "low"}},
}
MCP_SERVERS = {
    "inspo": {"type": "remote", "url": "https://inspomcp.dev/api/mcp", "enabled": True},
    "context7": {"type": "remote", "url": "https://mcp.context7.com/mcp", "enabled": True},
    "thinking": {"type": "local", "enabled": True,
                 "command": ["npx", "-y", "@modelcontextprotocol/server-sequential-thinking"]},
}
PREAMBLE = (
    "You are working in a git repository already checked out on your own branch. "
    "Complete the task below, run any tests you can, then stop. "
    "Do not run git commit or git push; the runner does that.\n\nTASK:\n"
)
AGENT_TIMEOUT = 2700
GIT_ID = ["-c", "user.name=hub", "-c", "user.email=hub@example.invalid"]


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True)


def endpoint_url(slug):
    return f"https://{WORKSPACE}--ep-{slug}-server.us-west.modal.direct/v1"


def opencode_config(base_url, model_id, mcp=""):
    cfg = {
        "$schema": "https://opencode.ai/config.json",
        "provider": {"modalep": {
            "npm": "@ai-sdk/openai-compatible", "name": "Modal endpoint",
            "options": {"baseURL": base_url, "apiKey": "{env:MODAL_PROXY_TOKEN}"},
            "models": {model_id: {"name": model_id, **MODEL_EXTRA.get(model_id, {})}},
        }},
        "permission": {"edit": "allow", "bash": "allow"},
    }
    if mcp:
        cfg["mcp"] = {n: MCP_SERVERS[n] for n in mcp.split(",") if n}
    return cfg


SCRIPT = r"""exec 2>&1
set -eu
git config --global user.name "agent-@@MODEL@@"
git config --global user.email "agent-@@MODEL@@@example.invalid"
cd /work
git clone -q base.bundle repo
cd repo
git checkout -q -b @@BRANCH@@
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/opencode.json <<'JSON'
@@CFG@@
JSON
export MODAL_PROXY_TOKEN="$MODAL_PROXY_TOKEN_ID.$MODAL_PROXY_TOKEN_SECRET"
@@TOKEN_ENV@@echo "== agent start: @@MODEL@@ (@@MODEL_ID@@) mcp=@@MCP@@"
set +e
ATTEMPT=0
while [ $ATTEMPT -lt 2 ]; do
  ATTEMPT=$((ATTEMPT+1))
  timeout @@TIMEOUT@@ opencode run -m modalep/@@MODEL_ID@@ @@PROMPT@@ < /dev/null 2>&1 | tee -a /tmp/agent.log
  RC=${PIPESTATUS[0]}
  CHANGED=$(git status --porcelain | wc -l)
  if [ "$RC" != 0 ] || [ "$CHANGED" != 0 ]; then break; fi
  echo "== attempt $ATTEMPT: exit 0 and no changes, retrying"
done
echo "== agent exit code: $RC (124 means timed out)"
{ echo "--- opencode logs"; tail -n 200 ~/.local/share/opencode/log/*.log 2>/dev/null; } >> /tmp/agent.log
git add -A
RESULT=OK
if git diff --cached --quiet; then
  RESULT=NO_CHANGES
else
  git commit -qm "agent(@@MODEL@@): stage @@STAGE@@"
  git bundle create /work/out.bundle HEAD refs/heads/@@BRANCH@@ 2>&1
fi
if [ "$RC" != 0 ]; then RESULT=FAILED; fi
echo "== result: $RESULT attempts=$ATTEMPT rc=$RC"
"""


def build_script(branch, model, model_id, base_url, task, stage, mcp=""):
    cfg = json.dumps(opencode_config(base_url, model_id, mcp), indent=2)
    token_env = ("export OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX=200000\n"
                 if model_id in MODEL_EXTRA else "")
    subs = {"MODEL": model, "MODEL_ID": model_id, "BRANCH": branch, "CFG": cfg,
            "TOKEN_ENV": token_env, "MCP": mcp, "STAGE": stage,
            "TIMEOUT": str(AGENT_TIMEOUT), "PROMPT": shlex.quote(PREAMBLE + task)}
    out = SCRIPT
    for k, v in subs.items():
        out = out.replace(f"@@{k}@@", v)
    return out


@app.function(image=ctrl_image, volumes={HUB: hub})
def ensure_repo(project: str):
    hub.reload()
    repo = f"{HUB}/repos/{project}.git"
    if os.path.isdir(repo):
        return repo
    os.makedirs(repo)
    git("init", "--bare", "-b", "main", repo)
    with tempfile.TemporaryDirectory() as t:
        git("init", "-b", "main", t)
        open(f"{t}/README.md", "w").write(f"# {project}\n")
        git("-C", t, "add", "-A")
        git(*GIT_ID, "-C", t, "commit", "-qm", "seed")
        git("-C", t, "push", "-q", repo, "main")
    hub.commit()
    return repo


def _read_b64(sb, path):
    p = sb.exec("bash", "-c", f"base64 -w0 {path} 2>/dev/null")
    out = p.stdout.read()
    p.wait()
    return base64.b64decode(out) if out else b""


@app.function(image=ctrl_image, volumes={HUB: hub}, timeout=60 * 60 * 3)
def run_task(model: str, project: str, task: str, stage: str, mcp: str = ""):
    hub.reload()
    slug, model_id = MODELS[model]
    ts = int(time.time())
    stem, branch = f"{model}-{ts}", f"stage-{stage}/{model}-{ts}"
    repo = f"{HUB}/repos/{project}.git"
    with tempfile.TemporaryDirectory() as t:
        git("-C", repo, "bundle", "create", f"{t}/base.bundle", "--all")
        base = open(f"{t}/base.bundle", "rb").read()

    sb_app = modal.App.lookup(APP_NAME + "-sandboxes", create_if_missing=True)
    sb = modal.Sandbox.create(app=sb_app, image=agent_image, timeout=60 * 60 * 2,
                              secrets=[modal.Secret.from_name("modal-proxy")])
    lines, result, rc = [], "FAILED", -1
    out_bundle = b""
    try:
        up = sb.exec("bash", "-c", "mkdir -p /work && base64 -d > /work/base.bundle")
        up.stdin.write(base64.b64encode(base))
        up.stdin.write_eof()
        up.stdin.drain()
        up.wait()
        p = sb.exec("bash", "-c", build_script(branch, model, model_id,
                                               endpoint_url(slug), task, stage, mcp))
        for line in p.stdout:
            lines.append(line)
            print(f"[{model}] {line}", end="")
        p.wait()
        rc = p.returncode
        out_bundle = _read_b64(sb, "/work/out.bundle")
        log_tail = _read_b64(sb, "/tmp/agent.log").decode("utf-8", "replace")
        lines.append("\n--- agent.log tail\n" + "\n".join(log_tail.splitlines()[-300:]))
    finally:
        sb.terminate(wait=True)

    for l in lines:
        m = re.match(r"== result: (\S+)", l)
        if m:
            result = m.group(1)
    if result == "OK" and not out_bundle:
        result = "NO_BUNDLE"
    d = f"{HUB}/runs/{stage}"
    os.makedirs(d, exist_ok=True)
    if out_bundle:
        open(f"{d}/{stem}.bundle", "wb").write(out_bundle)
    safe = re.sub(r"(wk|ws)-[A-Za-z0-9._-]+", "[REDACTED]", "".join(lines))
    log = (f"model: {model} ({model_id})\nbranch: {branch}\nsandbox rc: {rc}\n"
           f"result: {result}\n-----\n" + "\n".join(safe.splitlines()[-500:]) + "\n")
    meta = {"model": model, "branch": branch, "result": result, "bundle": bool(out_bundle)}
    open(f"{d}/{stem}.json", "w").write(json.dumps(meta))
    open(f"{d}/{stem}.log", "w").write(log)
    hub.commit()
    print(f"[{model}] {result}, runs/{stage}/{stem}")
    return meta


@app.function(timeout=60 * 60 * 3)
def run_all(project: str, task: str, stage: str, mcp: str = ""):
    calls = [run_task.spawn(n, project, task, stage, mcp) for n in CONTESTANTS]
    return [c.get() for c in calls]


@app.function(image=ctrl_image, volumes={HUB: hub})
def promote_fn(project: str, bundle: str, to: str = "main"):
    hub.reload()
    repo = f"{HUB}/repos/{project}.git"
    git("-C", repo, "fetch", f"{HUB}/{bundle}", f"HEAD:refs/heads/{to}")
    hub.commit()
    return f"{to} now at {git('-C', repo, 'rev-parse', '--short', to).stdout.strip()}"


@app.local_entrypoint()
def promote(bundle: str, project: str = "sandbox-test", to: str = "main"):
    print(promote_fn.remote(project, bundle, to))


@app.local_entrypoint()
def main(model: str = "glm", task: str = "Append one line to README.md that says hello.",
         project: str = "sandbox-test", stage: str = "test", mcp: str = ""):
    for n in mcp.split(","):
        if n and n not in MCP_SERVERS:
            raise SystemExit(f"unknown mcp {n}; choose from {list(MCP_SERVERS)}")
    if model != "all" and model not in MODELS:
        raise SystemExit(f"unknown model {model}; choose from {list(MODELS)} or 'all'")
    ensure_repo.remote(project)
    if model == "all":
        run_all.spawn(project, task, stage, mcp)
        print("started orchestrator for all five")
    else:
        call = run_task.spawn(model, project, task, stage, mcp)
        print(f"started {model}: call {call.object_id}")
