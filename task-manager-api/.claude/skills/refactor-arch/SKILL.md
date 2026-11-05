---
name: refactor-arch
description: Audits a backend codebase of any stack (Python/Flask, Node/Express, etc.) for architecture, security and code-quality anti-patterns, writes a severity-ranked audit report with exact file:line evidence, and — only after explicit user confirmation — refactors the project to a layered MVC architecture and validates that the app still boots and every original endpoint still responds. Use when the user runs /refactor-arch or asks to audit or refactor a legacy project's architecture.
argument-hint: "[report-path] [--audit-only]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# refactor-arch — Automated Architecture Audit & MVC Refactoring

You are a senior software architect. You run **three sequential phases** on the project in the
current working directory. Never skip a phase, never reorder them, and never modify a project
file before the user confirms at the end of Phase 2.

The skill directory is `${CLAUDE_SKILL_DIR}` (the folder containing this file; if that variable
appears unexpanded, use `.claude/skills/refactor-arch` relative to the project root). Knowledge lives in
`references/`; helper scripts live in `scripts/`. Read a reference file **when the phase that
needs it starts** — not all at once.

| Phase | Reference files to read first |
|---|---|
| 1 — Analysis | `references/project-analysis.md` |
| 2 — Audit | `references/anti-patterns-catalog.md`, `references/report-template.md` |
| 3 — Refactor | `references/mvc-guidelines.md`, `references/refactoring-playbook.md`, `references/validation-protocol.md` |

## Arguments

`$ARGUMENTS` may contain:

- a report path (anything ending in `.md`): where to save the Phase 2 report. Default:
  `<git-root>/reports/audit-<project-dir-name>.md` (use `git rev-parse --show-toplevel`; if not a
  git repo, use `./reports/`).
- `--audit-only`: stop after Phase 2 without asking.

## Ground rules

1. **Evidence over opinion.** Every finding cites `file:line` (or `file:start-end`) that you have
   actually read. Re-open the file to confirm line numbers before writing them. No invented findings.
2. **Technology-agnostic.** Detect the stack first (Phase 1), then use only the matching rows of the
   per-language tables in the references. Do not assume Flask or Express.
3. **Ignore non-project code:** `.git/`, `.claude/`, `node_modules/`, `.venv/`, `venv/`,
   `__pycache__/`, `dist/`, `build/`, lockfiles, `*.db`, generated files.
4. **Preserve the public contract.** Every original endpoint (method + path) must keep working with
   the same request format and compatible response shape. Deliberate behaviour changes are allowed
   **only** when they close a security hole found in Phase 2 (e.g. no longer returning password
   hashes) — list each one explicitly in the Phase 3 summary.
5. **Preserve the run commands** documented in the project's README / manifest (`python app.py`,
   `npm start`, seed scripts...). If one must change, update the manifest/README and say so.
6. Use the user's language for prose in reports (default: Brazilian Portuguese); keep the section
   headers of the templates in English exactly as written.

---

## PHASE 1 — Project Analysis (read-only)

1. Read `references/project-analysis.md`.
2. Inventory source files (Glob, honouring rule 3) and count lines of code
   (`wc -l` on the source files only).
3. Detect language, framework **with version** (from the manifest), dependencies, database engine,
   entry point, run command, and the application domain (infer from table/model/route names).
4. Map the current architecture: list every module and the responsibilities it mixes
   (routing / business rules / persistence / config / presentation), all routes (method + path +
   handler location) and all DB tables/models.
5. Classify the architecture level: `MONOLITH`, `PARTIALLY LAYERED` or `LAYERED` (criteria in the
   reference). This decides the Phase 3 strategy.
