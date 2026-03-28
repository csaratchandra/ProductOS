# Internal ProductOS Loop

This directory is reserved for the private self-hosting ProductOS loop used by the ProductOS PM.

## Structure

```text
internal/
  README.md
  ProductOS-Next/
```

`internal/ProductOS-Next/` is the working workspace where ProductOS is used to build the next ProductOS version.

It may contain:

- `inbox/` for raw notes, screenshots, transcripts, and imported source material
- `artifacts/` for machine-readable PM artifacts and agent inputs
- `docs/` for readable planning, review, status, and presentation material
- `handoffs/` for bounded AI-agent execution packages
- `feedback/` for ProductOS improvement suggestions discovered while self-hosting
- `prototypes/` for mockups, demos, and prototype outputs

## Promotion Rule

- Build and test ProductOS changes inside `internal/ProductOS-Next/`.
- Keep the full PM loop and working evidence there.
- Promote only approved reusable changes into `core/`, `components/`, `scripts/`, `templates/`, or `registry/`.
- Do not promote private self-hosting artifacts unless they are intentionally converted into reusable examples or fixtures.

## Git Rule

This directory is meant to stay private to one PM.

Recommended ignore rule:

```gitignore
internal/*
!internal/README.md
```
