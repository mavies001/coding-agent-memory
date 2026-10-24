#!/data/data/com.termux/files/usr/bin/bash
# usage: view_results.sh [stage[,stage2]] [port]
set -u
STAGE="${1:-ui1}"
PORT="${2:-8000}"
REPO="mavies001/agent-sandbox-test"
PAT=$(echo "$STAGE" | tr ',' '|')
ROOT="$HOME/results/$(echo "$STAGE" | tr ',' '_')"
mkdir -p "$ROOT"

echo "Finding branches for stage(s): $STAGE"
BRANCHES=$(gh api "repos/$REPO/branches" --paginate --jq '.[].name' | grep -E "^stage-($PAT)/" || true)
if [ -z "$BRANCHES" ]; then
  echo "No branches found for $STAGE"
  exit 1
fi

for m in glm kimi deepseek inkling muse qwen; do
  b=$(echo "$BRANCHES" | grep -E "^stage-($PAT)/$m-" | awk -F- '{print $NF, $0}' | sort -n | tail -1 | cut -d' ' -f2)
  [ -z "$b" ] && continue
  d="$ROOT/$m"
  if [ -f "$d/.branch" ] && [ "$(cat "$d/.branch")" = "$b" ]; then
    echo "$m: up to date ($b)"
  else
    rm -rf "$d"
    if gh repo clone "$REPO" "$d" -- --branch "$b" --single-branch -q; then
      echo "$b" > "$d/.branch"
      echo "$m: cloned $b"
    else
      echo "$m: clone failed"
    fi
  fi
done

python3 - "$ROOT" <<'PY'
import sys, os, html
root = sys.argv[1]
rows = []
for m in ["glm", "kimi", "deepseek", "inkling", "muse", "qwen"]:
    d = os.path.join(root, m)
    if not os.path.isdir(d):
        if m != "qwen":
            rows.append("<section><h2>%s</h2><p class='miss'>No result found.</p></section>" % m)
        continue
    bp = os.path.join(d, ".branch")
    branch = open(bp).read().strip() if os.path.exists(bp) else ""
    if os.path.exists(os.path.join(d, "index.html")):
        link = "<a class='btn' href='%s/'>Open page</a>" % m
    else:
        link = "<p class='miss'>No index.html in this branch.</p>"
    notes = ""
    np_ = os.path.join(d, "NOTES.md")
    if os.path.exists(np_):
        txt = open(np_, errors="replace").read()[:4000]
        notes = "<details><summary>NOTES.md (what the model claims)</summary><pre>%s</pre></details>" % html.escape(txt)
    rows.append("<section><h2>%s</h2><small>%s</small>%s%s</section>" % (m, html.escape(branch), link, notes))
page = """<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Results</title>
<style>body{font:16px system-ui;margin:0;padding:16px;background:#111;color:#eee}
section{border:1px solid #333;border-radius:12px;padding:12px;margin:0 0 12px}
h2{margin:0 0 4px}small{color:#888;display:block;margin-bottom:8px}
.btn{display:inline-block;background:#6c5;color:#111;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600}
.miss{color:#e66}pre{white-space:pre-wrap;font-size:13px}details{margin-top:10px}</style>
<h1>Results</h1>""" + "".join(rows)
open(os.path.join(root, "index.html"), "w").write(page)
print("index written")
PY

echo "Open http://localhost:$PORT/ in your browser. Ctrl+C to stop."
cd "$ROOT" && python3 -m http.server "$PORT" --bind 127.0.0.1
