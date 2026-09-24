from __future__ import annotations

import gc
import json
import os
import tempfile
import time
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
            status, body = post("/api/webhooks/gitlab", push(ref="refs/heads/harmony"))
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

            # webhook 触发同样落流水线任务行(2026-09-24):流水线页"最近任务"可见
            assert body["pipeline_job"]
            status, _, jobs_body = request(base_url, "/api/pipeline/jobs?limit=30")
            rows = json.loads(jobs_body)["items"]
            assert len(rows) == 1
            row = rows[0]
            assert row["trigger_source"] == "webhook" and row["status"] == "pending"
            assert row["branch"] == "dev" and row["jenkins_job"] == "swan-audio-build"
            assert row["result"]["jenkins_queue_id"] == 88
            assert row["result"]["build"]["commit"] == FULL_SHA[:7]

            # master 合入推送 → formal(正式服/release)自动打包
            status, body = post("/api/webhooks/gitlab", push(ref="refs/heads/master"))
            assert status == 200 and body["action"] == "triggered"
            assert captured[-1] == {"BRANCH": "master", "SERVER_TYPE": "formal",
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

            # core 仓(dev)推送(2026-09-23):同 sha 已按 app 口径登记也不去重,
            # 触发打包但不传 COMMIT(COMMIT 是 app 仓要签出的 commit,core sha 不适用)
            def push_core(ref: str = "refs/heads/dev") -> dict:
                return {"object_kind": "push", "ref": ref, "after": FULL_SHA,
                        "user_name": "wujianneng",
                        "project": {"path_with_namespace":
                                    "swan-app/swan-audio/hivi_network_flutter_core"}}

            status, body = post("/api/webhooks/gitlab", push_core())
            assert status == 200 and body["action"] == "triggered"
            assert "commit" not in body
            assert captured[-1] == {"BRANCH": "dev", "SERVER_TYPE": "test",
                                    "NOTES": "webhook%3Awujianneng"}
            # core master → formal;映射外分支照旧 skip
            status, body = post("/api/webhooks/gitlab", push_core(ref="refs/heads/master"))
            assert status == 200 and body["action"] == "triggered"
            assert captured[-1] == {"BRANCH": "master", "SERVER_TYPE": "formal",
                                    "NOTES": "webhook%3Awujianneng"}
            status, body = post("/api/webhooks/gitlab", push_core(ref="refs/heads/harmony"))
            assert status == 200 and body["action"] == "skipped"

            # webhook 行累计 5 条:app dev/master/坏 pusher + core dev/master;skip 不落行
            status, _, jobs_body = request(base_url, "/api/pipeline/jobs?limit=30")
            rows = json.loads(jobs_body)["items"]
            assert len(rows) == 5
            assert all(row["trigger_source"] == "webhook" for row in rows)
            assert sorted(row["branch"] for row in rows) == ["dev"] * 3 + ["master"] * 2
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
            gc.collect()  # 例外/回溯帧可能循环引用 sqlite 连接;Windows 删库文件需句柄已关



def test_webhook_build_resolver():
    """webhook 触发的流水线任务行:队列项已被清后按 NOTES webhook 前缀回查闭环(2026-09-24)。"""
    with tempfile.TemporaryDirectory() as temporary_directory:
        # 构建时间戳取"未来 1 分钟":回查按 timestamp >= 任务 created_at 筛候选,
        # 测试启动时刻若晚于任务创建会误伤,这里给足余量
        build_ts = int(time.time() * 1000) + 60_000

        class MockJenkins(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0") or 0)
                self.rfile.read(length)
                self.send_response(201)
                self.send_header("Location", "http://mock-jenkins/queue/item/77/")
                self.end_headers()

            def do_GET(self):
                def reply(payload):
                    body = json.dumps(payload).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                if "/queue/item/77/" in self.path:
                    self.send_response(404)  # 队列项已被清 → 走第二遍候选回查
                    self.end_headers()
                elif "tree=actions[parameters" in self.path:
                    # build_parameters 读原生 actions 平铺;NOTES 保持触发时的 URL 编码态
                    reply({"actions": [{"parameters": [
                        {"name": "NOTES", "value": "webhook%3Awujianneng"}]}]})
                elif "tree=builds[" in self.path:
                    reply({"builds": [{"number": 21, "result": None,
                                       "building": False, "timestamp": build_ts}]})
                elif "/job/swan-audio-build/21/" in self.path:
                    reply({"building": False, "result": "SUCCESS"})
                else:
                    self.send_response(404)
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

        try:
            # core 仓推送触发(无 COMMIT):任务行落库,queue_id=77
            payload = {"object_kind": "push", "ref": "refs/heads/dev", "after": FULL_SHA,
                       "user_name": "wujianneng",
                       "project": {"path_with_namespace":
                                   "swan-app/swan-audio/hivi_network_flutter_core"}}
            request_object = urllib.request.Request(
                f"{base_url}/api/webhooks/gitlab",
                data=json.dumps(payload).encode("utf-8"), method="POST",
                headers={"Content-Type": "application/json",
                         "X-GitLab-Token": WEBHOOK_SECRET})
            with urllib.request.urlopen(request_object, timeout=5) as response:
                body = json.loads(response.read())
            assert body["action"] == "triggered" and body["queue_id"] == 77
            job_id = body["pipeline_job"]
            assert job_id

            # 列表读取 → queue 404 → 候选回查(NOTES webhook 前缀)→ 构建 21 SUCCESS
            status, _, jobs_body = request(base_url, "/api/pipeline/jobs?limit=30")
            rows = json.loads(jobs_body)["items"]
            row = next(j for j in rows if j["job_id"] == job_id)
            assert row["trigger_source"] == "webhook"
            assert row["jenkins_build"] == 21
            assert row["status"] == "succeeded" and row["finished_at"]
            assert row["result"]["build"]["server_type"] == "test"
            assert row["result"]["jenkins_queue_id"] == 77
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
            gc.collect()  # 例外/回溯帧可能循环引用 sqlite 连接;Windows 删库文件需句柄已关


def test_build_pipeline_config():
    """打包型流水线(kind=build):配置校验 / run 触发打包 job / agent 不认领 /
    列表读取时向 Jenkins 惰性回查终态。"""
    with tempfile.TemporaryDirectory() as temporary_directory:
        captured = []
        build_result = {"building": False, "result": "SUCCESS"}

        class MockJenkins(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0") or 0)
                captured.append(dict(urllib.parse.parse_qsl(self.rfile.read(length).decode("utf-8"))))
                self.send_response(201)
                self.send_header("Location", "http://mock-jenkins/queue/item/88/")
                self.end_headers()

            def do_GET(self):
                def reply(payload):
                    body = json.dumps(payload).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                if "/queue/item/88/" in self.path:
                    reply({"executable": {"number": 9}})
                elif "/job/swan-audio-build/9/" in self.path:
                    reply(build_result)
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, *args):
                pass

        jenkins_server = ThreadingHTTPServer(("127.0.0.1", 0), MockJenkins)
        threading.Thread(target=jenkins_server.serve_forever, daemon=True).start()
        env_keys = ("JENKINS_BASE_URL", "JENKINS_USER", "JENKINS_API_TOKEN")
        env_backup = {key: os.environ.get(key) for key in env_keys}
        os.environ.update({
            "JENKINS_BASE_URL": f"http://127.0.0.1:{jenkins_server.server_address[1]}",
            "JENKINS_USER": "mock",
            "JENKINS_API_TOKEN": "mock",
        })
        server = create_server("127.0.0.1", 0, Path(temporary_directory) / "dashboard.sqlite3")
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base_url = f"http://127.0.0.1:{server.server_address[1]}"

        def create(payload: dict):
            # 400 属预期分支,request() 不捕 HTTPError,这里照 webhook 测试自行捕
            try:
                return request(base_url, "/api/pipeline-configs", "POST", payload)
            except urllib.error.HTTPError as error:
                return error.code, None, error.read()

        try:
            # 校验:server_type 非法 / branch 带命令字符(坑 15)→ 400
            status, _, _ = create({
                "config_id": "PIPE-BUILD-BAD", "name": "bad", "kind": "build",
                "schedule_type": "daily", "schedule_param": {"time": "04:17"},
                "build_param": {"branch": "dev", "server_type": "staging"}})
            assert status == 400
            status, _, _ = create({
                "config_id": "PIPE-BUILD-BAD", "name": "bad", "kind": "build",
                "schedule_type": "daily", "schedule_param": {"time": "04:17"},
                "build_param": {"branch": "dev & dir", "server_type": "test"}})
            assert status == 400

            # 合法创建:suite_id/include_build 强制置空,build_param 回显
            status, _, body = create({
                "config_id": "PIPE-BUILD-TEST", "name": "每日打包-测试服", "kind": "build",
                "schedule_type": "daily", "schedule_param": {"time": "04:17"},
                "build_param": {"branch": "dev", "server_type": "test"}})
            assert status == 201
            config = json.loads(body)
            assert config["kind"] == "build" and config["suite_id"] == ""
            assert config["include_build"] == 0
            assert config["build"] == {"branch": "dev", "server_type": "test"}
            assert config["next_run_at"]  # 调度器靠它到点触发

            # run:触发 swan-audio-build(NOTES 编码同 /api/builds),任务行 build 来源
            status, _, body = request(base_url, "/api/pipeline-configs/PIPE-BUILD-TEST/run",
                                      "POST", {})
            assert status == 201  # run 端点惯例返回 CREATED
            job = json.loads(body)["job"]
            assert captured[-1] == {"BRANCH": "dev", "SERVER_TYPE": "test",
                                    "NOTES": "pipeline%3APIPE-BUILD-TEST"}
            assert job["trigger_source"] == "build" and job["status"] == "pending"
            assert job["jenkins_job"] == "swan-audio-build"  # 派发已回填
            assert job["result"]["build"]["pipeline"] == "PIPE-BUILD-TEST"

            # 轮询认领不碰 build 任务(无 agent 跑用例)→ 无可认领任务
            try:
                request(base_url, "/api/pipeline/claim", "POST", {"agent": "t"})
                claim_status = 200
            except urllib.error.HTTPError as error:
                claim_status = error.code
            assert claim_status == 404

            # 列表读取 → resolver 惰性回查:queue→构建号 9 → SUCCESS → succeeded
            status, _, body = request(base_url, "/api/pipeline/jobs?limit=30")
            assert status == 200
            jobs = json.loads(body)["items"]
            target = next(j for j in jobs if j["trigger_source"] == "build")
            assert target["status"] == "succeeded" and target["jenkins_build"] == 9
            assert target["finished_at"]

            # 构建失败同样闭环:FAILURE → failed
            build_result.update({"result": "FAILURE"})
            status, _, body = request(base_url, "/api/pipeline-configs/PIPE-BUILD-TEST/run",
                                      "POST", {})
            assert status == 201  # run 端点惯例返回 CREATED
            status, _, body = request(base_url, "/api/pipeline/jobs?limit=30")
            jobs = json.loads(body)["items"]
            failed_job = next(j for j in jobs if j["trigger_source"] == "build"
                              and j["status"] != "succeeded")
            assert failed_job["status"] == "failed"
            assert "FAILURE" in failed_job["result"]["error"]

            # 测试流水线行为不变:kind 缺省 suite,run 照旧走执行任务通道
            status, _, body = create({
                "config_id": "PIPE-SUITE-OK", "name": "普通", "kind": "suite",
                "schedule_type": "once", "schedule_param": {"run_at": "2099-01-01T09:00"}})
            assert status == 201
            config = json.loads(body)
            assert config["kind"] == "suite" and config["build"] == {}
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
            gc.collect()  # 例外/回溯帧可能循环引用 sqlite 连接;Windows 删库文件需句柄已关


def test_build_resolver_same_config_collision():
    """同 config 一天多次触发且队列项已被 Jenkins 清掉:组内按触发序先到先得,
    老任务对老构建、新任务对新构建(2026-09-23 线上事故:04:17 任务错配到
    13:31 同 config 构建 12/13 的根因即回查只取最新一条)。"""
    with tempfile.TemporaryDirectory() as temporary_directory:
        build_status = {9: "FAILURE"}  # 构建 8 → SUCCESS(默认),9 → FAILURE

        class MockJenkins(BaseHTTPRequestHandler):
            queue_counter = 900  # 类属性:handler 每请求新建实例,计数不能挂 self

            def do_POST(self):
                MockJenkins.queue_counter += 1
                self.send_response(201)
                self.send_header(
                    "Location", f"http://mock-jenkins/queue/item/{MockJenkins.queue_counter}/")
                self.end_headers()

            def do_GET(self):
                def reply(payload):
                    body = json.dumps(payload).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                if "/queue/item/" in self.path:
                    # 队列项一律 404:模拟已出结果被清,逼回查路径
                    self.send_response(404)
                    self.end_headers()
                elif "tree=actions[parameters" in self.path:
                    # 参数查询(build_parameters 与 job_status 同路径,靠 tree 区分)
                    reply({"actions": [{"parameters": [
                        {"name": "NOTES", "value": "pipeline%3APIPE-COLLIDE"}]}]})
                elif self.path.startswith("/job/swan-audio-build/api/json"):
                    now_ms = int(time.time() * 1000)
                    reply({"builds": [
                        {"number": 9, "result": None, "building": False,
                         "timestamp": now_ms + 10},
                        {"number": 8, "result": None, "building": False,
                         "timestamp": now_ms}]})
                elif self.path.startswith("/job/swan-audio-build/"):
                    number = int(self.path.split("/job/swan-audio-build/")[1].split("/")[0])
                    reply({"building": False, "result": build_status.get(number, "SUCCESS")})
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, *args):
                pass

        jenkins_server = ThreadingHTTPServer(("127.0.0.1", 0), MockJenkins)
        threading.Thread(target=jenkins_server.serve_forever, daemon=True).start()
        env_keys = ("JENKINS_BASE_URL", "JENKINS_USER", "JENKINS_API_TOKEN")
        env_backup = {key: os.environ.get(key) for key in env_keys}
        os.environ.update({
            "JENKINS_BASE_URL": f"http://127.0.0.1:{jenkins_server.server_address[1]}",
            "JENKINS_USER": "mock",
            "JENKINS_API_TOKEN": "mock",
        })
        server = create_server("127.0.0.1", 0, Path(temporary_directory) / "dashboard.sqlite3")
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base_url = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            status, _, _ = request(base_url, "/api/pipeline-configs", "POST", {
                "config_id": "PIPE-COLLIDE", "name": "同日多跑", "kind": "build",
                "schedule_type": "daily", "schedule_param": {"time": "04:17"},
                "build_param": {"branch": "dev", "server_type": "test"}})
            assert status == 201

            # 同 config 连跑两次 → 两个 pending 任务,queue_id 递增
            queue_ids = []
            for _ in range(2):
                status, _, body = request(base_url, "/api/pipeline-configs/PIPE-COLLIDE/run",
                                          "POST", {})
                assert status == 201  # run 端点惯例返回 CREATED
                job = json.loads(body)["job"]
                queue_ids.append(job["result"]["jenkins_queue_id"])
            assert queue_ids == sorted(queue_ids) and len(set(queue_ids)) == 2

            # 列表读取触发 resolver:队列项 404 → 组内候选 [8, 9] 按触发序先到先得
            status, _, body = request(base_url, "/api/pipeline/jobs?limit=30")
            assert status == 200
            jobs = json.loads(body)["items"]
            by_queue = {j["result"]["jenkins_queue_id"]: j for j in jobs
                        if j["trigger_source"] == "build"}
            assert sorted(by_queue) == queue_ids
            first, second = (by_queue[q] for q in queue_ids)
            # 老任务(先触发)对老构建 8 且独立闭环为成功,而非抢到最新构建 9
            assert first["jenkins_build"] == 8 and first["status"] == "succeeded"
            assert first["finished_at"]
            assert second["jenkins_build"] == 9 and second["status"] == "failed"
            assert "FAILURE" in second["result"]["error"]
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
            gc.collect()  # 例外/回溯帧可能循环引用 sqlite 连接;Windows 删库文件需句柄已关
