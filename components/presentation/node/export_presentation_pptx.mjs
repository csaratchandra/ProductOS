#!/usr/bin/env node

import fs from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";

const require = createRequire(import.meta.url);

function usageCommand() {
  if (process.env.PRODUCTOS_PRESENTATION_PPT_USAGE) {
    return process.env.PRODUCTOS_PRESENTATION_PPT_USAGE;
  }
  const scriptPath = process.argv[1]
    ? path.relative(process.cwd(), process.argv[1])
    : "components/presentation/node/export_presentation_pptx.mjs";
  return `node ${scriptPath}`;
}

function normalizeText(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function truncateText(value, maxChars) {
  const text = normalizeText(value);
  if (text.length <= maxChars) return text;
  return `${text.slice(0, maxChars - 1).replace(/[ ,;:-]+$/, "").trimEnd()}...`;
}

function addEvidenceCards(slide, evidenceItems, startY, opts = {}) {
  const cols = opts.cols || 2;
  const cardW = opts.cardW || 4.9;
  const cardH = opts.cardH || 1.15;
  const gapX = opts.gapX || 0.25;
  const gapY = opts.gapY || 0.2;
  const baseX = opts.baseX || 0.7;
  const maxRows = opts.maxRows || 2;
  const maxItems = Math.min(evidenceItems.length, (opts.maxItems || cols * maxRows), cols * maxRows);

  evidenceItems.slice(0, maxItems).forEach((item, index) => {
    const col = index % cols;
    const row = Math.floor(index / cols);
    const x = baseX + col * (cardW + gapX);
    const y = startY + row * (cardH + gapY);
    slide.addShape(globalThis.__pptxShapeType.roundRect, {
      x,
      y,
      w: cardW,
      h: cardH,
      rectRadius: 0.08,
      fill: { color: "FFFFFF", transparency: 18 },
      line: { color: "D9D4CC", width: 1 },
    });
    slide.addText(item.label || "Evidence", {
      x: x + 0.12,
      y: y + 0.08,
      w: cardW - 0.24,
      h: 0.18,
      fontFace: "Aptos",
      fontSize: 9,
      bold: true,
      color: "1E5AA8",
      margin: 0,
    });
    slide.addText(truncateText(item.value || "", opts.valueChars || 92), {
      x: x + 0.12,
      y: y + 0.26,
      w: cardW - 0.24,
      h: 0.48,
      fontFace: "Aptos",
      fontSize: 13,
      color: "222222",
      margin: 0,
      valign: "mid",
      fit: "shrink",
    });
    slide.addText(truncateText(item.source_ref || "", 24), {
      x: x + 0.12,
      y: y + 0.86,
      w: 1.8,
      h: 0.16,
      fontFace: "Aptos",
      fontSize: 8,
      color: "1E5AA8",
      margin: 0,
    });
  });
}

function seriesMax(chartSpec) {
  return Math.max(
    1,
    ...(chartSpec.series || []).flatMap((series) => (series.data || []).map((value) => Number(value) || 0)),
    ...((chartSpec.heatmap_points || []).map((point) => Number(point.value) || 0))
  );
}

function renderChartFallback(slide, chartSpec, x, y, w, h) {
  if (!chartSpec) return;
  slide.addShape(globalThis.__pptxShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.06,
    fill: { color: "FFFFFF", transparency: 12 },
    line: { color: "D9D4CC", width: 1 },
  });
  slide.addText(truncateText(chartSpec.title || "Chart", 28), {
    x: x + 0.15,
    y: y + 0.12,
    w: w - 0.3,
    h: 0.18,
    fontFace: "Aptos",
    fontSize: 8,
    bold: true,
    color: "1E5AA8",
    margin: 0,
  });

  if (chartSpec.chart_type === "heatmap") {
    const cols = chartSpec.x_categories || [];
    const rows = chartSpec.y_categories || [];
    const cellW = Math.min(0.72, (w - 1.2) / Math.max(1, cols.length));
    const cellH = Math.min(0.38, (h - 0.7) / Math.max(1, rows.length));
    rows.slice(0, 3).forEach((rowLabel, rowIndex) => {
      slide.addText(truncateText(rowLabel, 10), {
        x: x + 0.05,
        y: y + 0.44 + rowIndex * cellH,
        w: 0.55,
        h: 0.12,
        fontFace: "Aptos",
        fontSize: 7,
        color: "555555",
        margin: 0,
      });
    });
    cols.slice(0, 4).forEach((colLabel, colIndex) => {
      slide.addText(truncateText(colLabel, 10), {
        x: x + 0.7 + colIndex * cellW,
        y: y + 0.28,
        w: cellW,
        h: 0.12,
        fontFace: "Aptos",
        fontSize: 7,
        color: "555555",
        margin: 0,
        align: "center",
      });
    });
    const maxValue = seriesMax(chartSpec);
    (chartSpec.heatmap_points || []).slice(0, 12).forEach((point) => {
      const transparency = 70 - Math.round((Number(point.value) / maxValue) * 55);
      slide.addShape(globalThis.__pptxShapeType.rect, {
        x: x + 0.7 + point.x * cellW,
        y: y + 0.44 + point.y * cellH,
        w: cellW - 0.04,
        h: cellH - 0.04,
        fill: { color: "1E5AA8", transparency: Math.max(8, transparency) },
        line: { color: "FFFFFF", width: 0.5 },
      });
      slide.addText(truncateText(point.label || String(point.value), 10), {
        x: x + 0.72 + point.x * cellW,
        y: y + 0.52 + point.y * cellH,
        w: cellW - 0.08,
        h: 0.12,
        fontFace: "Aptos",
        fontSize: 6,
        color: "FFFFFF",
        bold: true,
        align: "center",
        margin: 0,
      });
    });
    return;
  }

  const categories = (chartSpec.categories || []).slice(0, 4);
  const maxValue = seriesMax(chartSpec);
  if (chartSpec.chart_type === "stacked_bar") {
    categories.forEach((category, catIndex) => {
      const baseY = y + 0.42 + catIndex * 0.22;
      let cursorX = x + 1.2;
      slide.addText(truncateText(category, 16), {
        x: x + 0.12,
        y: baseY,
        w: 1.0,
        h: 0.12,
        fontFace: "Aptos",
        fontSize: 7,
        color: "555555",
        margin: 0,
      });
      (chartSpec.series || []).slice(0, 4).forEach((series, seriesIndex) => {
        const value = Number(series.data?.[catIndex] || 0);
        const segmentW = Math.max(0.12, ((w - 1.45) * value) / maxValue);
        slide.addShape(globalThis.__pptxShapeType.roundRect, {
          x: cursorX,
          y: baseY + 0.03,
          w: segmentW,
          h: 0.1,
          rectRadius: 0.03,
          fill: { color: ["1E5AA8", "444444", "B02B2B", "2F7D53"][seriesIndex % 4] },
          line: { color: ["1E5AA8", "444444", "B02B2B", "2F7D53"][seriesIndex % 4], transparency: 100 },
        });
        cursorX += segmentW + 0.02;
      });
    });
    return;
  }

  const plotX = x + 0.7;
  const plotY = y + 0.42;
  const plotW = w - 0.9;
  const plotH = h - 0.65;
  slide.addShape(globalThis.__pptxShapeType.line, {
    x: plotX,
    y: plotY + plotH,
    w: plotW,
    h: 0,
    line: { color: "C8DBED", width: 1 },
  });
  slide.addShape(globalThis.__pptxShapeType.line, {
    x: plotX,
    y: plotY,
    w: 0,
    h: plotH,
    line: { color: "C8DBED", width: 1 },
  });
  categories.forEach((category, index) => {
    slide.addText(truncateText(category, 10), {
      x: plotX + index * (plotW / Math.max(1, categories.length)),
      y: plotY + plotH + 0.04,
      w: 0.7,
      h: 0.1,
      fontFace: "Aptos",
      fontSize: 6,
      color: "555555",
      margin: 0,
      align: "center",
    });
  });
  (chartSpec.series || []).slice(0, 4).forEach((series, seriesIndex) => {
    const color = ["1E5AA8", "444444", "B02B2B", "2F7D53"][seriesIndex % 4];
    const effectiveType = series.type || (chartSpec.chart_type === "combo" && series.y_axis_index === 1 ? "bar" : chartSpec.chart_type);
    let previousPoint = null;
    (series.data || []).slice(0, categories.length).forEach((value, pointIndex) => {
      const px = plotX + 0.22 + pointIndex * (plotW / Math.max(1, categories.length));
      const py = plotY + plotH - ((Number(value) || 0) / maxValue) * (plotH - 0.12);
      if (effectiveType === "bar") {
        slide.addShape(globalThis.__pptxShapeType.roundRect, {
          x: px - 0.08 + seriesIndex * 0.05,
          y: py,
          w: 0.12,
          h: plotY + plotH - py,
          rectRadius: 0.03,
          fill: { color },
          line: { color, transparency: 100 },
        });
      } else {
        slide.addShape(globalThis.__pptxShapeType.ellipse, {
          x: px - 0.04,
          y: py - 0.04,
          w: 0.08,
          h: 0.08,
          fill: { color },
          line: { color, width: 0.5 },
        });
        if (previousPoint) {
          slide.addShape(globalThis.__pptxShapeType.line, {
            x: previousPoint.x,
            y: previousPoint.y,
            w: px - previousPoint.x,
            h: py - previousPoint.y,
            line: { color, width: 1.2 },
          });
        }
        previousPoint = { x: px, y: py };
      }
    });
  });
}

