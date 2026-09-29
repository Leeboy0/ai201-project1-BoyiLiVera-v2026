"""
Evidence for criterion 5: how long an answer takes to come back.

Nothing in the starter records time — run_eval.py logs answers and distances
but not duration — so this measures it. It times the two stages separately,
because criterion 5 failing is only useful if I can name which stage was slow:

    retrieval   store.py::search          local, no network
    generation  generate.py::answer_from_chunks   the API call

  python measure_latency.py --retrieval-only   # free, no model calls
  python measure_latency.py                    # 3 runs x 5 questions = 15 calls

The response cache is off, the same as run_eval.py does it — a cached answer
returns in microseconds and would make the numbers meaningless.
"""

import argparse
import statistics
import time

import config
import gate
from generate import answer_from_chunks
from questions import QUESTIONS
from store import search

TARGET_SECONDS = 20.0


def timed_once(question: str, retrieval_only: bool):
    t0 = time.perf_counter()
    results = search(question, top_k=config.TOP_K)
    t_retrieval = time.perf_counter() - t0

    if retrieval_only:
        return t_retrieval, None

    decision = gate.check(results)
    if not decision.passed:
        return t_retrieval, 0.0          # a refusal makes no API call

    t1 = time.perf_counter()
    answer_from_chunks(question, results, cache=False)
    return t_retrieval, time.perf_counter() - t1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--retrieval-only", action="store_true",
                    help="skip generation — costs no model calls")
    args = ap.parse_args()

    runs = 1 if args.retrieval_only else args.runs
    print(f"top-k {config.TOP_K} · cutoff {config.THRESHOLD} · "
          f"{runs} run(s) · target {TARGET_SECONDS:.0f}s end to end")
    print("Produced by measure_latency.py::main\n")

    for run in range(1, runs + 1):
        totals = []
        print(f"Run {run}")
        for n, item in enumerate(QUESTIONS, 1):
            retr, gen = timed_once(item["question"], args.retrieval_only)
            if gen is None:
                print(f"  Q{n}  retrieval {retr:6.3f}s")
                totals.append(retr)
                continue
            total = retr + gen
            totals.append(total)
            flag = "" if total < TARGET_SECONDS else "  ** OVER TARGET **"
            print(f"  Q{n}  retrieval {retr:6.3f}s  generation {gen:6.3f}s  "
                  f"total {total:6.3f}s{flag}")

        under = sum(t < TARGET_SECONDS for t in totals)
        print(f"  -> {under} of {len(totals)} under {TARGET_SECONDS:.0f}s "
              f"(slowest {max(totals):.3f}s, median {statistics.median(totals):.3f}s)\n")


if __name__ == "__main__":
    main()
