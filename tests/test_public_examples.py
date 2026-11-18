from __future__ import annotations

import copy
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PYTHON_EXAMPLES = ROOT / "examples" / "python"
sys.path.insert(0, str(PYTHON_EXAMPLES))

from batch_wine_search import batch_search
from client import collect
from export_vintages import export_run


SAMPLE_ROW = json.loads((ROOT / "data" / "sample-output.json").read_text(encoding="utf-8"))[0]
FIXTURE_TOKEN = "fixture-token"


class ApiState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.start_requests = []
        self.runs = {}
        self.fail_start = False
        self.summary_status = "succeeded"
        self.summary_reason = "result_limit"
        self.summary_rows_override = None

    def add_run(self, run_id: str, run_input: dict, rows: list[dict]) -> dict:
        store_id = "store-" + run_id
        dataset_id = "dataset-" + run_id
        run = {
            "id": run_id,
            "actId": "fixture-actor",
            "userId": "fixture-user",
            "startedAt": "2026-11-18T10:00:00.000Z",
            "finishedAt": "2026-11-18T10:00:01.000Z",
            "status": "SUCCEEDED",
            "statusMessage": "Fixture run completed",
            "isStatusMessageTerminal": True,
            "meta": {"origin": "API"},
            "options": {"build": "latest", "timeoutSecs": 180, "memoryMbytes": 256, "diskMbytes": 1024},
            "buildId": "fixture-build",
            "defaultDatasetId": dataset_id,
            "defaultKeyValueStoreId": store_id,
            "defaultRequestQueueId": "queue-" + run_id,
            "stats": {"durationMillis": 1000, "runTimeSecs": 1, "computeUnits": 0},
        }
        summary_rows = len(rows)
        if self.summary_rows_override is not None:
            summary_rows = self.summary_rows_override
        summary = {
            "status": self.summary_status,
            "reason": self.summary_reason,
            "rows": summary_rows,
            "sourceMatches": len(rows),
            "pendingRows": 0,
            "missingVintageIds": [],
        }
        self.runs[run_id] = {
            "run": run,
            "input": run_input,
            "rows": rows,
            "summary": summary,
        }
        return run

    def seed_existing_run(self, run_id: str = "run-existing") -> None:
        self.add_run(run_id, {}, [copy.deepcopy(SAMPLE_ROW)])