function renderHero(slide, slideDef) {
  const payload = slideDef.composition_payload || {};
  slide.addShape(globalThis.__pptxShapeType.roundRect, {
    x: 0.7,
    y: 1.85,
    w: 11.0,
    h: 0.9,
    rectRadius: 0.08,
    fill: { color: "FFFFFF", transparency: 18 },
    line: { color: "D9D4CC", width: 0.8 },
  });
  slide.addText(truncateText(payload.primary_claim || slideDef.core_message, 120), {
    x: 0.95,
    y: 2.0,
    w: 10.4,
    h: 0.36,
    fontFace: "Aptos",
    fontSize: 15,
    bold: true,
    color: "222222",
    margin: 0,
    fit: "shrink",
  });
  (payload.evidence_items || []).slice(0, 3).forEach((item, index) => {
    const y = 1.9 + index * 0.28;
    const width = 1.6 + index * 0.45;
    slide.addText(truncateText(item.label, 22), {
      x: 8.7,
      y,
      w: 2.2,
      h: 0.14,
      fontFace: "Aptos",
      fontSize: 8,
      bold: true,
      color: "1E5AA8",
      margin: 0,
    });
    slide.addShape(globalThis.__pptxShapeType.roundRect, {
      x: 10.9,
      y: y + 0.03,
      w: 0.55 + width,
      h: 0.08,
      rectRadius: 0.04,
      fill: { color: "1E5AA8", transparency: 8 },
      line: { color: "1E5AA8", transparency: 100 },
    });
  });
  slide.addShape(globalThis.__pptxShapeType.roundRect, {
    x: 0.7,
    y: 2.95,
    w: 11.0,
    h: 0.85,
    rectRadius: 0.08,
    fill: { color: "EAF1F8" },
    line: { color: "EAF1F8", width: 0.5 },
  });
  slide.addText(`Recommendation: ${payload.recommendation || slideDef.core_message}`, {
    x: 0.95,
    y: 3.12,
    w: 5.3,
    h: 0.28,
    fontFace: "Aptos",
    fontSize: 13,
    bold: true,
    color: "1E5AA8",
    margin: 0,
  });
  slide.addText(`Ask: ${payload.decision_ask || slideDef.core_message}`, {
    x: 6.15,
    y: 3.12,
    w: 5.1,
    h: 0.28,
    fontFace: "Aptos",
    fontSize: 13,
    bold: true,
    color: "1E5AA8",
    margin: 0,
  });
  addEvidenceCards(slide, payload.evidence_items || [], 4.1, { cols: 2, cardW: 5.2, cardH: 1.1, valueChars: 84 });
}

