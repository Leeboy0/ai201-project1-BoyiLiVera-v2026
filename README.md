# The Unofficial Guide

Boyi Li-Vera
Campus_life

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

This is a question-answering system over the `campus_life` corpus: 88 short
forum-style posts written by students about one university — dining halls,
residence buildings, individual courses, the library, transit, health services
and administrative deadlines. It answers specific factual questions that one
of those posts happens to contain the answer to, such as what a wash costs in
a particular residence or how many pages the printing quota covers. Questions
are matched to chunks by meaning, and a relevance gate refuses anything whose
closest chunk is further away than 0.55, so a question about Mongolia or
diesel engines gets "I don't have enough information about that" rather than
an invented answer. Every answer names the document it came from.

## Chunking Strategy

**Chunk size:** 3 sentences (not characters — see below)

**Overlap:** none between chunks; from unit 2, every chunk after the first
repeats its document's heading line

I split on sentences rather than on a character count, so `CHUNK_SIZE` and
`CHUNK_OVERLAP` in `config.py` are not what my chunker reads —
`chunker.py::split_documents` uses its own `max_sentences = 3`. The documents
made that choice for me. They are short: 88 posts, 178 to 549 characters, a
median of 309. Cutting those at 800 characters would have put two or three
whole posts in one chunk, and cutting at 200 would have split single posts
mid-sentence. Each post is also one topic — one building, one course, one
deadline — and a post's useful fact is usually one sentence with one or two
sentences of context around it, which is where 3 came from.

I changed my mind about one thing in unit 2. My original chunker took three
sentences at a time with nothing shared between chunks, and that turned out to
lose the subject: every document's name is in its heading line, the heading
lands in the first chunk, and so chunk 1 of `housing_morrow_house.txt` read
"... Laundry costs $1.50 wash" with the words "Morrow House" nowhere in it.
Three other buildings have near-identical laundry posts and one of them also
charges $1.50. I now prefix the heading to every chunk after the first. That
is the unit 2 improvement, and the diagnosis behind it is further down.

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
$ python app.py ask "How many black-and-white pages can a student print with their printing quota each semester?"

A student can print roughly 600 black-and-white pages per semester with their
printing quota.

Source: admin_printing_quota.txt

