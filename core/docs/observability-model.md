# Observability Model

Purpose: Define how ProductOS monitors its own operating quality so reliability, trust, and workflow performance do not remain invisible.

## Operating Signals

- workflow completion rate
- blocked workflow count
- publish-block incident count
- stale-evidence incident count
- integration failure and stale-sync count
- PM override count
- artifact rewrite rate
- benchmark trend movement

## Review Use

- weekly: inspect active operational degradation
- monthly: compare benchmark and reliability trends
- quarterly: review whether ProductOS is improving PM leverage or only adding structure

## Rule

- core operating metrics should be visible to leadership and PM-coach paths when they materially affect trust
- observability should support intervention, not vanity dashboards
