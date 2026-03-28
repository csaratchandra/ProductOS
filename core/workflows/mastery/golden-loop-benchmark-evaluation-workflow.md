# Golden Loop Benchmark Evaluation Workflow

Purpose: Define and refresh the `pm_superpower_benchmark` so V4 progress is judged by measured PM leverage across the first three golden loops rather than by artifact count.

## Inputs

- `pm_benchmark`
- `superpower_benchmark`
- recent `feature_scorecard` outputs for the slices affecting the active loop
- current golden-loop source artifacts such as `problem_brief`, `concept_brief`, `prd`, `increment_plan`, `release_readiness`, `feedback_cluster_state`, `gap_cluster_state`, and `improvement_loop_state`
- manual timing notes or benchmark observations where automation is incomplete
- current V4 scope and validation-tier policy

## Outputs

- `pm_superpower_benchmark`
- benchmark review summary
- benchmark-to-feature alignment note
- revise / continue recommendation for the active V4.0 slice

## Operating Sequence

1. Lock the active baseline version, candidate version, and review window.
2. Confirm the three golden loops being measured and the PM question for each loop.
3. Capture baseline values from the latest validated ProductOS evidence and any required manual timing observations.
4. Set explicit success thresholds for speed, rewrite reduction, alignment quality, and improvement-loop closure.
5. Assign the validation tier and required lanes before the benchmark is considered decision-ready.
6. Run AI review for logic and traceability, AI test checks for schema and regression coverage, and targeted manual validation for whether the thresholds are meaningful.
7. Compare the benchmark movement against the latest feature scorecards so a strong local feature score does not fake loop-level success.
8. Record continue, revise, hold, or fail guidance for the next bounded V4 slice.

## Rules

- do not claim V4 progress unless at least one golden-loop metric moves against the locked baseline
- do not let a good feature score override a weak benchmark result or vice versa
- keep evidence refs tied to approved artifacts rather than side-channel notes
- if manual measurement is still required, say so explicitly instead of implying a complete automated benchmark
- if a proposed V4 slice does not map to one of the golden loops, cut or defer it
- benchmark changes should update the next review date rather than silently shifting the baseline
