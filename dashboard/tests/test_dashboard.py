from __future__ import annotations

import json
import tempfile
import threading
import urllib.request
from pathlib import Path

from dashboard.server import create_server


def request(base_url: str, path: str, method: str = "GET", payload: dict | None = None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request_object = urllib.request.Request(
        f"{base_url}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request_object, timeout=5) as response:
        return response.status, response.headers.get_content_type(), response.read()


def test_dashboard_run_lifecycle_and_history():
    with tempfile.TemporaryDirectory() as temporary_directory:
        server = create_server("127.0.0.1", 0, Path(temporary_directory) / "dashboard.sqlite3")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            status, _, body = request(base_url, "/api/health")
            assert status == 200
            assert json.loads(body)["status"] == "ok"

            status, _, _ = request(base_url, "/api/runs", "POST", {
                "run_id": "run-android-1",
                "platform": "android",
                "app_version": "1.0.0",
                "device": "device-1",
                "started_at": "2026-09-04T01:00:00+00:00",
            })
            assert status == 201

            for case_status in ("passed", "failed", "skipped"):
                status, _, _ = request(base_url, "/api/runs/run-android-1/cases", "POST", {
                    "case_id": f"case-{case_status}",
                    "name": f"Case {case_status}",
                    "status": case_status,
                    "duration_seconds": 2.5,
                    "log": "OpenCV/OCR result",
                    "artifacts": {"screenshot": "case.png"},
                })
                assert status == 201

            status, _, body = request(base_url, "/api/runs/run-android-1/complete", "POST", {
                "status": "failed",
                "ended_at": "2026-09-04T01:01:00+00:00",
            })
            assert status == 200
            run = json.loads(body)
            assert run["total_cases"] == 3
            assert run["passed_cases"] == 1
            assert run["failed_cases"] == 1
            assert run["skipped_cases"] == 1
            assert run["pass_rate"] == 33.3
            assert len(run["cases"]) == 3

            status, _, body = request(base_url, "/api/runs?platform=android")
            assert status == 200
            assert [item["run_id"] for item in json.loads(body)["items"]] == ["run-android-1"]

            status, content_type, body = request(base_url, "/")
            assert status == 200
            assert content_type == "text/html"
            assert "UIAutotest 测试历史" in body.decode("utf-8")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

