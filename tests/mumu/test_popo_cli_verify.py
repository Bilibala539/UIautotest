"""
测试用例: POPO CLI 发送消息端到端验证

流程:
1. 通过 POPO CLI (fabric) 以王英账号发送消息给孟龄钊
2. 启动 MuMu 模拟器，登录王英的 POPO 账号
3. 打开王英与孟龄钊的 P2P 会话
4. 验证消息确实存在于聊天记录中
"""
import shutil
import subprocess
import json
import os
import time
import logging
from datetime import datetime

from conftest import BaseTest
from image.image_name_mapping import MESSAGE_TAB_BLUE
from utils.aw.search_region import Normal

logger = logging.getLogger(__name__)

# ========== POPO CLI 配置 ==========
FABRIC = shutil.which("fabric.cmd") or shutil.which("fabric") or "fabric"
RECEIVER_NAME = "孟龄钊"
RECEIVER_UID = "wb.menglingzhao02@mesg.corp.netease.com"
MESSAGE_PREFIX = "CLI自动化验证"


def _run_fabric(args: list) -> dict:
    """执行 fabric 命令并返回解析后的 JSON"""
    cmd = [FABRIC] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if result.returncode != 0:
        raise RuntimeError(f"fabric 命令失败: {result.stderr}")
    output = result.stdout.strip().lstrip("\ufeff")
    return json.loads(output)


def _is_cli_logged_in() -> bool:
    """检查 POPO CLI 是否已登录"""
    try:
        result = subprocess.run(
            [FABRIC, "auth", "status"],
            capture_output=True,
            encoding="utf-8",
        )
        data = json.loads(result.stdout.strip().lstrip("\ufeff"))
        return data.get("ok") is True
    except Exception:
        return False


def _auto_cli_login():
    """使用 Playwright 自动完成 CLI 登录"""
    from playwright.sync_api import sync_playwright

    logger.info("POPO CLI 未登录，正在自动登录...")

    resp = _run_fabric(["auth", "login", "--openid", "--no-browser"])
    auth_url = resp["data"]["authorization_url"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(auth_url, wait_until="networkidle")

        page.fill("#corp_id_for_corpid", "wangying43")
        page.fill("#corp_id_for_corppw", "Qwe1234!!")
        page.evaluate("document.getElementById('corp_id_for_privacy').checked = true")
        page.locator("form:has(#corp_id_for_corpid) input[type=button]").click(force=True)
        page.wait_for_timeout(5000)

        browser.close()

    subprocess.run([FABRIC, "auth", "login", "--resume"],
                   capture_output=True, encoding="utf-8")
    logger.info("POPO CLI 登录完成")


def send_message_via_cli(message: str) -> str:
    """
    通过 POPO CLI 发送消息给孟龄钊

    Args:
        message: 消息内容

    Returns:
        str: 实际发送的完整消息（含时间戳）
    """
    if not _is_cli_logged_in():
        _auto_cli_login()

    # 带时间戳的消息，用于精确验证
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_message = f"{message}_{timestamp}"

    logger.info(f"通过 CLI 发送消息: '{full_message}' -> {RECEIVER_UID}")

    resp = _run_fabric([
        "popo", "message_send_p2p",
        f"message={full_message}",
        f"receiver={RECEIVER_UID}",
    ])
    data = resp["data"]["data"]["data"]["data"]
    assert data.get("resultMsg") == "消息发送成功", f"CLI 发送消息失败: {data}"
    logger.info(f"CLI 消息发送成功: {full_message}")

    return full_message


class TestPopoCliMessageVerify(BaseTest):
    """
    POPO CLI 消息发送端到端验证

    验证步骤:
    1. 通过 POPO CLI 发送带唯一时间戳的消息给孟龄钊
    2. 在 MuMu 模拟器上以王英账号登录 POPO
    3. 打开与孟龄钊的 P2P 聊天窗口
    4. 通过 OCR 验证发送的消息确实出现在聊天记录中
    """

    def setup(self):
        """
        测试前准备:
        - 通过 CLI 发送消息（先于模拟器操作，确保消息已到达服务端）
        - 启动模拟器并登录王英账号
        """
        # 1. 先通过 CLI 发送消息
        self.sent_message = send_message_via_cli(MESSAGE_PREFIX)

        # 2. 登录王英账号到 MuMu 模拟器
        self.userA = self.users("wangying43")

    def test_verify_cli_message_in_chat(self):
        """
        测试场景: 验证 CLI 发送的消息在 POPO 客户端可见

        步骤:
        1. 在消息列表页找到孟龄钊的会话并点击进入
        2. 在聊天页面中通过 OCR 查找发送的消息文本
        3. 断言消息存在
        """
        # 1. 在消息列表中点击孟龄钊的会话
        #    CLI 刚发送了消息，该会话应在列表顶部
        logger.info("在消息列表中查找孟龄钊的会话...")
        self.userA.aw.click_text(RECEIVER_NAME, timeout=10)
        time.sleep(2)

        # 2. 验证已进入聊天页面（底部有"发送给"输入框）
        self.userA.aw.text_exists("发送给", region=Normal.HALF_DOWN)
        logger.info("已进入与孟龄钊的 P2P 聊天页面")

        # 3. 验证 CLI 发送的消息在聊天记录中可见
        #    使用消息前缀做 OCR 匹配（时间戳确保唯一性）
        logger.info(f"验证消息是否可见: '{self.sent_message}'")
        self.userA.aw.text_exists(self.sent_message, timeout=10)
        logger.info(f"验证通过: 消息 '{self.sent_message}' 在聊天记录中可见")

    def teardown(self):
        """
        测试后清理:
        - 返回消息列表页
        """
        # 按返回键回到消息列表
        for _ in range(5):
            self.userA.aw.press_back()
            time.sleep(0.5)
            if self.userA.aw.find_image(MESSAGE_TAB_BLUE, timeout=1):
                break
