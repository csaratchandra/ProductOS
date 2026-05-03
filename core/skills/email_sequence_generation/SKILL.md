# Email Sequence Generation

## 1. Purpose

Generate multi-email sequences for launch announcement, nurture, re-engagement, onboarding, and upsell campaigns — per email with subject line variants, preview text, body copy, CTA, and send timing.

## 2. Trigger / When To Use

Launch approaching. Lead nurture campaign needed. Re-engagement campaign for dormant users.

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

1. Define sequence type and goal: Launch (build excitement → launch → follow-up), Nurture (educate → build trust → convert), Re-engagement (remind → incentivize → win back).
2. Plan email cadence: Per email number, define purpose and send delay from previous.
3. Write subject lines: 2-4 variants per email. Short (mobile-optimized), curiosity-driven, benefit-first. No clickbait.
4. Write preview text: Extends subject line. 40-90 characters. Do not repeat subject line.
5. Compose body: Personalization tokens ({{first_name}}, {{company}}). Benefit-first, not feature-first. Scannable (short paragraphs, bullet points). One clear CTA per email.
6. Define CTA: Specific action. "Start Free Trial →" not "Learn More →".
7. Test against spam triggers: Check for spam words. Verify plain-text version renders correctly.

## 6. Output Specification

Primary output: `email_sequence` artifact

## 7. Guardrails

- Subject line is misleading: Promise not delivered in email body → reject. Breaks trust.
- Too many CTAs: Multiple actions in one email → fix. One email = one CTA. Multiple CTAs reduce conversion.
- When to escalate: Target segment is too small for meaningful campaign (<100 recipients). Sequence type not appropriate (onboarding sequence for product still in development — features not stable).

## 8. Gold Standard Checklist

- [ ] Per email: 2+ subject line variants for A/B testing
- [ ] Preview text complements subject line (not repeats it)
- [ ] Body is scannable (short paragraphs, bullet points where appropriate)
- [ ] One CTA per email
- [ ] Framework: email marketing best practices, conversion copywriting
- [ ] Framework alignment: Email marketing best practices, conversion copywriting, deliverability guidelines
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: messaging_house_construction, persona_narrative_card, segment_map
- **Downstream skills**: launch communication, marketing automation integration
- **Schemas**: email_sequence.schema.json

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
