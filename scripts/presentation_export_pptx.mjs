#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const entrypoint = path.join(
  __dirname,
  "..",
  "components",
  "presentation",
  "node",
  "export_presentation_pptx.mjs",
);

const result = spawnSync(process.execPath, [entrypoint, ...process.argv.slice(2)], {
  env: {
    ...process.env,
    PRODUCTOS_PRESENTATION_PPT_USAGE: "node scripts/presentation_export_pptx.mjs",
  },
  stdio: "inherit",
});

if (result.error) {
  throw result.error;
}

process.exit(result.status ?? 1);
