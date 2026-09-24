"""Swan 项目业务方法（flutter 端）。

页面控件 key 约定（accessibility resource_id）与既有用例
``tests/flutter/test_swan_login_logout.py`` 保持一致。
"""
from __future__ import annotations

import logging
import os
import re
import time

from image.image_name_mapping import (
    SWAN_DEVICE_ADD_BTN,
    SWAN_DEVICE_CARD_SELECTED,
    SWAN_DEVICE_SHEET_CHECKED,
    SWAN_DEVICE_SHEET_TITLE,
    SWAN_FAVORITE_PLAY_ALL,
    SWAN_HOME_MUSIC_SEARCH_BAR,
    SWAN_HOME_RADIO_SEARCH_BAR,
    SWAN_HOME_TAB_AI,
    SWAN_HOME_TAB_AI_SEL,
    SWAN_HOME_TAB_MUSIC,
    SWAN_HOME_TAB_MUSIC_SEL,
    SWAN_HOME_TAB_RADIO,
    SWAN_HOME_TAB_RADIO_SEL,
    SWAN_HOME_TAB_RECOMMEND,
    SWAN_HOME_TAB_RECOMMEND_SEL,
    SWAN_HOME_TAB_VISION,
    SWAN_HOME_TAB_VISION_SEL,
    SWAN_HISTORY_TOPBAR,
    SWAN_ME_FAVORITES_ROW,
    SWAN_PD_FAV_OFF,
    SWAN_PD_FAV_ON,
    SWAN_PD_MORE_BTN,
    SWAN_PD_PLAY_ALL,
    SWAN_PD_ROW_FAV_BTN,
    SWAN_PLAYER_DEVICE_BTN,
    SWAN_PLAYER_DISMISS_BTN,
    SWAN_PLAYER_FAV_BTN,
    SWAN_PLAYER_LOOP_LIST,
    SWAN_PLAYER_LOOP_SHUFFLE,
    SWAN_PLAYER_LOOP_SINGLE,
    SWAN_PLAYER_NEXT_BTN,
    SWAN_PLAYER_PAUSE_BTN,
    SWAN_PLAYER_PLAY_PAUSE_BTN,
    SWAN_PLAYER_PREV_BTN,
    SWAN_PLAYER_PROGRESS_BAR,
    SWAN_PLAYER_VOLUME_ICON,
    SWAN_PLAYER_VOLUME_MINUS,
    SWAN_PLAYER_VOLUME_PLUS,
    SWAN_PLAYER_VOLUME_POPUP,
    SWAN_PLAYER_VOLUME_SLIDER,
    SWAN_PLATFORM_NETEASE_ROW,
    SWAN_SEARCH_EMPTY,
    SWAN_SEARCH_SUBMIT,
    SWAN_TAB_DEVICE,
    SWAN_TAB_HOME,
    SWAN_TAB_ME,
    SWAN_TAB_PLATFORM,
)
from utils.aw.base.flutter_base import FlutterBaseAW
from utils.aw.business.common import CommonBusinessMixin

logger = logging.getLogger(__name__)


