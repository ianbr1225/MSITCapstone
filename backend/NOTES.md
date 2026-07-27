# RetainIQ — Development Notes

## Part A: Core Logic

The main challenge in this stage was deciding where the risk thresholds
should actually sit, and how to handle the boundary values consistently.
Since `engagement_score` is a continuous 0–100 value but `risk_level` needed
to be one of three discrete categories, an early version of the logic left
the edges of each band ambiguous — it wasn't immediately clear whether a
score of exactly 30 or 65 should round up or down. This was resolved by
explicitly defining each threshold as inclusive on the lower bound (e.g.
`30 <= engagement_score < 65` maps to Medium), and documenting that decision
directly in the function's docstring so it wouldn't need to be re-derived
later from behavior alone.

The second challenge was around Pydantic's response validation. Adding a
`response_model` to the FastAPI endpoint meant that any value the risk
engine produced now had to conform exactly to the `Literal["High","Medium",
"Low"]` type — a plain string typo anywhere in the engine would have caused
a silent 500 rather than a clear error. This was actually a useful forcing
function: it meant catching a mismatch between the engine's output and the
schema during development, rather than after deployment.

## Part B: Testing

Writing the parametrized boundary tests for `compute_risk_level()` surfaced
an edge case that wasn't obvious just from reading the function: an
engagement score of exactly 65 needed a dedicated test case, since it's the
kind of value that's easy to get right by accident and wrong on a later
refactor without anyone noticing. Having the boundary explicitly asserted in
`test_risk_engine.py` means any future change to the thresholds will fail
loudly instead of silently shifting a student's risk category.

The distinction between white-box and black-box testing became concrete
rather than academic once both test files existed side by side. The
white-box tests in `tests/unit/test_risk_engine.py` test the scoring
function directly, with full knowledge of its internal logic — they assert
on the exact threshold values because the thresholds are visible in the
source. The black-box tests in `tests/integration/test_api.py`, by contrast,
only interact with the system the way a real client would: hitting
`/api/risk-list` and checking the HTTP status, response shape, and schema,
without any assumption about how risk levels are computed internally. Having
both in the same suite meant a change to the internal logic (white-box) and
a change to the API contract (black-box) would be caught independently of
one another.

## Part C: Version Control

The project continues to use the two-branch model established in the
architecture phase: `main` is reserved for stable, milestone-ready states,
and `development` holds work in progress. This week's work was built on a
dedicated feature branch (`feature/core-risk-logic`) off `development`,
committed in stages rather than as a single batch, and merged back through
a pull request — consistent with the branching approach documented earlier
in the project.

Tagging each milestone (`v0.1` through `v0.4`) with annotated tags, and
publishing each as a GitHub Release, turns the commit history into something
that can be navigated at the level of *milestones* rather than individual
commits. For a capstone project spanning several weeks, this matters
practically: it means a reviewer — or a future version of the team — can
check out exactly the state of the project as it existed at the end of any
given week, rather than having to reconstruct that from commit dates or
messages alone.