function renderDecision(slide, slideDef) {
  const payload = slideDef.composition_payload || {};
  slide.addShape(globalThis.__pptxShapeType.roundRect, {
    x: 0.7,
    y: 1.95,
    w: 4.6,
    h: 4.0,
    rectRadius: 0.08,
    fill: { color: "EDF4FB" },
    line: { color: "C8DBED", width: 1 },
  });
  slide.addText(payload.decision_ask || "Decision ask", {
    x: 0.95,
    y: 2.15,
    w: 4.1,
    h: 0.45,
    fontFace: "Aptos",
    fontSize: 18,
    bold: true,
    color: "1E5AA8",
    margin: 0,
  });
  (payload.options || []).slice(0, 2).forEach((option, index) => {
    const y = 2.8 + index * 1.35;
    slide.addText(truncateText(option.label, 20), {
      x: 0.95,
      y,
      w: 1.7,
      h: 0.2,
      fontFace: "Aptos",
      fontSize: 10,
      bold: true,
      color: "1E5AA8",
      margin: 0,
    });
    slide.addText(truncateText(option.summary, 72), {
      x: 0.95,
      y: y + 0.18,
      w: 4.0,
      h: 0.45,
      fontFace: "Aptos",
      fontSize: 12,
      color: "222222",
      margin: 0,
      fit: "shrink",
    });
  });
  addEvidenceCards(slide, payload.evidence_items || [], 1.95, {
    cols: 1,
    cardW: 5.65,
    cardH: 1.12,
    gapX: 0,
    gapY: 0.18,
    baseX: 5.95,
    maxRows: 3,
    valueChars: 72,
  });
}