Sources retrieved: admin_printing_quota.txt, money_textbooks.txt, study_group_rooms.txt
Best distance: 0.1926 (passed the 0.55 gate)
```

**My relevance cutoff:** 0.55

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

I ran all ten through `python app.py retrieve "..."`, which prints the best
distance without spending a model call, and took the `min(distance)` that
`gate.py::check` compares against.

| Question | In corpus? | Best distance |
|---|---|---|
| How many black-and-white pages can a student print with their printing quota each semester? | yes | 0.1926 |
| How many minutes walking needed from Fenwick Court to central campus? | yes | 0.1926 |
| Which study rooms in the library have whiteboards that actually erase? | yes | 0.3966 |
| How much is a wash cost for Morrow house? | yes | 0.2504 |
| What is the maximum hours to work per week on campus? | yes | 0.3679 |
| What is the capital of Mongolia? | no | 0.8236 |
| How do I change the oil in a diesel engine? | no | 0.8493 |
| Who won the 1994 World Cup? | no | 0.8736 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.8329 |
| How do I write a for loop in Rust? | no | 0.8714 |

The two groups do not overlap and they are not close. In-corpus runs
0.193–0.397, out-of-corpus runs 0.824–0.874, so the gap is about 0.43 wide —
wider than the entire in-corpus range. Mid-gap would be 0.61, and the starter's
0.6 sits inside the gap and works. I picked **0.55** instead because the two
kinds of error are not equally bad: a false refusal is visible and annoying,
while a false answer is confident and wrong, which is the thing criterion 3
exists to catch. 0.55 still leaves 0.15 of headroom above my worst real
question, so no question I can answer is anywhere near the line, and it buys
margin against out-of-scope questions that land closer than these five did.
I checked what the cutoff does to both groups before setting it:

| cutoff | in-corpus answered | out-of-scope refused |
|---|---|---|
| 0.30 | 3/5 | 5/5 |
| 0.45 | 5/5 | 5/5 |
| **0.55** | **5/5** | **5/5** |
| 0.60 | 5/5 | 5/5 |
| 0.75 | 5/5 | 5/5 |
| 0.90 | 5/5 | 0/5 |

0.30 is the "refuses questions it had the answer to" failure and drops two of
my five. 0.90 is the "never refuses anything" failure and lets all five
out-of-scope questions through to the model.

## How I Used AI


**1.** I asked Claude to write `scorer.py` from the contract in `run_eval.py`.
What came back scored all fifteen answers in my before-log as correct, which
looked like it worked. It had not been shown a single wrong answer, so I added
`test_scorer.py` with ten hand-written cases that must fail — a refusal, an
incomplete answer, and the one that mattered: the right price quoted for the
wrong building, which my corpus makes easy. Six of the ten have to come back
`False`, so a scorer that always returned `True` would fail the suite. The
after-run then caught the scorer failing two *correct* answers, which none of
those ten cases covered, so the suite is still not finished.

**2.** I asked Claude to help find a pattern across my two misses rather than
explain them one at a time. It pointed out something I had not seen: both
misses sat on either side of retrieval, and four of my five criteria were
aimed at retrieval and embedding — the part that was already working. It also
pointed out that criterion 4 could not fail, because `chunker.py` enforces the
3-sentence limit in code. I revised that criterion rather than lowering it,
and the revised version is what produced the diagnosis my improvement came
from. I wrote the revision wording myself so the reasoning was mine.



# Unit 2



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
| 5. Answer comes back under 20 seconds | 15 of 15 | 4/5 | 4/5 | 5/5 | MISSED |

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

I revised this criterion in unit 2 — see criteria.md. The original passes
because `chunker.py::split_documents` sets `max_sentences = 3`, so no chunk it
produces can violate it. The revised version asks whether a chunk names the
subject of the document it came from, and that one misses.
`python check_chunks.py --subject`:

```
141 chunks · 49 never name their document's subject

  course_cs_210.txt  heading='CS 210 Data Structures'
    chunk 1: Midterms are curved, the final is not. Expect 8 to 10 hours a week outsi...

-> 92 of 141 chunks in the index name their subject
-> 13 of 15 RETRIEVED chunks name their subject
```

The two retrieved chunks that fail are `transit_shuttle.txt` chunk 1 (rank 2
for Q2) and `housing_morrow_house.txt` chunk 1 (rank 2 for Q4). The second one
matters: it reads "The good: cheapest housing tier by about $900 a year ...
Laundry costs $1.50 wash" with the words "Morrow House" nowhere in it, so a
price arrives at the model with no building attached to it.

### Criterion 5 — answer comes back under 20 seconds

Produced by `measure_latency.py::main`, three runs, cache off, retrieval and
generation timed separately:

```
Run 1
  Q1  retrieval  0.442s  generation 24.879s  total 25.322s  ** OVER TARGET **
  Q2  retrieval  0.044s  generation  0.956s  total  1.000s
  Q3  retrieval  0.028s  generation  0.582s  total  0.610s
  Q4  retrieval  0.025s  generation  0.730s  total  0.755s
  Q5  retrieval  0.022s  generation  0.511s  total  0.533s
  -> 4 of 5 under 20s (slowest 25.322s, median 0.755s)

Run 2
  Q1  retrieval  0.021s  generation  0.631s  total  0.652s
  Q2  retrieval  0.021s  generation  1.091s  total  1.112s
  Q3  retrieval  0.021s  generation  0.905s  total  0.925s
  Q4  retrieval  0.021s  generation  1.271s  total  1.293s
  Q5  retrieval  0.023s  generation 23.395s  total 23.418s  ** OVER TARGET **
  -> 4 of 5 under 20s (slowest 23.418s, median 1.112s)

Run 3
  Q1  retrieval  0.052s  generation  0.785s  total  0.838s
  Q2  retrieval  0.024s  generation  3.203s  total  3.228s
  Q3  retrieval  0.020s  generation  0.919s  total  0.939s
  Q4  retrieval  0.021s  generation  0.574s  total  0.594s
  Q5  retrieval  0.020s  generation  0.402s  total  0.422s
  -> 5 of 5 under 20s (slowest 3.228s, median 0.838s)