class SwanBusiness(CommonBusinessMixin, FlutterBaseAW):
    """Swan 项目业务编排（flutter 端），Swan 专属业务方法放这里。"""

    # 登录页 accessibility key（✅ = 2026-09-08 真机 uiautomator dump 验证）
    KEY_LOGIN_PAGE = "login_page"                        # ✅
    KEY_PHONE_FIELD = "login_phone_field"                # ✅
    KEY_AGREEMENT = "login_agreement_checkbox"           # ✅
    KEY_SUBMIT = "login_submit_button"                   # ✅ 文案"下一步"
    KEY_USE_PASSWORD_BUTTON = "login_use_password_button"  # ✅ 右上角"密码登入"切换
    KEY_AREA_CODE_BUTTON = "login_area_code_button"      # ✅ 区号"+86"
    KEY_THIRD_WECHAT_BUTTON = "login_third_party_wechat_button"  # ✅
    KEY_THIRD_WEIBO_BUTTON = "login_third_party_weibo_button"    # ✅
    KEY_CODE_FIELD = "login_code_field"                  # ✅ 验证码输入页（4 位，填满自动提交）
    KEY_USE_SMS_BUTTON = "login_use_sms_button"          # ✅ 密码页右上角"验证码登入"（与 use_password 互斥）
    KEY_PASSWORD_FIELD = "login_password_field"          # ✅ 2026-09-08 密码页 dump 实测
    KEY_ERROR_TEXT = "login_error_text"                  # ✅ 2026-09-08 密码登录失败提示（content-desc"密码错误，请重新输入！"）

    # 首页 accessibility key（✅ 2026-09-08 真机验证）
    KEY_TAB_RECOMMEND = "tab_recommend"                  # 首页
    KEY_TAB_PLATFORM = "tab_platform"                    # 平台
    KEY_TAB_DEVICE = "tab_device"                        # 设备
    KEY_TAB_ME = "tab_me"                                # 我的
    KEY_BOTTOM_PLAYER = "bottom_player"                  # 底部播放条

    # 我的 / 个人信息页（✅ 2026-09-08 真机验证）
    KEY_ME_PROFILE_ENTRY = "me_user_profile_entry"        # 我的页顶部账号入口
    KEY_PERSON_INFO_PAGE = "person_info_page"             # 个人信息修改页根节点
    KEY_LOGOUT_BUTTON = "person_info_logout_button"       # 退出登入
    KEY_CANCEL_ACCOUNT_BUTTON = "person_info_cancel_account_button"  # 注销账号（危险，勿点）

    # 平台页（✅ 2026-09-08 真机 dump 验证）
    KEY_PLATFORM_PAGE = "platform_page"                   # 平台页根节点（页面判据）
    KEY_NETEASE_PLATFORM_ENTRY = "netease_platform_entry"  # 网易云音乐行（⛔ 授权类，勿点）

    # 设备页（✅ 2026-09-08 真机 dump 验证）
    KEY_DEVICE_PAGE = "device_page"                       # 设备页根节点（页面判据）
    KEY_DEVICE_ADD_BUTTON = "device_add_button"            # 添加设备（⛔ 进配网流程，勿点）
    KEY_DEVICE_WIFI_SECTION = "device_wifi_section"        # 左侧 WIFI 分类
    # ⚠️ 设备卡 key 按设备 UUID 动态拼接，禁止写死后缀，一律用前缀匹配
    PREFIX_WIFI_DEVICE_CARD = "wifi_device_card_"          # 设备卡片（⛔ 勿点）
    PREFIX_WIFI_DEVICE_SETTINGS = "wifi_device_settings_"  # 设备设置（⛔ 含删除设备）
    PREFIX_WIFI_DEVICE_SYNC = "wifi_device_sync_"          # 同步设备（⛔ 向真机下发）

    # 全屏播放页（✅ 2026-09-08 真机 dump 验证）
    KEY_FULL_PLAYER_PAGE = "full_player_page"              # 播放页根节点（页面判据）
    KEY_PLAYER_DISMISS_BUTTON = "player_dismiss_button"    # 左上角收起
    KEY_PLAYER_PLAY_PAUSE_BUTTON = "player_play_pause_button"  # 播放/暂停（⛔ 只断言不点）
    KEY_PLAYER_VOLUME_BUTTON = "player_volume_button"      # 音量（⛔ 只断言不点）

    def go_home(self, timeout: float = 15.0) -> None:
        """回到首页（tab_recommend），用例收尾统一入口（G3/G4）。"""
        self.click_accessibility(self.KEY_TAB_RECOMMEND)
        assert self.wait_accessibility(self.KEY_TAB_ME, timeout=timeout), "未回到首页"

    def list_accessibility_keys_by_prefix(self, prefix: str) -> list[str]:
        """列出当前页面 resource_id 以 prefix 开头的语义 key（去重、有序）。

        用于设备卡这类按 UUID 动态拼接 key 的元素计数/存在性判断，
        避免把 UUID 写死在用例里。仅做判断，点击仍走 click_accessibility。
        """
        found: list[str] = []
        for node in self.dump_semantics():
            node_id = (node.get("resource_id") or "").split("/")[-1]
            if node_id.startswith(prefix) and node_id not in found:
                found.append(node_id)
        return found

    def login(
        self,
        phone: str | None = None,
        password: str | None = None,
        *,
        method: str = "password",
        wait_code: float = 60.0,
    ) -> None:
        """确保 Swan 已登录并回到首页，支持 password / sms 两种方式。

        App 须已打开，当前处于登录页或显示底部导航的已登录页面。
        已登录时直接复用当前会话，不校验账号身份，也不切换账号。
        未登录时，省略的凭据从 SWAN_PHONE / SWAN_PASSWORD 读取；
        显式空值会报错，密码保留原值。提交前重启 App 清除残留表单，
        包名取 SWAN_PACKAGE（默认 com.swan.network）。失败直接抛出。
        sms 模式通过现有验证码平台取码，wait_code 为取码等待秒数。
        """
        if method not in ("password", "sms"):
            raise ValueError("method 仅支持 password 或 sms")
        if self.accessibility_exists(self.KEY_TAB_ME):
            self.go_home()
            return

        phone = os.getenv("SWAN_PHONE") if phone is None else phone
        if not isinstance(phone, str) or not phone.strip():
            raise ValueError("请提供手机号或配置 SWAN_PHONE")
        phone = phone.strip()
        if method == "password":
            password = os.getenv("SWAN_PASSWORD") if password is None else password
            if not isinstance(password, str) or not password.strip():
                raise ValueError("请提供密码或配置 SWAN_PASSWORD")

        assert self.wait_accessibility(
            self.KEY_LOGIN_PAGE, timeout=15
        ), "login 需要从登录页或已登录的底部导航页面调用"
        self.relaunch_app(os.getenv("SWAN_PACKAGE", "com.swan.network"))
        if self.accessibility_exists(self.KEY_TAB_ME):
            self.go_home()
            return
        assert self.wait_accessibility(
            self.KEY_LOGIN_PAGE, timeout=15
        ), "重启后未进入登录页"
        if method == "password":
            self.login_with_password(phone, password)
        else:
            self.login_by_sms(phone, wait_code=wait_code)
        self.go_home()

    def login_with_password(self, phone: str, password: str) -> None:
        """密码登录（2026-09-08 真机实测流程），最终停在首页。

        实测流程（真机 c0614b6a 验证通过）：
        1. 若当前不在密码形态（无 login_password_field），点 login_use_password_button
           从验证码形态切入（密码页与验证码页同根 login_page，右上角互切）
        2. 点 login_phone_field → input_text 手机号（ASCII，adb input 直输可用）
        3. 点 login_password_field → input_text 密码
        4. press_back 收软键盘（实测只收键盘，不会像验证码输入页那样退出 App），
           否则键盘遮挡提交按钮
        5. 勾选 login_agreement_checkbox → 点 login_submit_button（文案"登录"，
           与验证码页"下一步"同 key 不同形态；未填满/未勾协议时置灰不可点）
        6. 等 tab_me 判进首页

        前提：协议勾选框处于未勾选态（登出后的全新登录页即如此）。登录页表单
        状态（已填文本/勾选态）在登出后会残留，若从"提交失败后的表单"直接重试，
        应先重启 App 重置表单（见 test_swan_password_login.py 收尾处理）。
        登录成功会顶掉本机旧会话（单点登录），属正常现象。
        """
        if not self.accessibility_exists(self.KEY_PASSWORD_FIELD):
            self.click_accessibility(self.KEY_USE_PASSWORD_BUTTON)
            assert self.wait_accessibility(
                self.KEY_PASSWORD_FIELD, timeout=10
            ), "切到密码登录形态失败（login_password_field 未出现）"
        self.click_accessibility(self.KEY_PHONE_FIELD)
        self.clear_input()  # 防表单残留：先清空再输入
        self.input_text(phone)
        self.click_accessibility(self.KEY_PASSWORD_FIELD)
        self.clear_input()
        self.input_text(password)
        self.press_back()
        self.click_accessibility(self.KEY_AGREEMENT)
        self.click_accessibility(self.KEY_SUBMIT)
        assert self.wait_accessibility(self.KEY_TAB_ME, timeout=20), "登录后未进入首页"

    def login_by_sms(self, phone: str, wait_code: float = 60.0) -> None:
        """验证码登录：输入手机号 → 下一步（自动发送验证码）→ 平台取码 → 填码自动提交。

        实测（2026-09-08）：点"下一步"后 App 自动发送验证码并跳到验证码输入页，
        没有"获取验证码"按钮；验证码 4 位，填满第 4 位自动提交进首页。
        确认验证码输入页出现后才向平台取码。
        前提：处于验证码登录形态，协议勾选框未勾选（全新登录页默认态）；
        若从勾选过的残留表单进入，调用方须先重启 App 重置表单。
        """
        # 已在首页视为已登录
        if self.accessibility_exists(self.KEY_TAB_ME):
            logger.info("已在首页，跳过登录")
            return
        self.enter_sms_code_step(phone)
        code = self._fetch_sms_code(phone, wait=wait_code)
        self.click_accessibility(self.KEY_CODE_FIELD)
        self.input_text(code)
        assert self.wait_accessibility(self.KEY_TAB_ME, timeout=20), "登录后未进入首页"

    def enter_sms_code_step(self, phone: str, timeout: float = 15.0) -> None:
        """验证码登录第一步：填手机号 → 勾协议 → 点"下一步"，停在验证码输入页。

        前提：全新验证码登录形态（协议未勾选）；"下一步"自动发送验证码
        （无独立"获取验证码"按钮），之后网关才能取到本次验证码。
        分步封装，供需要断言中间状态的用例使用；一步到位用 login_by_sms。
        """
        self.click_accessibility(self.KEY_PHONE_FIELD)
        self.clear_input()  # 防表单残留：先清空再输入
        self.input_text(phone)
        self.click_accessibility(self.KEY_AGREEMENT)
        self.click_accessibility(self.KEY_SUBMIT)
        assert self.wait_accessibility(
            self.KEY_CODE_FIELD, timeout=timeout
        ), "点击下一步后未进入验证码输入页（login_code_field 未出现）"

    def fill_sms_code(self, code: str) -> None:
        """向验证码输入框追加输入（adb input text 为追加语义），不主动提交。

        满 4 位由 App 自动提交（设计行为，见模块卡片已知坑5）；
        分段输入（如先 3 位断言不提交、再补第 4 位断言自动提交）即依赖追加语义。
        """
        self.click_accessibility(self.KEY_CODE_FIELD)
        self.input_text(code)

    def relaunch_app(self, package: str, timeout: float = 30.0) -> None:
        """杀进程后冷启动，等待冷启动落地页出现（已登录→首页 tab_me，未登录→登录页）。

        用途：登录页表单残留重置（登录页无状态持久化）、冷启动 token 恢复链路用例。
        落地页断言由调用方按登录态选择（tab_me 或 login_page）。
        """
        self.driver.stop_app(package)
        self.driver.start_app(package)
        landed = self.wait_accessibility(self.KEY_TAB_ME, timeout=timeout) or \
            self.wait_accessibility(self.KEY_LOGIN_PAGE, timeout=5)
        assert landed, "冷启动后既未到首页也未到登录页"

    def logout_if_needed(self) -> None:
        """若已登录则登出，回到登录页（G3/G4 清理约定）。

        路径：首页 tab_me → me_user_profile_entry → person_info_logout_button。
        注意 `person_info_cancel_account_button`（注销账号）就在旁边，禁止误点。
        """
        if not self.accessibility_exists(self.KEY_TAB_ME):
            logger.info("未登录，无需登出")
            return
        self.click_accessibility(self.KEY_TAB_ME)
        assert self.wait_accessibility(self.KEY_ME_PROFILE_ENTRY, timeout=10), "未进入我的页"
        self.click_accessibility(self.KEY_ME_PROFILE_ENTRY)
        assert self.wait_accessibility(self.KEY_PERSON_INFO_PAGE, timeout=10), "未进入个人信息页"
        self.click_accessibility(self.KEY_LOGOUT_BUTTON)
        assert self.wait_accessibility(self.KEY_LOGIN_PAGE, timeout=20), "登出后未回到登录页"

    # =================================================================
    # 域 3：播放器与播放控制（回归用例 11-28，方案 A12-A20）
    #
    # 定位铁律（方案 §0）：图像模板 > OCR 文本；运行时禁用 accessibility
    # key 与裸坐标 tap。播放页方法默认调用方已处于全屏播放页。
    # 断言口径：
    #   - 播放态 = 控制键图标 [图] + 封面区 region_changed 双证据（A16）；
    #   - 音量 = UI 态（音量百分比 OCR），声学断言已拍板降级（方案 §5③）；
    #   - select_device 会把输出真实下发到 rig 音箱（方案 §5②）。
    # 元素模板登记在 image/image_name_mapping.py「回归第一批·域3」段，
    # 当前为 image_ai 草稿路径；aw-verify 转正后需把登记处 draft=True 改 False。
    # =================================================================

    # 「播放全部」按钮按所在列表页区分（A13）
    _PLAY_ALL_TEMPLATES = {
        "favorite": SWAN_FAVORITE_PLAY_ALL,   # 我喜欢页
        "playlist": SWAN_PD_PLAY_ALL,         # 歌单详情页
    }

    # 播放控制键（A14）：⏸/⏮/⏭ 为域3 新截草稿；▶ 态复用已转正图
    _CONTROL_TEMPLATES = {
        "next": SWAN_PLAYER_NEXT_BTN,
        "prev": SWAN_PLAYER_PREV_BTN,
        "pause": SWAN_PLAYER_PAUSE_BTN,       # 播放中显示 ⏸
        "play": SWAN_PLAYER_PLAY_PAUSE_BTN,   # 暂停中显示 ▶
    }

    # 循环模式三态图标（A15）：循环钮当前态即三态图标之一，点按在三态间轮转
    _LOOP_TEMPLATES = {
        "list": SWAN_PLAYER_LOOP_LIST,
        "single": SWAN_PLAYER_LOOP_SINGLE,
        "shuffle": SWAN_PLAYER_LOOP_SHUFFLE,
    }

    # 音量滑条方向（A19 默认横向；弹窗实际布局待真机校准，纵向改 "y"）
    _VOLUME_SLIDER_AXIS = "x"
    # 设备页卡片：设备名行到状态行允许的最大纵向跨度（720x1600 口径，待真机校准）
    _CARD_BODY_SPAN = 300
    # 设备页 OCR 候选行下界（cy > 此值的项一律剔除，720x1600 口径）：底部
    # 播放条区 y≈1376-1476（verify-run3 实测），持久会话下播放条常驻设备名，
    # 不剔除会把设备名兜底匹配错配到播放条标题上（实测案例见 select_device 注）。
    _DEVICE_OCR_BOTTOM_LIMIT = 1350

    # OCR 设备名易混字符归一化映射（verify R2 实测：「HiVi M300MKII」被
    # 读成「HiVi M300MKIl」——罗马数字 II 与小写 l 同形，name in text
    # 精确匹配失败）。兜底比对时把两侧 l/I/1 统一映射到 1 再匹配。
    _OCR_CONFUSABLE_TRANS = str.maketrans({"l": "1", "I": "1", "1": "1"})

    _TIME_RE = re.compile(r"(\d{1,2}):(\d{2})")

    @classmethod
    def _ocr_compact(cls, text: str) -> str:
        """OCR 文本 compact 形式：去全部空格 + l/I/1 易混字符归一化。

        verify-run3 实测两类失真：①「HiVi M300MKII」被读成「HiViM300MKII>」
        （空格丢失，且带尾随杂字符），仅 l/I/1 归一化覆盖不了空格差异；
        ②被读成「HiVi M300MKIl」（II→Il 同形）。两侧都 compact 后再做
        包含比对可同时吞掉两种失真。
        """
        return text.translate(cls._OCR_CONFUSABLE_TRANS).replace(" ", "")

    def select_device(self, name: str, via: str = "card") -> None:
        """切换输出设备（A12，回归用例 11-12）。

        via="card"：设备页 OCR 定位目标设备名所在卡片（设备名精确包含
        优先，失配时两侧 compact 归一化——去空格 + l/I/1 易混字符映射——
        兜底再匹配，见 _ocr_compact 注；OCR 候选行剔除底部播放条区
        cy > _DEVICE_OCR_BOTTOM_LIMIT，播放条常驻设备名不作候选），点卡片
        状态行（「连接良好」行）。⚠️ 不点设备名本身——知识库实测设备名
        节点是设置入口（wifi_device_settings_<UUID>），内含删除设备风险。
        收尾断言卡片选中态 [图]。

        via="player"：播放页右上角设备切换钮 [图] 开弹层 → 断言弹层标题
        [图] → OCR 点目标设备行 → 断言行勾选态 [图]；若弹层随选择自动
        关闭，退化为断言已回播放页且页顶输出设备名 OCR 出现目标名。

        ⚠️ 选择会真实下发到 rig 音箱（方案 §5② 回归须真点真音箱），
        且跨用例不自动回切。
        """
        assert via in ("card", "player"), "via 仅支持 card / player"
        if via == "card":
            # 先剔除底部播放条区 OCR 项（cy > _DEVICE_OCR_BOTTOM_LIMIT）：
            # verify-run3 实测案例——卡片标题被 OCR 读成「HiViM300MKII>」
            # （空格丢失）致名字精确匹配失败，兜底错配到播放条常驻标题
            # 「HiVi M300MKII」（y≈1376-1476），随后以播放条 cy 找「连接
            # 良好」必然失败。播放条区本就不可点，整体剔除。
            items = [i for i in self.ocr_scan_page()
                     if i["cy"] <= self._DEVICE_OCR_BOTTOM_LIMIT]
            # 设备名比对：优先 OCR 文本精确包含；失配时两侧 compact 归一化
            # （去空格 + l/I/1 易混字符映射，见 _ocr_compact 注）兜底再匹配。
            # 实测案例1：OCR 把「HiVi M300MKII」读成「HiVi M300MKIl」
            # （II→Il），归一化后命中；案例2：读成「HiViM300MKII>」（空格
            # 丢失），去空格后命中。状态行「连接良好」定位逻辑不受影响。
            name_item = next((i for i in items if name in i["text"]), None)
            if name_item is None:
                compact_name = self._ocr_compact(name)
                name_item = next(
                    (i for i in items
                     if compact_name in self._ocr_compact(i["text"])),
                    None,
                )
                if name_item is not None:
                    logger.info(
                        "select_device: 设备名 %r 精确匹配失败，"
                        "compact 归一化（去空格+l/I/1）后命中 OCR 文本 %r",
                        name, name_item["text"])
            assert name_item is not None, f"设备页 OCR 未找到设备名 {name!r}"
            status_item = next(
                (i for i in items
                 if "连接良好" in i["text"]
                 and 0 < i["cy"] - name_item["cy"] <= self._CARD_BODY_SPAN),
                None,
            )
            assert status_item is not None, (
                f"设备 {name!r} 卡片上未找到状态行「连接良好」"
                "（设备可能离线，或卡片布局变化需校准 _CARD_BODY_SPAN）")
            self.tap(status_item["cx"], status_item["cy"])
            self.image_exists(SWAN_DEVICE_CARD_SELECTED, timeout=10)
        else:
            self.click_image(SWAN_PLAYER_DEVICE_BTN, timeout=10)
            self.image_exists(SWAN_DEVICE_SHEET_TITLE, timeout=10)
            self.click_text(name, timeout=10)
            if self.find_image(SWAN_DEVICE_SHEET_CHECKED, timeout=5) is not None:
                logger.info("设备弹层勾选态 [图] 已确认")
            else:
                # 弹层可能已随选择自动关闭：退化为核对播放页顶部输出设备名
                self.image_exists(SWAN_PLAYER_DISMISS_BTN, timeout=10)
                self.text_exists(name, timeout=10)

    def start_play(self, source: str = "favorite", mode: str = "all",
                   index: int = 0) -> None:
        """发起播放（A13，回归用例 13-14 及各域播放前置）。

        mode="all"：点所在列表页的「播放全部」[图]。source 为列表页：
        favorite=我喜欢页 / playlist=歌单详情页（调用方须已在该页）。
        mode="song"：OCR 点歌名开播。source 为歌名文本，index 为同名
        匹配序号（0=第一个，按 OCR 返回顺序）。

        收尾断言：播放页顶栏已渲染 [图] + 播放态双证据（assert_playing）。
        ⚠️ 隐含假设「点播放全部/歌曲行会进入全屏播放页」——无任务态探索
        未能验证，若真机实测不自动进入，需补一张迷你播放条控制区小图改走
        主动进播放页的路径（见交接遗留）。
        """
        if mode == "all":
            template = self._PLAY_ALL_TEMPLATES.get(source)
            if template is None:
                raise ValueError(
                    f"source 仅支持 {sorted(self._PLAY_ALL_TEMPLATES)}，收到 {source!r}")
            self.click_image(template, timeout=10)
        elif mode == "song":
            if index == 0:
                self.click_text(source, timeout=10)
            else:
                matches = [i for i in self.ocr_scan_page()
                           if source.lower() in i["text"].lower()]
                assert len(matches) > index, (
                    f"OCR 仅匹配到 {len(matches)} 处 {source!r}，取第 {index} 个失败")
                self.tap(matches[index]["cx"], matches[index]["cy"])
        else:
            raise ValueError("mode 仅支持 all / song")
        self.image_exists(SWAN_PLAYER_DISMISS_BTN, timeout=15)  # 已进入播放页
        self.assert_playing()

    def player_control(self, action: str = "play") -> None:
        """播放控制（A14，回归用例 16-22）。

        action="pause"/"play"：点 ⏸/▶ 后分别以 assert_paused/assert_playing
        双证据收尾。action="next"/"prev"：切歌后断言播放态保持；具体曲目
        是否切换由用例层用 assert_now_playing 按已知歌名复核（方法层不
        预设目标曲目）。
        """
        template = self._CONTROL_TEMPLATES.get(action)
        if template is None:
            raise ValueError("action 仅支持 next / prev / pause / play")
        self.click_image(template, timeout=10)
        if action == "pause":
            self.assert_paused()
        else:
            # play / next / prev 收尾都断言播放中（切歌不打断播放）
            self.assert_playing()

    def set_loop_mode(self, mode: str = "list") -> None:
        """切循环模式（A15，回归用例 15/19 及播放控制矩阵）。

        循环钮当前态图标即三态图之一，点一次切下一态；最多点 3 次直到
        目标态图标出现，收尾断言目标态图标在位 [图]。
        """
        target = self._LOOP_TEMPLATES.get(mode)
        if target is None:
            raise ValueError("mode 仅支持 list / single / shuffle")
        for _ in range(3):
            if self.find_image(target, threshold=0.8, timeout=2) is not None:
                break
            current = next(
                (tpl for name, tpl in self._LOOP_TEMPLATES.items()
                 if name != mode and self.find_image(tpl, timeout=1) is not None),
                None,
            )
            assert current is not None, "未找到循环模式按钮（三态图标均未匹配）"
            self.click_image(current, timeout=2)
        self.image_exists(target, timeout=5)

    def _vinyl_region(self) -> tuple[int, int, int, int]:
        """锚定封面（黑胶）检测区：以进度条矩形为锚，取其正上方等宽方形区。

        进度条整条 [图] 是播放页唯一稳定的横向锚点，封面区在其正上方。
        区位假设待真机校准（方案 §2.2 B4）。
        """
        rect = self.find_image_rect(SWAN_PLAYER_PROGRESS_BAR, timeout=10)
        assert rect is not None, "未找到进度条，无法锚定封面区"
        px, py, pw, _ph = rect
        y = max(0, py - pw)
        return (px, y, pw, py - y)

    def assert_playing(self) -> None:
        """播放态断言（A16）：⏸ 图标 [图] + 封面区画面在动（region_changed）双证据。"""
        self.image_exists(SWAN_PLAYER_PAUSE_BTN, timeout=10)
        assert self.region_changed(*self._vinyl_region()), (
            "播放态第二证据失败：⏸ 在位但封面区画面静止（黑胶未转动）")

    def assert_paused(self) -> None:
        """暂停态断言（A16）：▶ 图标 [图] + 封面区画面静止 双证据。

        注意不区分「无播放任务」与「已暂停」（两者都是 ▶ + 画面静止），
        调用方须保证当前存在播放任务。
        """
        self.image_exists(SWAN_PLAYER_PLAY_PAUSE_BTN, timeout=10)
        assert not self.region_changed(*self._vinyl_region()), (
            "暂停态第二证据失败：▶ 在位但封面区画面仍在动")

    def assert_now_playing(self, title: str, artist: str = "") -> None:
        """断言当前播放曲目（A17）：曲目区 OCR 歌名（及歌手）。

        player_title 是动态元素不截图，一律 OCR 文本断言；artist 缺省时
        只核对歌名。
        """
        self.text_exists(title, timeout=10)
        if artist:
            self.text_exists(artist, timeout=10)

    def seek_to(self, ratio: float, action: str = "drag") -> None:
        """跳转播放进度（A18，回归用例 23-24）。

        action="drag"：进度条整条 [图] 元素锚定，从左端拖到 ratio 位置
        （drag_on_template，B5）。
        action="click"：点击进度条上 ratio 比例位置（模板矩形锚定，非裸坐标）。

        收尾断言：OCR 进度条附近双时间，核对 已播 ≈ ratio × 总时长
        （容差 max(5s, 总时长 10%)）；OCR 取不到双时间时退化为播放态断言。
        """
        if action not in ("drag", "click"):
            raise ValueError("action 仅支持 drag / click")
        assert 0.0 <= ratio <= 1.0, "ratio 须在 0~1"
        if action == "drag":
            assert self.drag_on_template(
                SWAN_PLAYER_PROGRESS_BAR, 0.0, ratio, axis="x"), "进度条拖动失败"
        else:
            rect = self.find_image_rect(SWAN_PLAYER_PROGRESS_BAR, timeout=10)
            assert rect is not None, "未找到进度条"
            x, y, w, h = rect
            assert self.tap(x + int(w * ratio), y + h // 2), "进度条点击失败"
        times = self._ocr_progress_times(timeout=8)
        if times is not None:
            elapsed, total = times
            assert total > 0, f"进度时间异常：总时长为 {total}s（当前可能无播放任务）"
            tolerance = max(5.0, total * 0.1)
            assert abs(elapsed - total * ratio) <= tolerance, (
                f"seek 后进度 {elapsed}s 偏离目标 {ratio * total:.0f}s"
                f"（容差 {tolerance:.0f}s）")
        else:
            logger.warning("seek_to: OCR 未取得进度双时间，退化为播放态断言")
            self.assert_playing()

    def set_volume(self, value: int, action: str = "drag") -> None:
        """调节音量（A19，回归用例 25-26）。

        声学断言已拍板降级为 UI 态（方案 §5③）：
        - action="drag"：点音量图标 [图] 开弹窗 → 断言弹窗 [图] → 音量滑条
          整条 [图] 元素锚定拖到 value/100 位置 → 关弹窗后 OCR 播放页音量
          百分比核对 value（±5）。
        - action="click"：同上，改为点击滑条上 value/100 比例位置。
        - action="plus"/"minus"：value 为加减钮连点次数，收尾断言弹窗关闭
          且回到播放页（步进结果不核对具体百分比）。

        音量滑条方向默认横向（_VOLUME_SLIDER_AXIS），弹窗实际布局待真机
        校准，纵向改 "y" 即可。
        """
        if action not in ("drag", "click", "plus", "minus"):
            raise ValueError("action 仅支持 drag / click / plus / minus")
        if action in ("drag", "click"):
            assert 0 <= value <= 100, "drag/click 的 value 须为 0~100"
        else:
            assert value > 0, "plus/minus 的 value 须为正的连点次数"
        self.click_image(SWAN_PLAYER_VOLUME_ICON, timeout=10)       # 打开音量弹窗
        self.image_exists(SWAN_PLAYER_VOLUME_POPUP, timeout=10)     # 弹窗在位
        if action == "drag":
            start_ratio, end_ratio = self._volume_ratios(value)
            assert self.drag_on_template(
                SWAN_PLAYER_VOLUME_SLIDER, start_ratio, end_ratio,
                axis=self._VOLUME_SLIDER_AXIS), "音量滑条拖动失败"
        elif action == "click":
            rect = self.find_image_rect(SWAN_PLAYER_VOLUME_SLIDER, timeout=10)
            assert rect is not None, "未找到音量滑条"
            px, py = self._volume_point(rect, value)
            assert self.tap(px, py), "音量滑条点击失败"
        else:
            template = (SWAN_PLAYER_VOLUME_PLUS if action == "plus"
                        else SWAN_PLAYER_VOLUME_MINUS)
            for _ in range(value):
                self.click_image(template, timeout=5)
        self.press_back()  # 关弹窗回播放页（弹层关闭惯例，见知识库）
        self.image_exists(SWAN_PLAYER_VOLUME_ICON, timeout=10)      # 已回播放页
        if action in ("drag", "click"):
            self._assert_volume_percent(value)

    def volume_key(self, direction: str = "up", long_press: bool = False) -> None:
        """物理音量键调节音量（A20，回归用例 27-28）。

        走 driver keyevent（long_press=True 时 --longpress）。断言口径按
        拍板降级为 UI 态：按键前后 OCR 播放页音量百分比并核对增减方向；
        OCR 读不到百分比时退化为断言播放页仍在前台（音量图标 [图] 在位）。
        须在播放页调用。
        """
        assert direction in ("up", "down"), "direction 仅支持 up / down"
        before = self._ocr_volume_percent(timeout=5)
        key = "KEYCODE_VOLUME_UP" if direction == "up" else "KEYCODE_VOLUME_DOWN"
        if long_press:
            assert self.long_press_key(key), "音量键长按失败"
        else:
            assert self.press_key(key), "音量键按下失败"
        after = self._ocr_volume_percent(timeout=8)
        if before is not None and after is not None:
            if direction == "up":
                assert after > before, f"音量未升高：按键前 {before}% → 按键后 {after}%"
            else:
                assert after < before, f"音量未降低：按键前 {before}% → 按键后 {after}%"
        else:
            logger.warning("volume_key: OCR 未取得音量百分比，退化为前台锚点断言")
            self.image_exists(SWAN_PLAYER_VOLUME_ICON, timeout=10)

    # ---------- 域3 内部辅助 ----------

    def _ocr_progress_times(self, timeout: float = 8.0) -> tuple[int, int] | None:
        """OCR 进度条附近时间文本，返回 (已播秒数, 总时长秒数)。

        搜索区锚定进度条矩形并向左右各扩一条宽度、纵向扩若干倍条高的横带，
        避免误采页面其它含时间字样的文本（如歌名）。凑不齐两个时间返回 None。
        """
        rect = self.find_image_rect(SWAN_PLAYER_PROGRESS_BAR, timeout=5)
        if rect is None:
            return None
        px, py, pw, ph = rect
        region = (max(0, px - pw), max(0, py - ph * 3), pw * 3, ph * 7)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            found: list[tuple[str, str]] = []
            for item in self.ocr_scan_page(region=region):
                found.extend(self._TIME_RE.findall(item["text"]))
                if len(found) >= 2:
                    break
            if len(found) >= 2:
                elapsed = int(found[0][0]) * 60 + int(found[0][1])
                total = int(found[1][0]) * 60 + int(found[1][1])
                return elapsed, total
            self.sleep(0.5)
        return None

    def _ocr_volume_percent(self, timeout: float = 5.0) -> int | None:
        """OCR 页面音量百分比文本（如"35%"），返回整数；读不到返回 None。"""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for item in self.ocr_scan_page():
                m = re.search(r"(\d{1,3})\s*%", item["text"])
                if m:
                    return int(m.group(1))
            self.sleep(0.5)
        return None

    def _assert_volume_percent(self, expected: int, tolerance: int = 5,
                               timeout: float = 8.0) -> None:
        """核对音量 UI 态：OCR 百分比与目标差值 ≤ tolerance。"""
        actual = self._ocr_volume_percent(timeout=timeout)
        assert actual is not None, "OCR 未读到音量百分比文本，无法核对音量 UI 态"
        assert abs(actual - expected) <= tolerance, (
            f"音量 UI 显示 {actual}%，偏离目标 {expected}%（±{tolerance}）")

    @classmethod
    def _volume_ratios(cls, value: int) -> tuple[float, float]:
        """音量百分比 → 滑条拖动起止比例（纵向滑条下小上大）。"""
        ratio = value / 100.0
        if cls._VOLUME_SLIDER_AXIS == "x":
            return 0.0, ratio
        return 1.0, 1.0 - ratio

    @classmethod
    def _volume_point(cls, rect: tuple[int, int, int, int],
                      value: int) -> tuple[int, int]:
        """音量百分比 → 滑条矩形上的点击点。"""
        x, y, w, h = rect
        ratio = value / 100.0
        if cls._VOLUME_SLIDER_AXIS == "x":
            return x + int(w * ratio), y + h // 2
        return x + w // 2, y + int(h * (1.0 - ratio))

    # =================================================================
    # 域 4：导航（回归用例 29-31，方案 A21-A23）
    #
    # 定位铁律同域3（方案 §0）：图像模板 > OCR 文本；本域不使用
    # accessibility key。已知陷阱（知识库 flow_导航_四tab切换 / swan_首页）：
    #   - 顶 Tab 持久化：go_home 只回首页容器，顶 Tab 停留在上次选择，
    #     要稳定落在某顶 Tab 必须显式点它；
    #   - 推荐 Tab 存在完整/紧凑两种服务端布局轮换，依赖「歌单」卡的
    #     入口须容忍轮换（未找到时下拉刷新重试）。
    # =================================================================

    # 底部导航 4 图标（A21，未选中态，域4 新截草稿；「推荐」为「首页」的
    # 任务口径别名——底部标签 dump 文案是「首页」，顶 Tab 才叫「推荐」）。
    # 图标选中态不匹配未选中态模板，故目标页锚点可见时短路不点（见 go_bottom_tab）。
    _BOTTOM_TAB_TEMPLATES = {
        "首页": SWAN_TAB_HOME,
        "推荐": SWAN_TAB_HOME,
        "平台": SWAN_TAB_PLATFORM,
        "设备": SWAN_TAB_DEVICE,
        "我的": SWAN_TAB_ME,
    }

    # 顶 Tab 行 region（720x1600 口径）：顶 Tab 行 y≈80-170，上界留余量。
    # ⚠️ verify-run3 实测：未选中态小图（AITab按钮 仅 35x30）会与一级页
    # 内容区元素假阳性命中——平台页 0.836@(295,1171)、我的页 0.896@(120,831)
    # （SWAN收藏行）、音乐Tab按钮平台页 0.822，三个误命中 y 全部远在本
    # region 之外。故凡以未选中态图做「在首页」判断或点击定位处一律加本
    # region（region 是截图裁剪区，find_image 原生支持并自动加回偏移，
    # 非坐标定位，同 _HISTORY_TAB_ROW_REGION 口径）。
    _TOP_TAB_ROW_REGION = (0, 60, 720, 120)

    # 首页顶 Tab 5 张未选中态图（A22，均已转正）
    _TOP_TAB_TEMPLATES = {
        "推荐": SWAN_HOME_TAB_RECOMMEND,
        "音乐": SWAN_HOME_TAB_MUSIC,
        "AI": SWAN_HOME_TAB_AI,
        "可视音箱": SWAN_HOME_TAB_VISION,
        "电台": SWAN_HOME_TAB_RADIO,
    }

    # 顶 Tab 选中态锚点（verify R2 换锚：切换后统一断言「该 Tab 处于选中
    # 态」，不再依赖各 Tab 内容布局——新构建音乐 Tab 改歌单流后原「音乐
    # 搜索条」内容锚点已失效，且内容锚点各页一个样、选中态高亮图跨机更
    # 稳健。5 张选中态图为草稿，verify 转正后 image_name_mapping 登记处
    # 改正式路径）
    _TOP_TAB_ANCHORS = {
        "推荐": SWAN_HOME_TAB_RECOMMEND_SEL,
        "音乐": SWAN_HOME_TAB_MUSIC_SEL,
        "AI": SWAN_HOME_TAB_AI_SEL,
        "可视音箱": SWAN_HOME_TAB_VISION_SEL,
        "电台": SWAN_HOME_TAB_RADIO_SEL,
    }

    def _home_anchor_visible(self, timeout: float = 1.0) -> bool:
        """首页容器判据：任一顶 Tab 未选中态图可见（region 限定顶 Tab 行）。

        首页 5 个顶 Tab 至多 1 个处于选中态，任一张未选中态图可见即在
        首页容器（与 tests/flutter/swan_regression_common.py 的
        _ensure_logged_in_on_home 同口径，不依赖当前激活的是哪个顶 Tab）。
        ⚠️ 必须 region 限定 _TOP_TAB_ROW_REGION：未选中态小图在平台/我的页
        内容区有假阳性命中（verify-run3 实测 AITab按钮 0.836@(295,1171) /
        0.896@(120,831)），全屏匹配会让 go_bottom_tab「已在首页」假短路、
        go_top_tab 跳过纠偏、AI 模板误点进收藏页。
        """
        for template in self._TOP_TAB_TEMPLATES.values():
            if self.find_image(template, timeout=timeout,
                               region=self._TOP_TAB_ROW_REGION) is not None:
                return True
        return False

    def _tab_shell_anchor_visible(self, timeout: float = 1.0) -> bool:
        """全局 tab 壳（首页/平台/设备/我的 4 个一级页）判据。

        push 页（歌单详情/播放历史/搜索/选择歌单等）无底部 4 tab，本判据
        用于 back_to_tab_shell 里 press_back 前的防误退（首页按返回会退出 App）。
        """
        if self._home_anchor_visible(timeout=timeout):
            return True
        for template in (SWAN_PLATFORM_NETEASE_ROW, SWAN_DEVICE_ADD_BTN,
                         SWAN_ME_FAVORITES_ROW):
            if self.find_image(template, timeout=timeout) is not None:
                return True
        return False

    def _page_anchor_visible(self, name: str, timeout: float = 2.0) -> bool:
        """底部导航目标一级页的到位判据（go_bottom_tab 用，均不含计数字段）。"""
        if name == "首页":
            return self._home_anchor_visible(timeout=timeout)
        if name == "平台":
            if self.find_image(SWAN_PLATFORM_NETEASE_ROW, timeout=timeout) is not None:
                return True
            # ⚠️ 网易云行模板含「未授权」文案（映射文件已注），授权后该行
            # 文案变化，退化用右上角「消费明细」OCR 作次选锚点
            return self.find_text_by_ocr("消费明细", timeout=int(timeout)) is not None
        if name == "设备":
            return self.find_image(SWAN_DEVICE_ADD_BTN, timeout=timeout) is not None
        if name == "我的":
            return self.find_image(SWAN_ME_FAVORITES_ROW, timeout=timeout) is not None
        return False

    def go_bottom_tab(self, name: str, timeout: float = 15.0) -> None:
        """底部导航切换（A21，回归用例29）。name ∈ 首页(推荐)/平台/设备/我的。

        底部 4 图标 [图]（未选中态草稿模板）定位点击；目标页一级锚点已
        可见时短路返回（此时目标图标处于选中态，未选中态模板不匹配）。
        收尾断言：目标页锚点轮询至 timeout。
        须在全局 tab 壳页调用；push 页先 back_to_tab_shell。
        """
        template = self._BOTTOM_TAB_TEMPLATES.get(name)
        if template is None:
            raise ValueError(
                f"底部导航仅支持 {sorted(set(self._BOTTOM_TAB_TEMPLATES))}，收到 {name!r}")
        if self._page_anchor_visible(name):
            logger.info("go_bottom_tab: 已在%s页，短路返回", name)
            return
        self.click_image(template, timeout=10)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._page_anchor_visible(name, timeout=2):
                return
            self.sleep(0.5)
        assert False, f"点击底部导航「{name}」后 {timeout}s 内未检测到目标页锚点"

    def go_top_tab(self, name: str, timeout: float = 15.0) -> None:
        """首页顶 Tab 切换（A22，回归用例30）。name ∈ 推荐/音乐/AI/可视音箱/电台。

        顶 Tab 行只在首页容器渲染：不在首页时先经底部导航 [图] 回首页
        （顶 Tab 持久化陷阱，见域4 段注）。顶 Tab 用未选中态已转正图定位；
        目标 Tab 的未选中态图不可见即视为已停在该 Tab（选中态图标不匹配
        未选中态模板，同 tests/flutter/swan_regression_common.py
        _stay_on_recommend_tab 的判定口径）。
        到位断言：目标 Tab 选中态图 [图]（verify R2 换锚，五 Tab 同一口径，
        不依赖各 Tab 内容布局，见 _TOP_TAB_ANCHORS 注）。
        """
        template = self._TOP_TAB_TEMPLATES.get(name)
        if template is None:
            raise ValueError(
                f"顶 Tab 仅支持 {sorted(self._TOP_TAB_TEMPLATES)}，收到 {name!r}")
        if not self._home_anchor_visible():
            self.go_bottom_tab("首页")
        # 点击查找同样 region 限定顶 Tab 行：未选中态小图在内容区有假阳性
        # （verify-run3 实测 AITab按钮 我的页 0.896@(120,831)，全屏匹配会把
        # 点击落到「我的」页收藏行上误进收藏页）
        if self.find_image(template, timeout=2,
                           region=self._TOP_TAB_ROW_REGION) is not None:
            self.click_image(template, timeout=5)
        else:
            logger.info("go_top_tab: 顶 Tab「%s」未选中态图不可见，视为已停在该 Tab", name)
        self.image_exists(self._TOP_TAB_ANCHORS[name], timeout=timeout)

    def open_home_card(self, name: str, timeout: float = 15.0) -> None:
        """首页推荐 Tab 卡片进入（A23，回归用例31）。

        卡片内容动态且推荐 Tab 有完整/紧凑两种服务端布局轮换（知识库
        swan_首页），卡片定位一律 OCR 文案；「歌单」卡在紧凑布局下不存在，
        未找到时下拉刷新重试（_click_ocr_until_found）。支持卡片与到位断言：
          我喜欢 -> 我喜欢页（OCR 副标题「宝藏音乐，随心收藏」，本页特有判据）
          歌单 -> 歌单页（OCR 脚注「已加载全部」）
          最近播放/已播歌曲/已播歌手/已播专辑 -> 播放历史页（顶栏 [图]）
        AI 卡与个性化推荐卡落的页 KB 未探索（2026-09-11 R3 记录），不支持
        （传入即报错），待 explorer 补充后扩展。
        """
        self.go_top_tab("推荐")
        if name in ("最近播放", "已播歌曲", "已播歌手", "已播专辑"):
            self._click_ocr_until_found("已播歌曲" if name == "最近播放" else name,
                                        scroll="up")
            self.image_exists(SWAN_HISTORY_TOPBAR, timeout=timeout)
            return
        if name == "我喜欢":
            self._click_ocr_until_found("我喜欢", scroll="down")
            self.text_exists("宝藏音乐，随心收藏", timeout=timeout)
            return
        if name == "歌单":
            self._click_ocr_until_found("歌单", scroll="down")
            self.text_exists("已加载全部", timeout=timeout)
            return
        raise ValueError(
            "首页卡片仅支持 我喜欢/歌单/最近播放(已播歌曲/已播歌手/已播专辑)，"
            f"收到 {name!r}（AI/个性化推荐卡落的页 KB 未探索，暂不支持）")

    def _click_ocr_until_found(self, text: str, scroll: str = "up",
                               attempts: int = 3) -> None:
        """OCR 找文案点击；找不到按 scroll 方向滚一屏后重试（列表折叠/布局轮换）。

        「歌单」卡紧凑布局缺失靠下拉刷新触发轮换（知识库：下拉刷新不保证
        切换，重试仍失败则报错）；「已播歌曲」卡在最近播放区，可能被底部
        播放条遮挡下半部或位于折叠下方，需上滑露出（知识库 swan_播放历史页）。
        """
        for attempt in range(attempts):
            pos = self.find_text_by_ocr(text, timeout=3)
            if pos is not None:
                self.tap(pos[0], pos[1])
                return
            if scroll == "up":
                self.swipe_up()
            else:
                self.swipe_down()
        assert False, f"首页未找到「{text}」卡片（已滚动重试 {attempts} 次）"

    # =================================================================
    # 域 7：歌单、收藏与历史（回归用例 41-68，方案 A29-A32）
    #
    # 用例44-55（歌曲收藏）依赖「选择歌单」页（/player/select-playlist），
    # 该页 KB 无 UI 记录（入口未知，2026-09-11 R3 归因修正），按方案 §2.3
    # 定位指引实现，页标题文案/成功 toast 均为待真机校准假设（遗留）。
    # 按任务约束，含"0首歌"计数的 SWAN_FAVORITE_PLAY_ALL / SWAN_PD_PLAY_ALL
    # 两张模板不用于本域新方法的关键断言，到位判据一律用 OCR 文本或不含
    # 计数的已转正图（更多按钮/历史页顶栏）。
    # =================================================================

    # 平台代码 -> 歌单页/选择歌单页平台筛选文案（A29/A30 共用）
    _PLATFORM_TAB_TEXT = {
        "swan": "SWAN",
        "qq": "QQ音乐",
        "netease": "网易云音乐",
        "kugou": "酷狗音乐",
    }

    # 播放历史页布局区（720x1600 口径，知识库 bounds y≈204-276/贴底播放条
    # y≈1470，待真机校准；region 仅收窄 OCR/点击范围，非坐标定位）
    _HISTORY_TAB_ROW_REGION = (0, 180, 720, 140)     # 分类 Tab 行
    _HISTORY_CONTENT_REGION = (0, 330, 720, 1130)    # 内容区（下界避开贴底播放条）
    # 搜索结果页布局区（720x1600 口径，Tab 行 y≈218-288，待真机校准）
    _RESULTS_TAB_ROW_REGION = (0, 190, 720, 130)
    _RESULTS_CONTENT_REGION = (0, 330, 720, 1120)

    # 方案口径 kind -> 页内 Tab 文案（知识库 swan_播放历史页：六 Tab 为
    # 歌曲/艺人/专辑/歌单/电台/播客）
    _HISTORY_TAB_ALIASES = {
        "歌曲": "歌曲",
        "艺人": "艺人",
        "歌手": "艺人",
        "专辑": "专辑",
        "歌单": "歌单",
        "电台": "电台",
        "播客": "播客",
        "博客": "播客",
    }

    def open_playlist_detail(self, platform: str, playlist: str = "") -> None:
        """进入歌单详情页（A29/A30 用例前置）。

        路由：首页歌单卡 -> 歌单页 -> 按 platform 切筛选 Tab -> 歌单行。
        已在歌单详情页（更多按钮 [图] 可见，区别于同布局无更多按钮的
        收藏分组详情页/我喜欢页，知识库双路径对比实测）时短路。
        playlist 给定时按歌单名 OCR 点行；缺省点最上方歌单行（含「首歌」
        计数的行按 cy 取最小）。swan 平台无行时点「聚合」chip 重扫
        （SWAN Tab 有 创建/聚合 两个筛选 chip，聚合才是收藏歌单）。
        ⚠️ 第三方平台 Tab 需账号已授权（方案 §5⑤），未授权为授权空态
        （「授权已过期/去授权」，⛔ 去授权按钮禁止点击）。
        """
        platform_text = self._require_platform_text(platform)
        if self.find_image(SWAN_PD_MORE_BTN, timeout=2) is not None:
            return
        self.open_home_card("歌单")
        if platform_text != "SWAN":
            self.click_text(platform_text, timeout=10)   # 平台筛选 Tab 切换
        row = self._find_playlist_row(playlist)
        if row is None and platform == "swan" and not playlist:
            if self.find_text_by_ocr("聚合", timeout=3) is not None:
                self.click_text("聚合", timeout=5)
                row = self._find_playlist_row()
        assert row is not None, (
            f"歌单页 {platform_text} 筛选下未找到歌单行"
            + (f"「{playlist}」" if playlist else "")
            + "（账号可能无该平台歌单或未授权，见知识库授权空态）")
        self.tap(row["cx"], row["cy"])
        self.image_exists(SWAN_PD_MORE_BTN, timeout=15)  # 歌单详情页到位

    def _require_platform_text(self, platform: str) -> str:
        """平台代码 -> 页面筛选文案，非法值直接报错。"""
        text = self._PLATFORM_TAB_TEXT.get(platform)
        if text is None:
            raise ValueError(
                f"platform 仅支持 {sorted(self._PLATFORM_TAB_TEXT)}，收到 {platform!r}")
        return text

    def _find_playlist_row(self, playlist: str = "") -> dict | None:
        """OCR 找歌单行：指定歌单名时包含匹配；否则取含「首歌」计数的最上方
        一行（行格式「歌单名 N首歌」，OCR 可能拆开返回，点计数文案同样命中
        行热区）。"""
        items = self.ocr_scan_page()
        if playlist:
            return next((i for i in items if playlist in i["text"]), None)
        rows = [i for i in items if "首歌" in i["text"]]
        return min(rows, key=lambda i: i["cy"]) if rows else None

    def favorite_playlist(self, platform: str, state: str = "on",
                          timeout: float = 10.0) -> None:
        """歌单收藏/取消收藏（A29，回归用例41-43）。

        前置路由复用 open_playlist_detail（已在歌单详情页时短路）。收藏
        图标两态 [图]（域7 新截草稿）：state="on"/"off" 把图标置到目标态
        （已在目标态则不点）；"toggle" 翻转当前态。收尾断言目标态图标 [图]。
        ⚠️ 收藏结果持久化在账号收藏数据：用例层回滚用连续两次
        state="toggle"（无论初始态如何，两次翻转后回到原态）。
        """
        assert state in ("on", "off", "toggle"), "state 仅支持 on / off / toggle"
        self.open_playlist_detail(platform)
        current = self._playlist_fav_state()
        assert current is not None, (
            "歌单详情页未识别收藏图标态（两态模板均未匹配，请核对截图质量或页面改版）")
        target = state if state in ("on", "off") else ("off" if current == "on" else "on")
        if current != target:
            self.click_image(SWAN_PD_FAV_ON if current == "on" else SWAN_PD_FAV_OFF,
                             timeout=5)
        self.image_exists(SWAN_PD_FAV_ON if target == "on" else SWAN_PD_FAV_OFF,
                          timeout=timeout)

    def _playlist_fav_state(self) -> str | None:
        """歌单详情页收藏图标当前态：on / off / None（两态模板都未匹配）。"""
        if self.find_image(SWAN_PD_FAV_ON, timeout=2) is not None:
            return "on"
        if self.find_image(SWAN_PD_FAV_OFF, timeout=2) is not None:
            return "off"
        return None

    def collect_song(self, target_platform: str, playlist: str,
                     source: str = "player") -> None:
        """收藏歌曲到指定歌单（A30，回归用例44-55，12条合1）。

        source="player"：全屏播放页点歌曲收藏图标 [图]（调用方须已在播放页
        且有播放任务，域3 start_play 发起）；source="playlist_page"：歌单
        详情页歌曲行收藏图标 [图]（调用方须已在含歌曲的歌单详情页）。
        两路均进入「选择歌单」页完成目标选择：
          1. 断言页标题 OCR「选择歌单」（⚠️ KB 无该页 UI 记录，文案待真机校准）
          2. 页内若出现平台筛选文案则点选（该页是否带平台 Tab 待校准，
             找不到不阻塞，直接按歌单名点选）
          3. OCR 点目标歌单名；紧随其后若捕获「收藏成功」toast 记录日志
             （wait_toast 辅助证据，文案待校准故不作断言）
        收尾断言回到来源页：播放页收起钮 [图] / 歌单详情页更多按钮 [图]。
        ⚠️ 收藏结果无自动化回滚（删歌曲入口未探索），目标歌单建议用 rig
        测试账号聚合歌单（如「我的音乐」），数据污染由设备管理流程定期重置。
        """
        assert source in ("player", "playlist_page"), "source 仅支持 player / playlist_page"
        platform_text = self._require_platform_text(target_platform)
        if source == "player":
            self.click_image(SWAN_PLAYER_FAV_BTN, timeout=10)
            back_anchor = SWAN_PLAYER_DISMISS_BTN
        else:
            self.click_image(SWAN_PD_ROW_FAV_BTN, timeout=10)
            back_anchor = SWAN_PD_MORE_BTN
        self.text_exists("选择歌单", timeout=10)
        tab_pos = self.find_text_by_ocr(platform_text, timeout=3)
        if tab_pos is not None:
            self.tap(tab_pos[0], tab_pos[1])
        self.click_text(playlist, timeout=10)
        if self.wait_toast("收藏成功", timeout=3):
            logger.info("collect_song: 「收藏成功」toast 已捕获（辅助证据，不作断言）")
        self.image_exists(back_anchor, timeout=10)

    def assert_recent_played(self, kind: str, name: str, timeout: float = 10.0) -> None:
        """最近播放断言（A31，回归用例56-68，13条合1）。

        进入播放历史页（幂等，见 _open_recent_played）-> 切分类 Tab（歌曲
        为默认选中 Tab，其余按 kind 在 Tab 行 region 内 OCR 点击）-> 内容区
        OCR 断言条目 name（最多下滑 2 次重试）。kind 支持方案口径
        「歌手/博客」，页内 Tab 文案为 艺人/播客，此处归一（另支持 专辑）。
        ⚠️ KB 已知口径差异：首页「已播歌曲 N首」计数与历史页列表可能不一致
        （探索期实测卡片 1 首/页内空态），历史数据断言待 rig 有播放记录后校准。
        """
        tab = self._HISTORY_TAB_ALIASES.get(kind)
        if tab is None:
            raise ValueError(
                f"kind 仅支持 {sorted(set(self._HISTORY_TAB_ALIASES))}，收到 {kind!r}")
        self._open_recent_played()
        if tab != "歌曲":
            self.click_text(tab, timeout=10, region=self._HISTORY_TAB_ROW_REGION)
        self._assert_text_in_region(
            name, self._HISTORY_CONTENT_REGION, timeout,
            what=f"最近播放「{tab}」分类")

    def _open_recent_played(self) -> None:
        """进入播放历史页（幂等）：已在则返回；否则回 tab 壳 -> 推荐 Tab ->
        「已播歌曲」卡（可能被底部播放条遮挡或位于折叠下方，上滑重试）->
        顶栏 [图] 到位断言。"""
        if self.find_image(SWAN_HISTORY_TOPBAR, timeout=2) is not None:
            return
        self.back_to_tab_shell()
        self.go_top_tab("推荐")
        self._click_ocr_until_found("已播歌曲", scroll="up")
        self.image_exists(SWAN_HISTORY_TOPBAR, timeout=15)

    def back_to_tab_shell(self, max_backs: int = 3) -> None:
        """从任意 push 页回到全局 tab 壳（一级页）：收播放页 -> 按需 press_back。

        每次 press_back 前先用一级页锚点 [图] 确认不在 tab 壳（首页按返回
        会退出 App）；供域7/域8 用例与清理流程从深层页面退出，已在 tab 壳
        时零操作。
        """
        if self.find_image(SWAN_PLAYER_DISMISS_BTN, timeout=2) is not None:
            self.click_image(SWAN_PLAYER_DISMISS_BTN, timeout=5)
        for _ in range(max_backs):
            if self._tab_shell_anchor_visible():
                return
            self.press_back()
        assert self._tab_shell_anchor_visible(), (
            f"退出 push 页失败：press_back {max_backs} 次后仍未到全局 tab 壳")

    # =================================================================
    # 域 8：搜索（回归用例 69-72，方案 A33-A34）
    #
    # 搜索输入页/结果页均为全屏独立路由（无 bottom_player、无全局 4 tab），
    # 返回走 press_back 或 SWAN_SEARCH_BACK [图]。关键词仅英文可达
    # （adb 输入限制，中文待 IME 方案，属框架层待用户决策）。
    # =================================================================

    # 搜索入口 -> 搜索条图（均已转正；功能地图 8 处入口中仅推荐/电台两处
    # 真机验证过，平台域入口待 explorer 验证后扩展。home 条 PNG 文件名
    # 沿用历史「音乐Tab_搜索条」，物理内容已同名重截为推荐 Tab 搜索条，
    # 见 image_name_mapping.py 注）
    _SEARCH_ENTRY_BARS = {
        "home": SWAN_HOME_MUSIC_SEARCH_BAR,    # 首页推荐 Tab「跨平台搜索音乐」
        "radio": SWAN_HOME_RADIO_SEARCH_BAR,   # 电台 Tab「搜索电台」
    }

    def search(self, keyword: str, entry: str = "home", timeout: float = 15.0) -> None:
        """全域搜索（A33，回归用例69-72前半）。

        entry="home"/"radio" 对应推荐/电台 Tab 搜索条（已验证的两处入口）。
        新构建（verify R2 拍板口径）：音乐 Tab 已改为歌单流、搜索条回归
        首页默认推荐 Tab，entry="home" 跟随 App 现状切推荐 Tab 后点搜索条
        （非语义变更；原「go_top_tab("音乐") + 音乐 Tab 搜索条」链路废弃）。
        ⚠️ home 分支进推荐 Tab 后先回滚到顶再找搜索条：推荐 Tab 滚动位置
        跨操作持久化（verify-run3 实测 open_home_card 等下滚后推荐 Tab 停在
        下滚位，搜索条滚出屏幕，图锚与 OCR hint 都不可见）。
        推荐 Tab 有完整/紧凑两种服务端布局轮换（知识库 swan_首页），紧凑
        布局下搜索条图可能不可见，此时用 OCR hint「跨平台搜索音乐」兜底
        定位。
        流程：顶 Tab 切换 -> 搜索条进搜索输入页 -> OCR hint
        「搜索歌曲或艺术家等」定位输入框并点击聚焦 -> adb 输入关键词 ->
        搜索按钮 [图] 提交（用图不用 OCR 顶栏「搜索」，规避与自定义 T9
        键盘「搜索」键同名歧义，见知识库搜索 flow 风险注）。
        收尾断言：结果页六分类 Tab 行（region 限定 OCR「单曲」）+ 关键词
        回填输入框（OCR）。
        """
        bar = self._SEARCH_ENTRY_BARS.get(entry)
        if bar is None:
            raise ValueError(
                f"搜索入口仅支持 {sorted(self._SEARCH_ENTRY_BARS)}"
                f"（平台域入口 KB 未验证，暂不支持），收到 {entry!r}")
        if entry == "home":
            self.go_top_tab("推荐")   # 新构建：搜索条在推荐 Tab，音乐 Tab 已改歌单流
            # 先回滚到顶：推荐 Tab 滚动位置跨操作持久化（verify-run3 实测：
            # open_home_card 等下滚操作后推荐 Tab 停在下滚位，搜索条滚出
            # 屏幕，图锚与 OCR hint「跨平台搜索音乐」均不可见）。先探测
            # 可见性、不可见才 swipe_down 回滚——已回顶时盲滑会触发下拉
            # 刷新（下拉刷新引发完整/紧凑布局轮换，见 _click_ocr_until_found 注）。
            for _ in range(4):
                if (self.find_image(bar, timeout=1) is not None
                        or self.find_text_by_ocr("跨平台搜索音乐",
                                                 timeout=1) is not None):
                    break
                self.swipe_down()
            if self.find_image(bar, timeout=3) is not None:
                self.click_image(bar, timeout=10)
            else:
                # 紧凑布局轮换下搜索条图不可见：OCR hint 文案兜底定位
                self.click_text("跨平台搜索音乐", timeout=10)
        else:
            self.go_top_tab("电台")
            self.click_image(bar, timeout=10)
        self.text_exists("搜索歌曲或艺术家等", timeout=timeout)   # 搜索输入页生效
        self.click_text("搜索歌曲或艺术家等", timeout=5)          # 点击输入框聚焦
        self.input_text(keyword)
        self.text_exists(keyword, timeout=5)                      # 框内出现关键词
        self.click_image(SWAN_SEARCH_SUBMIT, timeout=10)          # 提交搜索
        self.text_exists("单曲", timeout=timeout,
                         region=self._RESULTS_TAB_ROW_REGION)     # 结果页 Tab 行渲染
        self.text_exists(keyword, timeout=5)                      # 关键词回填

    def assert_search_results(self, tab: str, platforms=None,
                              timeout: float = 10.0) -> None:
        """搜索结果分类断言（A34，回归用例69-72后半）。

        须在搜索结果页调用（search() 收尾即停在此页）。tab ∈ 单曲/艺人/
        专辑/歌单/电台/播客（方案口径「博客」归一为页内文案「播客」），
        Tab 行 region 限定点击，原地切换内容区。platforms 为空/None ->
        断言空态（未授权账号稳定态：SWAN_SEARCH_EMPTY [图]，缺失时退化
        OCR「没有找到相关结果」）；platforms 非空 -> 逐个断言平台名出现在
        结果区（已授权账号；结果行内平台标注文案待真机校准）。
        """
        tab_text = {"博客": "播客"}.get(tab, tab)
        if tab_text not in ("单曲", "艺人", "专辑", "歌单", "电台", "播客"):
            raise ValueError(
                f"tab 仅支持 单曲/艺人/专辑/歌单/电台/播客(博客)，收到 {tab!r}")
        self.click_text(tab_text, timeout=timeout, region=self._RESULTS_TAB_ROW_REGION)
        if not platforms:
            if self.find_image(SWAN_SEARCH_EMPTY, timeout=timeout) is None:
                self.text_exists("没有找到相关结果", timeout=5)
            return
        for platform in platforms:
            self._assert_text_in_region(
                platform, self._RESULTS_CONTENT_REGION, timeout,
                what=f"搜索「{tab_text}」结果区")

    def _assert_text_in_region(self, text: str, region, timeout: float,
                               what: str, scrolls: int = 2) -> None:
        """region 内 OCR 断言文本，未命中时上滑整屏重试（列表折叠下方条目）。"""
        for attempt in range(scrolls + 1):
            if self.find_text_by_ocr(text, timeout=int(timeout), region=region) is not None:
                return
            if attempt < scrolls:
                self.swipe_up()
        assert False, f"{what}未找到 {text!r}（已上滑重试 {scrolls} 次）"
