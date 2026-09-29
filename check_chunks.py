"""
Evidence for criterion 4: are the retrieved chunks at most 3 sentences?

Criterion 4 is about chunks, not about answers, so nothing here makes a model
call and nothing varies between runs — `store.py::search` is deterministic and
so is counting sentences. One pass is the whole measurement, the same way
run_eval.py treats the relevance gate.

    python check_chunks.py            # the 15 chunks my 5 questions retrieve
    python check_chunks.py --all      # every chunk in the index
    python check_chunks.py --subject  # criterion 4 as revised in unit 2
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


def names_its_subject(chunk, document_text: str) -> bool:
    """
    Does this chunk say what it is about?

    Criterion 4 as revised in unit 2. The subject of each document is its
    heading — the first line, "CS 210 Data Structures" or "Laundry in Morrow
    House". chunker.py::split_documents batches three sentences at a time with
    no overlap, so only the FIRST chunk of a document carries that heading;
    every later chunk has to name the subject in its own prose or it doesn't
    name it at all.
    """
    heading = document_text.strip().split("\n")[0]
    words = [w for w in re.findall(r"[A-Za-z0-9]+", heading) if len(w) > 3]
    if not words:
        return True
    return any(w.lower() in chunk.text.lower() for w in words)


def check_subjects():
    """Criterion 4 as revised: every chunk names the document's subject."""
    from chunker import split_documents
    from ingest import load_documents

    documents = load_documents()
    text_of = {d.source: d.text for d in documents}
    chunks = split_documents(documents)

    unnamed = [c for c in chunks if not names_its_subject(c, text_of[c.source])]
    print(f"{len(chunks)} chunks · {len(unnamed)} never name their "
          f"document's subject\n")
    for c in unnamed[:6]:
        heading = text_of[c.source].strip().split("\n")[0]
        print(f"  {c.source}  heading={heading!r}")
        print(f"    chunk {c.index}: {c.text[:72]}...")
    if len(unnamed) > 6:
        print(f"  ... and {len(unnamed) - 6} more")
    print(f"\n-> {len(chunks) - len(unnamed)} of {len(chunks)} chunks in the "
          f"index name their subject")

    # The criterion is scoped to the chunks my five questions actually retrieve.
    retrieved = named = 0
    for item in QUESTIONS:
        for r in search(item["question"], top_k=config.TOP_K):
            retrieved += 1
            named += names_its_subject(r, text_of[r.source])
    print(f"-> {named} of {retrieved} RETRIEVED chunks name their subject")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="every chunk in the index")
    ap.add_argument("--subject", action="store_true",
                    help="criterion 4 as revised in unit 2")
    args = ap.parse_args()

    print(f"Produced by check_chunks.py::main · chunks from "
          f"chunker.py::split_documents · retrieval by store.py::search")
    if args.subject:
        print("Criterion 4 as revised in unit 2: "
              "every retrieved chunk names its document's subject\n")
    else:
        print(f"Target: every retrieved chunk at most "
              f"{MAX_SENTENCES} sentences\n")

    if args.subject:
        check_subjects()
        return

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
