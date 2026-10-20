"""Swan P06(M10 可视音箱 Vision)包级业务方法 mixin(tcbatch 批次新增)。

纯 mixin 类不继承;挂入 SwanBusiness MRO 由集成统一处理(禁改 swan.py)。
方法一律以基础 AW 原语(click_text/text_exists/find_text_by_ocr/click_image/
press_back/input_text/swipe_up 等)编排,不依赖业务层既有方法。

Vision 域页面族(/vision/wallpaper、/vision/wake-words、/vision/voice-pack、
/vision/advanced-settings*)在知识库标记为「绑定可视音箱后可达、绑定态内容
未探索」(knowledge/swan/pages/swan_Vision域不可达页.md;未绑定态 Tab 内容区
零可点节点,2026-09-10 真机实测)。因此:

- 各入口方法前置一律为「已登录 + 已绑定 MG100 + 已停首页可视音箱 Tab」
  (用例侧经 ensure_logged_in_on_home + go_top_tab('可视音箱') 到位;
  设备页路径见 open_vision_wallpaper_from_device);
- 域内入口/落地锚点全部走 OCR 文本探测(子串匹配),落地断言用候选文案
  命中制(_vision_expect_any_text),未标定文案由 package_report.template_needs
  统一登记,待 explorer 绑定 MG100 后实测标定。
"""
from __future__ import annotations

# 方案编辑器素材条目候选文案(待 explorer 绑定 MG100 实测标定后填入,
# 知识库绑定态未探索——见 package_report.template_needs)。
_EDITOR_MATERIAL_HINTS: tuple = ()

# 语音包行候选锚:KB swan_所有角色页 2026-09-10 Wave5 实测系统角色名
# (语音包行与角色一一对应,行内含角色名文案)。
_VOICE_PACK_ROW_HINTS = ("小薇", "惠威百科", "惠声远", "云舒雁")


