#!/usr/bin/env python3
"""Endpoint smoke test used to validate the refactor-arch skill output.

Usage:
    python3 scripts/smoke.py <spec.json> <base_url> [--out results.json] [--compare baseline.json]

The spec is a JSON list of requests executed in order (so state-changing calls
such as POST/PUT/DELETE build on each other exactly as in the baseline run):

    [{"name": "list products", "method": "GET", "path": "/produtos"},
     {"name": "create product", "method": "POST", "path": "/produtos",
      "body": {...}, "headers": {...}}]

Each result records the status code and the response body. With --compare the
status codes are diffed against a previous run (the pre-refactor baseline) and
the top-level JSON keys are compared, so intentional value changes (e.g. a
password hash no longer being leaked) are reported, not hidden.
Only the standard library is used, so it runs in any Python 3.8+ environment.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request


def call(base_url, req):
    data = None
    headers = {"Accept": "application/json"}
    headers.update(req.get("headers", {}))
    if "body" in req:
        data = json.dumps(req["body"]).encode()
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(base_url + req["path"], data=data, method=req["method"], headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            status, raw = resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read().decode()
    except Exception as e:  # connection refused, timeout...
        return {"status": None, "body": f"<request failed: {e}>"}
    try:
        body = json.loads(raw)
    except ValueError:
        body = raw
    return {"status": status, "body": body}


def shape(body):
    """Top-level keys of a JSON body (or of its first element for lists)."""
    if isinstance(body, list):
        return ["[list]"] + (shape(body[0]) if body else [])
    if isinstance(body, dict):
        return sorted(body.keys())
    return ["<text>"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("base_url")
    ap.add_argument("--out")
    ap.add_argument("--compare")
    args = ap.parse_args()

    with open(args.spec) as f:
        spec = json.load(f)
    baseline = None
    if args.compare:
        with open(args.compare) as f:
            baseline = {r["name"]: r for r in json.load(f)}

    results, failures = [], 0
    for req in spec:
        res = call(args.base_url.rstrip("/"), req)
        entry = {"name": req["name"], "method": req["method"], "path": req["path"], **res}
        results.append(entry)
        expected = req.get("expect")
        mark = "✓"
        note = ""
        if res["status"] is None or res["status"] >= 500:
            mark, failures = "✗", failures + 1
        elif expected is not None and res["status"] != expected:
            mark, failures = "✗", failures + 1
            note = f"(expected {expected})"
        if baseline and req["name"] in baseline:
            b = baseline[req["name"]]
            if b["status"] != res["status"] and expected is None:
                mark, failures = "✗", failures + 1
                note = f"(baseline {b['status']})"
            added = set(shape(res["body"])) - set(shape(b["body"]))
            removed = set(shape(b["body"])) - set(shape(res["body"]))
            if added or removed:
                note += f" keys +{sorted(added)} -{sorted(removed)}"
        print(f"  {mark} {res['status']} {req['method']:6} {req['path']:40} {req['name']} {note}".rstrip())

    print(f"\n{len(results) - failures}/{len(results)} requests OK")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
