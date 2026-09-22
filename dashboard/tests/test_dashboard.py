from __future__ import annotations

import json
import os
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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
            assert "Swan 测试平台" in body.decode("utf-8")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


WEBHOOK_SECRET = "hook-secret"
FULL_SHA = "ab12cd34ef56" * 3 + "ab12"


def test_gitlab_webhook_auto_build():
    with tempfile.TemporaryDirectory() as temporary_directory:
        # mock Jenkins:对 buildWithParameters 回 201+Location,捕获 form 参数
        captured = []

        class MockJenkins(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0") or 0)
                captured.append(dict(urllib.parse.parse_qsl(self.rfile.read(length).decode("utf-8"))))
                self.send_response(201)
                self.send_header("Location", "http://mock-jenkins/queue/item/88/")
                self.end_headers()

            def log_message(self, *args):
                pass

        jenkins_server = ThreadingHTTPServer(("127.0.0.1", 0), MockJenkins)
        threading.Thread(target=jenkins_server.serve_forever, daemon=True).start()
        env_keys = ("JENKINS_BASE_URL", "JENKINS_USER", "JENKINS_API_TOKEN", "GITLAB_WEBHOOK_SECRET")
        env_backup = {key: os.environ.get(key) for key in env_keys}
        os.environ.update({
            "JENKINS_BASE_URL": f"http://127.0.0.1:{jenkins_server.server_address[1]}",
            "JENKINS_USER": "mock",
            "JENKINS_API_TOKEN": "mock",
            "GITLAB_WEBHOOK_SECRET": WEBHOOK_SECRET,
        })
        server = create_server("127.0.0.1", 0, Path(temporary_directory) / "dashboard.sqlite3")
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base_url = f"http://127.0.0.1:{server.server_address[1]}"

        def post(path: str, payload: dict, token: str | None = WEBHOOK_SECRET):
            headers = {"Content-Type": "application/json"}
            if token is not None:
                headers["X-GitLab-Token"] = token
            request_object = urllib.request.Request(
                f"{base_url}{path}", data=json.dumps(payload).encode("utf-8"),
                method="POST", headers=headers)
            try:
                with urllib.request.urlopen(request_object, timeout=5) as response:
                    return response.status, json.loads(response.read())
            except urllib.error.HTTPError as error:
                return error.code, json.loads(error.read())

        def push(ref: str = "refs/heads/dev", after: str = FULL_SHA,
                 user: str = "wujianneng", kind: str = "push") -> dict:
            return {"object_kind": kind, "ref": ref, "after": after, "user_name": user,
                    "project": {"path_with_namespace": "swan-app/swan-audio/hivi-network-flutterapp"}}

        try:
            # 未带/带错 token → 401(非 2xx 交 GitLab 丢弃重试策略)
            status, _ = post("/api/webhooks/gitlab", push(), token=None)
            assert status == 401
            status, _ = post("/api/webhooks/gitlab", push(), token="wrong")
            assert status == 401
            assert captured == []

            # 非 push 事件 / 映射外分支 → 恒 200 skip,不碰 Jenkins
            status, body = post("/api/webhooks/gitlab", push(kind="note"))
            assert status == 200 and body["action"] == "skipped"
            status, body = post("/api/webhooks/gitlab", push(ref="refs/heads/master"))
            assert status == 200 and body["action"] == "skipped"
            status, body = post("/api/webhooks/gitlab", push(after="0" * 40))
            assert status == 200 and body["action"] == "skipped"
            assert captured == []

            # dev 合入推送 → 触发 Jenkins,参数服务端组装
            status, body = post("/api/webhooks/gitlab", push())
            assert status == 200 and body["action"] == "triggered"
            assert body["job"] == "swan-audio-build"
            assert body["commit"] == FULL_SHA[:7]
            assert captured[-1] == {"BRANCH": "dev", "SERVER_TYPE": "test",
                                    "COMMIT": FULL_SHA, "NOTES": "webhook%3Awujianneng"}

            # pusher 带命令特殊字符 → 不进 notes,回退固定前缀(坑 15 注入面)
            status, body = post("/api/webhooks/gitlab", push(user="x & dir"))
            assert status == 200 and body["action"] == "triggered"
            assert captured[-1]["NOTES"] == "webhook"

            # 同 commit 已登记 → 去重 skip(先手工登记同 commit 行)
            status, _, _ = request(base_url, "/api/apks", "POST", {
                "apk_id": f"swan-dev-{FULL_SHA[:7]}-20260922-test", "branch": "dev",
                "commit_hash": FULL_SHA[:7], "server_type": "test",
                "file_path": "/tmp/x.apk", "source": "auto-build",
            })
            assert status == 201
            status, body = post("/api/webhooks/gitlab", push())
            assert status == 200 and body["action"] == "skipped"
            assert "已登记" in body["reason"]
        finally:
            for key, value in env_backup.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            server.shutdown()
            server.server_close()
            jenkins_server.shutdown()
            jenkins_server.server_close()