function renderRisk(slide, slideDef) {
  const payload = slideDef.composition_payload || {};
  slide.addShape(globalThis.__pptxShapeType.roundRect, {
    x: 0.7,
    y: 1.95,
    w: 3.1,
    h: 2.1,
    rectRadius: 0.06,
    fill: { color: "FFFFFF", transparency: 10 },
    line: { color: "D9D4CC", width: 1 },
  });
  for (let row = 0; row < 3; row += 1) {
    for (let col = 0; col < 3; col += 1) {
      slide.addShape(globalThis.__pptxShapeType.rect, {
        x: 0.92 + col * 0.88,
        y: 2.18 + row * 0.52,
        w: 0.76,
        h: 0.42,
        fill: { color: row === 0 ? "F6D7D4" : row === 1 ? "F6E7C8" : "DDEDDD", transparency: 8 },
        line: { color: "FFFFFF", width: 0.5 },
      });
    }
  }
  slide.addText("Impact", {
    x: 0.55,
    y: 2.82,
    w: 0.5,
    h: 0.14,
    fontFace: "Aptos",
    fontSize: 7,
    bold: true,
    color: "555555",
    rotate: 270,
    margin: 0,
  });
  slide.addText("Likelihood", {
    x: 1.45,
    y: 3.72,
    w: 1.2,
    h: 0.14,
    fontFace: "Aptos",
    fontSize: 7,
    bold: true,
    color: "555555",
    margin: 0,
  });
  const likelihoodPos = { low: 0, medium: 1, high: 2 };
  const impactPos = { high: 0, medium: 1, low: 2 };
  (payload.risk_items || []).slice(0, 4).forEach((item, index) => {
    const col = likelihoodPos[item.likelihood] ?? 1;
    const row = impactPos[item.impact] ?? 1;
    slide.addShape(globalThis.__pptxShapeType.ellipse, {
      x: 1.12 + col * 0.88,
      y: 2.27 + row * 0.52,
      w: 0.34,
      h: 0.24,
      fill: { color: "1E5AA8" },
      line: { color: "1E5AA8", width: 0.5 },
    });
    slide.addText(String(index + 1), {
      x: 1.205 + col * 0.88,
      y: 2.325 + row * 0.52,
      w: 0.16,
      h: 0.08,
      fontFace: "Aptos",
      fontSize: 7,
      bold: true,
      color: "FFFFFF",
      align: "center",
      margin: 0,
    });
  });
  (payload.risk_items || []).slice(0, 2).forEach((item, index) => {
    const x = 4.1 + index * 3.85;
    slide.addShape(globalThis.__pptxShapeType.roundRect, {
      x,
      y: 2.0,
      w: 3.55,
      h: 1.8,
      rectRadius: 0.08,
      fill: { color: "FBEDEC" },
      line: { color: "E3B8B5", width: 1 },
    });
    slide.addText(truncateText(item.label, 74), {
      x: x + 0.15,
      y: 2.16,
      w: 3.2,
      h: 0.44,
      fontFace: "Aptos",
      fontSize: 14,
      bold: true,
      color: "7A2418",
      margin: 0,
      fit: "shrink",
    });
    slide.addText(`${item.likelihood} likelihood / ${item.impact} impact`, {
      x: x + 0.15,
      y: 2.68,
      w: 3.1,
      h: 0.18,
      fontFace: "Aptos",
      fontSize: 9,
      color: "7A2418",
      margin: 0,
    });
    slide.addText(`Owner: ${truncateText(item.owner, 28)}`, {
      x: x + 0.15,
      y: 2.94,
      w: 3.1,
      h: 0.18,
      fontFace: "Aptos",
      fontSize: 9,
      color: "7A2418",
      margin: 0,
    });
    slide.addText(truncateText(item.mitigation, 82), {
      x: x + 0.15,
      y: 3.2,
      w: 3.15,
      h: 0.46,
      fontFace: "Aptos",
      fontSize: 10,
      color: "222222",
      margin: 0,
      fit: "shrink",
    });
  });
  addEvidenceCards(slide, payload.evidence_items || [], 4.15, { cols: 2, cardW: 5.2, cardH: 0.98, valueChars: 70 });
}

