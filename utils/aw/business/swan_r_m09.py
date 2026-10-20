"""Swan 回归 M09「AI 助手」域业务方法 mixin（tcbatch L09 新增，2026-10-20）。

仅供本包用例经 userA 调用；挂入 SwanBusiness MRO 由主会话集成时统一完成。
页面锚全部来自 wave5 真机探索 dumps（explorer_output/wave5/dumps/，基线
账号 13555555555 实测），OCR 文本优先。

方法体内只编排基础 AW 层（utils/aw/aw_base.py + base/android_base.py，
见 METHODS_catalog.txt）：登录与顶 Tab 导航（ensure_logged_in_on_home /
go_top_tab 属业务层）由用例自行完成后再调本组方法。不引入 self.aw 中间层、
不硬编码点击坐标、不做无超时硬等待（轮询一律带 timeout）。

AI 对话断言纪律：AI 回复文案不可精确断言——断言落在可观察状态上（气泡
以内容区新增 OCR 文本行呈现、输入框占位回显、历史条目存在）。
"""

from __future__ import annotations

import re
import time

from image.image_name_mapping import SWAN_HOME_AI_ROLE_SETTINGS


class SwanRM09Mixin:
    """M09 AI 助手域回归业务方法（纯 mixin，不继承，不与现有方法重名）。"""

    # ---- OCR 搜索区域（窗口内像素；与 swan.py _LOGIN_SUBMIT_REGION 同口径，
    #      wave5 dumps 窗口 720x1600）----
    # 顶栏区：二级页页题（y≈107-155）/聊天页角色名（y≈120-163）+设备副标题
    # （y≈165-195）；AI 首页画廊与历史入口行（y≥388）在区外，可区分同文案。
    _AI_TOPBAR_REGION = (0, 60, 720, 170)
    # 聊天页消息内容区：排除顶栏（角色名/设备副标题）与底部输入区
    # （placeholder y≈1450-1490）、免责声明行（y≈1562-1590）。
    _AI_CHAT_CONTENT_REGION = (0, 250, 720, 1050)
    # 角色编辑器音色表单回显区：当前音色显示行（y≈727-760）；音色列表行
    # 自 y≈890 起，在区外，可区分同文案的表单回显与列表行。
    _AI_VOICE_FORM_REGION = (0, 560, 720, 300)

    # ---------- 私有探测辅助 ----------

    def _ocr_first(self, texts, timeout: int = 10, region=None):
        """轮询 OCR 命中 texts 中任一文案，返回命中文案，全超时返回 None。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            for text in texts:
                if self.find_text_by_ocr(text, timeout=1, region=region) is not None:
                    return text
            self.sleep(0.5)
        return None

    @staticmethod
    def _norm_ocr_text(text: str) -> str:
        """OCR 文本归一化：去空白与标点（全/半角差异抖动下稳定比对）。"""
        return re.sub(r"[^\w一-鿿]", "", text or "")

    # ---------- 页面锚点断言 ----------

    def assert_ai_home_gallery(self) -> str:
        """断言已停在 AI 首页且角色画廊已渲染（角色卡名/入口行锚）。"""
        hit = self._ocr_first(("小薇", "惠威百科", "添加更多AI角色"), timeout=15)
        assert hit is not None, (
            "AI 首页未渲染角色画廊锚点（小薇/惠威百科/添加更多AI角色 均未命中）[OCR]")
        return hit

    def open_ai_roles_page(self) -> None:
        """AI 首页（顶 Tab 已在 AI）→ 所有角色页（角色设置入口 [图]）。

        到位断言：顶栏页题「所有角色」。
        """
        self.click_image(SWAN_HOME_AI_ROLE_SETTINGS, timeout=10)
        assert self.text_exists(
            "所有角色", timeout=10, region=self._AI_TOPBAR_REGION) is not None, (
            "角色设置入口点击后未落地「所有角色」页 [OCR·顶栏区]")

    def open_ai_role_editor(self) -> None:
        """AI 首页（顶 Tab 已在 AI）→ 新建角色编辑器（添加更多AI角色行）。

        到位断言：顶栏页题「自定义设置」。全程不触碰 完成/生成 等禁区控件。
        """
        self.click_text("添加更多AI角色", timeout=10)
        assert self.text_exists(
            "自定义设置", timeout=10, region=self._AI_TOPBAR_REGION) is not None, (
            "添加更多AI角色点击后未落地角色编辑器「自定义设置」[OCR·顶栏区]")

    def open_ai_history_page(self) -> None:
        """AI 首页（顶 Tab 已在 AI）→ AI 历史页（历史对话记录行）。

        到位断言：顶栏页题「历史对话记录」（与 AI 首页同名入口行靠区域区分：
        入口行 y≈840-875 在顶栏区外）。
        """
        self.click_text("历史对话记录", timeout=10)
        assert self.text_exists(
            "历史对话记录", timeout=10, region=self._AI_TOPBAR_REGION) is not None, (
            "历史对话记录点击后未落地历史页（顶栏页题未命中）[OCR·顶栏区]")

    def open_ai_chat_by_role(self, role: str) -> None:
        """AI 首页（顶 Tab 已在 AI）→ 点角色卡进入该角色对话页。

        到位断言：底部输入区占位「发送消息」+ 免责声明「内容由AI生成」
        （聊天页双锚，wave5 实测 conf≥0.84/0.99）。
        """
        self.click_text(role, timeout=10)
        assert self.text_exists("发送消息", timeout=10) is not None, (
            f"角色卡「{role}」点击后未落地对话页（输入区占位未命中）[OCR]")
        assert self.text_exists("内容由AI生成", timeout=5) is not None, (
            f"角色卡「{role}」对话页缺「内容由AI生成」免责声明锚 [OCR]")

    # ---------- AI 对话发送（可观察状态口径） ----------

    def send_chat_text(self, text: str) -> None:
        """发送一条 ASCII 文本消息，断言气泡上屏且输入框清空回显占位。

        发送动作经输入框聚焦 + 回车键（发送按钮为无文案控件，锚未截取，
        见 report.template_needs）；断言以内容区出现所发文本（自身气泡回显）
        与输入区占位文案回归为可观察状态，不断言 AI 回复内容。
        仅支持 ASCII 文本：input_text 经 adb 注入，中文/emoji/部分符号不可达。
        """
        self.click_text("发送消息", timeout=10)
        self.input_text(text)
        self.press_key("enter")
        assert self.find_text_by_ocr(
            text, timeout=20, region=self._AI_CHAT_CONTENT_REGION) is not None, (
            f"发送后内容区未出现消息文本「{text}」（回车未上屏，需标定发送锚）[OCR]")
        assert self.text_exists("发送消息", timeout=8) is not None, (
            "发送后输入框未清空（占位文案未回归）[OCR]")

    def assert_chat_token(self, token: str, present: bool = True) -> None:
        """断言当前对话内容区含/不含指定消息令牌（会话隔离与恢复的可观察状态）。

        present=True：令牌作为消息气泡文本出现在内容区（超时 15s）；
        present=False：内容区不存在对侧会话令牌（串扰反断言，短探测 3s）。
        """
        if present:
            assert self.find_text_by_ocr(
                token, timeout=15, region=self._AI_CHAT_CONTENT_REGION) is not None, (
                f"当前会话内容区未出现消息令牌「{token}」[OCR·内容区]")
        else:
            assert self.find_text_by_ocr(
                token, timeout=3, region=self._AI_CHAT_CONTENT_REGION) is None, (
                f"当前会话内容区出现了他会话令牌「{token}」（串扰错位）[OCR·内容区]")

    def wait_ai_reply_bubble(self, known_texts, timeout: int = 60) -> str | None:
        """等待 AI 回复气泡出现：内容区出现不在 known_texts 中的新文本行。

        AI 回复文案不可精确断言——以「内容区新增归一化文本行」作为回复气泡
        出现的可观察状态（传输层探针，非语义断言）。归一化去空白标点，规避
        OCR 对既有气泡的逐帧抖动误报。超时返回 None（回复时效边界由执行轮
        标定，见 report.template_needs）。
        """
        known = {self._norm_ocr_text(t) for t in known_texts}
        deadline = time.time() + timeout
        while time.time() < deadline:
            for item in self.ocr_scan_page(region=self._AI_CHAT_CONTENT_REGION):
                norm = self._norm_ocr_text(item.get("text", ""))
                if len(norm) >= 2 and norm not in known:
                    return item.get("text", "")
            self.sleep(1.0)
        return None

    # ---------- 画廊手势 ----------

    def swipe_ai_gallery_card(self, direction: str = "next") -> None:
        """AI 首页角色画廊 PageView 横滑一张卡（next=看下一张，prev=回滑）。

        坐标由 get_window_rect 动态计算（窗口相对），不硬编码；手势落点取
        窗口高度 1/3 处（角色卡行 y≈390-570/1600）。
        """
        rect = self.driver.get_window_rect()
        assert rect, "get_window_rect 失败，无法计算画廊横滑手势"
        _, _, w, _h = rect
        y = _h // 3
        if direction == "next":
            x1, x2 = w * 2 // 3, w // 3
        else:
            x1, x2 = w // 3, w * 2 // 3
        self.swipe(x1, y, x2, y, duration=0.4)

    # ---------- 区域限定文本探针（公开入口，供用例直接调用） ----------

    def find_ai_topbar_text(self, text: str, timeout: int = 10):
        """顶栏区(0,60,720,170)限定查找文本（页题/角色名/设备副标题）。"""
        return self.text_exists(text, timeout=timeout, region=self._AI_TOPBAR_REGION)

    def find_ai_voice_form_text(self, text: str, timeout: int = 10):
        """角色编辑器语音表单区(0,560,720,300)限定查找文本（当前音色回显）。"""
        return self.text_exists(text, timeout=timeout, region=self._AI_VOICE_FORM_REGION)

    def scan_ai_chat_content(self):
        """对话页内容区(0,250,720,1050) OCR 快照（气泡/消息文本行列表）。"""
        return self.ocr_scan_page(region=self._AI_CHAT_CONTENT_REGION)
