#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.presentation.python.productos_presentation import (  # noqa: E402
    build_evidence_pack,
    build_presentation_story,
    build_publish_check,
    build_ppt_export_plan,
    build_render_spec,
    build_slide_spec,
    write_html_presentation,
    write_ppt_presentation,
)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the ProductOS presentation component outputs from a presentation brief.",
    )
    parser.add_argument("presentation_brief", type=Path, help="Path to a presentation_brief JSON file.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for generated outputs. Defaults to tmp/presentations/<presentation_brief_id>/",
    )
    parser.add_argument(
        "--aspect-ratio",
        choices=["16:9", "4:3"],
        default="16:9",
        help="Aspect ratio for the render spec and derived exports.",
    )
    parser.add_argument(
        "--skip-ppt",
        action="store_true",
        help="Skip native python-pptx export even if the dependency is installed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    brief_path = args.presentation_brief.resolve()
    presentation_brief = load_json(brief_path)
    brief_id = presentation_brief["presentation_brief_id"]
    output_dir = (args.output_dir or ROOT / "tmp" / "presentations" / brief_id).resolve()

    evidence_pack = build_evidence_pack(presentation_brief)
    presentation_story = build_presentation_story(presentation_brief, evidence_pack)
    render_spec = build_render_spec(
        presentation_brief,
        presentation_story,
        aspect_ratio=args.aspect_ratio,
    )
    slide_spec = build_slide_spec(
        presentation_brief,
        aspect_ratio=args.aspect_ratio,
    )
    publish_check = build_publish_check(presentation_brief, render_spec)
    export_plan = build_ppt_export_plan(render_spec)

    output_paths = {
        "evidence_pack": output_dir / f"{brief_id}.evidence-pack.json",
        "presentation_story": output_dir / f"{brief_id}.presentation-story.json",
        "render_spec": output_dir / f"{brief_id}.render-spec.json",
        "slide_spec": output_dir / f"{brief_id}.slide-spec.json",
        "publish_check": output_dir / f"{brief_id}.publish-check.json",
        "ppt_export_plan": output_dir / f"{brief_id}.ppt-export-plan.json",
        "html": output_dir / f"{brief_id}.html",
    }

    write_json(output_paths["evidence_pack"], evidence_pack)
    write_json(output_paths["presentation_story"], presentation_story)
    write_json(output_paths["render_spec"], render_spec)
    write_json(output_paths["slide_spec"], slide_spec)
    write_json(output_paths["publish_check"], publish_check)
    write_json(output_paths["ppt_export_plan"], export_plan)
    write_html_presentation(render_spec, output_paths["html"])

    print(f"Generated presentation outputs for {brief_id}:")
    for label, path in output_paths.items():
        print(f"  - {label}: {path}")

    if not args.skip_ppt:
        ppt_path = output_dir / f"{brief_id}.pptx"
        try:
            write_ppt_presentation(render_spec, ppt_path)
        except RuntimeError as error:
            print(f"  - pptx: skipped ({error})")
        else:
            print(f"  - pptx: {ppt_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
