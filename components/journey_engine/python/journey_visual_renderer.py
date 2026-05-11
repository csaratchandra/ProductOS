from __future__ import annotations

import json
from html import escape
from typing import Any


def _default_tokens() -> dict[str, Any]:
    return {
        "colors": {
            "primary": {"base": "#2563EB"},
            "neutral": {"white": "#FFFFFF", "50": "#F8FAFC", "100": "#F1F5F9", "200": "#E2E8F0", "300": "#CBD5E1", "500": "#64748B", "700": "#334155", "900": "#0F172A"},
            "semantic": {"success": "#16A34A", "warning": "#D97706", "error": "#DC2626", "info": "#0EA5E9"},
        },
        "typography": {"font_family": "Inter, system-ui, sans-serif"},
        "spacing": {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px"},
        "shadows": {"sm": "0 1px 2px rgba(0,0,0,0.05)", "md": "0 4px 6px rgba(0,0,0,0.07)", "lg": "0 10px 15px rgba(0,0,0,0.1)"},
        "radii": {"sm": "4px", "md": "8px", "lg": "12px", "full": "9999px"},
    }


def _resolve_tokens(design_tokens: dict[str, Any] | None) -> dict[str, Any]:
    if design_tokens is None:
        return _default_tokens()
    defaults = _default_tokens()
    merged: dict[str, Any] = {}
    for key in defaults:
        if key in design_tokens:
            if isinstance(defaults[key], dict) and isinstance(design_tokens[key], dict):
                merged[key] = {**defaults[key], **design_tokens[key]}
            else:
                merged[key] = design_tokens[key]
        else:
            merged[key] = defaults[key]
    return merged


def _emotion_color(emotion_label: str, tokens: dict[str, Any]) -> str:
    label = (emotion_label or "neutral").lower()
    colors = tokens.get("colors", {})
    semantic = colors.get("semantic", {})
    primary = colors.get("primary", {})
    neutral = colors.get("neutral", {})
    mapping = {
        "frustrated": semantic.get("error", "#DC2626"),
        "confused": semantic.get("warning", "#D97706"),
        "neutral": neutral.get("500", "#64748B"),
        "satisfied": primary.get("base", "#2563EB"),
        "delighted": semantic.get("success", "#16A34A"),
    }
    return mapping.get(label, neutral.get("500", "#64748B"))


def _drop_off_color(risk: str, tokens: dict[str, Any]) -> str:
    risk = (risk or "none").lower()
    semantic = tokens.get("colors", {}).get("semantic", {})
    mapping = {
        "high": semantic.get("error", "#DC2626"),
        "medium": semantic.get("warning", "#D97706"),
        "low": semantic.get("success", "#16A34A"),
        "none": tokens.get("colors", {}).get("neutral", {}).get("300", "#CBD5E1"),
    }
    return mapping.get(risk, mapping["none"])


def _channel_icon(channel: str) -> str:
    mapping = {
        "website": "🌐",
        "app": "📱",
        "email": "✉️",
        "phone": "📞",
        "chat": "💬",
        "social_media": "📣",
        "sales_call": "🤝",
        "support_ticket": "🎫",
        "knowledge_base": "📚",
        "community": "👥",
        "in_product": "🧩",
        "webinar": "🎥",
        "event": "📅",
        "referral": "🔗",
        "review_site": "⭐",
        "partner": "🤝",
        "other": "📎",
    }
    return mapping.get(channel, "📎")


def _build_css(tokens: dict[str, Any]) -> str:
    font = escape(tokens.get("typography", {}).get("font_family", "Inter, system-ui, sans-serif"))
    bg = tokens.get("colors", {}).get("neutral", {}).get("50", "#F8FAFC")
    panel = tokens.get("colors", {}).get("neutral", {}).get("white", "#FFFFFF")
    ink = tokens.get("colors", {}).get("neutral", {}).get("900", "#0F172A")
    muted = tokens.get("colors", {}).get("neutral", {}).get("500", "#64748B")
    line = tokens.get("colors", {}).get("neutral", {}).get("200", "#E2E8F0")
    shadow_md = tokens.get("shadows", {}).get("md", "0 4px 6px rgba(0,0,0,0.07)")
    radii_md = tokens.get("radii", {}).get("md", "8px")
    radii_lg = tokens.get("radii", {}).get("lg", "12px")
    radii_full = tokens.get("radii", {}).get("full", "9999px")
    return f"""
    :root {{
      --bg: {bg};
      --panel: {panel};
      --ink: {ink};
      --muted: {muted};
      --line: {line};
      --shadow-md: {shadow_md};
      --radius-md: {radii_md};
      --radius-lg: {radii_lg};
      --radius-full: {radii_full};
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: {font};
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
    }}
    .cjm-container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px 16px;
    }}
    .cjm-header {{
      margin-bottom: 24px;
    }}
    .cjm-header h1 {{
      font-size: 1.75rem;
      font-weight: 600;
      margin-bottom: 8px;
    }}
    .cjm-meta {{
      font-size: 0.875rem;
      color: var(--muted);
    }}
    .cjm-meta span + span {{
      margin-left: 16px;
    }}
    .timeline-wrapper {{
      position: relative;
      margin-bottom: 32px;
    }}
    .timeline-scroll {{
      overflow-x: auto;
      padding-bottom: 8px;
    }}
    .timeline-track {{
      display: flex;
      gap: 16px;
      min-width: max-content;
      padding: 8px 4px;
    }}
    .stage-card {{
      flex: 0 0 220px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 16px;
      cursor: pointer;
      position: relative;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .stage-card:hover {{
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }}
    .stage-card .top-border {{
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    }}
    .stage-name {{
      font-size: 0.875rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 8px;
      margin-top: 4px;
    }}
    .emotion-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: var(--radius-full);
      background: var(--bg);
      margin-bottom: 10px;
    }}
    .emotion-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 10px;
    }}
    .chip {{
      font-size: 0.75rem;
      padding: 3px 10px;
      border-radius: var(--radius-full);
      background: var(--bg);
      border: 1px solid var(--line);
      color: var(--muted);
    }}
    .pain-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      color: #DC2626;
    }}
    .pain-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #DC2626;
    }}
    .mot-marker {{
      position: absolute;
      top: -10px;
      right: 12px;
      font-size: 1.1rem;
    }}
    .svg-curve-wrapper {{
      height: 200px;
      margin-bottom: -32px;
      position: relative;
      z-index: 1;
      pointer-events: none;
    }}
    .svg-curve-wrapper svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}
    .opportunities-section {{
      margin-top: 32px;
    }}
    .opportunities-section h2 {{
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 16px;
    }}
    .opp-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
    }}
    .opp-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      padding: 16px;
      border-left: 4px solid;
    }}
    .opp-card h3 {{
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 6px;
    }}
    .opp-meta {{
      font-size: 0.75rem;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    .detail-panel {{
      position: fixed;
      top: 0;
      right: 0;
      width: 420px;
      max-width: 90vw;
      height: 100vh;
      background: var(--panel);
      border-left: 1px solid var(--line);
      box-shadow: -8px 0 24px rgba(0,0,0,0.1);
      z-index: 1000;
      transform: translateX(100%);
      transition: transform 0.3s ease;
      overflow-y: auto;
      padding: 24px;
    }}
    .detail-panel.open {{
      transform: translateX(0);
    }}
    .detail-panel .close-btn {{
      position: absolute;
      top: 16px;
      right: 16px;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: 1px solid var(--line);
      background: var(--bg);
      cursor: pointer;
      font-size: 1rem;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .detail-panel h2 {{
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 16px;
      padding-right: 40px;
    }}
    .detail-section {{
      margin-bottom: 20px;
    }}
    .detail-section h3 {{
      font-size: 0.875rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    .detail-section p, .detail-section li {{
      font-size: 0.875rem;
      line-height: 1.6;
    }}
    .detail-section ul {{
      padding-left: 18px;
    }}
    .quote {{
      font-style: italic;
      border-left: 3px solid var(--line);
      padding-left: 12px;
      color: var(--muted);
    }}
    .risk-bar-bg {{
      height: 8px;
      border-radius: var(--radius-full);
      background: var(--line);
      overflow: hidden;
      margin-top: 6px;
    }}
    .risk-bar-fill {{
      height: 100%;
      border-radius: var(--radius-full);
      transition: width 0.3s ease;
    }}
    .overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.25);
      z-index: 999;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }}
    .overlay.open {{
      opacity: 1;
      pointer-events: auto;
    }}
    @media (max-width: 640px) {{
      .stage-card {{ flex: 0 0 180px; padding: 12px; }}
      .detail-panel {{ width: 100%; max-width: 100%; }}
    }}
"""


def _build_js() -> str:
    return """
(function() {
  const panel = document.getElementById('detail-panel');
  const overlay = document.getElementById('detail-overlay');
  const closeBtn = document.getElementById('detail-close');

  function openPanel(stageId) {
    const card = document.querySelector('[data-stage-id="' + stageId + '"]');
    if (!card) return;
    const data = JSON.parse(card.getAttribute('data-stage-json'));
    populatePanel(data);
    panel.classList.add('open');
    overlay.classList.add('open');
  }

  function closePanel() {
    panel.classList.remove('open');
    overlay.classList.remove('open');
  }

  function populatePanel(data) {
    document.getElementById('panel-title').textContent = data.stage_name.replace(/_/g, ' ');
    document.getElementById('panel-desc').textContent = data.description || '';
    document.getElementById('panel-actions').innerHTML = (data.persona_actions || []).map(a => '<li>' + escapeHtml(a) + '</li>').join('');
    document.getElementById('panel-thoughts').textContent = data.persona_thoughts || '';
    document.getElementById('panel-touchpoints').innerHTML = (data.touchpoints || []).map(t => '<span class="chip">' + escapeHtml(t) + '</span>').join('');
    document.getElementById('panel-channels').innerHTML = (data.channels || []).map(c => '<span class="chip">' + escapeHtml(channelIcon(c)) + ' ' + escapeHtml(c) + '</span>').join('');
    document.getElementById('panel-pains').innerHTML = (data.pain_points || []).map(p => '<li>' + escapeHtml(p) + '</li>').join('');
    document.getElementById('panel-persons').innerHTML = (data.persons_involved || []).map(p => '<span class="chip">' + escapeHtml(p) + '</span>').join('');
    document.getElementById('panel-time').textContent = data.time_spent || '';

    const riskEl = document.getElementById('panel-risk-fill');
    const riskLabel = document.getElementById('panel-risk-label');
    const riskMap = { high: ['100%', '#DC2626'], medium: ['60%', '#D97706'], low: ['30%', '#16A34A'], none: ['0%', '#CBD5E1'] };
    const cfg = riskMap[(data.drop_off_risk || 'none').toLowerCase()] || riskMap.none;
    riskEl.style.width = cfg[0];
    riskEl.style.backgroundColor = cfg[1];
    riskLabel.textContent = (data.drop_off_risk || 'none').toUpperCase();
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function channelIcon(ch) {
    const map = {
      website: '🌐', app: '📱', email: '✉️', phone: '📞', chat: '💬',
      social_media: '📣', sales_call: '🤝', support_ticket: '🎫',
      knowledge_base: '📚', community: '👥', in_product: '🧩',
      webinar: '🎥', event: '📅', referral: '🔗', review_site: '⭐',
      partner: '🤝', other: '📎'
    };
    return map[ch] || '📎';
  }

  document.querySelectorAll('.stage-card').forEach(card => {
    card.addEventListener('click', () => openPanel(card.getAttribute('data-stage-id')));
  });

  closeBtn.addEventListener('click', closePanel);
  overlay.addEventListener('click', closePanel);

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closePanel();
    const openCard = document.querySelector('.stage-card.open');
    let target = null;
    if (e.key === 'ArrowRight') {
      const cards = Array.from(document.querySelectorAll('.stage-card'));
      const idx = cards.findIndex(c => c.classList.contains('open'));
      target = cards[idx + 1];
    }
    if (e.key === 'ArrowLeft') {
      const cards = Array.from(document.querySelectorAll('.stage-card'));
      const idx = cards.findIndex(c => c.classList.contains('open'));
      target = cards[idx - 1];
    }
    if (target) {
      openPanel(target.getAttribute('data-stage-id'));
      target.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    }
  });

  document.querySelectorAll('.stage-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.stage-card').forEach(c => c.classList.remove('open'));
      card.classList.add('open');
    });
  });
})();
"""


def _build_emotion_curve_svg(
    stages: list[dict[str, Any]],
    tokens: dict[str, Any],
    peak_stage_name: str | None = None,
    valley_stage_name: str | None = None,
) -> str:
    if not stages:
        return ""
    count = len(stages)
    width = max(800, count * 180)
    height = 200
    padding_x = 60
    padding_y = 30
    plot_width = width - padding_x * 2
    plot_height = height - padding_y * 2

    points = []
    for i, stage in enumerate(stages):
        score = stage.get("emotion_score", 5)
        x = padding_x + (i / max(1, count - 1)) * plot_width
        y = padding_y + plot_height - ((score - 1) / 9) * plot_height
        points.append((x, y, score, stage.get("stage_id"), stage.get("stage_name")))

    # Smooth cubic bezier path
    if len(points) == 1:
        path_d = f"M {points[0][0]},{points[0][1]}"
    else:
        segments = []
        segments.append(f"M {points[0][0]},{points[0][1]}")
        for i in range(len(points) - 1):
            x0, y0 = points[i][0], points[i][1]
            x1, y1 = points[i + 1][0], points[i + 1][1]
            cpx1 = x0 + (x1 - x0) * 0.4
            cpy1 = y0
            cpx2 = x1 - (x1 - x0) * 0.4
            cpy2 = y1
            segments.append(f"C {cpx1},{cpy1} {cpx2},{cpy2} {x1},{y1}")
        path_d = " ".join(segments)

    # Gradient fill path
    fill_d = path_d + f" L {points[-1][0]},{height} L {points[0][0]},{height} Z"

    # Annotations using metadata-provided stage names when available
    annotations = []
    peak_pt = None
    valley_pt = None
    for pt in points:
        if peak_stage_name and pt[4] == peak_stage_name:
            peak_pt = pt
        if valley_stage_name and pt[4] == valley_stage_name:
            valley_pt = pt
    if peak_pt is None:
        peak_pt = max(points, key=lambda p: p[2])
    if valley_pt is None:
        valley_pt = min(points, key=lambda p: p[2])

    for label, pt in [("PEAK", peak_pt), ("VALLEY", valley_pt)]:
        x, y, score, stage_id, stage_name = pt
        annotations.append(
            f'<text x="{x}" y="{y - 12}" text-anchor="middle" font-size="11" font-weight="600" fill="#334155">{label}</text>'
        )
        annotations.append(
            f'<circle cx="{x}" cy="{y}" r="5" fill="none" stroke="#334155" stroke-width="2"/>'
        )

    # Stage labels under x-axis
    stage_labels = []
    for pt in points:
        x = pt[0]
        stage_name = pt[4]
        stage_labels.append(
            f'<text x="{x}" y="{height - 8}" text-anchor="middle" font-size="10" fill="#64748B">{escape(str(stage_name).replace("_", " "))}</text>'
        )

    primary = tokens.get("colors", {}).get("primary", {}).get("base", "#2563EB")
    annotations_html = "".join(annotations)
    stage_labels_html = "".join(stage_labels)
    return f"""<svg viewBox="0 0 {width} {height}" preserveAspectRatio="none">
      <defs>
        <linearGradient id="curveGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="{primary}" stop-opacity="0.25"/>
          <stop offset="100%" stop-color="{primary}" stop-opacity="0.02"/>
        </linearGradient>
      </defs>
      <path d="{fill_d}" fill="url(#curveGrad)" stroke="none"/>
      <path d="{path_d}" fill="none" stroke="{primary}" stroke-width="3" stroke-linecap="round"/>
      {annotations_html}
      {stage_labels_html}
    </svg>"""


def render_customer_journey_map_html(
    journey_map: dict[str, Any],
    design_tokens: dict[str, Any] | None = None,
) -> str:
    """Render a standalone interactive HTML customer journey map.

    Args:
        journey_map: Validated customer_journey_map.json payload
        design_tokens: Optional design_token_set.json for theming

    Returns:
        Complete HTML string with embedded CSS and JS
    """
    tokens = _resolve_tokens(design_tokens)
    stages = list(journey_map.get("journey_stages", []))
    stages.sort(key=lambda s: s.get("stage_order", 0))
    moments = {m["stage_id"]: m for m in journey_map.get("moments_of_truth", [])}
    opportunities = list(journey_map.get("opportunities", []))
    title = escape(journey_map.get("title", "Customer Journey Map"))
    persona_refs = journey_map.get("target_persona_refs", [])
    segment_ref = journey_map.get("target_segment_ref", "")

    # Build stage cards
    stage_cards = []
    for stage in stages:
        stage_id = stage.get("stage_id", "")
        stage_name = escape(str(stage.get("stage_name", "")).replace("_", " "))
        emotion_label = stage.get("emotion_label", "neutral")
        emotion_score = stage.get("emotion_score", 5)
        color = _emotion_color(emotion_label, tokens)
        pain_points = stage.get("pain_points", [])
        touchpoints = stage.get("touchpoints", [])
        moment = moments.get(stage_id)

        top_border = f'<div class="top-border" style="background:{color}"></div>'
        emotion_badge = (
            f'<div class="emotion-badge" style="color:{color}">'
            f'<span class="emotion-dot" style="background:{color}"></span>'
            f'{escape(emotion_label)} ({emotion_score})</div>'
        )

        touchpoint_chips = ""
        if touchpoints:
            chips = "".join(f'<span class="chip">{escape(tp)}</span>' for tp in touchpoints[:3])
            if len(touchpoints) > 3:
                chips += f'<span class="chip">+{len(touchpoints) - 3}</span>'
            touchpoint_chips = f'<div class="chips">{chips}</div>'

        pain_badge = ""
        if pain_points:
            pain_badge = (
                f'<div class="pain-badge"><span class="pain-dot"></span>'
                f'{len(pain_points)} pain point{"s" if len(pain_points) > 1 else ""}</div>'
            )

        mot_marker = ""
        if moment:
            mot_marker = '<div class="mot-marker" title="Moment of Truth">★</div>'

        stage_json = json.dumps(stage, ensure_ascii=False)
        card = (
            f'<div class="stage-card" data-stage-id="{escape(stage_id)}" data-stage-json="{escape(stage_json)}">'
            f'{top_border}{mot_marker}'
            f'<div class="stage-name">{stage_name}</div>'
            f'{emotion_badge}'
            f'{touchpoint_chips}'
            f'{pain_badge}'
            f'</div>'
        )
        stage_cards.append(card)

    # Build emotion curve
    overall_curve = journey_map.get("overall_emotion_curve", {})
    svg_curve = _build_emotion_curve_svg(
        stages,
        tokens,
        peak_stage_name=overall_curve.get("peak_emotion_stage"),
        valley_stage_name=overall_curve.get("valley_emotion_stage"),
    )

    # Build opportunity blocks
    opp_cards = []
    for opp in opportunities:
        stage_id = opp.get("stage_id", "")
        stage_name = next((s.get("stage_name", stage_id) for s in stages if s.get("stage_id") == stage_id), stage_id)
        impact = opp.get("potential_impact", "incremental")
        effort = opp.get("effort_estimate", "medium")
        impact_colors = {
            "transformative": "#7C3AED",
            "significant": "#2563EB",
            "incremental": "#64748B",
        }
        border_color = impact_colors.get(impact, "#64748B")
        opp_cards.append(
            f'<div class="opp-card" style="border-left-color:{border_color}">'
            f'<h3>{escape(opp.get("title", ""))}</h3>'
            f'<div class="opp-meta">Stage: {escape(str(stage_name).replace("_", " "))} • Impact: {escape(impact)} • Effort: {escape(effort)}</div>'
            f'<p>{escape(opp.get("description", ""))}</p>'
            f'</div>'
        )

    meta_parts = []
    if persona_refs:
        meta_parts.append(f"<span>Personas: {', '.join(escape(p) for p in persona_refs)}</span>")
    if segment_ref:
        meta_parts.append(f"<span>Segment: {escape(segment_ref)}</span>")
    meta_html = "\n".join(meta_parts)

    css = _build_css(tokens)
    js = _build_js()
    stage_cards_html = "\n".join(stage_cards)
    opp_cards_html = "\n".join(opp_cards)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
  <div class="cjm-container">
    <header class="cjm-header">
      <h1>{title}</h1>
      <div class="cjm-meta">{meta_html}</div>
    </header>

    <div class="timeline-wrapper">
      <div class="svg-curve-wrapper">{svg_curve}</div>
      <div class="timeline-scroll">
        <div class="timeline-track">
          {stage_cards_html}
        </div>
      </div>
    </div>

    <section class="opportunities-section">
      <h2>Opportunities</h2>
      <div class="opp-grid">
        {opp_cards_html}
      </div>
    </section>
  </div>

  <div id="detail-overlay" class="overlay"></div>
  <aside id="detail-panel" class="detail-panel">
    <button id="detail-close" class="close-btn" aria-label="Close panel">&times;</button>
    <h2 id="panel-title"></h2>
    <div class="detail-section">
      <h3>Description</h3>
      <p id="panel-desc"></p>
    </div>
    <div class="detail-section">
      <h3>Persona Actions</h3>
      <ul id="panel-actions"></ul>
    </div>
    <div class="detail-section">
      <h3>Persona Thoughts</h3>
      <p id="panel-thoughts" class="quote"></p>
    </div>
    <div class="detail-section">
      <h3>Touchpoints</h3>
      <div id="panel-touchpoints" class="chips"></div>
    </div>
    <div class="detail-section">
      <h3>Channels</h3>
      <div id="panel-channels" class="chips"></div>
    </div>
    <div class="detail-section">
      <h3>Pain Points</h3>
      <ul id="panel-pains"></ul>
    </div>
    <div class="detail-section">
      <h3>Drop-off Risk</h3>
      <div class="risk-bar-bg"><div id="panel-risk-fill" class="risk-bar-fill"></div></div>
      <p id="panel-risk-label" style="font-size:0.75rem; margin-top:4px; color:#64748B;"></p>
    </div>
    <div class="detail-section">
      <h3>Persons Involved</h3>
      <div id="panel-persons" class="chips"></div>
    </div>
    <div class="detail-section">
      <h3>Time Spent</h3>
      <p id="panel-time"></p>
    </div>
  </aside>

  <script>{js}</script>
</body>
</html>
"""
