# Artifact To Visual Rendering Workflow

Purpose: Convert structured ProductOS artifacts into high-clarity visuals that support decisions, alignment, and agent transparency without distorting the source message.

## Inputs

- structured source artifacts such as `presentation_brief`, `portfolio_state`, `workflow_state`, `artifact_trace_map`, `issue_log`, and `visual_map_spec`
- audience and rendering context
- visual style system

## Outputs

- visual rendering brief
- audience-specific visual spec
- `visual_map_spec`
- optional `render_spec`, `slide_spec`, and `ppt_export_plan`
- optional slide, memo, dashboard, or workshop-board rendering

## Rules

- visuals must preserve the meaning of the source artifact
- choose the smallest visual that explains the decision or system clearly
- choose the map family that matches the decision: roadmap, journey, process, workflow, capability, product, feature, mind map, SWOT, or impact-effort
- reuse shared visual primitives first: `map_canvas` for staged or networked maps and `matrix_map` for two-axis prioritization or strategy views
- make workflow state, blocked points, and handoffs visible when operational clarity matters
- adapt the same visual source across slide, memo, dashboard, and customer-safe forms where needed
- keep native-shape export intent explicit in `ppt_export_plan` so PPT output does not collapse all maps into generic bullet slides
- escalate when the requested visual would overstate certainty or hide risk
