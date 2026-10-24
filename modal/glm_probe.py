import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import modal

app = modal.App("glm-probe")
BASE = "https://ayokemi--ep-glm-5-3-server.us-west.modal.direct"


def run_chat(label, extra, prompt, tok, max_tokens=32000):
    body = {
        "model": "zai-org/GLM-5.3",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "stream": True,
    }
    body.update(extra)
    req = urllib.request.Request(
        BASE + "/v1/chat/completions",
        json.dumps(body).encode(),
        {"Authorization": "Bearer " + tok, "Content-Type": "application/json"},
    )
    t0 = time.time()
    chunks = content = reasoning = 0
    first_r = ""
    last_r = ""
    first_content_at = None
    reasoning_before = None
    finish = None
    done = False
    try:
        resp = urllib.request.urlopen(req, timeout=900)
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                done = True
                break
            try:
                j = json.loads(data)
            except Exception:
                continue
            chunks += 1
            for ch in j.get("choices", []):
                d = ch.get("delta") or {}
                c = d.get("content") or ""
                r = d.get("reasoning_content") or d.get("reasoning") or ""
                if r:
                    if len(first_r) < 500:
                        first_r += r
                    last_r = (last_r + r)[-500:]
                reasoning += len(r)
                if c and first_content_at is None:
                    first_content_at = time.time() - t0
                    reasoning_before = reasoning
                content += len(c)
                if ch.get("finish_reason"):
                    finish = ch["finish_reason"]
        fc = "never" if first_content_at is None else f"{first_content_at:.0f}s (after {reasoning_before} reasoning chars)"
        return (
            f"{label} | content starts: {fc} | content chars: {content} | reasoning chars: {reasoning} | "
            f"finish: {finish} | DONE: {done} | total {time.time() - t0:.0f}s\n"
            f"   reasoning START: {first_r[:400]!r}\n   reasoning END: {last_r[-400:]!r}"
        )
    except urllib.error.HTTPError as e:
        return f"{label} | HTTP {e.code} after {time.time() - t0:.0f}s: {e.read()[:300]!r}"
    except Exception as e:
        return f"{label} | ERROR after {time.time() - t0:.0f}s: {e!r}"


def run_messages(label, prompt, tok, max_tokens=16000):
    body = {
        "model": "zai-org/GLM-5.3",
        "max_tokens": max_tokens,
        "thinking": {"type": "disabled"},
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        BASE + "/v1/messages",
        json.dumps(body).encode(),
        {
            "Authorization": "Bearer " + tok,
            "x-api-key": tok,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
    )
    t0 = time.time()
    try:
        r = json.load(urllib.request.urlopen(req, timeout=900))
        text = think = 0
        for b in r.get("content", []):
            if b.get("type") == "text":
                text += len(b.get("text") or "")
            elif b.get("type") == "thinking":
                think += len(b.get("thinking") or "")
        return (
            f"{label} | stop_reason: {r.get('stop_reason')} | text chars: {text} | thinking chars: {think} | "
            f"usage: {r.get('usage')} | total {time.time() - t0:.0f}s"
        )
    except urllib.error.HTTPError as e:
        return f"{label} | HTTP {e.code} after {time.time() - t0:.0f}s: {e.read()[:300]!r}"
    except Exception as e:
        return f"{label} | ERROR after {time.time() - t0:.0f}s: {e!r}"


@app.function(secrets=[modal.Secret.from_name("modal-proxy")], timeout=2400)
def probe(prompt: str):
    tok = os.environ["MODAL_PROXY_TOKEN_ID"] + "." + os.environ["MODAL_PROXY_TOKEN_SECRET"]
    jobs = [
        lambda: run_chat("C: chat, reasoning_effort=low, 32000", {"reasoning_effort": "low"}, prompt, tok),
        lambda: run_chat("D: chat, thinking disabled (Z.ai style), 32000", {"thinking": {"type": "disabled"}}, prompt, tok),
        lambda: run_messages("E: Anthropic /v1/messages, thinking disabled, 16000", prompt, tok),
    ]
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(j) for j in jobs]
        for f in futs:
            print(f.result(), flush=True)


@app.local_entrypoint()
def main(prompt_file: str = "history/stage-ui1/prompt.md"):
    call = probe.spawn(open(prompt_file).read())
    print("started:", call.object_id)
