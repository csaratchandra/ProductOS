# Presentation Quality Auto-Check Model

Purpose: Define automatic quality checks applied to every generated presentation slide to ensure consulting-grade output — action titles, pyramid principle, MECE structure, evidence placement, skimmability, and visual consistency.

## Required Checks (Per Slide)

| Check | Rule | Auto-Detection |
|---|---|---|
| Action Title | Slide title is a complete sentence communicating the insight, not a topic label. "Q2 revenue grew 23% driven by enterprise segment" not "Q2 Revenue." | Detect: if title is a noun phrase (no verb), flag. Minimum 5 words. |
| One Message | Each slide communicates exactly one key message. Supporting evidence is subordinate. | Detect: if >3 distinct claims in body text, flag. |
| Pyramid Principle | Executive reads titles only → gets the complete narrative. Body supports titles. | Detect: generate title-only summary. Check if it makes sense as standalone narrative. |
| MECE Structure | Slides are Mutually Exclusive and Collectively Exhaustive for the topic scope. | Detect: check for overlapping content across slides. Check for gaps in coverage. |
| Evidence Placement | Every data point has a visible source citation. | Detect: scan for numbers without source annotations. |
| Skimmable | Content hierarchy: title (read first) → visual/data (glance) → body text (read if interested) → evidence note (read if skeptical). | Detect: check content structure follows hierarchy order. |
| Visual Consistency | Fonts, colors, spacing, alignment consistent with design token set. | Detect: validate CSS against design token references. |
| Audience Fit | Content matches audience mode (executive: answer-first, team: operating detail, customer: no internal-only). | Detect: scan for internal-only markers in customer-mode decks. |

## Minimum Publish Bar

- All slides pass action title check
- Title-only narrative is coherent and complete
- Every data point has source citation
- No slide has >3 distinct claims
- Audience-specific content gating applied