6. Print exactly this block (fill every field; nothing else in between):

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language + version if known>
Framework:     <framework + version>
Dependencies:  <runtime deps, comma separated>
Domain:        <one line describing the business domain and main entities>
Architecture:  <level> — <one line explanation>
Source files:  <N> files analyzed (~<LOC> lines)
Entry point:   <file> (<run command>)
DB:            <engine> — tables: <t1, t2, ...>
Endpoints:     <N> routes (<files where they are declared>)
================================
```

## PHASE 2 — Architecture Audit (read-only, ends with a confirmation gate)

1. Read `references/anti-patterns-catalog.md` and `references/report-template.md`.
2. Run the candidate scanner (fast, regex-based, may have false positives/negatives):
   `python3 ${CLAUDE_SKILL_DIR}/scripts/scan_antipatterns.py .`
3. **Read every source file in full** and check it against every catalog entry that applies to the
   detected stack — including the ones the scanner cannot see (God class, business logic in routes,
   missing transactions, N+1 through ORM relationships, duplication, naming...). Confirm or discard
   each scanner hit.
4. Always check the **Deprecated APIs** entry (AP-17) against the detected language/framework
   versions and recommend the modern replacement.
5. Build the report following the template exactly:
   - one finding per anti-pattern **per location cluster** (group repeated occurrences of the same
     problem in the same file into one finding listing all lines);
   - ordered CRITICAL → HIGH → MEDIUM → LOW, then by file;
   - summary counts must match the findings list.
6. Print the full report, then save the same content to the report path (see Arguments) — creating
   the `reports/` folder if needed. This report file is the **only** file you may write before
   confirmation.
7. If `--audit-only` was passed, stop here. Otherwise end your turn with exactly:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**STOP. Do not continue, do not edit any project file, until the user answers.** If the answer is
anything other than an explicit yes (`y`, `yes`, `s`, `sim`, "proceed"...), stop and summarise.

## PHASE 3 — Refactoring to MVC + Validation

1. Read `references/mvc-guidelines.md`, `references/refactoring-playbook.md` and
   `references/validation-protocol.md`.
2. **Capture the baseline BEFORE touching code** (validation-protocol §1): write the endpoint spec
   to `.refactor-arch/endpoints.json` covering every route from Phase 1 (happy path + main error
   path), boot the ORIGINAL app on a free port with a fresh database, record responses with
   `python3 ${CLAUDE_SKILL_DIR}/scripts/endpoint_smoke.py .refactor-arch/endpoints.json <url> --out .refactor-arch/baseline.json`,
   then stop the app and delete any database file the run created.
3. Choose the strategy from the Phase 1 architecture level (mvc-guidelines §"Strategy by starting
   point"): full restructure for `MONOLITH`, in-place evolution for `PARTIALLY LAYERED`, targeted
   fixes for `LAYERED`. Print the target directory tree before writing it.
4. Apply the transformations from the playbook, finding by finding, CRITICAL first. Every finding in
   the report must end up either **fixed** or **explicitly deferred with a reason**.
5. Remove the files made obsolete by the restructure (old god modules) — no dead duplicates.
   Keep dependency manifests consistent (add new runtime deps you introduced; prefer the standard
   library or the framework's own utilities over new packages).
6. Validate (validation-protocol §2-§4): install deps if needed, boot the refactored app with the
   original run command, re-run the smoke spec with `--compare .refactor-arch/baseline.json`, re-run
   the scanner, and fix + re-validate until boot succeeds and every endpoint responds as expected.
   Never claim a ✓ you did not observe in command output.
7. Stop every process you started and delete runtime artefacts (DB files, `__pycache__`). Keep
   `.refactor-arch/` (baseline + spec) as evidence.
8. Print exactly this block:

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<tree of the new source layout, annotated with each layer>

## Findings Resolution
<ID> [SEVERITY] <title> — FIXED: <how> | DEFERRED: <why>
...

## Intentional Behaviour Changes
- <endpoint>: <what changed and which finding it fixes>   (or "None")

## Validation
  ✓|✗ Application boots without errors (<command>)
  ✓|✗ All endpoints respond correctly (<passed>/<total> smoke requests)
  ✓|✗ No catalog anti-patterns remaining (scanner: <N> hits, all reviewed)
================================
```
