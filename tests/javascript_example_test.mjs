import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { collect } from "../examples/javascript/request.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const input = JSON.parse(await fs.readFile(path.join(root, "data", "sample-input.json"), "utf8"));
const result = await collect(input, {
  token: process.env.APIFY_API_TOKEN,
  apiUrl: process.env.PUBLIC_EXAMPLE_TEST_API_URL,
  pollIntervalMs: 0,
  timeoutMs: 5000,
});

assert.equal(result.summary.status, "succeeded");
assert.equal(result.rows.length, result.summary.rows);
assert.equal(result.rows[0].vintageId, 1200001);
console.log("JavaScript API fixture passed");
