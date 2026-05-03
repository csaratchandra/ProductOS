# Demo Video Script Generation

## 1. Purpose

Generate structured demo video scripts with timestamped segments, visual descriptions, audio narration, key moments, opening hook, and closing CTA — optimized for 3-5 minute product demonstrations.

## 2. Trigger / When To Use

Product launch approaching. Sales demo needed. Marketing video content planned. PM presenting product externally.

## 3. Prerequisites

- Relevant upstream artifacts for the skill domain
- Evidence sources (source note cards, research artifacts, competitive data)
- Defined scope from PM or mission context

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `primary_input` | `object` | Upstream artifact schemas | Yes | Core input for the skill |
| `context` | `array[object]` | Supporting artifacts | No | Additional context |

## 5. Execution Steps

1. Define audience and goal: Who is watching? What do they need to believe after watching?
2. Write opening hook: First 15 seconds — capture attention. State the problem the viewer experiences. Hint at the solution. Do not start with "Hi, I'm X from Company Y."
3. Structure segments: 3-5 segments showing key workflows. Order: most impactful first (viewer may not watch entire video). Each segment: visual description (what's on screen), audio narration (what speaker says), key message (what viewer should remember), timestamp and duration.
4. Show, don't tell: Every audio claim should have a corresponding visual. "ProductOS generates competitive analysis in 90 seconds" → show the 90-second scan in action.
5. Include real data: Prototypes and dashboards shown with realistic data, not lorem ipsum.
6. Write closing CTA: Specific next step. "Start free trial at productos.dev" with urgency if appropriate.
7. Keep to time: Target 3-5 minutes. If longer, cut secondary segments or shorten transitions.

## 6. Output Specification

Primary output: `demo_video_script` artifact

## 7. Guardrails

- Narration describes what viewer can already see: "As you can see, I'm clicking the button" → fix. Narration should explain WHY, not WHAT.
- Too long: >5 minutes → cut. Viewer attention drops 50% after 2 minutes, 80% after 5 minutes.
- When to escalate: Product is not stable enough for a demo — feature behavior may change before video ships. Prototype quality <4/5 — not suitable for external demo.

## 8. Gold Standard Checklist

- [ ] Opening hook is <15 seconds and doesn't start with introduction
- [ ] Every audio claim has a corresponding visual
- [ ] Key message per segment is one sentence the viewer should remember
- [ ] Total duration 3-5 minutes
- [ ] Framework: demo video best practices, Apple keynote presentation style
- [ ] Framework alignment: Demo video best practices, presentation design, storytelling
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: prototype_html_generation, messaging_house_construction, persona_narrative_generation
- **Downstream skills**: marketing content, sales enablement, launch communication
- **Schemas**: demo_video_script.schema.json

## 11. Maturity Band Variations

| Band | Depth |
|---|---|
| 0→1 | Exhaustive: full depth with qualitative exploration |
| 1→10 | Deep: comprehensive coverage |
| 10→100 | Standard: focused on highest-impact outputs |
| 100→10K+ | Focused: data-driven, portfolio-level |

## 12. Validation Criteria

- **Schema conformance**: validates against associated artifact schemas
- **Test file**: TBD in validation sprint
- **Example fixture**: associated `.example.json` files
