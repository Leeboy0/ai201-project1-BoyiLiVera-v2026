# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

## Chunking Strategy

**Chunk size:**
**Overlap:**

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: health_center.txt#0 — produced by: chunker.py::split_documents


The health centre 

Walk-in hours are 8am to 11am; everything after that is by appointment and appointments run about a week out. If something is urgent, go at 8am and wait rather than booking. Counselling is separate, in the same building, and has its own intake process with a shorter wait than people expect — usually three or four days for a first session.


**Chunk 2** — source: course_cs_340.txt#0 — produced by: chunker.py::split_documents


CS 340 Databases

I'm a junior and I've done this twice now. Format is lecture twice a week plus a project that runs the whole term. Assessment: one midterm and a final, both open-book.


**Chunk 3** — source: dining_halden_hall.txt#0 — produced by: chunker.py::split_documents


Halden Hall

I lived here my sophomore year. Wait times: rarely more than 8 minutes, even at noon. The thing worth going for is soup rotation, and the bread is baked on site.


**Chunk 4** — source: health_center.txt#0 — produced by: chunker.py::split_documents

The health centre

Walk-in hours are 8am to 11am; everything after that is by appointment and appointments run about a week out. If something is urgent, go at 8am and wait rather than booking. Counselling is separate, in the same building, and has its own intake process with a shorter wait than people expect — usually three or four days for a first session.


**Chunk 5** — source: housing_morrow_house_laundry.txt#0 — produced by: chunker.py::split_documents


Laundry in Morrow House

Machines take $1.50 wash, $1.25 dry, coin or card. There are eight washers and six dryers for the building, which is the wrong ratio and means the dryers back up on Sunday evenings. Best time to do laundry here is Tuesday or Wednesday morning.


## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** How many black-and-white pages can a student print with their printing quota each semester?

**Answer:** A student can print roughly 600 black-and-white pages per semester with their printing quota.

```
```

**My relevance cutoff:** 0.55

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
|  |  |  |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I used AI to help me understand the code snippet and how to modify them based on my terminal outputs and requirements. 

**2.** I used AI to learn concepts related to RAG and AI systems. 

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

Corpus `campus_life`, top-k 3, relevance cutoff 0.55. Run log:
[results/run_2026-09-23_1613_before.md](results/run_2026-09-23_1613_before.md),
produced by `run_eval.py::main`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunk size should be limited | 15 of 15 | 15/15 | 15/15 | 15/15 | MET |
| 5. Answer comes back under 20 seconds | 15 of 15 |  |  |  |  |

Three of these come out identical in all three columns, and that is correct
rather than lazy for the same reason the brief gives for criterion 3.
Criteria 1 and 4 are properties of **retrieval and chunking**, not of the
generated answer: `store.py::search` is deterministic and so is counting
sentences, so one pass is the whole measurement. Criterion 2 is the only one
here that depends on what the model wrote, and criterion 5 is the only one
that can drift between runs for reasons outside my code.

The three runs really were three runs. Two of the five questions came back
with textually different answers across them, which a cached result could not
do — `run_eval.py:67` passes `cache=False` on purpose:

```
Q5 run 1: The maximum is 20 hours a week during term (source: money_jobs.txt).
Q5 run 2: The maximum is 20 hours a week during term (money_jobs.txt).
```

### Criterion 1 — retrieved chunk contains the answer

Retrieval by `store.py::search`, printed by `app.py::cmd_retrieve`. The
answer-bearing chunk comes back at rank 1 for all five questions; this is the
hardest of the five, because three other buildings have near-identical laundry
documents and one of them charges the same $1.50:

```
Question: How much is a wash cost for Morrow house?

#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.2504     housing_morrow_house_laundry.txt Laundry in Morrow House  Machines take $1.50 wash, $...
2   0.3501     housing_morrow_house.txt         The good: cheapest housing tier by about $900 a year...
3   0.4264     housing_innisfree_hall_laundry.txt Laundry in Innisfree Hall  Machines take $1.75 wash,...

Gate: best distance 0.250 is under the 0.55 cutoff
```

### Criterion 2 — every answer names a source

Written by `generate.py::answer_from_chunks`, logged by
`run_eval.py::write_report`. All 15 answers name a retrieved filename;
`scorer.py::names_a_source` is what I check it with:

```
### How many black-and-white pages can a student print with their printing quota each semester? — run 1

- Best distance: 0.1926 (passed the gate)
- Sources retrieved: admin_printing_quota.txt, money_textbooks.txt, study_group_rooms.txt

A student can print roughly 600 black-and-white pages per semester with their printing quota.

Source: admin_printing_quota.txt
```

### Criterion 3 — the gate stops out-of-corpus questions

Produced by `run_eval.py::check_out_of_scope`, cutoff 0.55:

```
| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.824 | refused |
| How do I change the oil in a diesel engine? | 0.849 | refused |
| Who won the 1994 World Cup? | 0.874 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.833 | refused |
| How do I write a for loop in Rust? | 0.871 | refused |
```

### Criterion 4 — chunk size should be limited

Produced by `check_chunks.py::main`, chunks from
`chunker.py::split_documents`, retrieval by `store.py::search`:

```
Q4: How much is a wash cost for Morrow house?
   #1  3 sentence(s)   268 chars  housing_morrow_house_laundry.txt
   #2  3 sentence(s)   225 chars  housing_morrow_house.txt
   #3  3 sentence(s)   267 chars  housing_innisfree_hall_laundry.txt

-> 15 of 15 retrieved chunks are at most 3 sentences
```

Across the whole index, `python check_chunks.py --all` reports
`141 chunks in the index · longest 3 sentences · 0 over 3`.

### Criterion 5 — answer comes back under 20 seconds

Produced by `measure_latency.py::main`. Retrieval alone, which costs no model
calls:

```
Run 1
  Q1  retrieval  0.481s
  Q2  retrieval  0.019s
  Q3  retrieval  0.017s
  Q4  retrieval  0.021s
  Q5  retrieval  0.021s
  -> 5 of 5 under 20s (slowest 0.481s, median 0.021s)
```

<!-- TODO: run `python measure_latency.py` (15 model calls) to get the
     end-to-end numbers, then fill the three Run cells and the verdict for
     criterion 5 above. Q1's 0.481s is the embedding model loading on first
     use; every call after it is ~0.02s. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