class SwanRP06Mixin:
    """P06(M10 可视音箱 Vision)复用业务方法(基础 AW 原语编排)。"""

    def _vision_expect_any_text(self, texts, timeout: int = 10) -> str:
        """Vision 域页面落地断言:依次探测候选 OCR 锚点,命中即返回该文案。

        候选文案均为语义预测(页面未探索),全部未命中断言失败。
        """
        for text in texts:
            if self.find_text_by_ocr(text, timeout=2) is not None:
                return text
        assert False, f"Vision 页面锚点均未出现: {list(texts)}"

    def open_vision_wallpaper_page(self, timeout: int = 10) -> None:
        """进入壁纸主页面(/vision/wallpaper)。

        前置:已停首页可视音箱 Tab 且已绑定 MG100(未绑定态无入口)。
        入口锚:内容区「壁纸」(文案未标定,OCR 子串匹配兼容「壁纸设置」式)。
        """
        self.click_text("壁纸", timeout=timeout)
        self._vision_expect_any_text(("壁纸", "Vision", "素材"), timeout=timeout)

    def open_vision_wallpaper_from_device(self, timeout: int = 15) -> None:
        """设备页路径进入壁纸主页面(vision-POS-001 流程)。

        前置:已到设备页且名下已绑定 MG100(TESTDEV-MG100-01,需人工预置)。
        链路:设备卡名 OCR「MG100」→ 详情/入口面「Vision」配置入口 → 壁纸主页面。
        """
        self.click_text("MG100", timeout=timeout)
        self.click_text("Vision", timeout=timeout)
        self._vision_expect_any_text(("壁纸", "Vision"), timeout=timeout)

    def open_vision_wake_words_page(self, timeout: int = 10) -> None:
        """进入唤醒词页(/vision/wake-words)。前置:已停可视音箱 Tab。"""
        self.click_text("唤醒词", timeout=timeout)
        self._vision_expect_any_text(("唤醒词",), timeout=timeout)

    def open_wake_word_create_form(self, timeout: int = 10) -> None:
        """唤醒词页 → 新建唤醒词输入态。前置:已到唤醒词页。

        止步保存前(保存=aiRouseWord 服务端写+设备同步——禁区 2)。
        """
        self.click_text("新建", timeout=timeout)
        self._vision_expect_any_text(("新建", "保存", "取消", "唤醒词"), timeout=timeout)

    def open_vision_ai_roles_page(self, timeout: int = 10) -> None:
        """进入 Vision AI 角色页(/vision/ai-roles)。前置:已停可视音箱 Tab。

        入口锚「角色」OCR 子串匹配兼容「AI角色」「AI 角色」两种文案。
        """
        self.click_text("角色", timeout=timeout)
        self._vision_expect_any_text(("AI角色", "AI 角色", "角色"), timeout=timeout)

    def open_vision_voice_pack_page(self, timeout: int = 10) -> None:
        """进入语音包页(/vision/voice-pack)。前置:已停可视音箱 Tab。

        入口路径二选一(YAML POS-004):Vision 页直入口(探测「语音包」),
        无则经 AI 角色页角色卡音色包入口(探测「音色」)。
        """
        if self.find_text_by_ocr("语音包", timeout=3) is None:
            self.click_text("角色", timeout=timeout)
            self.click_text("音色", timeout=timeout)
        self._vision_expect_any_text(("语音包", "音色"), timeout=timeout)

    def open_vision_advanced_settings(self, timeout: int = 10) -> None:
        """进入高级设置总页(/vision/advanced-settings)。前置:已停可视音箱 Tab。"""
        self.click_text("高级设置", timeout=timeout)
        self._vision_expect_any_text(("高级设置", "方案"), timeout=timeout)

    def open_vision_platform_page(self, platform: str, timeout: int = 10) -> None:
        """高级设置总页 → 单平台页(/vision/advanced-settings/platform)。

        前置:已到高级设置总页。platform 传平台分组卡 OCR 文案(如「酷狗」,
        terraceType=4;「电台」命中 0/5/6 电台类分组卡)。
        """
        self.click_text(platform, timeout=timeout)
        self._vision_expect_any_text(("新建", "方案", "素材"), timeout=timeout)

    def open_vision_scheme_editor(self, platform: str, timeout: int = 10) -> None:
        """单平台页 → 方案编辑器(/vision/advanced-settings/scheme-editor)。

        前置:已到高级设置总页。经平台分组卡进单平台页后点「新建」进入;
        止步保存前(保存=uploadVisualInfo type="4" 写——禁区 2)。
        """
        self.open_vision_platform_page(platform, timeout=timeout)
        self.click_text("新建", timeout=timeout)
        self._vision_expect_any_text(
            ("新建", "方案", "壁纸", "保存", "完成"), timeout=timeout)

    def pick_voice_pack_row(self, timeout: int = 10) -> str:
        """语音包列表整行点击(整行=选中+试听热区,YAML NEG-003/POS-017/018 契约)。

        前置:已到语音包页。行锚用 KB 实测系统角色名候选,命中即点击并返回
        该行名;候选均未命中直接断言失败暴露(锚点待标定,见 template_needs)。
        """
        for name in _VOICE_PACK_ROW_HINTS:
            if self.find_text_by_ocr(name, timeout=3) is not None:
                self.click_text(name, timeout=timeout)
                return name
        assert False, (
            f"语音包行锚未命中(候选全缺): {list(_VOICE_PACK_ROW_HINTS)}"
            "——条目锚点待标定,见 package_report.template_needs")

    def pick_vision_editor_materials(self, category: str, count: int,
                                     timeout: int = 10) -> int:
        """方案编辑器:点分类 Tab 后尝试勾选 count 个素材条目,返回成功勾选数。

        前置:已到方案编辑器。素材条目文案候选未标定(知识库绑定态未探索),
        _EDITOR_MATERIAL_HINTS 为空时恒返 0——标定后填入候选即全局生效。
        勾选为纯选择态(不保存=零写,禁区 2 安全)。
        """
        self.click_text(category, timeout=timeout)
        picked = 0
        for text in _EDITOR_MATERIAL_HINTS:
            if picked >= count:
                break
            if self.find_text_by_ocr(text, timeout=2) is not None:
                self.click_text(text, timeout=5)
                picked += 1
        return picked
