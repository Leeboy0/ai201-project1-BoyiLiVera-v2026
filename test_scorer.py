"""
Tests for scorer.py. No API calls — nothing here talks to a model.

Two halves:

  REPLAY — every answer my system really produced, read back out of the run
  log in results/. Retrieval is re-run live (deterministic, free) so `judge`
  gets real Result objects, the same as it does under run_eval.py.

  HARD CASES — answers I wrote by hand that SHOULD fail. A scorer I have only
  ever seen say "pass" is untested: if it returned True unconditionally, the
  replay half alone would look perfect.

    python test_scorer.py
    python test_scorer.py results/run_2026-09-23_1613_before.md
"""

import re
import sys
from pathlib import Path

import config
import scorer
from gate import REFUSAL
from questions import QUESTIONS
from store import search

# ─── Replay: the answers the system really gave ──────────────────────────────

BLOCK = re.compile(
    r"^### (?P<question>.+?) — run (?P<run>\d+)\n"      # heading
    r".*?^```\n(?P<answer>.*?)^```",                    # first fenced block
    re.S | re.M,
)


def latest_log() -> Path | None:
    logs = sorted(config.RESULTS_DIR.glob("run_*.md"))
    return logs[-1] if logs else None


def replay(path: Path) -> tuple[int, int]:
    text = path.read_text()
    expects_for = {q["question"].strip(): q["expects"] for q in QUESTIONS}

    print(f"REPLAY — {path.name}\n")
    passed = total = 0
    for m in BLOCK.finditer(text):
        question = m.group("question").strip()
        answer = m.group("answer").strip()
        expects = expects_for.get(question)
        if expects is None:
            continue   # a question from an older version of questions.py

        results = search(question, top_k=config.TOP_K)
        verdict = scorer.judge(question, expects, answer, results)
        sourced = scorer.names_a_source(answer, results)

        total += 1
        passed += verdict
        print(f"  {'pass' if verdict else 'FAIL'}  "
              f"{'sourced' if sourced else 'NO SOURCE':<9}  "
              f"run {m.group('run')}  {question[:54]}")
        if not verdict:
            print(f"        expects {expects!r}")
            print(f"        answer  {answer[:90]!r}")

    print(f"\n  -> {passed} of {total} runs scored as correct")
    return passed, total


# ─── Hard cases: answers that must NOT pass ──────────────────────────────────
# (question index into QUESTIONS, answer, expected verdict, what it tests)

HARD_CASES = [
    (4, "A wash costs $1.50 for Morrow House. Source: housing_morrow_house.txt",
     True, "real answer, phrased differently from `expects`"),
    (4, "Laundry is $1.50 for a wash at Old Brewhouse (housing_old_brewhouse_laundry.txt).",
     False, "right price, WRONG BUILDING — the trap in this corpus"),
    (4, REFUSAL,
     False, "a refusal to a question the corpus covers"),
    (4, "Doing laundry costs money and prices vary by building.",
     False, "fluent, sourceless, contains no number"),
    (1, "Students get 600 pages.",
     True, "hedge word 'roughly' dropped — still correct"),
    (1, "Students get $30 of printing credit per semester.",
     False, "true, but not the fact the question asked for"),
    (2, "It takes 18 minutes to walk from Tamsin Court to central campus.",
     False, "right number, wrong residence"),
    (3, "rooms 210 and 211 have whiteboards that erase.",
     True, "lowercase — casing must not matter"),
    (3, "Room 210 has a whiteboard.",
     False, "incomplete — 211 is missing"),
    (5, "You may work up to 20 hours a week during term.",
     True, "reordered, still correct"),
]


def hard_cases() -> tuple[int, int]:
    print("\nHARD CASES\n")
    ok = 0
    for idx, answer, want, why in HARD_CASES:
        item = QUESTIONS[idx - 1]
        question = item["question"].strip()
        results = search(question, top_k=config.TOP_K)
        got = scorer.judge(question, item["expects"], answer, results)
        good = got is want
        ok += good
        print(f"  {'ok  ' if good else 'BAD '} judge={str(got):<5} want={str(want):<5}  {why}")
        if not good:
            print(f"        Q{idx} {answer[:80]!r}")
    print(f"\n  -> {ok} of {len(HARD_CASES)} hard cases behaved as intended")
    return ok, len(HARD_CASES)


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_log()
    if path and path.exists():
        replay(path)
    else:
        print("No run log in results/ to replay. Run run_eval.py first.\n")

    ok, n = hard_cases()
    sys.exit(0 if ok == n else 1)