```

13 of 15 under 20 seconds, so this one misses. Both failures are in
generation, never retrieval: the two offenders spent 24.879s and 23.395s
inside `generate.py::answer_from_chunks` while retrieval in the same call took
0.442s and 0.023s. Neither was a rate-limit pause, which my criterion
excludes — `generate.py` prints `[rate limit]` to stderr on both its pacing
path and its retry path, stderr was captured, and nothing printed.

## Verdicts

Against the targets I wrote in unit 1, not new ones.

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer (4 of 5) | MET | The chunk holding the answer came back at rank 1 for all five questions, so 5/5 clears the 4/5 target with a whole rank to spare. Measured against chunk text rather than against the answer, because this criterion is about retrieval — `scorer.py::judge` grades the answer and would have been the wrong instrument. |
| 2 | Every answer names a source (5 of 5) | MET | All 15 answers name a filename that was actually retrieved, checked with `scorer.py::names_a_source` rather than by eye. Not close: the failure mode would be an answer naming no file at all, and none did. |
| 3 | Gate stops out-of-corpus questions (4 of 5) | MET | All five out-of-scope questions were refused, and not narrowly — the closest was 0.824 against a 0.55 cutoff, so the nearest miss had 0.27 of margin. This is the least fragile of the five. |
| 4 | Chunk size should be limited (15 of 15) | MET | All 15 retrieved chunks are at most 3 sentences. I am calling it MET because that is what the target said, but the honest reading is that it could not have gone any other way: `chunker.py::split_documents` enforces the limit in code. That is why I revised it in criteria.md, and the revised version — every retrieved chunk names its document's subject — comes out 13 of 15 and MISSES. |
| 5 | Answer comes back under 20 seconds (15 of 15) | MISSED | 4/5, 4/5, 5/5 — 13 of 15. My target was every question on every run, and two calls blew it at 24.879s and 23.395s, so a target that has to hold does not hold. It would have been MET at a 4-of-5 target, which is exactly the kind of "shows up occasionally" the brief warns against, so it stays a miss. |

## Diagnoses

Two misses: criterion 5, and criterion 4 in the form I revised it to.

### Criterion 5 — stage: generation

Both failures were questions that ran *fast* on the other two passes, so
neither the question, its chunks, nor the prompt can be the cause:

| | run 1 | run 2 | run 3 |
|---|---|---|---|
| Q1 generation | **24.879s** | 0.631s | 0.785s |
| Q5 generation | 0.511s | **23.395s** | 0.402s |

Retrieval in those same two calls took 0.442s and 0.023s, so the whole
overrun is inside `generate.py::answer_from_chunks`. The two have different
mechanisms and only one of them is my code:

- **Q1 run 1 was the first API call of the process.** `generate.py::_get_client`
  builds the client lazily — it imports `google.genai` and constructs
  `genai.Client` on first use, and that happens inside the region
  `measure_latency.py::timed_once` is timing. The 24.879s is an SDK import
  plus client construction plus one round-trip, not one round-trip. The same
  question cost 0.631s on the next pass, once the client existed.
- **Q5 run 2 has no such explanation.** Steady state, mid-run, 23.395s, and
  the same question took 0.511s and 0.402s either side of it. Not a rate-limit
  pause: `generate.py` prints `[rate limit]` to stderr on both its pacing path
  (line 99) and its retry path (line 260), stderr was captured, and nothing
  printed. I am recording this as service-side tail latency with the cause
  unknown rather than guessing at a mechanism I cannot show.

The first of those is a flaw in how I measured rather than in the pipeline,
which makes criterion 5 a revision candidate on the same grounds as criterion
4: it should exclude one-time client construction the way it already excludes
rate-limit pauses.

### Criterion 4 (revised) — stage: chunking

`chunker.py::split_documents` batches sentences three at a time with **no
overlap**, and each document's subject lives only in its heading line, which
is part of the first sentence and therefore lands in chunk 0. Every chunk
after the first carries facts with no subject attached to them. That is 49 of
141 chunks in the index, and 2 of the 15 my five questions retrieve:

```
housing_morrow_house.txt  heading="Morrow House — what it's actually like"
  chunk 1: "The good: cheapest housing tier by about $900 a year, and the
            singles are real singles. The bad: known damp problem on the
            ground floor; two rooms were taken offline in 2024. Laundry
            costs $1.50 wash, $1.25 dry, coin or card."
