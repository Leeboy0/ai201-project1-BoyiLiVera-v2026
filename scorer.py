"""
How I decide whether an answer was right.

`run_eval.py` finds this file automatically and calls `judge` once per run,
so the Run columns in results/ carry pass/fail instead of blank cells.

WHY THESE RULES AND NOT `expects in answer`
-------------------------------------------
I started with the obvious scorer — `expects.lower() in answer.lower()` — and
ran it against the fifteen answers in results/run_2026-09-23_1613_before.md.
It scored 4 of 5. The one it failed was this:

    expects: "$1.50 wash"
    answer:  "A wash costs $1.50 for Morrow House."

That answer is completely correct. The scorer failed it because my `expects`
string happens to use the word order from the document ("$1.50 wash") and the
model used ordinary English ("a wash costs $1.50"). A scorer that reports a
right answer as a failure is worse than no scorer: it would have sent me off
diagnosing a retrieval problem that does not exist.

So `judge` checks the facts rather than the phrasing, in three parts:

  1. A refusal is never a pass.
  2. Every NUMBER in `expects` must appear in the answer. In all five of my
     questions the number IS the answer — 600 pages, 18 minutes, rooms 210
     and 211, $1.50, 20 hours. Word order around a number varies between runs;
     the number itself does not.
  3. Every KEY WORD in `expects` must appear — the non-numeric words, minus
     hedges and filler ("roughly", "a", "per"). This stops a bare number from
     passing on its own.
  4. Any PROPER NOUN in the question must appear in the answer. This is the
     one that does real work on my corpus: the laundry documents are
     near-identical boilerplate that differs only by building name and price,
     and Old Brewhouse also charges $1.50 for a wash. Without this rule, an
     answer about the wrong building would score as a pass on rules 1-3.

Rule 4 is deliberately narrow — it only fires on questions that name something
(Morrow House, Fenwick Court). Three of my five questions have no proper noun
and are judged on the fact alone.
"""

import re

from gate import REFUSAL

# Words in `expects` that carry no fact. "roughly 600" is right whether or not
# the model says "roughly", so requiring the hedge would fail correct answers.
FILLER = {
    "a", "an", "the", "of", "for", "per", "in", "on", "at", "to", "and",
    "roughly", "about", "around", "approximately", "during", "each", "is",
}

# Capitalised words that start a question rather than name a thing.
NOT_A_NAME = {
    "how", "what", "which", "who", "where", "when", "why", "is", "are",
    "do", "does", "can", "i", "my",
}


def _norm(text: str) -> str:
    """Lowercase, collapse whitespace. Comparisons happen on this form."""
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _numbers(text: str) -> list[str]:
    """Every number in the text, as written. '$1.50 wash' -> ['1.50']"""
    return re.findall(r"\d+(?:\.\d+)?", text)


def _key_words(text: str) -> list[str]:
    """The words in `expects` that carry the fact."""
    words = re.findall(r"[a-z][a-z-]+", _norm(text))
    return [w for w in words if w not in FILLER]


def _proper_nouns(question: str) -> list[str]:
    """
    Names the question is asking about — 'Morrow', 'Fenwick', 'Court'.

    Skips the first word, which is capitalised because it starts a sentence,
    and skips question words that can appear mid-sentence.
    """
    words = re.findall(r"\b[A-Z][a-z]+\b", question.strip())
    first = question.strip().split()[:1]
    if first and words and words[0] == first[0].strip("?,."):
        words = words[1:]
    return [w for w in words if w.lower() not in NOT_A_NAME]


def judge(question: str, expects: str, answer: str, results) -> bool:
    """
    Did this run answer the question correctly?

    Returns a real True/False — run_eval.py looks the result up in a dict
    rather than testing truthiness, so 1/0 would crash it.
    """
    a = _norm(answer)

    # 1. A refusal is a fail. It may be the *right* behaviour for an
    #    out-of-scope question, but these five are questions my corpus covers.
    if not a or a == _norm(REFUSAL):
        return False

    # 2. The numbers are the fact.
    if not all(n in a for n in _numbers(expects)):
        return False

    # 3. The words around them, minus filler.
    if not all(w in a for w in _key_words(expects)):
        return False

    # 4. Right fact, right subject.
    if not all(name.lower() in a for name in _proper_nouns(question)):
        return False

    return True


def names_a_source(answer: str, results) -> bool:
    """
    Criterion 2: does this answer name at least one source document?

    Not called by run_eval.py — `judge` only returns one verdict — so I call
    this myself when I aggregate the per-question rows into the per-criterion
    table. generate.py tells the model to name the filename it used, so I look
    for a retrieved filename in the answer rather than just the word "source".
    """
    a = _norm(answer)
    return any(_norm(r.source) in a for r in results)
