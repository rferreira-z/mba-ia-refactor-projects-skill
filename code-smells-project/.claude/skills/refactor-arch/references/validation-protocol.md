# Validation Protocol (Phase 3)

The refactor is only "complete" when these checks pass **in command output you observed**.

## §1 Baseline (before changing any project file)

1. Write `.refactor-arch/endpoints.json` — an ordered list covering **every** route from the Phase 1
   inventory: at least one happy-path request and the main error path (404 / 400) per route.
   Order matters: creates before updates before deletes, so IDs line up between runs.

   ```json
   [
     {"name": "list products", "method": "GET", "path": "/produtos"},
     {"name": "create product", "method": "POST", "path": "/produtos", "body": {"nome": "X", "preco": 1, "estoque": 1}},
     {"name": "login sql injection", "method": "POST", "path": "/login", "body": {"email": "a' --", "senha": "x"}, "expect": 401}
   ]
   ```
   `expect` pins a status that the refactored app must return even if the baseline differed
   (use it for security fixes). Requests to guarded admin routes may carry `"headers"`.
2. Pick a free port (`lsof -iTCP:<port> -sTCP:LISTEN` must be empty; ports 5000/3000 are often busy
   — e.g. macOS AirPlay uses 5000). Override the port without editing code when possible
   (`flask --app app run --port 5199`; for a hard-coded Node port, start a throwaway harness that
   requires the original modules, or set `PORT` if supported).
3. Start from a fresh database (move/delete the SQLite file, run the documented seed script).
4. Boot the ORIGINAL app in the background, wait until it answers, then:
   `python3 <skill>/scripts/endpoint_smoke.py .refactor-arch/endpoints.json http://127.0.0.1:<port> --out .refactor-arch/baseline.json`
5. Stop the app (`kill <pid>`), delete the DB file it created.

## §2 Boot check (after refactoring)

1. Install dependencies if the manifest changed (`pip install -r requirements.txt` / `npm install`).
2. Fresh DB + documented seed script.
3. Start with the **documented run command** (or its port-overridden equivalent) in the background,
   capture stdout/stderr to a log file, and confirm: process alive after 2-3 s, no traceback/stack
   trace in the log, root or health endpoint answers.
4. Python: also run `python -m compileall -q src` (or the package dir) and import the app factory.
   Node: `node --check` on each changed file.

## §3 Endpoint check

`python3 <skill>/scripts/endpoint_smoke.py .refactor-arch/endpoints.json http://127.0.0.1:<port> --compare .refactor-arch/baseline.json --out .refactor-arch/after.json`

- Exit code 0 = no 5xx, no connection errors, every status equals the baseline (or the pinned `expect`).
- The script also prints top-level JSON key differences: each one must be either identical or an
  intentional change from the Phase 2 report (e.g. `senha` removed). Explain each in the summary.
- If a request fails: read the server log, fix, restart, re-run. Repeat until green.

## §4 Anti-pattern re-scan

Run `python3 <skill>/scripts/scan_antipatterns.py .` again. Every remaining hit must be reviewed:
either fixed, or a documented false positive (e.g. `print` inside a CLI seed script, the word
"password" in a validation message). Report `<N> hits, all reviewed` honestly.

## §5 Cleanup

Kill every process you started (`kill`, verify with `lsof`), delete DB files / `__pycache__` /
logs created during validation, keep `.refactor-arch/endpoints.json`, `baseline.json`, `after.json`.
