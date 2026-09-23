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
    SWAN_DEVICE_CARD_SELECTED,
    SWAN_DEVICE_SHEET_CHECKED,
    SWAN_DEVICE_SHEET_TITLE,
    SWAN_FAVORITE_PLAY_ALL,
    SWAN_PD_PLAY_ALL,
    SWAN_PLAYER_DEVICE_BTN,
    SWAN_PLAYER_DISMISS_BTN,
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

    _TIME_RE = re.compile(r"(\d{1,2}):(\d{2})")

    def select_device(self, name: str, via: str = "card") -> None:
        """切换输出设备（A12，回归用例 11-12）。

        via="card"：设备页 OCR 定位目标设备名所在卡片，点卡片状态行
        （「连接良好」行）。⚠️ 不点设备名本身——知识库实测设备名节点是
        设置入口（wifi_device_settings_<UUID>），内含删除设备风险。
        收尾断言卡片选中态 [图]。

        via="player"：播放页右上角设备切换钮 [图] 开弹层 → 断言弹层标题
        [图] → OCR 点目标设备行 → 断言行勾选态 [图]；若弹层随选择自动
        关闭，退化为断言已回播放页且页顶输出设备名 OCR 出现目标名。

        ⚠️ 选择会真实下发到 rig 音箱（方案 §5② 回归须真点真音箱），
        且跨用例不自动回切。
        """
        assert via in ("card", "player"), "via 仅支持 card / player"
        if via == "card":
            items = self.ocr_scan_page()
            name_item = next((i for i in items if name in i["text"]), None)
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