function renderTimeline(slide, slideDef) {
  const payload = slideDef.composition_payload || {};
  const events = payload.timeline_events || [];
  events.slice(0, 4).forEach((event, index) => {
    const x = 0.8 + index * 2.7;
    slide.addShape(globalThis.__pptxShapeType.line, {
      x,
      y: 3.05,
      w: index === events.length - 1 ? 0.0 : 2.3,
      h: 0,
      line: { color: "1E5AA8", width: 1.5 },
    });
    slide.addShape(globalThis.__pptxShapeType.ellipse, {
      x,
      y: 2.9,
      w: 0.18,
      h: 0.18,
      fill: { color: "1E5AA8" },
      line: { color: "1E5AA8", width: 1 },
    });
    slide.addText(event.timing, {
      x: x - 0.02,
      y: 2.58,
      w: 0.5,
      h: 0.18,
      fontFace: "Aptos",
      fontSize: 9,
      bold: true,
      color: "1E5AA8",
      margin: 0,
    });
    slide.addText(truncateText(event.label, 42), {
      x: x - 0.02,
      y: 3.18,
      w: 2.2,
      h: 0.4,
      fontFace: "Aptos",
      fontSize: 11,
      bold: true,
      color: "222222",
      margin: 0,
      fit: "shrink",
    });
    slide.addText(truncateText(event.dependency, 48), {
      x: x - 0.02,
      y: 3.62,
      w: 2.2,
      h: 0.35,
      fontFace: "Aptos",
      fontSize: 9,
      color: "555555",
      margin: 0,
      fit: "shrink",
    });
  });
  addEvidenceCards(slide, payload.evidence_items || [], 4.45, { cols: 2, cardW: 5.2, cardH: 1.0, valueChars: 70 });
}

