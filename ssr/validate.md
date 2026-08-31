# Anchor validation harness

Any anchor set must clear **rho ≥ 0.70 on two independent runs** before its input type switches to SSR.

## Method

1. Elicit per-axis free text from ≥3 personas × ≥6 independent reps on a real stimulus.
   One answer per axis, each answering only its own question. No numbers anywhere.
2. Rate each answer two ways:
   - **SSR** — `rate.py` with that type's anchor file.
   - **Referee** — a model given *the same five anchors*, asked which the speaker is closest to.
     Do NOT use a generic "1=negative, 5=positive" referee; it is meaningless for non-polar axes and
     understates rho by ~0.3.
3. Spearman rho between the two, pooled and per axis.
4. Per-axis rho is the diagnostic. A single axis near 0 or negative means that axis is asking about the
   **artifact** rather than the respondent — see the boundary finding in `../SSR-RETROFIT.md`.

## Anchor law

All five anchors for an axis share the same register and topic vocabulary. Only stance varies.
An anchor set whose positive end echoes the stimulus vocabulary while its negative end does not will
score skeptics as enthusiasts — measured, not theoretical.
