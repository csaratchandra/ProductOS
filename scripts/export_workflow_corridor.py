#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.workflow_corridor.python.productos_workflow_corridor.runtime import (
    build_workflow_corridor_bundle,
    write_corridor_html,
    write_corridor_payload,
)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the ProductOS workflow corridor pipeline from a source bundle."
    )
    parser.add_argument("source_bundle", type=Path, help="Path to the source bundle JSON file.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for generated outputs. Defaults to tmp/workflow-corridor/<slug>/",
    )
    parser.add_argument(
        "--audience-mode",
        default="customer_safe_public",
        choices=["customer_safe_public", "buyer_exec", "operator_review", "product_browse"],
    )
    parser.add_argument(
        "--publication-mode",
        default="publishable_external",
        choices=["publishable_external", "product_browse", "internal_review"],
    )
    args = parser.parse_args()

    source_bundle = load_json(args.source_bundle.resolve())
    slug = source_bundle.get("corridor_id") or source_bundle.get("title", "workflow-corridor")
    output_dir = args.output_dir or ROOT / "tmp" / "workflow-corridor" / str(slug).replace(" ", "-").lower()

    bundle = build_workflow_corridor_bundle(
        source_bundle,
        audience_mode=args.audience_mode,
        publication_mode=args.publication_mode,
    )

    for name, payload in bundle.items():
        write_corridor_payload(payload, output_dir / f"{name}.json")
    write_corridor_html(bundle["corridor_render_model"], output_dir / "workflow_corridor.html")

    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
