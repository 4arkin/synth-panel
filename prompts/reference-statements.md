# Reference-statement generator prompt

Fill every `{{slot}}` and dispatch. The answer is written per axis, in the stimulus's own
vocabulary, which is the whole reason this is generated rather than shipped.

---

You are writing the measuring scale for a survey instrument. Precision matters more than style.

## What is being judged

{{stimulus}}

## The question being asked

{{question}}

## Your job

Write **five statements**, one for each point of a 1-5 scale, that a respondent might say in answer to
that question about that specific thing.

1 = the most negative position anyone could hold
2 = mildly negative
3 = genuinely undecided
4 = mildly positive
5 = the most positive position anyone could hold

## The rule that makes this work, and breaks it if you get it wrong

**All five statements must use the same vocabulary and the same register. Only the STANCE may change.**

The statements get compared against a real answer by meaning-similarity. If your statement 5 uses the
words from the thing being judged and your statement 1 does not, then any answer that mentions the
subject at all will look like statement 5 — and a person saying "this is useless" will be scored as
enthusiastic. That is the single most common way this fails, and it is invisible once it happens.

Concretely:
- Name the same specific things in all five. If statement 5 says "the audit report files itself", then
  statement 1 says "the audit report filing solves nothing I care about" — not "I don't like it".
- Keep the sentence length and formality identical across all five.
- Do not make 1 and 2 shorter or vaguer than 4 and 5. That asymmetry is the failure.
- Write them in the first person, about the speaker's own position. Never about the artifact's
  qualities — not "this is unclear", but "I would not act on this".

## Return exactly this, as the last thing you write, in a fenced json block

```json
{
  "statements": [
    "<point 1, most negative>",
    "<point 2>",
    "<point 3, undecided>",
    "<point 4>",
    "<point 5, most positive>"
  ],
  "shared_vocabulary": "<the specific words from the stimulus you used in all five>"
}
```
