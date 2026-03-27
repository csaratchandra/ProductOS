# V6 Distribution Checklist

Status: active
Audience: PM, engineering, repo maintainer
Owner: ProductOS PM
Updated At: 2026-03-27

## Purpose

Prepare the promoted V6 repo state for git publication and PM download.

## Repo Publication

- ensure the V6 release artifacts are checked in
- ensure `registry/releases/release_6_0_0.json` is present
- ensure the root README points PMs to `workspaces/product-starter/`
- ensure the starter guide explains `init-workspace`
- use [v6-public-distribution-manifest.md](/Users/sarat/Documents/code/ProductOS/workspaces/productos-v2/docs/planning/v6-public-distribution-manifest.md) as the canonical include and exclude list for the public V6 repo
- tag the repo at `v6.0.0`
- push the commit and tag to the canonical remote

## PM Download Surface

- present `workspaces/product-starter/` as the reusable starter
- present `workspaces/productos-v2/` as self-hosting-only
- keep `current-plan.md` as the human-readable release-plan entry point
- keep the starter lifecycle bundle inspectable without reading runtime code

## Recommended Publish Notes

- ProductOS V6.0.0 is the stable line
- the promoted slice is lifecycle traceability through `release_readiness`
- the starter workspace is the supported path for new products and features
- launch and outcome traceability remain the next bounded expansion

## Blocking Reality In This Workspace

- no git remote is currently configured in this local checkout
- upload or push cannot happen until a remote is added or the repo is moved into a checkout with one configured
