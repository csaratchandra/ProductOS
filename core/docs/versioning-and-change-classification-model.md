# Versioning And Change Classification Model

Purpose: Define how ProductOS classifies change scope and recommends whether work belongs in a major release, a minor version, or a patch/X-version update.

## Why This Exists

PMs should not have to improvise version significance every time a release is prepared.

ProductOS should distinguish between:

- major product changes
- feature-level additions or significant enhancements
- minor improvements
- bug fixes
- internal-only maintenance

This model is for release planning, release notes, and workspace adoption records.

## Core Rule

Versioning should reflect product impact, not engineering effort alone.

The classification should answer:

1. did the user experience change materially
2. did existing user behavior or workflow expectations break
3. did the PM need new communication, migration, or enablement
4. is the change customer-visible or internal-only

## Change Classes

### Major product change

Use when the release changes the product meaningfully enough that users, customers, or downstream teams must rethink how they use it.

Typical signs:

- breaks or significantly alters an established workflow
- introduces a new operating model
- changes core navigation, information architecture, or mental model
- requires migration, retraining, or explicit rollout guidance
- changes commitments, trust boundaries, or customer-safe behavior materially

Default version impact:

- `major`

### Feature enhancement

Use when the release adds or expands a meaningful capability without breaking the core product model.

Typical signs:

- adds a net-new user capability
- expands an important existing feature
- changes user value materially but not destructively
- needs release communication and possibly enablement, but not migration

Default version impact:

- `minor`

### Minor improvement

Use when the product gets better in a noticeable but non-transformational way.

Typical signs:

- improves clarity, speed, polish, or usability
- reduces friction in an existing flow
- adds supporting value without changing the main operating model

Default version impact:

- `minor`

### Bug fix

Use when the release restores expected behavior or fixes incorrect behavior.

Typical signs:

- behavior was broken, inconsistent, or incorrect
- the right user communication is short and factual
- no new mental model is introduced

Default version impact:

- `patch`

### Internal-only maintenance

Use when the work affects internals, infrastructure, test harnesses, or documentation without materially changing product behavior for end users.

Typical signs:

- customer-visible behavior is unchanged
- used for reliability, refactoring, compatibility, or internal operations
- may matter for internal release records but not external notes

Default version impact:

- `patch`

## Decision Rules

### Recommend `major` when

- a core workflow changes materially
- a product promise or trust boundary changes materially
- existing users need retraining, migration, or strong enablement
- backward compatibility is materially affected

### Recommend `minor` when

- the release adds meaningful new capability
- the release improves an important workflow without breaking it
- the release is customer-visible and value-bearing, but not disruptive

### Recommend `patch` when

- the release is mostly bug fixes or internal-only changes
- customer-visible behavior does not change materially
- the release restores expected behavior rather than redefining it

## Mixed Releases

If one release contains multiple change classes:

- choose the highest version impact represented in the approved scope
- keep the release note explicit about the different classes inside the release

Example:

- one feature enhancement plus three bug fixes should still usually be `minor`

## Communication Rules

### Major releases

Should include:

- what changed
- why it changed
- who is affected
- migration or enablement guidance
- known transition risks

### Minor releases

Should include:

- what is new or improved
- who benefits
- what workflow is better now

### Patch releases

Should include:

- what was fixed
- whether any user action is required
- whether the change is internal-only or user-visible

## ProductOS-Specific Guidance

For ProductOS itself:

- a new PM operating model or cockpit behavior change may qualify as `major`
- a strong new agent capability may qualify as `minor` unless it changes the core product model
- validation, testing, and internal structural hardening without PM-facing impact should usually be `patch`

## Required Output From Classification

Each release decision should be able to state:

- `change_classification`
- `release_type`
- `customer_visible`
- `classification_rationale`
- `communication_expectation`

If ProductOS cannot explain those fields clearly, the classification is weak.
