"""P02（M02 会话与登录）包级新业务方法 mixin（tcbatch 批量转换，2026-10-20）。

仅承载本批登录域用例间复用的编排步骤，全部用基础 AW 方法
（click_text/click_image/find_image/find_text_by_ocr/input_text/clear_input/
press_back/ocr_scan_page/sleep）与 image_name_mapping 已注册常量实现；
不含任何既有业务方法调用（挂入 SwanBusiness MRO 后即可静态解析）。
语义口径与 utils/aw/business/swan.py 登录域实现保持一致：
- 验证码形态锚 = [OCR]「密码登入」入口；密码形态锚 = 密码框 [图] / [OCR]「验证码登入」；
- 协议勾选两态图幂等切换（点未选态图勾选、点已选态图取消）；
- 短信步主按钮门控 = SWAN_LOGIN_SUBMIT_ENABLED 可用态图可见性；
- 密码步主按钮门控 = SWAN_PWD_LOGIN_SUBMIT_ENABLED（草稿图，密码页无
  「下一步」按钮，与置灰「下一步」的形似互扰在本页不成立）。
"""
from __future__ import annotations

import re
import time

from image.image_name_mapping import (
    SWAN_AREA_CODE_CHINA_ROW,
    SWAN_LOGIN_AGREEMENT_CHECKED,
    SWAN_LOGIN_AGREEMENT_UNCHECKED,
    SWAN_LOGIN_PHONE_FIELD,
    SWAN_LOGIN_SUBMIT_ENABLED,
    SWAN_PASSWORD_FIELD,
    SWAN_PWD_LOGIN_SUBMIT_ENABLED,
    SWAN_TAB_DEVICE,
    SWAN_TAB_HOME,
    SWAN_TAB_ME,
    SWAN_TAB_PLATFORM,
)


