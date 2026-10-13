# The persona generator

**The product is the generator.** A panel judges your work as the people in it, so those people must be
your buyers. The generator builds them from your project: consumer buyers, or a B2B buying committee.
`examples/personas/` holds a complete worked panel, so that you can see the shape of a good persona
file.

The method comes from *Scaling Synthetic Data Creation with 1,000,000,000 Personas*
(**arXiv:2406.20094**, Tencent AI Lab). The two operations below are theirs. Their dataset is not bundled
here. It is CC BY-NC-SA, and its one-line descriptors are thinner than a persona that you build from your
own material.

## Text-to-persona. Sweep and extract.

Read the context that you can reach. Extract personas as **roles in a buying decision**, never as
demographics:

- who **benefits** if this works
- who **pays** for it
- who **blocks** it, and on what grounds
- who is **served today** by the thing that they use instead
- who **already left**, and why

Age, city and job title are set dressing. What predicts an answer is the person's position in the
decision, and what it costs them to be wrong.

A consumer product has the same roles in fewer people. The same person benefits and pays. The blocker
is the habit, the free alternative, or the partner who sees the bank statement.

## Persona-to-persona. Build the rest of the room.

You usually find one person clearly. It is the champion, because the champion is the one who writes
things down. Derive the others from them. Given a champion, who signs? Who has to change their workflow?
Whose budget shrinks if the company adopts this? Who recommended the current solution and has to admit
that they were wrong?

This operation makes a buying committee out of thin context, and it is where most of the value of a
synthetic panel comes from. The blocker that you did not model is the objection that you did not plan
for.

## Start from the project. Ask only for what is missing.

The user's project usually tells you what the product does, who it is for and what it costs. Use that
first. If you cannot name who pays, what they use today or why they would say no, ask the user the
questions in `AGENTS.md` step 2. A panel that you build from the project and the answers carries the
label `hypothesis — grounded`.

## Markets and segments

The same role answers differently in a different market. To compare markets or segments, build the same
roles one time for each, with that market's situation, current alternative and objections. Run the same
material on each set, and compare the answers role against role.

## Ground every persona that you can

Use at least one **verbatim line** from a buyer per persona, where a real source exists. Quote it in the
persona file. The product's own copy is not buyer language. A persona with no buyer line is marked
`hypothesis` and carries that label into every output that it appears in.

Real sources include the user's own customers and the public market: call transcripts, support threads
and emails, and also reviews of the current solution and forum threads about the problem. Record the
source in the persona file.

Grounding is the user's strongest lever. The fidelity label tells them how far they pulled it.

## Build a pool, compose per run

Build a pool of 6 to 9 personas where the context supports it, with **at least two skeptics** and **at
least three distinct roles**. Four is enough to start. Each run uses 3 to 5 of them, with **at least one
skeptic** and **at least two distinct roles**, and `panel` rotates them. A persona used in the last two runs sits out the next one, unless the pool is too small. Rotation
means that a revised draft meets fresh readers.

The constraint that matters is the skeptic. A panel that can say no gives its yes a meaning.

## Persona file shape

```markdown
# <slug>

name: <first name, an age if it helps you hear them>
cluster: <one short word for their seat in the decision: user, payer, blocker, or your own>
role_and_context: <their position in the buying decision, and the life or company around it>
current_situation: <what they are dealing with right now>
current_alternative: <what they use for this today — the real competitor is usually this, not a product>
objection_pattern: <what makes them say no>
skepticism: <1-10>
signature_phrase: <something they would actually say, verbatim from source if you have one, no quotes>
grounding: evidence-anchored | hypothesis
source: <where the verbatim line came from, or "none — hypothesis">
```

The fields map slot for slot onto `prompts/worker.md`, and the prompt speaks to the persona as "you".
`role_and_context` comes directly after "You are <name>.", so write every field as a fragment with no
pronoun: "Bootstrapped founder, two co-founders, fourteen months in." Run `panel --dry-run` to read a
prompt as the persona receives it.

A persona with `skepticism` of 7 or more counts as a skeptic. `cluster` is what "distinct roles" counts,
so personas in the same seat share a cluster. Prose below the fields, such as the `What changes their
mind` section in the examples, is a note for you and the user. The worker prompt does not include it.

`signature_phrase` is load-bearing. The worker prompt tells the persona to use it verbatim. If the phrase
is absent from the returned reaction, the persona drifted into generic-assistant voice in the middle of
the answer.

## A persona always comes from context

The project, the user's answers and real buyer sentences are context. If you have none of them, ask the
questions first. Five personas invented from nothing agree with each other about a market that none of
them saw.