```

The words "Morrow House" appear nowhere in it. That chunk comes back at rank 2
for my laundry question, so a price reaches the model with no building
attached — and three other buildings have near-identical laundry documents,
one of which (`housing_old_brewhouse_laundry.txt`) also charges $1.50 for a
wash. Nothing in the chunk itself would let the model tell them apart.

### The pattern

The pattern is about my criteria, not my code: **both misses sit on either
side of retrieval, and nothing that touches retrieval missed.** Criterion 1
got the answer at rank 1 for 5 of 5. Criterion 3 refused all five out-of-scope
questions with 0.27 of margin. Criterion 4's original could not fail at all.
Four of my five criteria were pointed at the strongest stage of the pipeline,
and the two things that did break — chunks that lose their subject, and one
slow network call — are the stages immediately before and after it, which
nothing I wrote was watching.

### Were my targets set low

Three of the five, and I can say which and to what.

- **Criterion 1** asks only that *a* retrieved chunk contain the answer. All
  three wrong-building laundry chunks can come back alongside the right one
  and it still passes, which is exactly the situation Q4 is in. I would
  tighten it to: the answer-bearing chunk is rank 1, **and** no chunk in the
  top 3 gives a conflicting value for the same fact. That misses today on Q4.
- **Criterion 3** passed with 0.27 of margin, which means it was never going
  to tell me anything. I would replace the count with a margin: every
  out-of-scope question above 0.75, not merely above the 0.55 cutoff.
- **Criterion 4's original** was unfalsifiable, which is why it is revised in
  criteria.md rather than merely unmet.

Criteria 2 and 5 I would leave where they are. Criterion 2 is a genuine
all-or-nothing property, and criterion 5's 20 seconds was loose on purpose —
it missed, and the miss was informative.

## The Improvement

**What I changed:** One change, in `chunker.py::split_documents`: every chunk
after the first now carries its document's heading line at the top of it. A
new helper, `chunker.py::document_heading`, pulls the first line of a document
and ignores it if it looks like a sentence rather than a heading. Nothing else
moved — same corpus, same embedding model, same `TOP_K = 3`, same 0.55 cutoff,
same questions, same scorer.

Before and after, the same chunk:

```
housing_morrow_house.txt#1  — before
  The good: cheapest housing tier by about $900 a year, and the singles are
  real singles. The bad: known damp problem on the ground floor; two rooms
  were taken offline in 2024. Laundry costs $1.50 wash, $1.25 dry, coin or card.

housing_morrow_house.txt#1  — after
  Morrow House — what it's actually like
  The good: cheapest housing tier by about $900 a year, and the singles are
  real singles. The bad: known damp problem on the ground floor; two rooms
  were taken offline in 2024. Laundry costs $1.50 wash, $1.25 dry, coin or card.
```

**Why I picked it:** My chunking diagnosis named this exact mechanism — no
overlap plus subject-only-in-the-heading meant 49 of 141 chunks carried facts
with nothing saying what they were about — and prefixing the heading is the
smallest change that puts the subject back.

Note that unit 1's Sample Chunks section above shows chunks from *before* this
change, which is why those five have no heading repeated in them. I left them
as they were rather than regenerating them.

### Run Log — After

`python run_eval.py --label after` →
[results/run_2026-09-29_1959_after.md](results/run_2026-09-29_1959_after.md),
plus `check_chunks.py` and `measure_latency.py` for criteria 4 and 5.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunk size should be limited | 15 of 15 | 15/15 | 15/15 | 15/15 | MET |
| 4b. *(revised)* Chunk names its subject | 15 of 15 | 15/15 | 15/15 | 15/15 | MET |
| 5. Answer comes back under 20 seconds | 15 of 15 | 5/5 | 5/5 | 5/5 | MET |

Side by side with before:

| Criterion | Before | After |
|---|---|---|
| 1. Retrieved chunk contains the answer | 5/5 MET | 5/5 MET |
| 2. Every answer names a source | 5/5 MET | 5/5 MET |
| 3. Gate stops out-of-corpus questions | 5/5 MET | 5/5 MET |
| 4. Chunk size should be limited | 15/15 MET | 15/15 MET |
| 4b. *(revised)* Chunk names its subject | **13/15 MISSED** | **15/15 MET** |
| 5. Answer comes back under 20 seconds | **13/15 MISSED** | **15/15 MET** |

**Criterion 4b**, `python check_chunks.py --subject`:

```
141 chunks · 0 never name their document's subject