@contextmanager
def api_fixture():
    state = ApiState()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def send_json(self, status: int, payload) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def send_dataset_page(self, offset: int, limit: int, rows: list[dict], page: list[dict]) -> None:
            body = json.dumps(page).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Apify-Pagination-Offset", str(offset))
            self.send_header("X-Apify-Pagination-Limit", str(limit))
            self.send_header("X-Apify-Pagination-Count", str(len(page)))
            self.send_header("X-Apify-Pagination-Total", str(len(rows)))
            self.send_header("X-Apify-Pagination-Desc", "false")
            self.end_headers()
            self.wfile.write(body)

        def authorized(self) -> bool:
            return self.headers.get("Authorization") == "Bearer " + FIXTURE_TOKEN

        def do_POST(self) -> None:
            parsed = urlsplit(self.path)
            if not self.authorized():
                self.send_json(401, {"error": "unauthorized"})
                return
            run_path = "/v2/acts/datascraperes~vivino-wine-scraper/runs"
            sync_path = "/v2/acts/datascraperes~vivino-wine-scraper/run-sync-get-dataset-items"
            if parsed.path not in (run_path, sync_path):
                self.send_json(404, {"error": "not found"})
                return

            size = int(self.headers.get("Content-Length", "0"))
            run_input = json.loads(self.rfile.read(size).decode("utf-8"))
            with state.lock:
                state.start_requests.append(
                    {
                        "input": run_input,
                        "query": parse_qs(parsed.query),
                        "authorized": True,
                    }
                )
                if state.fail_start:
                    self.send_json(503, {"error": "fixture start unavailable"})
                    return
                row = copy.deepcopy(SAMPLE_ROW)
                if run_input.get("searchTerm", "").casefold() == "rioja":
                    row["name"] = "Example Rioja 2021"
                if parsed.path == run_path:
                    run_id = "run-" + str(len(state.runs) + 1)
                    state.add_run(run_id, run_input, [row])
            if parsed.path == sync_path:
                self.send_json(201, [row])
            else:
                self.send_json(201, {"data": {"id": run_id}})

        def do_GET(self) -> None:
            parsed = urlsplit(self.path)
            if not self.authorized():
                self.send_json(401, {"error": "unauthorized"})
                return

            parts = parsed.path.strip("/").split("/")
            if len(parts) == 3 and parts[:2] == ["v2", "actor-runs"]:
                run_data = state.runs.get(parts[2])
                if not run_data:
                    self.send_json(404, {"error": "run not found"})
                    return
                self.send_json(200, {"data": run_data["run"]})
                return

            if (
                len(parts) == 5
                and parts[0:2] == ["v2", "key-value-stores"]
                and parts[4] == "SUMMARY"
            ):
                store_id = parts[2]
                run_data = next(
                    (entry for entry in state.runs.values()
                     if entry["run"]["defaultKeyValueStoreId"] == store_id),
                    None,
                )
                if not run_data:
                    self.send_json(404, {"error": "record not found"})
                    return
                self.send_json(200, run_data["summary"])
                return

            if len(parts) == 4 and parts[0:2] == ["v2", "datasets"] and parts[3] == "items":
                dataset_id = parts[2]
                run_data = next(
                    (entry for entry in state.runs.values()
                     if entry["run"]["defaultDatasetId"] == dataset_id),
                    None,
                )
                if not run_data:
                    self.send_json(404, {"error": "dataset not found"})
                    return
                query = parse_qs(parsed.query)
                offset = int(query.get("offset", ["0"])[0])
                limit = int(query.get("limit", ["100"])[0])
                page = run_data["rows"][offset : offset + limit]
                self.send_dataset_page(offset, limit, run_data["rows"], page)
                return

            self.send_json(404, {"error": "not found"})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield state, "http://127.0.0.1:" + str(server.server_port)
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


