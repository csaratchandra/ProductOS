"""ProductOS presentation runtime."""

from .runtime import (
    build_evidence_pack,
    build_presentation_story,
    build_publish_check,
    build_ppt_export_plan,
    build_render_spec,
    build_slide_spec,
    render_render_spec_html,
    render_slide_spec_html,
    theme_preset,
    write_html_presentation,
    write_ppt_presentation,
    write_render_spec_payload,
    write_slide_spec_payload,
)

__all__ = [
    "build_evidence_pack",
    "build_presentation_story",
    "build_publish_check",
    "build_ppt_export_plan",
    "build_render_spec",
    "build_slide_spec",
    "render_render_spec_html",
    "render_slide_spec_html",
    "theme_preset",
    "write_html_presentation",
    "write_ppt_presentation",
    "write_render_spec_payload",
    "write_slide_spec_payload",
]
