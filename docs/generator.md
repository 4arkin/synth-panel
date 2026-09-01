# The persona generator

**The product is the generator, not a pool.** This repo ships no personas of its own for you to
judge your work with. A persona built from someone else's business tells you nothing about yours.
`examples/personas/` holds a worked example so that you can see the shape. It is not a panel for you to
use.

The method comes from *Scaling Synthetic Data Creation with 1,000,000,000 Personas*
(**arXiv:2406.20094**, Tencent AI Lab). The two operations below are theirs. Their **dataset** is not
bundled here and must stay out. It is CC BY-NC-SA, and its one-line web-derived descriptors install the
thinnest tier of the fidelity ladder at industrial scale, which contradicts the entire premise.

## Text-to-persona. Sweep and extract.

Read whatever context you can reach. Extract personas as **roles in a buying decision**, never as
demographics:

- who **benefits** if this works
- who **pays** for it
- who **blocks** it, and on what grounds
- who is **served today** by whatever they use instead
- who **already left**, and why

Age, city and job title are set dressing. What predicts an answer is the person's position in the
decision, and what it costs them to be wrong.

## Persona-to-persona. Build the rest of the room.

You usually find one person clearly. It is the champion, because the champion is the one who writes
things down. Derive the others from them. Given a champion, who signs? Who has to change their workflow?
Whose budget shrinks if the company adopts this? Who recommended the incumbent and has to admit that
they were wrong?

This operation makes a buying committee out of thin context, and it is where most of the value of a
synthetic panel comes from. The blocker that you did not model is the objection that you did not plan
for.

## Ground every persona that you can

Use at least one **verbatim line** from a real source per persona, where a real source exists. Quote it
in the persona file. A persona with no verbatim line is marked `hypothesis` and carries that label into
every output that it appears in.

This is the user's lever, not the tool's. The tool cannot manufacture validity. It can only be honest
about how much it has, which is what the fidelity label is for.

## Compose per run

Use 3 to 5 personas, with **at least one skeptic** and **at least two distinct roles**. Rotate them. A
persona used in the last two runs sits out the next one, unless the pool is too small. Rotation stops
consecutive runs on a revised draft from replaying the same reaction.

The constraint that matters is the skeptic. A panel that cannot say no has told you nothing when it says
yes.

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

The fields map slot for slot onto `prompts/worker.md`. `signature_phrase` is load-bearing. The worker
prompt tells the persona to use it verbatim. If the phrase is absent from the returned reaction, the
persona drifted into generic-assistant voice in the middle of the answer.

## When there is nothing to build from

Say so. A panel of five personas invented from a homepage produces five confident, articulate and
mutually reinforcing opinions about a market that none of them saw. You cannot tell from the output that
this is what happened.

Anyone in that position needs an ICP exercise or a conversation with a real buyer. Both of those beat
anything that this repo can do for them today.