class PublicExampleTests(unittest.TestCase):
    def test_primary_search_uses_one_bounded_authenticated_start(self) -> None:
        with api_fixture() as (state, api_url):
            client, run, summary, rows = collect(
                {"searchTerm": "Barolo", "maxResults": 3},
                token=FIXTURE_TOKEN,
                api_url=api_url,
                max_total_charge_usd="0.003",
                page_size=1,
            )
            self.assertEqual(run.status, "SUCCEEDED")
            self.assertEqual(summary["status"], "succeeded")
            self.assertEqual(len(rows), 1)
            self.assertEqual(len(state.start_requests), 1)
            request = state.start_requests[0]
            self.assertTrue(request["authorized"])
            self.assertEqual(request["input"]["searchTerm"], "Barolo")
            self.assertEqual(request["query"]["maxTotalChargeUsd"], ["0.003"])
            self.assertIsNotNone(client)

    def test_batch_starts_once_per_distinct_term_and_deduplicates_vintages(self) -> None:
        with api_fixture() as (state, api_url):
            rows = batch_search(
                ["Barolo", " barolo ", "Rioja"],
                token=FIXTURE_TOKEN,
                api_url=api_url,
                page_size=1,
            )
            self.assertEqual(len(state.start_requests), 2)
            self.assertEqual(
                [entry["input"]["searchTerm"] for entry in state.start_requests],
                ["Barolo", "Rioja"],
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["vintageId"], SAMPLE_ROW["vintageId"])
            self.assertEqual(
                [entry["query"]["maxTotalChargeUsd"] for entry in state.start_requests],
                [["0.003"], ["0.003"]],
            )

    def test_partial_summary_keeps_confirmed_rows_without_restarting(self) -> None:
        with api_fixture() as (state, api_url):
            state.summary_status = "partial"
            state.summary_reason = "source_wait"
            _, _, summary, rows = collect(
                {"searchTerm": "Barolo", "maxResults": 3},
                token=FIXTURE_TOKEN,
                api_url=api_url,
                page_size=1,
            )
            self.assertEqual(summary["status"], "partial")
            self.assertEqual(len(rows), 1)
            self.assertEqual(len(state.start_requests), 1)

    def test_start_failure_is_not_replayed(self) -> None:
        with api_fixture() as (state, api_url):
            state.fail_start = True
            with self.assertRaisesRegex(RuntimeError, "does not send a second start"):
                collect(
                    {"searchTerm": "Barolo"},
                    token=FIXTURE_TOKEN,
                    api_url=api_url,
                )
            self.assertEqual(len(state.start_requests), 1)

    def test_summary_mismatch_blocks_export_without_another_start(self) -> None:
        with api_fixture() as (state, api_url):
            state.summary_rows_override = 2
            with self.assertRaisesRegex(RuntimeError, "row count differs"):
                collect(
                    {"searchTerm": "Barolo"},
                    token=FIXTURE_TOKEN,
                    api_url=api_url,
                    page_size=1,
                )
            self.assertEqual(len(state.start_requests), 1)

    def test_existing_run_export_does_not_start_an_actor(self) -> None:
        with api_fixture() as (state, api_url):
            state.seed_existing_run()
            with tempfile.TemporaryDirectory() as directory:
                destination = Path(directory) / "vintages.csv"
                count = export_run(
                    "run-existing",
                    destination,
                    token=FIXTURE_TOKEN,
                    api_url=api_url,
                    page_size=1,
                )
                self.assertEqual(count, 1)
                self.assertEqual(len(state.start_requests), 0)
                with destination.open(encoding="utf-8", newline="") as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["vintageId"], str(SAMPLE_ROW["vintageId"]))
                self.assertEqual(rows[0]["winery"], SAMPLE_ROW["winery"]["name"])

    def test_curl_example_uses_sync_endpoint_and_small_cost_cap(self) -> None:
        curl = shutil.which("curl.exe") or shutil.which("curl")
        if not curl:
            self.skipTest("curl is not installed")
        with api_fixture() as (state, api_url):
            url = (
                api_url
                + "/v2/acts/datascraperes~vivino-wine-scraper/"
                + "run-sync-get-dataset-items?timeout=300&maxTotalChargeUsd=0.003"
            )
            result = subprocess.run(
                [
                    curl,
                    "--fail",
                    "--silent",
                    "--show-error",
                    "--request",
                    "POST",
                    url,
                    "--header",
                    "Authorization: Bearer " + FIXTURE_TOKEN,
                    "--header",
                    "Content-Type: application/json",
                    "--data-binary",
                    "@data/sample-input.json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=15,
                check=True,
            )
            rows = json.loads(result.stdout)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["vintageId"], SAMPLE_ROW["vintageId"])
            self.assertEqual(len(state.start_requests), 1)
            self.assertEqual(
                state.start_requests[0]["query"]["maxTotalChargeUsd"], ["0.003"]
            )

    def test_javascript_example_uses_the_authenticated_api_fixture(self) -> None:
        with api_fixture() as (state, api_url):
            environment = os.environ.copy()
            environment["PUBLIC_EXAMPLE_TEST_API_URL"] = api_url
            environment["APIFY_API_TOKEN"] = FIXTURE_TOKEN
            result = subprocess.run(
                ["node", str(ROOT / "tests" / "javascript_example_test.mjs")],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                timeout=15,
                check=True,
            )
            self.assertIn("JavaScript API fixture passed", result.stdout)
            self.assertEqual(len(state.start_requests), 1)
            self.assertEqual(state.start_requests[0]["query"]["maxTotalChargeUsd"], ["0.003"])


if __name__ == "__main__":
    unittest.main()
