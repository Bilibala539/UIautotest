# CASE-ID: ai-POS-032
"""Swan 回归·AI 助手域：朗读设备列表硬件类型过滤（ai-POS-032）。

步骤 → AW 映射：
1. 对话页打开设备选择弹层 → open_ai_chat_by_role("小薇") → click_text
   ("暂无设备")（设备 chip；授权门控 SWAN_AI_PLATFORM 环境需授权态——
   未授权时 click 后无弹层即条件 skip）→ SWAN_DEVICE_SHEET_TITLE 锚
   （弹层标题「选择设备」，OCR 可读，可用可点）
2. 断言手机扬声器在列 + Wi-Fi 型号 H76D/H76G 不在列 → 手机扬声器
   OCR 断言；Wi-Fi 行存在性探针（弹层设备行无统一文案锚——需 H76D/
   H76G+普通型号同时在线的场景前置，基线环境无设备在线即条件 skip）→
   行命中后：text_not_exists("H76D") + text_not_exists("H76G") + 普通
   型号在列
3. 选择硬件类型外设备不发起朗读 → ⛔ 零选择（设备行点击写 closeAudio
   协议=禁区）→ press_back 关弹层 → 暂无设备 chip 态不变

数据说明：硬件过滤为服务端/客户端联动契约面（Wi-Fi 型号排除表），
需多设备在线 rig；基线环境条件 skip。

cleanup：无（弹层零选择关闭；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiReadAloudDeviceFilter(SwanRM09Mixin, BaseTest):
    """朗读设备弹层硬件类型过滤（设备行探针条件门，零选择）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_device_sheet_hw_filter(self):
        """弹层手机扬声器在列，Wi-Fi 型号排除，零选择关闭。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_chat_by_role("小薇")
        self.userA.click_text("暂无设备", timeout=10)

        # 步骤 1：设备选择弹层锚（弹层标题文案未标定，探针条件门）
        if self.userA.find_text_by_ocr("选择设备", timeout=8) is None:
            self.userA.press_back()
            pytest.skip(
                "设备选择弹层标题/行文案 OCR 无锚（弹层未探索，"
                "template_needs: 设备行形态/H76D 排除表）——已零选择关闭")

        # 步骤 2：手机扬声器在列
        assert self.userA.find_text_by_ocr("手机扬声器", timeout=8) is not None, (
            "弹层未见「手机扬声器」行 [OCR]")

        # 步骤 2：Wi-Fi 设备行探针（需 H76D/H76G+普通型号在线场景前置）
        wifi_rows = self.userA.ocr_scan_page()
        row_texts = [item.get("text", "") for item in wifi_rows]
        has_wifi_dev = any(("H76" in t) for t in row_texts)
        has_normal_dev = any(
            kw in t for t in row_texts for kw in ("扬声器", "音箱"))
        if not (has_wifi_dev and has_normal_dev):
            self.userA.press_back()
            pytest.skip(
                "朗读设备硬件过滤需 H76D/H76G+普通型号同时在线（rig 设备"
                "前置缺失，template_needs: 设备行形态/H76D 排除表）——"
                "弹层已零选择关闭")

        # 步骤 2：硬件过滤断言（Wi-Fi 型号排除 + 普通型号在列）
        assert self.userA.text_not_exists("H76D", timeout=5), (
            "弹层出现 Wi-Fi 型号 H76D（硬件过滤失效）[OCR]")
        assert self.userA.text_not_exists("H76G", timeout=5), (
            "弹层出现 Wi-Fi 型号 H76G（硬件过滤失效）[OCR]")

        # 步骤 3：零选择关闭弹层
        self.userA.press_back()
        assert self.userA.find_text_by_ocr("暂无设备", timeout=8) is not None, (
            "弹层关闭后设备 chip 态异常 [OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
