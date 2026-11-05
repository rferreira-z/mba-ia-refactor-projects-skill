#!/usr/bin/env python3
"""Regex-based candidate scanner for the refactor-arch anti-pattern catalog.

Usage: python3 scan_antipatterns.py <project_dir>

Prints one line per hit:  AP-xx  SEVERITY  path:line  <trimmed code>
Hits are CANDIDATES: the agent must open the file and confirm each one. Structural anti-patterns
(God class, fat routes, duplication, missing transactions) cannot be detected by regex and must be
found by reading the code. Standard library only; works on any OS with Python 3.8+.
"""
import os
import re
import sys

SKIP_DIRS = {".git", ".claude", "node_modules", ".venv", "venv", "env", "__pycache__", "dist",
             "build", "coverage", ".refactor-arch", "instance"}
EXT_LANG = {".py": "py", ".js": "js", ".mjs": "js", ".cjs": "js", ".ts": "js"}

SQL_KW = r"(SELECT|INSERT|UPDATE|DELETE)\b"

# (id, severity, languages, regex, description)
RULES = [
    ("AP-01", "CRITICAL", "py,js",
     r"""(?i)\b\w*(secret|passw(or)?d|pass|pwd|api_?key|gateway_?key|token|senha)\w*["']?\]?\s*[:=]\s*["'][^"'\s]{4,}["']""",
     "hardcoded credential/secret"),
    ("AP-01", "CRITICAL", "py,js", r"""["'](pk|sk)_live_\w+|["']AKIA[0-9A-Z]{12,}""", "live API key literal"),
    ("AP-02", "CRITICAL", "py", r"""execute\(\s*f["']|execute\([^)]*["']\s*\+|""" + SQL_KW + r""".*["']\s*\+\s*(\w|$)""",
     "SQL built by string concatenation/interpolation"),
    ("AP-02", "CRITICAL", "py", r"""query\s*\+=\s*["'].*(AND|OR|WHERE)""", "SQL built incrementally from strings"),
    ("AP-02", "CRITICAL", "js", r"""(run|get|all|query|exec)\(\s*`[^`]*""" + SQL_KW + r"""[^`]*\$\{""", "SQL template literal interpolation"),
    ("AP-02", "CRITICAL", "js", r"""(?i)["'`]\s*""" + SQL_KW + r"""[^"'`]*["'`]\s*\+""", "SQL string concatenation"),
    ("AP-04", "CRITICAL", "py", r"""hashlib\.(md5|sha1|sha256)\(""", "fast/unsalted hash (passwords?)"),
    ("AP-04", "CRITICAL", "js", r"""createHash\(\s*['"](md5|sha1)['"]|toString\(\s*['"]base64['"]\s*\)""", "weak hashing / encoding as crypto"),
    ("AP-05", "CRITICAL", "py,js",
     r"""(?i)(route|get|post|put|patch|delete|add_url_rule)\(\s*["'`][^"'`]*/(admin|reset|query|debug|exec)""",
     "admin/destructive route (check auth)"),
    ("AP-06", "CRITICAL", "py,js", r"""(?i)["'](secret_key|password|senha|pass)["']\s*:""", "sensitive field in response/serializer"),
    ("AP-06", "CRITICAL", "js", r"""console\.log\(.*\$\{[^}]*\b(card|cc|\w*Key|pass|pwd|secret)\b""", "sensitive value logged"),
    ("AP-08", "HIGH", "py", r"""^\s*global\s+\w+""", "mutable global state"),
    ("AP-08", "HIGH", "js", r"""^(let|var)\s+\w+\s*=\s*(\{\}|\[\]|0|null)\s*;?""", "module-level mutable state"),
    ("AP-10", "HIGH", "py", r"""debug\s*=\s*True|\[["']DEBUG["']\]\s*=\s*True|host\s*=\s*["']0\.0\.0\.0["']""", "debug mode / bind all interfaces"),
    ("AP-12", "HIGH", "py,js", r"""(?i)fake[-_]?(jwt|token)""", "fake/predictable auth token"),
    ("AP-15", "MEDIUM", "py", r"""^\s*except\s*:""", "bare except"),
    ("AP-15", "MEDIUM", "py", r"""jsonify\(\{\s*["'](erro|error)["']\s*:\s*str\(e\)""", "raw exception message returned to client"),
    ("AP-17", "MEDIUM", "py", r"""datetime\.utcnow\(|\butcnow\b(?!_)|utcfromtimestamp\(""", "deprecated datetime.utcnow/utcfromtimestamp"),
    ("AP-17", "MEDIUM", "py", r"""\.query\.get\(""", "legacy SQLAlchemy Query.get (use db.session.get)"),
    ("AP-17", "MEDIUM", "py", r"""before_first_request|JSONEncoder|\bimport imp\b|distutils|pkg_resources""", "deprecated/removed API"),
    ("AP-17", "MEDIUM", "js", r"""new Buffer\(|url\.parse\(|fs\.exists\(|createCipher\(|util\.is(Array|Date)\(|require\(['"]body-parser['"]\)""", "deprecated Node/Express API"),
    ("AP-19", "LOW", "py,js", r"""[<>]=?\s*\d{3,}\b|\*\s*0\.\d+""", "magic number"),
    ("AP-22", "LOW", "py", r"""^\s*print\(""", "print used as logging"),
    ("AP-22", "LOW", "js", r"""console\.log\(""", "console.log used as logging"),
    ("AP-23", "LOW", "py", r"""type\(\w+(\[['"]\w+['"]\])?\)\s*==""", "type() == instead of isinstance"),
]

