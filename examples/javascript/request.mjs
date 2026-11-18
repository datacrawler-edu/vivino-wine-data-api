import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ACTOR_ID = "datascraperes~vivino-wine-scraper";
const DEFAULT_API_URL = "https://api.apify.com";
const EVENT_BUDGET_USD = "0.003";
const PAGE_SIZE = 100;

async function request(apiUrl, token, relativePath, options = {}) {
  const response = await fetch(apiUrl.replace(/\/$/, "") + "/v2/" + relativePath, {
    ...options,
    headers: {
      Authorization: "Bearer " + token,
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) {
    throw new Error("Apify API returned HTTP " + response.status + ".");
  }
  const payload = await response.json();
  return payload && Object.prototype.hasOwnProperty.call(payload, "data")
    ? payload.data
    : payload;
}

export async function collect(
  runInput,
  {
    token = process.env.APIFY_API_TOKEN,
    apiUrl = DEFAULT_API_URL,
    pollIntervalMs = 2000,
    timeoutMs = 240000,
  } = {},
) {
  if (!token) {
    throw new Error("Set APIFY_API_TOKEN before calling the Actor.");
  }

  let started;
  try {
    started = await request(
      apiUrl,
      token,
      "acts/" + ACTOR_ID + "/runs?timeout=180&maxTotalChargeUsd=" + EVENT_BUDGET_USD,
      { method: "POST", body: JSON.stringify(runInput) },
    );
  } catch {
    throw new Error(
      "The start response was unavailable. Inspect existing runs in Apify Console before trying again; this example does not send a second start.",
    );
  }

  const runId = started.id;
  console.error("Run ID: " + runId);
  const deadline = Date.now() + timeoutMs;
  let run = null;
  while (Date.now() < deadline) {
    run = await request(apiUrl, token, "actor-runs/" + runId);
    if (["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"].includes(run.status)) {
      break;
    }
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
  if (!run || run.status !== "SUCCEEDED") {
    throw new Error(
      "Inspect existing run " + runId + "; it did not finish successfully. Do not start another run automatically.",
    );
  }

  const summary = await request(
    apiUrl,
    token,
    "key-value-stores/" + run.defaultKeyValueStoreId + "/records/SUMMARY",
  );
  if (!summary || !["succeeded", "partial", "failed"].includes(summary.status)) {
    throw new Error("The run has no readable SUMMARY record or its status is unknown.");
  }
  if (summary.status === "failed") {
    throw new Error("The SUMMARY record reports failure; inspect run " + runId + ".");
  }

  const rows = [];
  const seenVintages = new Set();
  let offset = 0;
  while (true) {
    const page = await request(
      apiUrl,
      token,
      "datasets/" + run.defaultDatasetId
        + "/items?clean=false&desc=false&limit=" + PAGE_SIZE + "&offset=" + offset,
    );
    if (!Array.isArray(page)) {
      throw new Error("Dataset API did not return an item array.");
    }
    for (const row of page) {
      if (!Number.isInteger(row.vintageId) || seenVintages.has(row.vintageId)) {
        throw new Error("The Dataset contains a missing or duplicate vintageId.");
      }
      seenVintages.add(row.vintageId);
      rows.push(row);
    }
    offset += page.length;
    if (page.length < PAGE_SIZE) break;
  }

  if (summary.rows !== rows.length) {
    throw new Error("Dataset row count differs from SUMMARY; inspect run " + runId + ".");
  }
  if (summary.status === "partial") {
    console.error(
      "Partial collection: reason=" + summary.reason
        + ", missingVintageIds=" + JSON.stringify(summary.missingVintageIds || []),
    );
  }
  return { runId, summary, rows };
}

async function main() {
  const scriptPath = fileURLToPath(import.meta.url);
  const root = path.resolve(path.dirname(scriptPath), "../..");
  const runInput = JSON.parse(
    await fs.readFile(path.join(root, "data", "sample-input.json"), "utf8"),
  );
  const result = await collect(runInput);
  console.log(JSON.stringify(result.rows, null, 2));
}

const invokedPath = process.argv[1] ? path.resolve(process.argv[1]) : "";
if (invokedPath === fileURLToPath(import.meta.url)) {
  await main();
}
