#!/usr/bin/env python3
"""Convert a `claude -p --output-format stream-json --verbose` log into a readable transcript.

Usage: python3 scripts/extract_transcript.py run.jsonl [--text-only] > transcript.md

Prints the assistant's text blocks in order (what the user sees in the terminal) and, unless
--text-only is given, a one-line summary of every tool call, followed by the session id and cost.
"""
import json
import sys


def main():
    path = sys.argv[1]
    text_only = "--text-only" in sys.argv
    session, cost, turns = None, None, None
    with open(path) as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except ValueError:
                continue
            session = ev.get("session_id", session)
            if ev.get("type") == "assistant":
                for block in ev["message"].get("content", []):
                    if block.get("type") == "text" and block["text"].strip():
                        print(block["text"].rstrip() + "\n")
                    elif block.get("type") == "tool_use" and not text_only:
                        inp = block.get("input", {})
                        detail = inp.get("command") or inp.get("file_path") or inp.get("pattern") or inp.get("skill") or ""
                        detail = str(detail).replace("\n", " ")[:160]
                        print(f"> [tool] {block['name']}: {detail}\n")
            elif ev.get("type") == "result":
                cost, turns = ev.get("total_cost_usd"), ev.get("num_turns")
    print(f"<!-- session_id={session} turns={turns} cost_usd={cost} -->")


if __name__ == "__main__":
    main()
