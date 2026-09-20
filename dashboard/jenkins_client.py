"""Jenkins 客户端(M3):平台侧触发与查询 Jenkins 构建。

凭据只从环境变量读取(部署机 .env.local 注入,不进 git):
  JENKINS_BASE_URL  例 http://127.0.0.1:8082
  JENKINS_USER      例 admin
  JENKINS_API_TOKEN API Token(非登录密码)

约定:
  - 所有失败都返回 {"ok": False, "error": str, ...} 结构化结果,不抛裸栈;
  - trigger 用 form 编码调 buildWithParameters,成功从 Location 头解析 queue id;
  - queue_item 轮询队列项,executable.number 出现即拿到 build 号;
  - job_status 查询构建进行中/终态。
"""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


def config() -> dict:
    """读取配置;缺任一关键项返回 {}(调用方据 ok=False 短路走本地兜底)。"""
    base = os.environ.get("JENKINS_BASE_URL", "").strip().rstrip("/")
    user = os.environ.get("JENKINS_USER", "").strip()
    token = os.environ.get("JENKINS_API_TOKEN", "").strip()
    if not base or not user or not token:
        return {}
    return {"base": base, "user": user, "token": token}


def _auth_header(cfg: dict) -> str:
    secret = f"{cfg['user']}:{cfg['token']}".encode("utf-8")
    return "Basic " + base64.b64encode(secret).decode("ascii")


def _request(method: str, url: str, data: bytes | None = None,
             headers: dict | None = None, timeout: int = 10):
    """发请求,返回 (status, headers, body_text);HTTPError/网络错误由调用方接。"""
    request = urllib.request.Request(url, data=data, method=method,
                                     headers=headers or {})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return (response.status, dict(response.headers),
                response.read().decode("utf-8", "replace"))


def _fail(error: str, **extra) -> dict:
    return {"ok": False, "error": error, **extra}


def trigger(job: str, params: dict) -> dict:
    """触发参数化构建(form 编码)。

    成功:{"ok": True, "queue_id": int|None, "location": str}
      (Jenkins 返回 201 + Location: .../queue/item/<id>/)
    失败:{"ok": False, "error": str, "status_code": int?}
    """
    cfg = config()
    if not cfg:
        return _fail("JENKINS_BASE_URL/JENKINS_USER/JENKINS_API_TOKEN 未配置")
    url = f"{cfg['base']}/job/{urllib.parse.quote(job, safe='')}/buildWithParameters"
    body = urllib.parse.urlencode(params).encode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Authorization": _auth_header(cfg),
    }
    try:
        status, resp_headers, text = _request("POST", url, data=body, headers=headers)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:200]
        return _fail(f"HTTP {error.code}: {detail}", status_code=error.code)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return _fail(f"Jenkins 连接失败: {error}")
    if status not in (200, 201):
        return _fail(f"HTTP {status}", status_code=status)
    location = resp_headers.get("Location", "")
    matched = re.search(r"/queue/item/(\d+)", location)
    return {"ok": True, "queue_id": int(matched.group(1)) if matched else None,
            "location": location}


def queue_item(queue_id: int) -> dict:
    """查队列项。executable.number 出现 → {"ok": True, "build": n};
    仍在排队 → {"ok": True, "build": None};查询失败 → {"ok": False, "error"}。"""
    cfg = config()
    if not cfg:
        return _fail("JENKINS_BASE_URL/JENKINS_USER/JENKINS_API_TOKEN 未配置")
    url = f"{cfg['base']}/queue/item/{int(queue_id)}/api/json"
    try:
        status, _, text = _request("GET", url, headers={"Authorization": _auth_header(cfg)})
    except urllib.error.HTTPError as error:
        return _fail(f"HTTP {error.code}", status_code=error.code)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return _fail(f"Jenkins 连接失败: {error}")
    if status != 200:
        return _fail(f"HTTP {status}", status_code=status)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        return _fail(f"响应非 JSON: {error}")
    executable = data.get("executable") or {}
    return {"ok": True, "build": executable.get("number"),
            "cancelled": bool(data.get("cancelled", False))}


def job_status(job: str, build: int) -> dict:
    """查询构建状态:{"ok": True, "building": bool, "result": "SUCCESS"|...|None}。"""
    cfg = config()
    if not cfg:
        return _fail("JENKINS_BASE_URL/JENKINS_USER/JENKINS_API_TOKEN 未配置")
    url = f"{cfg['base']}/job/{urllib.parse.quote(job, safe='')}/{int(build)}/api/json"
    try:
        status, _, text = _request("GET", url, headers={"Authorization": _auth_header(cfg)})
    except urllib.error.HTTPError as error:
        return _fail(f"HTTP {error.code}", status_code=error.code)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return _fail(f"Jenkins 连接失败: {error}")
    if status != 200:
        return _fail(f"HTTP {status}", status_code=status)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        return _fail(f"响应非 JSON: {error}")
    return {"ok": True, "building": bool(data.get("building", False)),
            "result": data.get("result")}
