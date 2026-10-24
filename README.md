# coding-agent-memory

Memory and runner for a multi-model remote coding setup: five open models build the
same stage on their own GitHub branches, a judge ranks them, a human approves.

New chat or new agent: read AGENTS.md, then STATE.md, DECISIONS.md, ERRORS.md,
history/INDEX.md. Never put tokens in this repo.

- modal/run_agent.py: runner (Modal sandbox + OpenCode headless)
- modal/glm_probe.py: direct endpoint probe for GLM, run inside Modal with the stored secret
- tools/view_results.sh: download each model's newest branch, build an index page, serve on localhost
- history/: stage prompts, results, verdicts, judge rubric