function renderComparison(slide, slideDef) {
  const payload = slideDef.composition_payload || {};
  if (payload.chart_spec) {
    renderChartFallback(slide, payload.chart_spec, 0.7, 1.95, 11.0, 1.25);
  } else {
    (payload.comparison_rows || []).slice(0, 2).forEach((row, index) => {
      const x = 0.7 + index * 5.55;
      slide.addShape(globalThis.__pptxShapeType.roundRect, {
        x,
        y: 1.95,
        w: 5.1,
        h: 1.25,
        rectRadius: 0.06,
        fill: { color: "FFFFFF", transparency: 12 },
        line: { color: "D9D4CC", width: 1 },
      });
      slide.addText(truncateText(row.dimension, 24), {
        x: x + 0.15,
        y: 2.1,
        w: 2.8,
        h: 0.16,
        fontFace: "Aptos",
        fontSize: 8,
        bold: true,
        color: "1E5AA8",
        margin: 0,
      });
      slide.addText(`Now: ${truncateText(row.current_state, 26)}`, {
        x: x + 0.15,
        y: 2.38,
        w: 2.1,
        h: 0.18,
        fontFace: "Aptos",
        fontSize: 9,
        color: "555555",
        margin: 0,
      });
      slide.addText(`Next: ${truncateText(row.target_state, 26)}`, {
        x: x + 2.55,
        y: 2.38,
        w: 2.1,
        h: 0.18,
        fontFace: "Aptos",
        fontSize: 9,
        color: "1E5AA8",
        margin: 0,
      });
      slide.addText(truncateText(row.highlight, 34), {
        x: x + 0.15,
        y: 2.68,
        w: 4.5,
        h: 0.18,
        fontFace: "Aptos",
        fontSize: 8,
        color: "222222",
        margin: 0,
      });
    });
  }
  slide.addShape(globalThis.__pptxShapeType.roundRect, {
    x: 0.7,
    y: 3.45,
    w: 11.0,
    h: 1.75,
    rectRadius: 0.04,
    fill: { color: "FFFFFF", transparency: 14 },
    line: { color: "D9D4CC", width: 1 },
  });
  const headers = ["Dimension", "Current", "Target", "Highlight"];
  const colX = [0.95, 3.9, 6.35, 8.8];
  headers.forEach((header, index) => {
    slide.addText(header, {
      x: colX[index],
      y: 3.63,
      w: 2.1,
      h: 0.18,
      fontFace: "Aptos",
      fontSize: 9,
      bold: true,
      color: "1E5AA8",
      margin: 0,
    });
  });
  (payload.comparison_rows || []).slice(0, 3).forEach((row, index) => {
    const y = 4.0 + index * 0.36;
    [row.dimension, row.current_state, row.target_state, row.highlight].forEach((value, col) => {
      slide.addText(truncateText(value, 38), {
        x: colX[col],
        y,
        w: 2.1,
        h: 0.25,
        fontFace: "Aptos",
        fontSize: 10,
        color: "222222",
        margin: 0,
        fit: "shrink",
      });
    });
  });
  addEvidenceCards(slide, payload.evidence_items || [], 5.35, { cols: 2, cardW: 5.2, cardH: 0.82, valueChars: 62 });
}

