"""
Evidence for criterion 4: are the retrieved chunks at most 3 sentences?

Criterion 4 is about chunks, not about answers, so nothing here makes a model
call and nothing varies between runs — `store.py::search` is deterministic and
so is counting sentences. One pass is the whole measurement, the same way
run_eval.py treats the relevance gate.

    python check_chunks.py            # the 15 chunks my 5 questions retrieve
    python check_chunks.py --all      # every chunk in the index
"""

import argparse
import re

import config
from questions import QUESTIONS
from store import search

MAX_SENTENCES = 3


def sentences(text: str) -> list[str]:
    """Same split chunker.py::split_into_sentences uses, so the counts agree."""
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="every chunk in the index")
    args = ap.parse_args()

    print(f"Produced by check_chunks.py::main · chunks from "
          f"chunker.py::split_documents · retrieval by store.py::search")
    print(f"Target: every retrieved chunk at most {MAX_SENTENCES} sentences\n")

    if args.all:
        from chunker import split_documents
        from ingest import load_documents
        chunks = split_documents(load_documents())
        counts = [len(sentences(c.text)) for c in chunks]
        over = [n for n in counts if n > MAX_SENTENCES]
        print(f"{len(chunks)} chunks in the index · longest {max(counts)} "
              f"sentences · {len(over)} over {MAX_SENTENCES}")
        return

    total = ok = 0
    for n, item in enumerate(QUESTIONS, 1):
        print(f"Q{n}: {item['question'].strip()}")
        for i, r in enumerate(search(item["question"], top_k=config.TOP_K), 1):
            count = len(sentences(r.text))
            total += 1
            ok += count <= MAX_SENTENCES
            flag = "" if count <= MAX_SENTENCES else "  ** OVER **"
            print(f"   #{i}  {count} sentence(s)  {len(r.text):>4} chars  "
                  f"{r.source}{flag}")
        print()
    print(f"-> {ok} of {total} retrieved chunks are at most "
          f"{MAX_SENTENCES} sentences")


if __name__ == "__main__":
    main()