-> 141 of 141 chunks in the index name their subject
-> 15 of 15 RETRIEVED chunks name their subject
```

**Criterion 1**, `python app.py retrieve "How much is a wash cost for Morrow house?"`
— the question the diagnosis was about:

```
#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.1834     housing_morrow_house.txt         Morrow House — what it's actually like The good: che...
2   0.2504     housing_morrow_house_laundry.txt Laundry in Morrow House  Machines take $1.50 wash, $...
3   0.3960     housing_morrow_house_laundry.txt Laundry in Morrow House Sunday after 6pm you will wa...

Gate: best distance 0.183 is under the 0.55 cutoff
```

**Criterion 3**, produced by `run_eval.py::check_out_of_scope`:

```
| What is the capital of Mongolia? | 0.824 | refused |
| How do I change the oil in a diesel engine? | 0.849 | refused |
| Who won the 1994 World Cup? | 0.886 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.844 | refused |
| How do I write a for loop in Rust? | 0.871 | refused |
  -> gate refused 5 of 5
```

**Criterion 5**, produced by `measure_latency.py::main`:

```
Run 1  -> 5 of 5 under 20s (slowest 12.778s, median 0.611s)
Run 2  -> 5 of 5 under 20s (slowest  0.652s, median 0.626s)
Run 3  -> 5 of 5 under 20s (slowest  2.728s, median 0.585s)
```

**Did it help?**

Yes for the criterion it was aimed at, and I can show the mechanism rather
than just the number. Criterion 4b went from 13/15 to 15/15, and the two
questions whose chunks had been missing their subject are the two whose
distances moved:

| Question | Best distance before | after |
|---|---|---|
| Q1 printing quota | 0.1926 | 0.1926 |
| Q2 walk from Fenwick Court | 0.1926 | 0.1926 |
| Q3 whiteboards | 0.3966 | 0.3966 |
| **Q4 Morrow House wash** | **0.2504** | **0.1834** |
| **Q5 hours worked per week** | **0.3679** | **0.2241** |

Three questions did not move at all, which is what I would expect: their
answers were already in first chunks, and first chunks were not touched. The
two that moved are exactly the two whose answer lived in a later chunk. The
out-of-scope questions moved slightly *further* away (0.874 → 0.886,
0.833 → 0.844), so the gap the 0.55 cutoff sits in got wider rather than
narrower.

The better evidence is what came back rather than how far away it was. Before
the change, the top 3 for the Morrow House question were Morrow House,
Morrow House, and **Innisfree Hall** — a different building charging $1.75.
After it, all three are Morrow House documents. The wrong-building distractor
is out of the prompt entirely.

**Criterion 5 also went from MISSED to MET, and I do not think my change
caused that.** Nothing I touched is in the generation path, and the two
failures I diagnosed were a one-time client construction inside my timing
region and one unexplained 23-second API call. Neither recurred this time —
the first call cost 1.248s instead of 24.879s. That is the same measurement
finding a quieter network, not an improvement. Reporting it as a win would be
claiming credit for noise.

**One thing got worse, and it is my scorer rather than my system.**
`run_eval.py` marked Q5 as `fail` on runs 1 and 3, and the answers are right:

```
run 1: The maximum number of hours you can work per week on campus is 20 hours.
       Source: money_jobs.txt
