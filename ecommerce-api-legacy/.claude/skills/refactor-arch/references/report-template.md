# Audit Report Template (Phase 2)

Print the report exactly in this structure and save the same Markdown to the report file.
Section headers and field labels stay in English; descriptions use the user's language.

## Rules

1. Findings are ordered **CRITICAL → HIGH → MEDIUM → LOW**; inside a severity, by file path.
2. Number findings sequentially (`F-01`, `F-02`...) after sorting; include the catalog ID (`AP-xx`).
3. `File:` holds exact locations that you re-checked: `path:line`, `path:start-end`, or several
   comma-separated locations for the same problem in the same file. For a problem spread across
   files, list each `path:lines` on the same line separated by `; `.
4. `Evidence:` quotes the offending code (max 3 short lines, trimmed) so a reviewer can verify fast.
5. `Summary` counts must equal the number of findings of each severity; `Total` equals their sum.
6. The **Deprecated APIs** section is mandatory: list each deprecated call with its replacement or
   state "No deprecated APIs detected for <stack/version>".
7. End with the confirmation question (unless `--audit-only`).

## Template

````markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project dir name>
Stack:   <Language + Framework version>
Files:   <N> analyzed | ~<LOC> lines of code
Date:    <YYYY-MM-DD>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| F-01 | CRITICAL | <title> | `<file:lines>` |
| ... | | | |

## Findings

### F-01 [CRITICAL] <Anti-pattern title> (AP-xx)
File: <path:lines>
Evidence: `<short code quote>`
Description: <what is wrong, concretely, in this code>
Impact: <consequence: security, maintainability, testability, performance>
Recommendation: <concrete fix; reference the playbook pattern PB-xx>

### F-02 [HIGH] ...

## Deprecated APIs
| Location | Deprecated API | Modern replacement |
|---|---|---|
| `<file:line>` | `<call>` | `<replacement>` |

## Architecture Notes
- Current architecture: <MONOLITH | PARTIALLY LAYERED | LAYERED> — <one line>
- Proposed target: <short description of the MVC layout that Phase 3 will produce>

================================
Total: <N> findings
================================
````

After saving the file, print:

```text
Report saved to <path>
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Example finding (good)

```markdown
### F-03 [CRITICAL] SQL Injection (AP-02)
File: models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 174, 280, 291-297
Evidence: `cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")`
Description: 14 queries are built by concatenating request values; `/login` with email `admin@loja.com' --` authenticates without a password.
Impact: Authentication bypass, full read/write of the database.
Recommendation: Use parameterized queries in the model layer (PB-02).
```

## Example finding (bad — do not do this)

```markdown
### [HIGH] Code is messy
File: controllers.py
Description: The code has problems.
```
(no line numbers, no catalog ID, no evidence, no actionable recommendation)
