# The persona generator

**The product is the generator, not a pool.** This repo ships no personas of its own to run your work past,
because a persona built from someone else's business tells you nothing about yours. `examples/personas/`
holds a worked example so you can see the shape; it is not a panel for you to use.

Method borrowed from *Scaling Synthetic Data Creation with 1,000,000,000 Personas*
(**arXiv:2406.20094**, Tencent AI Lab) — the two operations below are theirs. Their **dataset** is not
bundled and should not be: it is CC BY-NC-SA, and its one-line web-derived descriptors would install the
thinnest tier of the fidelity ladder at industrial scale, which contradicts the entire premise.

## Text-to-persona · sweep and extract

Read whatever context you can reach. Extract personas as **roles in a buying decision**, never as
demographics:

- who **benefits** if this works
- who **pays** for it
- who **blocks** it, and on what grounds
- who is **served today** by whatever they use instead
- who **already left**, and why

Age, city and job title are set dressing. What predicts an answer is the person's position in the decision
and what it costs them to be wrong.

## Persona-to-persona · build the rest of the room

You will usually find one person clearly — the champion, because they are the one who writes things down.
Derive the others from them. Given a champion, who signs? Who has to change their workflow? Whose budget
shrinks if this is adopted? Who recommended the incumbent and would have to admit they were wrong?

This is the operation that makes a buying committee out of thin context, and it is where most of the value
of a synthetic panel actually comes from — the blocker you had not modelled is the objection you had not
planned for.

## Ground every persona you can

At least one **verbatim line** from a real source per persona, where a real source exists. Quote it in the
persona file. A persona with no verbatim reference statement is marked `hypothesis` and carries that label into every
output it appears in.

This is the user's lever, not the tool's. The tool cannot manufacture validity. It can only be honest about
how much it has, which is what the fidelity label is for.

## Compose per run

3–5 personas, with **at least one skeptic** and **at least two distinct roles**. Rotate — a persona used in
the last two runs sits out the next one unless the pool is too small, so consecutive runs on a revised draft
do not just replay the same reaction.

The constraint that matters is the skeptic. A panel that cannot say no has told you nothing when it says yes.

## Persona file shape

```markdown
# <slug>

name: <first name, an age if it helps you hear them>
role_and_context: <their position in the buying decision, and the company around it>
current_situation: <what they are dealing with right now>
current_alternative: <what they use for this today — the real competitor is usually this, not a product>
objection_pattern: <what makes them say no>
skepticism: <1-10>
signature_phrase: "<something they would actually say, verbatim from source if you have one>"
grounding: evidence-anchored | hypothesis
source: <where the verbatim line came from, or "none — hypothesis">
```

The fields map slot-for-slot onto `prompts/worker.md`. `signature_phrase` is load-bearing: the worker is told
to use it verbatim, and its absence from the returned reaction is how you detect a persona that drifted
into generic-assistant voice mid-answer.

## When there is nothing to build from

Say so. A panel of five personas invented from a homepage will produce five confident, articulate, mutually
reinforcing opinions about a market none of them have seen, and you will not be able to tell from the
output that this is what happened.

Anyone in that position needs an ICP exercise or a conversation with a real buyer, and both of those beat
anything this repo can do for them today.
