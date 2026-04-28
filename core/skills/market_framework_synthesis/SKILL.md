# Market Framework Synthesis

## Purpose

Select and apply the smallest useful market framework set for a bounded PM decision.

## Trigger / When To Use

Use when `market_analysis_brief`, `market_sizing_brief`, or `market_share_brief` work risks becoming generic summary instead of decision support.

## Inputs

- market evidence and competitor evidence
- current problem, concept, or strategy context
- framework registry or explicit decision scope

## Outputs

- selected framework rationale
- explicit framework-to-artifact mapping
- market synthesis that explains why the chosen framework fits

## Guardrails

- do not use more frameworks than the decision requires
- keep sizing and market narrative separate when confidence differs
- preserve evidence gaps instead of smoothing them over

## Execution Pattern

1. restate the decision the market work must support
2. choose the framework set with explicit applicability logic
3. synthesize only the conclusions that the chosen framework can support
4. record remaining gaps and what would change the recommendation

## Validation Expectations

- framework choice should be explainable in one paragraph
- outputs should feel decision-oriented rather than encyclopedic
- evidence gaps should remain visible
