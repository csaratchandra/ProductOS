# Competitive Radar Scan

## 1. Purpose

Continuously monitor competitor digital surfaces — websites, pricing pages, documentation, blogs, review platforms, app stores, social channels, job postings, changelogs, patent filings, and press releases — to detect material changes and generate structured competitive intelligence alerts with severity scoring and recommended PM actions.

## 2. Trigger / When To Use

- Scheduled automatic scan interval fires (default: every 24 hours)
- PM triggers manual scan via `./productos run competitive-radar --competitor-id X`
- Competitive signal landscape detects anomaly requiring immediate scan
- New competitor added to dossier → initial baseline scan initiated
- Regulatory change tracker detects development in monitored jurisdiction → triggers adjacent competitive scan

## 3. Prerequisites

- `competitor_dossier` artifact with named competitors and priority levels
- `competitor_radar_state` initialized with monitored surfaces per competitor
- Source note cards or reference URLs for each monitored surface
- Network access to target surfaces (some surfaces may be behind login — mark as degraded)
- `runtime_adapter_registry` entry with browsing/web-fetch capability

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `competitor_radar_state` | `object` | `competitor_radar_state.schema.json` | Yes | Full radar state artifact | Contains monitored_competitors with surface URLs and last_known_state_hash |
| `monitored_competitors` | `array` | `competitor_radar_state.monitored_competitors` | Yes | Array of competitor monitoring configs | Each entry has surfaces with URLs |
| `scan_mode` | `enum` | CLI argument or scheduler | Yes | `"full_scan" \| "targeted_scan" \| "change_investigation"` | Full rescan all surfaces vs targeted competitor vs deep-dive on specific change |
| `max_scan_time_seconds` | `integer` | Scheduler config | No | `300` | Timeout per full scan cycle |

## 5. Execution Steps

1. **Load radar state**: Read `competitor_radar_state` artifact. Verify all surface URLs are still active. Flag any 404/403/inaccessible surfaces for `radar_health` update.
2. **Fetch surface content**: For each monitored surface, fetch current content. Use vendor-neutral web fetch capability (same across codex/claude/windsurf/opencode). Store raw text + metadata.
3. **Compute content hash**: Generate hash of fetched content. Compare against `last_known_state_hash`. If identical → mark `check_status: unchanged` and skip further analysis. If different → mark `check_status: changed` and proceed to step 4. If fetch fails → mark `check_status: error`.
4. **Classify change type**: Analyze content delta. Classify into: `feature_launch`, `pricing_update`, `positioning_shift`, `hiring_signal`, `acquisition`, `partnership`, `funding`, `leadership_change`, `product_retirement`, or `other`. Use keyword detection + semantic analysis. Multiple change types are possible from a single surface.
5. **Score severity**: Per detected change, calculate: threat_level (existential/major/moderate/minor/none), urgency (immediate/short_term/medium_term/long_term), strategic_significance (free-text analysis). Composite severity: `f(threat_level, urgency, competitor_priority_level)`.
6. **Assess competitive impact**: Map to affected segments and features. Identify which existing artifacts reference this competitor and would be impacted. Determine if change nullifies an existing differentiation claim or creates a new gap.
7. **Generate intelligence alert**: Per detected change that meets threshold (severity >= informational), create `competitive_intelligence_alert` artifact. Include: headline, description, evidence URLs, severity, confidence, competitive_impact, affected_artifacts, recommended_pm_action, suggested_response_timeframe.
8. **Link to previous alerts**: Check for related previous alerts (same competitor, similar change type within 30 days). If found, link via `previous_related_alert_ids`. If this change supersedes a previous alert, mark old alert as `superseded`.
9. **Update radar state**: Write new `last_known_state_hash` values. Update `last_change_detected_at`. Regenerate `change_detection_summary` and `active_alerts_count`. Update `radar_health`.
10. **Route alerts to PM**: Critical/high severity → immediate notification (dashboard alert + PM action digest). Medium severity → queued for daily digest. Low/informational → logged for weekly review.
11. **Trigger downstream cascades**: High or critical alerts trigger: automatic `competitive_feature_matrix` refresh recommendation, automatic `battle_card` regeneration flag, optional `competitor_dossier` update suggestion. If drift detected (competitor move nullifies an existing claim) → trigger `drift_and_impact_propagation` skill.
12. **Emit feature scorecard**: Record scan results. Radar reachability %, change detection rate, false positive rate, PM action rate on alerts. Feed into `feature_scorecard` for competitive intelligence capability.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `competitor_radar_state` (updated) | `object` | `competitor_radar_state.schema.json` | Yes | Updated with new hashes, timestamps, and health |
| `competitive_intelligence_alerts` | `array[object]` | `competitive_intelligence_alert.schema.json` | Yes | One alert per detected change meeting threshold |
| `radar_health_report` | `object` | `competitor_radar_state.radar_health` | Yes | Reachability stats and surface status |
| `feature_scorecard_update` | `object` | `feature_scorecard.schema.json` | No | Scorecard for competitive monitoring capability |

## 7. Guardrails

