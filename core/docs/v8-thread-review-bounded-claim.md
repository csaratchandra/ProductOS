# V8 Thread Review Bounded Claim

Purpose: define the exact external wording ProductOS may use for the completed V8 thread-review capability.

## Allowed External Wording

Preferred short claim:

`ProductOS turns messy PM workspace inputs into canonical lifecycle state and a reviewable item thread with linked docs, proof, and release context.`

Preferred fuller claim:

`ProductOS can adopt a notes-first workspace into canonical lifecycle state and generate a repo-backed thread-review package for a canonical item, including HTML review, Markdown review, a governed deck, and a workspace-level review index.`

## Why This Claim Is Safe

This wording is backed by repo proof because the current implementation:

- generates thread-review bundles from canonical lifecycle artifacts
- renders one thread in multiple governed forms from the same source state
- preserves section-level truth labels instead of flattening missing proof
- scales to multiple lifecycle items through a generated index
- includes a release-boundary check that keeps the claim narrower than the implementation fantasy

## Disallowed Wording

Do not say:

- `ProductOS is a PM web app`
- `ProductOS replaces PM review`
- `ProductOS publishes thread-review surfaces safely to external users`
- `ProductOS is a complete multi-user collaborative PM portal`
- `ProductOS autonomously drives product work end to end without PM oversight`

## Current Boundary

The current boundary is:

- internal dogfood: yes
- controlled demo: yes
- broad external launch claim: no
- customer-safe publication: no
- hosted collaborative app claim: no

## Upgrade Path For A Stronger Claim

The external wording may broaden only after these are proved:

- customer-safe thread-review publication controls
- explicit sharing and distribution path beyond local generated outputs
- manual validation on external-user comprehension and safety
- stronger launch packaging for multi-thread product review outside the repo