function renderMetricStrip(slide, slideDef) {
  const rows = slideDef.composition_payload?.comparison_rows || [];
  if (slideDef.composition_payload?.chart_spec) {
    renderChartFallback(slide, slideDef.composition_payload.chart_spec, 0.7, 1.95, 11.0, 1.5);
  }
  rows.slice(0, 3).forEach((row, index) => {
    const x = 0.7 + index * 3.7;
    slide.addShape(globalThis.__pptxShapeType.roundRect, {
      x,
      y: slideDef.composition_payload?.chart_spec ? 3.7 : 2.0,
      w: 3.35,
      h: 1.45,
      rectRadius: 0.08,
      fill: { color: "EDF4FB" },
      line: { color: "C8DBED", width: 1 },
    });
    slide.addText(row.dimension, {
      x: x + 0.15,
      y: (slideDef.composition_payload?.chart_spec ? 3.86 : 2.16),
      w: 3.0,
      h: 0.16,
      fontFace: "Aptos",
      fontSize: 9,
      bold: true,
      color: "1E5AA8",
      margin: 0,
    });
    slide.addText(truncateText(row.current_state, 28), {
      x: x + 0.15,
      y: (slideDef.composition_payload?.chart_spec ? 4.14 : 2.44),
      w: 3.0,
      h: 0.34,
      fontFace: "Aptos Display",
      fontSize: 18,
      bold: true,
      color: "222222",
      margin: 0,
      fit: "shrink",
    });
    slide.addText(truncateText(row.highlight, 36), {
      x: x + 0.15,
      y: (slideDef.composition_payload?.chart_spec ? 4.6 : 2.9),
      w: 3.0,
      h: 0.32,
      fontFace: "Aptos",
      fontSize: 9,
      color: "555555",
      margin: 0,
      fit: "shrink",
    });
    slide.addShape(globalThis.__pptxShapeType.roundRect, {
      x: x + 0.15,
      y: (slideDef.composition_payload?.chart_spec ? 4.92 : 3.22),
      w: 2.6,
      h: 0.08,
      rectRadius: 0.04,
      fill: { color: "1E5AA8", transparency: 14 + index * 18 },
      line: { color: "1E5AA8", transparency: 100 },
    });
  });
  addEvidenceCards(slide, slideDef.composition_payload?.evidence_items || [], slideDef.composition_payload?.chart_spec ? 5.3 : 4.05, { cols: 2, cardW: 5.2, cardH: 0.98, valueChars: 66 });
}

function renderAppendix(slide, slideDef) {
  const rows = slideDef.composition_payload?.comparison_rows || [];
  rows.slice(0, 3).forEach((row, index) => {
    const y = 2.0 + index * 0.78;
    slide.addShape(globalThis.__pptxShapeType.roundRect, {
      x: 0.7,
      y,
      w: 11.0,
      h: 0.62,
      rectRadius: 0.04,
      fill: { color: "FFFFFF", transparency: 18 },
      line: { color: "D9D4CC", dash: "dash", width: 1 },
    });
    slide.addText(row.current_state, {
      x: 0.9,
      y: y + 0.1,
      w: 2.7,
      h: 0.16,
      fontFace: "Aptos",
      fontSize: 8,
      bold: true,
      color: "1E5AA8",
      margin: 0,
    });
    slide.addText(truncateText(row.target_state, 72), {
      x: 3.25,
      y: y + 0.09,
      w: 5.3,
      h: 0.18,
      fontFace: "Aptos",
      fontSize: 10,
      color: "222222",
      margin: 0,
      fit: "shrink",
    });
    slide.addText(truncateText(row.highlight, 34), {
      x: 8.9,
      y: y + 0.09,
      w: 2.4,
      h: 0.18,
      fontFace: "Aptos",
      fontSize: 9,
      color: "555555",
      margin: 0,
      fit: "shrink",
    });
  });
  addEvidenceCards(slide, slideDef.composition_payload?.evidence_items || [], 4.75, { cols: 2, cardW: 5.2, cardH: 0.9, valueChars: 64 });
}

