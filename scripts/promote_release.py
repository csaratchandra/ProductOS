#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.python.productos_runtime.release import promote_release_from_ralph


def _default_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote a successful Ralph loop into the official ProductOS core release."
    )
    parser.add_argument(
        "--ralph-path",
        type=Path,
        required=True,
        help="Path to the Ralph loop state artifact to promote.",
    )
    parser.add_argument("--released-at", default=_default_timestamp())
    parser.add_argument("--approved-by", default="ProductOS PM")
    parser.add_argument(
        "--eval-run-report-path",
        type=Path,
        help="Optional path to the frozen eval run report that must be healthy before promotion.",
    )
    parser.add_argument(
        "--feature-portfolio-review-path",
        type=Path,
        help="Optional path to the feature portfolio review that must be healthy before promotion.",
    )
    args = parser.parse_args()

    result = promote_release_from_ralph(
        ROOT,
        args.ralph_path,
        released_at=args.released_at,
        approved_by=args.approved_by,
        eval_run_report_path=args.eval_run_report_path,
        feature_portfolio_review_path=args.feature_portfolio_review_path,
    )
    print(
        f"Promoted ProductOS to V{result['target_version']} using {args.ralph_path} "
        f"and wrote {result['release_path'].relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