class SwanRP02Mixin:
    """P02 登录域批量转换用例的复用编排方法（纯类，不继承）。"""

    # 重发倒计时 OCR 形态：知识库实测「重新发送(54s)」；OCR 可能把括号段
    # 拆成独立条目，故补充一条独立「(N」「(Ns)」括号计数兜底模式。
    _RESEND_COUNTDOWN_RE = re.compile(r"重新发送\s*[（(]\s*(\d{1,2})")
    _RESEND_PAREN_RE = re.compile(r"[（(]\s*(\d{1,2})\s*s?\s*[）)]")
    # 登录页区号按钮回填值（+86/+852/+998 等；登录页内 +NN 文案仅区号按钮一处）
    _AREA_CODE_RE = re.compile(r"\+\d{2,3}")

    # ---------- 登录页表单编排 ----------

    def fill_phone_number(self, phone: str) -> None:
        """点击手机号输入框 → 清空 → 输入 → 收软键盘（密码/验证码两形态通用）。"""
        self.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.clear_input()  # 防表单残留：先清空再输入
        self.input_text(phone)
        self.press_back()  # 收软键盘：避免遮挡协议框/提交按钮的图定位

    def accept_agreement(self) -> None:
        """幂等勾选协议：未选态图可见才点，勾后已选态图 [图] 断言。"""
        if self.find_image(SWAN_LOGIN_AGREEMENT_UNCHECKED, timeout=3) is not None:
            self.click_image(SWAN_LOGIN_AGREEMENT_UNCHECKED, timeout=5)
        assert self.find_image(SWAN_LOGIN_AGREEMENT_CHECKED, timeout=3) is not None, (
            "协议勾选失败（勾选后已选态图 [图] 未命中，请核对两态模板）")

    def cancel_agreement(self) -> None:
        """幂等取消协议勾选：已选态图可见才点，取消后未选态图 [图] 断言。"""
        if self.find_image(SWAN_LOGIN_AGREEMENT_CHECKED, timeout=3) is not None:
            self.click_image(SWAN_LOGIN_AGREEMENT_CHECKED, timeout=5)
        assert self.find_image(SWAN_LOGIN_AGREEMENT_UNCHECKED, timeout=3) is not None, (
            "协议取消失败（取消后未选态图 [图] 未命中，请核对两态模板）")

    def ensure_password_form(self) -> None:
        """幂等切到密码登录形态并断言就绪（已在密码形态时短路）。

        形态探测双判据同 SwanBusiness.login_with_password：密码框 [图]（空态）
        或 [OCR]「验证码登入」（密码页特有回切钮）；两判据均不可见才点
        [OCR]「密码登入」切入。
        """
        if self.find_image(SWAN_PASSWORD_FIELD, timeout=2) is not None \
                or self.find_text_by_ocr("验证码登入", timeout=2) is not None:
            return
        self.click_text("密码登入", timeout=10)
        assert self.find_image(SWAN_PASSWORD_FIELD, timeout=10) is not None \
            or self.find_text_by_ocr("验证码登入", timeout=3) is not None, (
            "切到密码登录形态失败（密码框 [图] 与「验证码登入」[OCR] 均未命中）")

    # ---------- 主按钮门控断言 ----------

    def assert_sms_submit_enabled(self, enabled: bool, timeout: int = 3) -> None:
        """短信步主按钮「下一步」可用/置灰断言（可用态图 [图] 可见性）。"""
        hit = self.find_image(SWAN_LOGIN_SUBMIT_ENABLED, timeout=timeout) is not None
        assert hit == enabled, (
            f"短信步主按钮门控不符：期望{'可用' if enabled else '置灰'}，"
            f"实际{'可用态图命中' if hit else '可用态图未命中'}")

    def assert_password_submit_enabled(self, enabled: bool, timeout: int = 3) -> None:
        """密码步主按钮「登录」可用/置灰断言（可用态草稿图 [图] 可见性）。

        密码页无「下一步」按钮，可用态图与置灰「下一步」模板的形似互扰在本页
        不成立（见模块 docstring）；图缺失时按未命中处理（同 probe 口径）。
        """
        import os

        if not os.path.exists(SWAN_PWD_LOGIN_SUBMIT_ENABLED):
            assert not enabled, (
                "密码步主按钮可用态模板未入库，无法断言启用态（请先补截转正）")
            return
        hit = self.find_image(SWAN_PWD_LOGIN_SUBMIT_ENABLED, timeout=timeout) is not None
        assert hit == enabled, (
            f"密码步主按钮门控不符：期望{'可用' if enabled else '置灰'}，"
            f"实际{'可用态图命中' if hit else '可用态图未命中'}")

    def assert_not_on_home(self, timeout: int = 2) -> None:
        """断言未进入已登录首页（底部导航 4 图 [图] 全部不可见）。

        登录失败/未提交类用例的收尾反断言：任一导航图可见即说明登录已成功，
        与预期失败语义相悖。
        """
        for template in (SWAN_TAB_HOME, SWAN_TAB_PLATFORM, SWAN_TAB_DEVICE, SWAN_TAB_ME):
            assert self.find_image(template, timeout=timeout) is None, (
                "不应进入已登录首页，但底部导航图 [图] 可见（登录校验失效？）")

    # ---------- 区号选择页 ----------

    def index_bar_letters(self, timeout: int = 10) -> list[str]:
        """OCR 探针收集区号页索引条单字母（离散 A-Z 项），≥3 个视为索引条呈现。

        索引条为细条单字母（无注册模板、content-desc 运行时不可用），以
        OCR 离散单字母命中数做存在性探针；超时返回已收集字母（可能为空）。
        """
        deadline = time.monotonic() + timeout
        found: dict[str, None] = {}
        while time.monotonic() < deadline:
            for item in self.ocr_scan_page():
                text = item.get("text", "").strip()
                if len(text) == 1 and "A" <= text <= "Z":
                    found.setdefault(text, None)
            if len(found) >= 3:
                return list(found)
            self.sleep(1.0)
        return list(found)

    def read_backfill_area_code(self, timeout: int = 10) -> str | None:
        """OCR 读取登录页区号按钮回填值（+NNN），未读到返回 None。"""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for item in self.ocr_scan_page():
                m = self._AREA_CODE_RE.search(item.get("text", ""))
                if m:
                    return m.group(0)
            self.sleep(1.0)
        return None

    def open_area_page(self, code: str) -> None:
        """点击区号按钮（OCR 文案 +86/+852 等）进入区号选择页并断言到位。"""
        self.click_text(code, timeout=10)
        assert self.find_text_by_ocr("选择归属地", timeout=10) is not None, (
            f"点击区号按钮 {code} 后未进入区号选择页（[OCR]「选择归属地」未命中）")

    def select_area_row(self, row_text: str) -> None:
        """点选区号行（OCR 国家名），断言自动返回登录页（标题消失）。"""
        self.click_text(row_text, timeout=10)
        assert self.find_text_by_ocr("选择归属地", timeout=5) is None, (
            f"点选区号行 {row_text!r} 后未自动返回登录页（区号页标题仍在）")

    def select_china_area_row(self) -> None:
        """点选「中国 +86」整行（已转正整行图，防误匹配港/澳/台行首）。"""
        self.click_image(SWAN_AREA_CODE_CHINA_ROW, timeout=10)
        assert self.find_text_by_ocr("选择归属地", timeout=5) is None, (
            "点选中国行后未自动返回登录页（区号页标题仍在）")

    # ---------- 验证码重发倒计时 ----------

    def read_resend_countdown(self, timeout: int = 10) -> int | None:
        """OCR 读取重发按钮倒计时秒数（「重新发送(Ns)」），未读到返回 None。

        读到「重新发送」但无括号计数（冷却已归零的可点态）同样返回 None。
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for item in self.ocr_scan_page():
                text = item.get("text", "")
                m = self._RESEND_COUNTDOWN_RE.search(text) \
                    or (self._RESEND_PAREN_RE.search(text)
                        if "重新" in text or "发送" in text or "s" in text else None)
                if m:
                    return int(m.group(1))
            self.sleep(1.0)
        return None

    def wait_resend_ready(self, timeout: float = 90.0) -> None:
        """轮询等待重发冷却归零（倒计时计数消失且「重新发送」可点态在屏）。

        冷却 60s：等待上限默认 90s 留余量；超时断言失败（带现场说明）。
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            countdown = self.read_resend_countdown(timeout=2)
            if countdown is None \
                    and self.find_text_by_ocr("重新发送", timeout=1) is not None:
                return
            self.sleep(1.0)
        assert False, (
            f"重发冷却 {timeout:.0f}s 内未归零（「重新发送(N)」计数文本持续在屏；"
            "请核对倒计时实现/OCR 读数）")

    # ---------- 验证码步页内返回（ADD1 复审捞回面） ----------

    def back_to_phone_step(self) -> None:
        """验证码步经页内返回箭头回手机号步（NEG-005 裁决定案通道）。

        定案口径（login-NEG-005 overallExpect）：系统 press_back=退出 App、
        relaunch=冷却不落盘丢失（NEG-024 定案），页内返回箭头=回手机号步
        （_backToPhoneStep，PFLogin:229,736-744）——箭头为唯一页内返回通道。
        箭头为无文字 glyph，OCR 探针「←」/「<-」子串命中点击（OCR 文本优先
        原则正面执行）；未命中=模板缺口暴露（返回箭头图未截取，report
        template_needs 已登记，补截转正后可切 [图] 主路径）。
        到位断言：手机号步特有锚「密码登入」[OCR] 回归（验证码步无此文案）。
        """
        hit_text = None
        for item in self.ocr_scan_page():
            text = str(item.get("text", "")).strip()
            if "←" in text or text in ("<-", "‹"):
                hit_text = text
                break
        assert hit_text is not None, (
            "验证码页页内返回箭头未探到（OCR glyph「←」/「<-」未命中）——"
            "箭头图为未截取模板（report.template_needs 已登记），"
            "press_back=退出 App 不可用，请补截箭头图转正后切 [图] 主路径")
        self.click_text(hit_text, timeout=5)
        assert self.find_text_by_ocr("密码登入", timeout=10) is not None, (
            "点击页内返回箭头后未回手机号步（「密码登入」[OCR] 未命中）")

    # ---------- 密码框明文切换（ADD1 复审捞回面） ----------

    def reveal_password_text(self, token: str) -> str | None:
        """点密码框右端明文切换钮切明文，OCR 读回框内文本行（未读到 None）。

        闭眼图标入模于 SWAN_PASSWORD_FIELD 模板右段（image_name_mapping
        元素注记「右侧闭眼图标入模」），明文切换点击=模板 rect 右端比例位
        微拖（_click_track 同款元素锚定手势，非坐标点击）；点后密码页
        press_back 只收键盘（POS-009 定案）不退页。token 为已输密码的
        特征子串（OCR 局部命中锚，l/I/1 同形由 compact 兜底）。
        """
        rect = self.find_image_rect(SWAN_PASSWORD_FIELD, timeout=10)
        assert rect is not None, "密码框 [图] 未命中（未在密码登入页？）"
        x, y, w, h = rect
        target_x = x + int(w * 0.93)  # 右端明文切换钮位（模板右段入模）
        target_y = y + h // 2
        self.swipe(target_x - max(2, int(w * 0.02)), target_y,
                   target_x, target_y, 0.3)
        self.press_back()  # 收软键盘（密码页 back 语义=收键盘）
        for item in self.ocr_scan_page():
            text = str(item.get("text", ""))
            if token.lower() in text.lower():
                return text
        return None

    # ---------- 区号页手势滚动（ADD1 复审捞回面） ----------

    def swipe_up_step(self, distance: int = 500) -> None:
        """AWBase.swipe_up 薄封装（区号页滚动/越界探针用；userA 链路静态可解析）。"""
        self.swipe_up(distance)

    def swipe_down_step(self, distance: int = 500) -> None:
        """AWBase.swipe_down 薄封装（区号页回滚/越界探针用；userA 链路静态可解析）。"""
        self.swipe_down(distance)
