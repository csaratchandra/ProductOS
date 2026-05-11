# Strategy Discovery Superpower Plan

Status: active
Audience: PM, engineering, design, leadership
Owner: ProductOS PM
Updated At: 2026-04-21

## Goal

Make the next version of ProductOS better at strategy and discovery judgment before expanding deeper research automation or broader autonomy.

The target is a `PM judgment amplifier`: help one PM decide what to believe, what to bet on, and what to test next with less reconstruction.

## Bounded Slice

Slice 1 is the strategy spine.

Implement:

- `strategy_context_brief`
- `product_vision_brief`
- `mission-to-strategy-spine-workflow`
- downstream routing rules that preserve the new strategy refs
- one reference proof chain from mission to problem framing

Do not implement in this slice:

- new UI surfaces
- broader autonomous PM claims
- external publication adapters
- expanded financial-model tooling

## Acceptance Gate

This slice is complete only when:

1. the new strategy artifacts validate in the core example set
2. workflow docs route strategy questions through the strategy spine explicitly
3. the readable document system defines one synced Product Strategy / Vision document sourced from the new artifacts
4. the reference workspace shows `mission_brief -> strategy_context_brief -> product_vision_brief -> market_strategy_brief -> problem_brief`

## Follow-On Slices

After the strategy spine:

1. discovery operations
2. opportunity and validation spine
3. AI discovery controls
4. strategic memory and thesis review
5. PM strategy cockpit
