# PM Benchmarking Model

Purpose: Define how ProductOS measures whether PM capability is improving in credible, repeatable terms rather than through subjective claims alone.

## Benchmark Dimensions

- output quality: quality score across PRDs, status updates, and decision artifacts
- decision quality: clarity of tradeoffs, rationale, and follow-through quality
- speed to insight: time from new input to usable PM recommendation
- rewrite rate: percentage of draft output materially rewritten before use
- operating reliability: rate of blocked publish events, missing owners, and stale evidence incidents

## Benchmark Shape

Each benchmark should include:

- baseline metrics before the intervention or comparison period
- current metrics for the active period
- explicit trend judgment for quality, speed, and rework
- reference examples that represent the target bar
- recommended focus areas for the next review cycle

## Feature Scorecards

Use `feature_scorecard` as the stage-level companion to the benchmark.

The benchmark says whether ProductOS is improving across the golden loops.

The scorecard says whether one specific feature slice is actually `5/5` yet.

Any feature score below `5` should route explicit feedback into the improvement loop rather than hiding behind aggregate benchmark language.

## Evaluation Cadence

- weekly: operational checks on rewrite rate, blocked outputs, and missing-owner events
- monthly: benchmark refresh for output quality and speed-to-insight trends
- quarterly: broader PM growth review with decision quality calibration

## Rule

- benchmark claims should point to observable artifact or workflow evidence
- "world-class" language should always be paired with a concrete reference example
- if current metrics are absent, ProductOS should say the benchmark is incomplete rather than imply improvement