QUERY_CALL = {
    "py": re.compile(r"""\.query\.|cursor\d*\.execute\(|\.execute\(|db\.session\.(get|query|execute|scalars)"""),
    "js": re.compile(r"""\b(db|this\.db|self\.db)\.(get|all|run|query)\("""),
}
LOOP = {
    "py": re.compile(r"""^\s*for\s+.+\s+in\s+.+:\s*$"""),
    "js": re.compile(r"""\.forEach\(|\bfor\s*\(|\.map\(\s*(async\s*)?\(?\w*\)?\s*=>"""),
}


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            lang = EXT_LANG.get(os.path.splitext(name)[1])
            if lang:
                yield os.path.join(dirpath, name), lang


def n_plus_one(lines, lang):
    """Query calls nested inside a loop body (indent-based for Python, brace-depth for JS)."""
    hits = []
    if lang == "py":
        loop_indents = []
        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            loop_indents = [li for li in loop_indents if li < indent]
            if loop_indents and QUERY_CALL["py"].search(line):
                hits.append(i)
            if LOOP["py"].match(line):
                loop_indents.append(indent)
    else:
        depth, loop_depths = 0, []
        for i, line in enumerate(lines, 1):
            if loop_depths and QUERY_CALL["js"].search(line):
                hits.append(i)
            if LOOP["js"].search(line):
                loop_depths.append(depth)
            depth += line.count("{") - line.count("}")
            loop_depths = [d for d in loop_depths if d < depth]
    return hits


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    compiled = [(ap, sev, set(langs.split(",")), re.compile(rx), desc) for ap, sev, langs, rx, desc in RULES]
    total = 0
    for path, lang in iter_files(root):
        rel = os.path.relpath(path, root)
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
        if len(lines) > 150:
            print(f"AP-03  CRITICAL  {rel}:1-{len(lines)}  large module ({len(lines)} lines) - check for God class")
            total += 1
        for i, line in enumerate(lines, 1):
            for ap, sev, langs, rx, desc in compiled:
                if lang in langs and rx.search(line):
                    print(f"{ap}  {sev:8}  {rel}:{i}  [{desc}] {line.strip()[:110]}")
                    total += 1
        for i in n_plus_one(lines, lang):
            print(f"AP-13  MEDIUM    {rel}:{i}  [query inside loop] {lines[i - 1].strip()[:110]}")
            total += 1
    print(f"\n{total} candidate hits (verify each by reading the code)")


if __name__ == "__main__":
    main()
