# CASE-ID: ai-NEG-019
"""Swan 回归·AI 助手域：余额不足双通道·魔法串与状态事件一致（ai-NEG-019）。

步骤 → AW 映射：
1. 0 额度账号发送文本触发服务端余额检查 → 运行时条件门：
   SWAN_AI_ZERO_BALANCE_ACCT=1（0 惠币受控账号预置后置位，未置位 skip
   ——余额值不可 UI 预置，人工预置后经环境变量声明）→ chat 小薇 +
   send_chat_text → wait_ai_reply_bubble 捕获回复 → 归一化断言魔法串
   「抱歉！余额不足！」（服务端逐字符契约，坑 2 A 通道锚
   ai_chat_controller.dart:589；OCR 标点容差经去符号归一比对）
2. 通道 B 实时入口触发余额不足 → 依赖 ai_chat_realtime_action 无文案
   图标（模板未截取）→ 步骤 1 断言完成后条件 skip（充值弹框出现即止，
   不进充值支付——禁区 1）
3. 双通道一致性 → 模板补齐后复核两通道反馈齐备

数据说明：魔法串为确定性服务端契约（非 AI 语义生成），精确断言符合
对话断言纪律；支付域归 M14 不在本用例范围。

cleanup：无（0 额度路径不产生计费；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import os
import re

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiInsufficientBalanceDual(SwanRM09Mixin, BaseTest):
    """余额不足双通道（0 额度受控账号条件门 + 实时通道图标条件 skip）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_insufficient_balance_dual_channel(self):
        """A 通道魔法串回归锁定；B 通道入口图标缺模板即条件 skip。"""
        if os.environ.get("SWAN_AI_ZERO_BALANCE_ACCT", "").strip() != "1":
            pytest.skip(
                "需 0 惠币余额受控账号（人工预置后设 "
                "SWAN_AI_ZERO_BALANCE_ACCT=1 运行；基线账号余额非 0）")
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")

        # 步骤 1：文本通道触发余额检查，断言魔法串契约
        self.userA.open_ai_chat_by_role("小薇")
        self.userA.send_chat_text("balance probe NEG-019")
        reply = self.userA.wait_ai_reply_bubble(
            ["balance probe NEG-019"], timeout=90)
        assert reply is not None, (
            "0 额度发送后 90s 内未捕获回复（A 通道余额检查未收敛）[OCR·内容区]")
        norm = re.sub(r"[^\w一-鿿]", "", reply)
        assert "抱歉余额不足" in norm or "余额不足" in norm, (
            f"回复未命中余额不足魔法串契约（坑 2 A 通道锚）: {reply}")

        # 步骤 2：通道 B 依赖实时通话入口（无文案图标，模板未截取）
        pytest.skip(
            "通道 B 实时通话入口为无文案图标（template_needs: "
            "ai_chat_realtime_action）——A 通道魔法串已锁定，补模板后"
            "B 通道转全自动")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
