# Contributing

ProductOS is distributed under the Apache License 2.0 and accepts suggestions,
fixes, and improvements through issues and pull requests.

## Contribution Guidelines

- Keep changes bounded and traceable.
- Preserve the separation between `core/` and `workspaces/`.
- Do not introduce runtime dependencies on legacy V1 paths.
- Update docs, examples, or schemas when behavior or artifact shape changes.
- Run the relevant local validation before submitting changes.

## Local Checks

- `python3 scripts/validate_artifacts.py`
- `pytest`

## License

By submitting a contribution, you agree that your contribution will be licensed
under Apache License 2.0.
