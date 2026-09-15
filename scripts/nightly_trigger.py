"""Nightly 触发器(步骤 11 双通道之一):在 .166 上由计划任务调用。

每日凌晨向本机平台服务 POST 一个 nightly 任务,
执行 agent(各执行机上的 scripts/pipeline_agent.py --loop)会领取执行。

部署:.166 计划任务 NightlyPipelineTrigger,每日 01:33
  C:\\Program Files\\Python312\\python.exe E:\\uiautotest\\scripts\\nightly_trigger.py
"""
from __future__ import annotations

import json
import sys
import urllib.request

TRIGGER_URL = "http://127.0.0.1:8080/api/pipeline/trigger"
PAYLOAD = {
    "trigger_source": "nightly",
    "platform": "flutter",
    "case_filter": "tests/flutter/test_case_driver.py",
}


def main() -> int:
    request = urllib.request.Request(
        TRIGGER_URL,
        data=json.dumps(PAYLOAD, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = json.loads(response.read().decode("utf-8"))
        print(f"nightly job triggered: {body.get('job_id')}")
        return 0
    except Exception as error:  # noqa: BLE001 — 触发失败让计划任务记非零退出
        print(f"trigger failed: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
