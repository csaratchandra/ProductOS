# Feature Scoring Model

Purpose: Define how ProductOS scores a feature slice after dogfood use so the next version is judged by real PM leverage rather than by artifact count.

## Core Rule

Every meaningful feature slice should produce a `feature_scorecard` after dogfood review.

The scorecard is not a replacement for `pm_superpower_benchmark`.

The scorecard is the stage-level check that says whether one feature is truly superpower-grade yet.

The benchmark remains the cross-loop proof that ProductOS is improving over time.

## Required Dimensions

Score every feature on these five dimensions:

- `pm_leverage`
- `output_quality`
- `reliability`
- `autonomy_quality`
- `repeatability`

Each dimension is scored from `1` to `5`.

## Score Meaning

- `5`: superpower level; promote as the current standard
- `4`: strong and internally usable; keep active, but route the remaining gaps into feedback
- `3`: useful but not claim-worthy; route to the improvement loop before counting it as done
- `2`: partial and manual-heavy; redesign or narrow the slice
- `1`: broken, misleading, or demo-only; block

## Routing Rule

Any score below `5` must produce explicit `feedback_items`.

- `4` may remain in internal use if the slice is non-blocking
- `3` or below should not count toward ProductOS superpower claims
- `1` or `2` should usually block promotion

Every sub-`5` gap should route into the existing loop:

1. log or update the issue in `productos_feedback_log`
2. cluster repeated pain in `feedback_cluster_state`
3. route accepted work through `improvement_loop_state`
4. rescore the feature after the next bounded dogfood pass

## Relationship To Benchmarks

Use `feature_scorecard` to answer:

- is this specific feature good enough right now
- what is stopping it from becoming `5/5`
- what should feed the next improvement slice

Use `pm_superpower_benchmark` to answer:

- are the golden loops actually improving
- is ProductOS compounding PM leverage over time

Do not use benchmark movement to hide weak feature quality.

Do not use a good feature score to fake benchmark movement that has not happened.