run 2: The maximum on-campus work is 20 hours a week during the term (from money_jobs.txt).
```

My `expects` is "20 hours a week during term", and `scorer.py::judge` requires
every key word from `expects` to appear. Runs 1 and 3 say "20 hours" and stop,
so they fail a rule I wrote specifically to avoid failing correct answers. The
before-run happened to phrase all three the same way and hid this. I have left
the scorer alone rather than fixing it mid-experiment, because changing the
instrument between the before and after runs would make the two logs
incomparable — but it means the run log's own pass/fail column reads 13/15
where the answers were 15/15 correct.

## What's Still Broken

No criterion is still missed, which is not the same as nothing being left.
Four things are open, and the first two are the ones that would bite a real
user.

**My scorer fails correct answers.** `scorer.py::judge` requires every key
word from `expects` to appear in the answer, so "20 hours" fails against
"20 hours a week during term" even though it answers the question. It cost me
two cells in the after log. The fix is to stop treating `expects` as one
string: mark which part is the fact that must appear ("20 hours") and which
part is context that may or may not ("a week during term"). I stopped because
changing the scorer between the before and after runs would have made the two
logs incomparable, and comparability was worth more this unit than two cells.
This is the first thing I would do next unit.

**Criterion 5's measurement includes a cost that is not the pipeline's.**
`measure_latency.py::timed_once` times the first call of the process with the
`google.genai` import and client construction inside it, which is what made
the before-run's 24.879s. The fix is one throwaway call before timing starts,
the same way the criterion already excludes rate-limit pauses. I did not do it
this unit for the same comparability reason, and because leaving it in gave me
a second observation of the same artifact.

**The chunker's notion of a heading is a guess.** `chunker.py::document_heading`
takes the first line and rejects it if it ends in a full stop or runs past 80
characters. That happens to be right for all 88 documents in `campus_life`,
because they are forum posts with titles. On a corpus without titles it would
prefix the first sentence of every document to every chunk, which is worse
than doing nothing. I stopped here because this is the corpus I have and I
would rather ship a rule I have checked than a general one I have not.

**Nothing measures whether the retrieved set is self-consistent.** Criterion 1
passes as long as *a* chunk holds the answer, so a top-3 containing both
"$1.50" for Morrow House and "$1.75" for Innisfree would pass while handing the
model two answers to the same question. My change happened to clear the
distractors out of Q4's top 3, but nothing in my criteria would have told me
if it hadn't. That is the criterion I would add next, and it is written up
below.

## What I'd Do Differently

Three of the five, and the pattern is the same each time: I wrote criteria
about the stage that was already working.

**Criterion 1** is the one I would change first. "The retrieved chunks include
one that contains the answer" passes even when the other two chunks contradict
it, which is the actual failure mode of this corpus — four buildings with
near-identical laundry posts, two of them charging the same $1.50. I would
write it as: the answer-bearing chunk is rank 1, **and** no other chunk in the
top 3 gives a different value for the same fact. That would have failed before
my change and passed after it, which is exactly what a criterion aimed at my
diagnosis should do. As written, criterion 1 read 5/5 both times and told me
nothing.

**Criterion 3** passed with 0.27 of margin — the closest out-of-scope question
was 0.824 against a 0.55 cutoff. A criterion that cannot get close to failing
is not measuring anything. I would replace the count with the margin: every
out-of-scope question at least 0.20 above the cutoff. Then the number moves
when something changes, and I would notice a corpus or an embedding model that
narrowed the gap before it started letting questions through.

**Criterion 4** I already revised, and the revision is the one I would keep. Its
original form asked for something `chunker.py` enforces in code, so it could
not fail; the revised form asks whether a chunk names its own subject, which
could fail, did fail at 13/15, and named the fix.

What I would keep: criterion 2, which is genuinely all-or-nothing, and
criterion 5's 20 seconds, which was loose on purpose and still missed — the
loose target is what made the miss informative rather than noise. And I would
write at least one criterion per stage next time. Four of my five pointed at
retrieval and embedding, and both things that actually broke were in chunking
and generation, on either side of the part I was watching.