function renderDefaultEvidence(slide, slideDef) {
  addEvidenceCards(slide, slideDef.composition_payload?.evidence_items || [], 2.35, { cols: 2, cardW: 5.2, cardH: 1.05, valueChars: 76 });
}

async function main() {
  const [inputPath, outputPath] = process.argv.slice(2);

  if (!inputPath || !outputPath) {
    console.error(`Usage: ${usageCommand()} <render-spec.json> <output.pptx>`);
    process.exit(2);
  }

  let pptxgen;
  try {
    const mod = require("pptxgenjs");
    pptxgen = mod.default || mod;
  } catch {
    console.error("pptxgenjs is not installed. Install it first, then rerun this command.");
    console.error("Suggested: npm install pptxgenjs");
    process.exit(1);
  }

  const raw = await fs.readFile(inputPath, "utf8");
  const renderSpec = JSON.parse(raw);
  const pptx = new pptxgen();
  globalThis.__pptxShapeType = pptx.ShapeType;
  pptx.layout = renderSpec.aspect_ratio === "4:3" ? "LAYOUT_4:3" : "LAYOUT_WIDE";
  pptx.author = "ProductOS";
  pptx.subject = renderSpec.render_spec_id || renderSpec.slide_spec_id;
  pptx.title = renderSpec.render_spec_id || renderSpec.slide_spec_id;

  for (const slideDef of renderSpec.slides) {
    const slide = pptx.addSlide();
    slide.background = { color: "F7F2E8" };
    slide.addShape(globalThis.__pptxShapeType.line, {
      x: 0.6,
      y: 0.38,
      w: 11.2,
      h: 0,
      line: { color: "1E5AA8", width: 2 },
    });
    slide.addText(slideDef.headline || slideDef.title, {
      x: 0.6,
      y: 0.56,
      w: 11.2,
      h: 0.62,
      fontFace: "Aptos Display",
      fontSize: 20,
      bold: true,
      color: "111111",
      fit: "shrink",
    });

    let cursorY = 1.5;
    slide.addText(truncateText(slideDef.core_message || slideDef.title, 116), {
      x: 0.8,
      y: cursorY,
      w: 10.8,
      h: 0.5,
      fontFace: "Aptos",
      fontSize: 14,
      bold: true,
      color: "222222",
      margin: 0.06,
      fit: "shrink",
    });
    cursorY += 0.6;

    if (slideDef.composition_type === "hero_statement") {
      renderHero(slide, slideDef);
    } else if (slideDef.composition_type === "decision_frame") {
      renderDecision(slide, slideDef);
    } else if (slideDef.composition_type === "risk_matrix") {
      renderRisk(slide, slideDef);
    } else if (slideDef.composition_type === "timeline_with_dependencies") {
      renderTimeline(slide, slideDef);
    } else if (slideDef.composition_type === "comparison_table") {
      renderComparison(slide, slideDef);
    } else if (slideDef.composition_type === "metric_strip") {
      renderMetricStrip(slide, slideDef);
    } else if (slideDef.composition_type === "appendix_evidence") {
      renderAppendix(slide, slideDef);
    } else {
      renderDefaultEvidence(slide, slideDef);
    }

    slide.addText(`Sources: ${truncateText((slideDef.source_refs || []).join(", "), 82)}`, {
      x: 0.8,
      y: 6.85,
      w: 10.8,
      h: 0.22,
      fontFace: "Aptos",
      fontSize: 8,
      color: "1E5AA8",
      margin: 0.04,
    });
    slide.addNotes(`
Primary claim: ${slideDef.composition_payload?.primary_claim || slideDef.core_message}
Speaker notes: ${slideDef.speaker_notes || ""}
`);
  }

  await pptx.writeFile({ fileName: outputPath });
  console.log(`PPTX written: ${outputPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
