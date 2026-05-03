# Blog Post Brief Generation

## 1. Purpose

Generate SEO-researched blog post briefs with target keywords, search intent analysis, key points, unique angle, competitor content analysis, internal link strategy, and word count targets.

## 2. Trigger / When To Use

Content calendar planning. Marketing content pack generation. PM requests thought leadership content.

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

1. Identify topic from product differentiators: Which capabilities are most differentiated? What questions do PM prospects most frequently ask?
2. Research target keyword: Search volume, competition level, related queries. Select primary keyword.
3. Define search intent: Informational (learning), Commercial investigation (comparing tools), Transactional (buying), Navigational (finding specific resource).
4. Outline key points: 5-7 substantive points. Each point: specific claim with supporting data.
5. Find unique angle: What makes this piece NOT generic? Original data? Beta tester insights? Competitive analysis?
6. Analyze competitor content: What ranks #1 for the target keyword? What does it do well? What does it miss? Opportunity: do what they miss.
7. Define internal link strategy: Link to product pages, feature pages, related blog posts.
8. Write title variants: Working title + 2-3 alternatives. Optimized for CTR.

## 6. Output Specification

Primary output: `blog_post_brief` artifact

## 7. Guardrails

- Generic angle: "AI for product management" with no unique data → reject. Must have a specific, differentiated angle.
- Keyword stuffing: Target keyword repeated unnaturally → flag. SEO writing should read naturally.
- When to escalate: No unique angle possible — product is at parity on this topic. Choose a different topic where we have differentiation.

## 8. Gold Standard Checklist

- [ ] Target keyword is researched (search volume, competition checked)
- [ ] Search intent matches content format
- [ ] Unique angle differentiates from top-10 ranking content
- [ ] Key points are substantive — not "AI is changing PM"
- [ ] Framework: SEO best practices, content marketing strategy
- [ ] Framework alignment: SEO content strategy, content marketing, journalistic writing
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: messaging_house_construction, competitive_feature_matrix, persona_narrative_generation
- **Downstream skills**: content calendar, social media pack, email_sequence
- **Schemas**: blog_post_brief.schema.json

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