- **Failure condition: Surface unreachable (3 consecutive errors)**: Detection criteria: `check_status == "error"` for 3 consecutive scan cycles → response: mark surface as `not_reachable`. Alert PM. Surface excluded from scans until PM resets.
- **Failure condition: False positive storm (>5 changes from single surface in one scan)**: Detection criteria: >5 changes detected from single surface → response: flag as likely false positive (content is dynamic, e.g., rotating testimonials). Mark changes as `low` confidence. Suppress alerts for this surface for 7 days.
- **Failure condition: Rate limiting detected**: Detection criteria: fetch returns 429/403 with anti-bot message → response: pause this surface for 24 hours. Reduce check frequency for this surface. Notify PM.
- **When to stop and escalate to PM**: Three primary competitors all show significant change within same 24-hour window (coordinated response?). Radar health drops to `critical`. AI detects change it cannot classify with >= moderate confidence.
- **When output should be marked low-confidence**: Content delta is ambiguous (minor text changes, can't determine significance). Single-source change without corroboration from another surface. Change detected on dynamic content surface (JavaScript-rendered, rotating content).
- **When skill should refuse to generate**: No competitors configured in `competitor_radar_state`. All surfaces marked as `not_reachable`. PM has not approved competitive monitoring for this workspace.

## 8. Gold Standard Checklist

- [ ] Every detected change has at least one evidence URL pointing to the source surface
- [ ] Change classification uses specific evidence, not guesswork — "their pricing page now shows $299/seat" not "they probably changed pricing"
- [ ] Severity scoring is conservative: default to one level lower if evidence is thin
- [ ] Competitive impact assessment explicitly names which of our features/claims are affected
- [ ] Recommended PM action is actionable, not vague ("review strategy" → "update battle_card section 3 to reflect new pricing")
- [ ] Alerts do not pile up — previous alerts on same topic are linked or superseded
- [ ] Radar health accurately reflects reachability (not reporting "healthy" with 3 surfaces in error)
- [ ] External framework alignment: validates against CI competitive intelligence best practices (SCIP — Strategic & Competitive Intelligence Professionals)
- [ ] No alert is generated for cosmetic changes (color changes, image swaps, typo fixes) unless they indicate rebranding/positioning shift

## 9. Examples

### Excellent Output (5/5)
See `core/examples/artifacts/competitive_intelligence_alert.example.json` for the canonical alert format. Key qualities:
- Specific feature name and evidence URL
- Concrete competitive threat analysis with named features at risk
- Actionable PM recommendation with priority and timeframe
- Clear differentiation identification ("we lead on X, they lead on Y")

### Poor Output (2/5) — What to Avoid

```json
{
  "alert_id": "bad_alert",
  "headline": "Competitor made some changes",
  "description": "Their website looks different. Might be a new feature or just a redesign.",
  "severity": "high",
  "confidence": "low",
  "recommended_pm_action": "Look into this when you have time."
}
```

**Why this fails:**
- Headline and description are vague — provides zero actionable intelligence
- Severity marked "high" with "low" confidence — contradictory; high severity on low confidence evidence is noise
- No evidence URL to the source surface
- Recommended action is passive and non-specific
- No competitive impact assessment — PM has to do the entire analysis themselves

## 10. Cross-References

- **Upstream skills**: `source_discovery`, `source_normalization`, `freshness_scoring`, `competitive_entity_resolution`
- **Downstream skills**: `competitive_shift_analysis`, `drift_and_impact_propagation`, `battle_card_generation`, `freshness_and_staleness_scan`
- **Related entity schemas**: `core/schemas/entities/feature.schema.json`, `core/schemas/entities/market.schema.json`
- **Related artifact schemas**: `core/schemas/artifacts/competitor_radar_state.schema.json`, `core/schemas/artifacts/competitive_intelligence_alert.schema.json`, `core/schemas/artifacts/competitive_feature_matrix.schema.json`, `core/schemas/artifacts/competitor_dossier.schema.json`
- **Related workflows**: `core/workflows/research/research-command-center-workflow.md`, `core/workflows/decision-intelligence/market-strategy-definition-workflow.md`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Exhaustive scanning: all surface types for all competitors. Daily frequency. Deep analysis on every change regardless of severity. | Multi-source corroboration required for every alert. Minimum 2 evidence URLs per alert. | Every alert includes full competitive impact with segment-level detail. Battle card auto-updated. |
| 1→10 | Deep scanning: priority surfaces for primary competitors. Daily frequency. Deep analysis on high+critical only. | Single source acceptable for low/medium severity alerts. High/critical require 2+ sources. | Critical/high alerts get full treatment. Medium/low alerts summarized in daily digest. |
| 10→100 | Standard scanning: key surfaces (website, pricing, G2, blog). 2x weekly frequency. Analysis on medium+ severity. | Single source acceptable for all but critical. Automated scoring prioritized over manual-depth analysis. | Alerts focus on competitive gaps and opportunity windows. Noise suppression more aggressive. |
| 100→10K+ | Focused scanning: pricing and major feature surfaces only. Weekly frequency. Analysis on high+critical only. | Quantitative data preferred over qualitative. Automated classification OK for all levels. | Alerts integrated into portfolio-level competitive view. Individual competitor alerts aggregated. |

## 12. Validation Criteria

- **Schema conformance**: validates against `core/schemas/artifacts/competitor_radar_state.schema.json`, `core/schemas/artifacts/competitive_intelligence_alert.schema.json`
- **Test file**: `tests/test_v10_competitive_radar.py`
- **Example fixture**: `core/examples/artifacts/competitor_radar_state.example.json`, `core/examples/artifacts/competitive_intelligence_alert.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` — all 12 elements present and non-empty
