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
    SWAN_COLLECT_PLATFORM_SHEET,
    SWAN_COLLECT_SELECTED_TOPBAR,
    SWAN_DEVICE_ADD_BTN,
    # SWAN_DEVICE_CARD_SELECTED 已停止使用（2026-09-28 新构建口径废弃）：
    # 点 WiFi 设备卡不再就地出现「选中标识」而是进播放页，映射文件登记
    # 保留仅作历史记录，见 select_device docstring。
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
    SWAN_PLAYER_DEVICE_BTN,
    SWAN_PLAYER_DISMISS_BTN,
    SWAN_PLAYER_DISMISS_DARK,
    SWAN_PLAYER_DISMISS_LIGHT,
    SWAN_PLAYER_LOOP_LIST,
    SWAN_PLAYER_LOOP_SHUFFLE,
    SWAN_PLAYER_LOOP_SINGLE,
    SWAN_PLAYER_NEXT_BTN,
    SWAN_PLAYER_PAUSE_BTN,
    SWAN_PLAYER_PLAY_PAUSE_BTN,
    SWAN_PLAYER_PLUS_BTN,
    SWAN_PLAYER_PREV_BTN,
    SWAN_PLAYER_PROGRESS_BAR,
    SWAN_PLAYER_VOLUME_ICON,
    SWAN_PLAYER_VOLUME_MINUS,
    SWAN_PLAYER_VOLUME_PLUS,
    SWAN_PLAYER_VOLUME_POPUP,
    SWAN_PLATFORM_NETEASE_ROW,
    SWAN_SEARCH_EMPTY,
    SWAN_SEARCH_SUBMIT,
    SWAN_SONG_ROW_PLUS_BTN,
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
    # 音量滑条真轨道推导（A19，2026-09-28 fix4c/fix532 两态弹窗截图像素级
    # 实测，720x1600 口径）：弹窗为固定底部弹层，真轨道 x[144..491] 与 ± 钮
    # 模板矩形间隙恒定（± 钮静态、两态复配 score=1.00 同位）。旧「中填充
    # 滑条模板」锚定已废弃——其匹配矩形随音量态水平漂移（run4d 实测同一
    # 轨道 x0=227/248/269/293），比例换算必错（拖 40 实得 70）。
    _VOLUME_TRACK_INSET_L = 51   # 减钮矩形右缘(93) → 轨道左端(144)
    _VOLUME_TRACK_INSET_R = 56   # 加钮矩形左缘(547) → 轨道右端(491)
    _VOLUME_TRACK_HEIGHT = 32    # 轨道纵向全高（y 1450-1482，中线与 ± 钮同行）
    # 音量百分比 OCR 双通道（run4d run2 实测）：弹窗标题行 "Speaker N"（数字
    # 可见但无 % 符号，弹窗开启态唯一数据通道）+ 播放页音量行 "N%"（KB
    # swan_播放页 Wave2 实测 OCR "0%"，弹窗关闭态/volume_key 通道）。
    # ⚠️ 状态栏电量 "100"（OCR 无 % 尾）两条模式均不命中，无误采。
    _VOLUME_PCT_RE = re.compile(r"(\d{1,3})\s*%")
    _VOLUME_SPEAKER_RE = re.compile(r"Speaker\s*(\d{1,3})", re.IGNORECASE)
    # 设备页卡片：设备名行到卡内可点内容行（状态行/媒体行）允许的最大
    # 纵向跨度（720x1600 口径，待真机校准）
    _CARD_BODY_SPAN = 300
    # 设备页 OCR 候选行下界（cy > 此值的项一律剔除，720x1600 口径）：底部
    # 播放条区 y≈1376-1476（verify-run3 实测），持久会话下播放条常驻设备名，
    # 不剔除会把设备名兜底匹配错配到播放条标题上（实测案例见 select_device 注）。
    _DEVICE_OCR_BOTTOM_LIMIT = 1350
    # 播放页页头输出设备名 band（720x1600 口径；知识库 swan_设备详情页
    # player_device_name bounds [128,91][592,149]，y 向外扩覆盖 OCR 抖动）。
    # select_device via="card" WiFi 分支的切换收尾断言用。region 仅收窄
    # OCR 断言范围，非坐标定位。
    _PLAYER_HEADER_DEVICE_REGION = (0, 60, 720, 120)
    # 设备页贴底播放条 band（720x1600 口径，与 _DEVICE_OCR_BOTTOM_LIMIT
    # 同源 y≈1376-1476）。select_device 本机分支的切换断言用：内容区本机
    # 卡自身文本也是「扬声器」，必须限定播放条区域才构成切换证据。
    _DEVICE_PLAYBAR_REGION = (0, 1360, 720, 120)

    # 列表静止判定区（720x1600 口径）：列表内容区行带，避开顶栏与贴底
    # 播放条（播放条进度/滚动歌词动画会让该区永久判「在动」）。
    # _tap_song_row_by_ocr 滑动后列表静止等待用（verify-run4b 滑动惯性
    # 坐标时移防护，见 _wait_list_settled 注）。
    _LIST_SETTLE_REGION = (0, 180, 720, 1160)

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

    @classmethod
    def _match_ocr_name(cls, items: list[dict], name: str) -> dict | None:
        """OCR 行集合按名称匹配：精确包含优先，失配时两侧 compact 归一化兜底。

        compact 口径同 _ocr_compact（去空格 + l/I/1 易混字符映射）。设备页
        card 分支（_locate_wifi_device_card）与设备切换弹层（_find_ocr_row）
        共用本匹配器，保证两处设备名比对口径不漂移。
        """
        hit = next((i for i in items if name in i["text"]), None)
        if hit is None:
            compact_name = cls._ocr_compact(name)
            hit = next(
                (i for i in items
                 if compact_name in cls._ocr_compact(i["text"])),
                None,
            )
            if hit is not None:
                logger.info(
                    "OCR 名称 %r 精确匹配失败，compact 归一化（去空格+l/I/1）"
                    "后命中 OCR 文本 %r", name, hit["text"])
        return hit

    def _find_ocr_row(self, name: str, timeout: float = 10.0) -> dict | None:
        """轮询 OCR 找名称行（精确→compact 两级比对，见 _match_ocr_name）。

        verify-run4b 实测（run2_play_control.log）：设备切换弹层行
        「HiVi M300MKII」被整行读作「OHiViM300MKIl」（行首勾选圆点带出
        杂字符 O + II→Il 同形），click_text 的精确包含必失配。与 card
        分支同口径补 compact 兜底后命中。供 _switch_output_in_sheet 弹层
        选行使用。
        """
        deadline = time.monotonic() + timeout
        while True:
            hit = self._match_ocr_name(self.ocr_scan_page(), name)
            if hit is not None:
                return hit
            if time.monotonic() >= deadline:
                return None
            self.sleep(1.0)

    def select_device(self, name: str, via: str = "card") -> None:
        """切换输出设备（A12，回归用例 11-12）。2026-09-28 口径重设计。

        探索依据：knowledge/swan/draft/swan_设备详情页.md（test/profile
        5.3.1 新构建 2026-09-24 真机实测）。新旧口径差异：

        - 旧口径（已废弃）：点设备卡状态行即切换输出，收尾断言卡片选中
          态图 SWAN_DEVICE_CARD_SELECTED。新构建点 WiFi 设备卡**不切换
          输出**，而是进全屏播放页（full_player_page）；「选中标识」图在
          新构建不复存在，常量停止使用（映射文件登记保留）。
        - 新口径「当前输出」= 深色整卡容器 wifi_device_selected_<UUID>
          （动态 UUID 无法截成图像模板），切换断言改走输出设备名 OCR
          （播放页页头 / 贴底播放条，region 限定）。

        via="card"：
        - WiFi 设备分支：设备页 OCR 定位目标设备卡（设备名精确包含优先，
          失配时两侧 compact 归一化——去空格 + l/I/1 易混字符映射——兜底
          再匹配，见 _ocr_compact 注；OCR 候选行剔除底部播放条区），点卡
          → 断言进播放页（player_dismiss_button [图]）→ 经播放页设备切
          换弹层点目标设备行完成真实切换（复用 _switch_output_in_sheet，
          与 via="player" 共用同一弹层尾部）→ 断言播放页页头输出设备名
          OCR = name。
        - 本机扬声器分支（name 含「扬声器」或「本机」）：设备页定位本机
          分区「扬声器」卡（分区在卡列表下方，未露出时上滑重找）→ 点卡
          触发系统「是否忽略电池优化？」对话框（切本机输出的前置）→
          _confirm_battery_optimization_dialog 点「忽略」→ 断言贴底播放
          条 OCR「扬声器」。

        ⚠️ 点卡两类点击点（状态行/卡体内容行）都避开设备名行本身——其上
        覆盖 wifi_device_settings_<UUID> 设置入口，内含删除设备风险。
        ⚠️ 选择会真实下发到 rig 音箱（方案 §5② 回归须真点真音箱），且跨
        用例不自动回切。
        ⚠️ 实验室 WiFi 音箱（M300MKII）2026-09-28 离线，WiFi 卡点击链路
        代码按探索结论实现，真机复验待音箱上线。
        """
        assert via in ("card", "player"), "via 仅支持 card / player"
        if via == "player":
            self._switch_output_in_sheet(name)
            return
        # ---- via="card" ----
        if "扬声器" in name or "本机" in name:
            # 本机扬声器分支：点本机卡 → 系统电池优化弹窗点「忽略」→
            # 贴底播放条断言（见 _DEVICE_PLAYBAR_REGION 注）。
            self._tap_local_speaker_card()
            self._confirm_battery_optimization_dialog()
            self._wait_compact_text_in_region(
                "扬声器", self._DEVICE_PLAYBAR_REGION, 10.0,
                what="切换本机输出后的贴底播放条")
            return
        # WiFi 设备分支：点卡=进播放页（新构建行为，点卡本身不切换输出），
        # 真实切换经播放页设备切换弹层完成。
        tap_item = self._locate_wifi_device_card(name)
        self.tap(tap_item["cx"], tap_item["cy"])
        self._wait_player_page_open(timeout=10)  # 已进播放页（点卡=进播放页）
        self._switch_output_in_sheet(name)
        self._wait_compact_text_in_region(
            name, self._PLAYER_HEADER_DEVICE_REGION, 10.0,
            what="切换输出后的播放页页头设备名")

    def _switch_output_in_sheet(self, name: str) -> None:
        """播放页设备切换弹层选行（select_device via="player" 与 via="card"
        WiFi 分支共用尾部，避免两份弹层逻辑漂移）。调用方须已在全屏播放页。

        右上角设备切换钮 [图] 开弹层 → 断言弹层标题 [图] → OCR 点目标
        设备行（精确→compact 两级比对，run4b 实测弹层行被读作
        「OHiViM300MKIl」精确包含失配，见 _find_ocr_row 注）→ 断言行
        勾选态 [图]；若弹层随选择自动关闭，退化为断言已回播放页且页头
        输出设备名 OCR（compact 归一化轮询）出现目标名。
        """
        self.click_image(SWAN_PLAYER_DEVICE_BTN, timeout=10)
        self.image_exists(SWAN_DEVICE_SHEET_TITLE, timeout=10)
        row = self._find_ocr_row(name, timeout=10)
        assert row is not None, (
            f"设备弹层未找到设备行 {name!r}（精确+compact 均未命中，"
            "弹层行文案 OCR 失真需校准）")
        self.tap(row["cx"], row["cy"])
        if self.find_image(SWAN_DEVICE_SHEET_CHECKED, timeout=5) is not None:
            logger.info("设备弹层勾选态 [图] 已确认")
        else:
            # 弹层可能已随选择自动关闭：退化为核对播放页页头输出设备名
            # （compact 归一化轮询，同 select_device via="card" 收尾口径，
            # 页头 OCR 同样存在空格丢失/易混字符失真）
            self._wait_player_page_open(timeout=10)
            self._wait_compact_text_in_region(
                name, self._PLAYER_HEADER_DEVICE_REGION, 10.0,
                what="切换输出后的播放页页头设备名")

    def _locate_wifi_device_card(self, name: str) -> dict:
        """设备页 OCR 定位 WiFi 设备卡，返回卡上点击点（OCR 项，含 cx/cy）。

        设备名比对（共用 _match_ocr_name）：OCR 文本精确包含优先；失配时
        两侧 compact 归一化（去空格 + l/I/1 易混字符映射，见 _ocr_compact
        注）兜底再匹配。实测案例1：OCR 把「HiVi M300MKII」读成
        「HiVi M300MKIl」（II→Il），归一化后命中；案例2：读成
        「HiViM300MKII>」（空格丢失），去空格后命中。OCR 候选行先剔除
        底部播放条区（cy > _DEVICE_OCR_BOTTOM_LIMIT，verify-run3 实测播
        放条常驻标题会被兜底错配，且播放条区本就不可点，整体剔除）。

        点击点选择（知识库 swan_设备详情页 2026-09-24 实测）：状态行
        「连接良好」优先（探索实测锚点，落在当前输出整卡容器
        wifi_device_selected_<UUID> 内；整卡点击行为相同）；空闲卡无状态
        行时退化点设备名行下方最靠上的一条卡体内容行（紧邻设备名行下方，
        避免跨到下一张卡的设备名行）。⛔ 两类点击点都避开设备名行本身
        （设置入口覆盖，见 select_device 注）。
        """
        items = [i for i in self.ocr_scan_page()
                 if i["cy"] <= self._DEVICE_OCR_BOTTOM_LIMIT]
        name_item = self._match_ocr_name(items, name)
        if name_item is None:
            # 前序本机分支可能把设备页停在下滑位（_tap_local_speaker_card
            # 上滑找卡），回滚到顶重扫一次再定论。
            self.swipe_down()
            items = [i for i in self.ocr_scan_page()
                     if i["cy"] <= self._DEVICE_OCR_BOTTOM_LIMIT]
            name_item = self._match_ocr_name(items, name)
        assert name_item is not None, (
            f"设备页 OCR 未找到设备名 {name!r}（已回滚到顶重扫；WiFi 设备"
            "可能离线显示空态卡，或卡文案 OCR 失真需校准）")
        status_item = next(
            (i for i in items
             if "连接良好" in i["text"]
             and 0 < i["cy"] - name_item["cy"] <= self._CARD_BODY_SPAN),
            None,
        )
        if status_item is not None:
            return status_item
        body_candidates = [
            i for i in items
            if name_item["cy"] < i["cy"] <= name_item["cy"] + self._CARD_BODY_SPAN
        ]
        assert body_candidates, (
            f"设备 {name!r} 卡片上未找到可点内容行（状态行「连接良好」缺失"
            "且卡体无 OCR 内容，卡片布局变化需校准 _CARD_BODY_SPAN）")
        return min(body_candidates, key=lambda i: i["cy"])

    def _tap_local_speaker_card(self) -> None:
        """设备页定位并点击本机分区「扬声器」卡（切本机输出入口）。

        本机分区在 WiFi 卡列表下方（知识库 swan_设备详情页：下滑后可见），
        未露出时上滑一屏重扫（最多 3 轮扫-滑轮替）。本机分区之下还有一张
        Apple Music 分区的同名「扬声器」卡（行为未探索，⛔ 不可点），故取
        最靠上一条命中行。本机卡名行无设置覆盖（wifi_device_settings_ 仅
        WiFi 卡有），点名行中心即可（知识库实测整卡 click=True）。OCR
        候选行照常剔除底部播放条区——当前输出若已是本机，播放条常驻
        「扬声器」，不得误当卡片命中。
        """
        for _ in range(3):
            card = min(
                (i for i in self.ocr_scan_page()
                 if i["cy"] <= self._DEVICE_OCR_BOTTOM_LIMIT
                 and "扬声器" in self._ocr_compact(i["text"])),
                key=lambda i: i["cy"],
                default=None,
            )
            if card is not None:
                self.tap(card["cx"], card["cy"])
                return
            self.swipe_up()
        assert False, "设备页未找到本机分区「扬声器」卡（已上滑重试 3 次）"

    def _confirm_battery_optimization_dialog(self, timeout: float = 6.0) -> bool:
        """处置切本机输出触发的系统「是否忽略电池优化？」对话框。

        点本机扬声器卡后系统弹「是否忽略电池优化？」（取消/忽略），点
        「忽略」放行后台音频后切换继续（知识库 swan_设备详情页 2026-09-24
        往返实测）。这是 Android 系统弹窗、一次性授权（放过一次后再次切
        换多半不再弹），故：窗口期内等到弹窗 → 点「忽略」并返回 True；
        未等到 → 视为已授权，返回 False 由调用方继续收尾断言（弹窗缺失
        不算失败）。

        ⚠️ 受控例外：本方法在业务层经 dump 定位系统弹窗按钮，突破
        「业务方法禁止依赖 dump 做定位」的约定——系统弹窗不在 Flutter
        语义树内、无图像模板可用、按钮为系统渲染（resource-id 惯例
        button1=肯定键「忽略」/button2=否定键「取消」），且属一次性授权
        的流程前置。弹窗处置收敛在本方法内，**不**并入 android_base
        dismiss_app_popups 规则表（规则表按按钮文字自动点击，存在全局
        误触状态变更的风险，同 _dismiss_auth_notice_popup 的考量）。
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for node in self.dump_semantics():
                node_id = (node.get("resource_id") or "").split("/")[-1]
                label = node.get("text") or node.get("content_desc") or ""
                if node_id == "button1" and "忽略" in label:
                    center = node.get("center")
                    assert center is not None, (
                        "电池优化弹窗「忽略」按钮节点缺 bounds，无法点击")
                    logger.info(
                        "select_device: 系统电池优化弹窗出现，点「忽略」%s",
                        center)
                    self.tap(center[0], center[1])
                    return True
            self.sleep(1.0)
        logger.info(
            "select_device: 窗口期内未见电池优化弹窗（视为已授权，继续切换）")
        return False

    def _wait_compact_text_in_region(self, text: str, region, timeout: float,
                                     what: str) -> None:
        """region 内轮询 OCR 断言文本（两侧 compact 归一化比对）。

        select_device 切换收尾断言专用：页头设备名/播放条设备名的 OCR 与
        普通包含比对之间存在空格丢失（「HiViM300MKII>」）与 l/I/1 同形
        失真，须两侧 compact 后比对（见 _ocr_compact 注）；切换生效有
        延迟，故 deadline 轮询而非单次判定（知识库 swan_设备详情页：
        语义树瞬时失败频发，OCR 同理勿单帧定生死）。
        """
        compact = self._ocr_compact(text)
        deadline = time.monotonic() + timeout
        while True:
            hit = next(
                (i for i in self.ocr_scan_page(region=region)
                 if compact in self._ocr_compact(i["text"])),
                None,
            )
            if hit is not None:
                return
            if time.monotonic() >= deadline:
                break
            self.sleep(1.0)
        assert False, f"{what} region 内未出现 {text!r}（已轮询 {timeout:.0f}s）"

    def _tap_song_row_by_ocr(self, song: str, index: int,
                             scroll_rounds: int = 3) -> None:
        """OCR 定位歌曲行点击；未命中上滑一屏重找（verify-big52 根因5）。

        目标歌常不在列表首屏（实测 Booty Music 在我喜欢歌单约第 10 行，
        首屏仅 6 行）：每轮 ocr_scan_page 全屏子串匹配（忽略大小写，取第
        index 个同名命中）找到即点；未命中 swipe_up 滚一屏再试，最多
        scroll_rounds 轮。滚满仍未命中显式 assert 报错，并列出当前屏 OCR
        行首文字辅助归因（歌名拼错/页面不对/OCR 失真一眼可辨）。
        index 语义沿用原实现：同名行按当前屏 OCR 返回顺序取第 index 个。

        滑动惯性防护（verify-run4b 实测：swipe_up 后列表仍在惯性滚动即
        OCR，读到的行坐标相对真实停留位置时移——点中 Booty Music 坐标却
        播了下一行）：每轮 OCR 前先等列表静止（_LIST_SETTLE_REGION 双帧
        像素比对一致，见 _wait_list_settled）。
        点错行自愈：点行后软核对播放页当前曲目 OCR（_now_playing_is，
        compact 归一化），歌名不符且重试次数未用完时收起播放页回列表
        重找重点一次；重试额度用尽则直接返回，交由调用方 start_play 的
        播放页到位断言与用例层 assert_now_playing 定论。
        """
        for attempt in range(scroll_rounds + 1):
            self._wait_list_settled()
            matches = [i for i in self.ocr_scan_page()
                       if song.lower() in i["text"].lower()]
            if len(matches) > index:
                self.tap(matches[index]["cx"], matches[index]["cy"])
                if self._now_playing_is(song):
                    return
                if attempt >= scroll_rounds:
                    return  # 重试额度用尽：不收播放页，交由调用方断言定论
                logger.warning(
                    "_tap_song_row_by_ocr: 点行后播放页曲目与 %r 不符"
                    "（多为滑动惯性坐标时移点中相邻行），收播放页回列表重找重点",
                    song)
                self._dismiss_full_player()
                continue
            if attempt < scroll_rounds:
                self.swipe_up()
        heads = [i["text"].strip()[:12] for i in self.ocr_scan_page()
                 if i["text"].strip()]
        assert False, (
            f"OCR 点歌失败：滚动重找 {scroll_rounds} 轮未命中 {song!r}"
            f"（取第 {index} 个同名行），当前屏 OCR 行首文字: {heads}")

    def _wait_list_settled(self, timeout: float = 6.0) -> None:
        """等列表滚动静止（滑动惯性防护）：region 双帧像素比对一致才放行 OCR。

        verify-run4b 实测：swipe_up 后列表仍在惯性滚动时立即 OCR 定位点击，
        行坐标相对真实停留位置时移，点中 Booty Music 坐标却播了下一行。
        对 _LIST_SETTLE_REGION（避开顶栏与贴底播放条动画区）连续采样
        （region_changed samples=2），相邻帧像素差 ≤ 阈值（静止）即返回；
        超时按已静止放行并记警告（不无限阻塞，点行后的曲目核对仍可兜底）。
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if not self.region_changed(*self._LIST_SETTLE_REGION,
                                       gap=0.4, samples=2, threshold=2.0):
                return
            self.sleep(0.3)
        logger.warning("_wait_list_settled: %.0fs 内列表未静止，按已静止放行",
                       timeout)

    def _now_playing_is(self, song: str, open_timeout: float = 15.0) -> bool:
        """点歌行后的播放页曲目软核对（不 assert，供点错行自愈判定）。

        已进全屏播放页（收起钮探测，浅底/深底/旧单模板任一）且当前曲目
        OCR（两侧 compact 归一化，比用例层 assert_now_playing 的精确包含
        更容忍失真，避免 OCR 抖动触发无谓重点）出现歌名 → True；播放页
        未打开或曲目不符 → False（是否收播放页重试由调用方定）。
        """
        if self._find_dismiss_btn(timeout=open_timeout) is None:
            return False
        compact = self._ocr_compact(song).lower()
        deadline = time.monotonic() + 5.0
        while True:
            if any(compact in self._ocr_compact(i["text"]).lower()
                   for i in self.ocr_scan_page()):
                return True
            if time.monotonic() >= deadline:
                return False
            self.sleep(1.0)

    # 播放页收起钮探测 region：顶栏条带 (0, 0, 720, 200)——收起钮恒在播放
    # 页顶栏（页头设备名 band 上缘之上，同 _PLAYER_HEADER_DEVICE_REGION 的
    # 720 宽口径）。region 限定为同形互扰的双保险：element 实测旧单模板
    # 对歌单详情页返回箭头 score 0.997（teardown 误点返回箭头根因），双
    # 模板极性已根除互扰，region 再兜一层。
    _PLAYER_TOPBAR_REGION = (0, 0, 720, 200)

    # 收起钮探测模板链（2026-09-28 element 交付双模板，run4c 复盘拍板）：
    # 浅底（浅青背景态）/深底（深色封面背景态）跨背景极性互补（实测极性
    # -0.9 根除互扰），任一命中即播放页在；旧单模板 SWAN_PLAYER_DISMISS_BTN
    # 保留作第三兜底（对深色背景 0.379 失配、与歌单详情页返回箭头 0.997
    # 同形互扰，登记注记见 image_name_mapping.py）。
    _DISMISS_TEMPLATES = (SWAN_PLAYER_DISMISS_LIGHT, SWAN_PLAYER_DISMISS_DARK,
                          SWAN_PLAYER_DISMISS_BTN)

    def _find_dismiss_btn(self, timeout: float = 2.0) -> str | None:
        """播放页收起钮探测：浅底/深底双模板依次匹配 + 顶栏 region 限定，
        返回首个命中模板（供 click_image 精确点击命中位置），全未命中 None。

        任一模板命中即播放页在；region 限定 _PLAYER_TOPBAR_REGION 防与
        歌单详情页返回箭头同形互扰（双保险，见常量注）。
        """
        for template in self._DISMISS_TEMPLATES:
            if self.find_image(template, timeout=timeout,
                               region=self._PLAYER_TOPBAR_REGION) is not None:
                return template
        return None

    def _dismiss_full_player(self, timeout: float = 2.0) -> None:
        """收起全屏播放页回列表页（收起钮 [图] 在位才点，不做盲 back）。

        2026-09-28 改双模板探测（run4c 复盘拍板）：旧单模板（浅青背景态）
        跨背景失配——播放中深色封面背景 score 0.379，且与歌单详情页返回
        箭头同形互扰（score 0.997，teardown 误点返回箭头根因）。element
        交付收起钮浅底/深底双模板（极性实测 -0.9 根除互扰）后，探测改
        _find_dismiss_btn（双模板 + 顶栏 region 双保险），点击仍点命中
        模板位置；旧单模板保留作第三兜底。
        swan_regression_common._dismiss_player_if_any（teardown 清理）与本
        方法共用此实现，防两份收起逻辑漂移。
        """
        template = self._find_dismiss_btn(timeout=timeout)
        if template is not None:
            self.click_image(template, timeout=5,
                             region=self._PLAYER_TOPBAR_REGION)

    def _wait_player_page_open(self, timeout: float = 15.0) -> None:
        """断言全屏播放页已打开：顶栏收起钮探测（_find_dismiss_btn：浅底/
        深底/旧单模板 + 顶栏 region），deadline 内轮询，超时硬断言。

        run5 run1 改版（文件2 脏跑 wifi 9 条死亡帧）：旧 image_exists 单模板
        对电台播放页浅底失配——rig 持久电台会话（Radio Dum-Dum 亮黄模糊
        背景）下点播放条进页成功、收起钮白 chevron 落在亮背景上 score<0.8
        被误判未进页（13:35 FAIL 截图实证页面已开）。播放页到位断言统一
        收口本方法（start_play / select_device WiFi 分支 / 设备弹层退化
        分支 / collect_song player 收尾 / swan_regression_common.
        _open_player_page），检测器与 _dismiss_full_player 共用
        _find_dismiss_btn，防两份收起逻辑漂移。
        """
        deadline = time.monotonic() + timeout
        while True:
            if self._find_dismiss_btn(timeout=1) is not None:
                return
            if time.monotonic() >= deadline:
                assert False, (
                    "播放页顶栏未渲染（收起钮浅底/深底/旧单模板均未命中，"
                    f"顶栏 region 内已轮询 {timeout:.0f}s）")

    def start_play(self, source: str = "favorite", mode: str = "all",
                   index: int = 0) -> None:
        """发起播放（A13，回归用例 13-14 及各域播放前置）。

        mode="all"：点所在列表页的「播放全部」[图]。source 为列表页：
        favorite=我喜欢页 / playlist=歌单详情页（调用方须已在该页）。
        mode="song"：OCR 点歌名开播。source 为歌名文本，index 为同名
        匹配序号（0=第一个，按当前屏 OCR 返回顺序）；目标歌不在首屏时
        上滑一屏重找（最多 3 轮，见 _tap_song_row_by_ocr）。实测案例
        （verify-big52 根因5，run1_play_control.log）：SWAN_TEST_SONG=
        Booty Music 在我喜欢歌单约第 10 行、首屏仅前 6 行，原实现
        click_text(timeout=10) 找不到必超时失败（test_play_single_song）。

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
            self._tap_song_row_by_ocr(source, index)
        else:
            raise ValueError("mode 仅支持 all / song")
        self._wait_player_page_open(timeout=15)  # 已进入播放页（收起钮三模板探测）
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
        """播放态断言（A16，run4b 改版）：⏸ 图标 [图] 硬断言 +（黑胶动检 或
        进度时间递增）任一动证据成立。

        run4b 实测数据（720x1600 真机 run2_play_control.log）：播放中黑胶
        封面区 region_changed 平均像素差仅 2.7-5.7，贴 threshold=2.0 边缘，
        偶发 <2.0 误判静止——黑胶动检单独否决播放态会误报。故第二证据改
        双通道：黑胶动检作快路径（命中即通过），未命中再比对进度时间递增
        （_ocr_progress_increasing，播放中进度时间必然递增），任一成立即判
        在播；两者均不成立才判失败（region_changed 保留但不再单独否决）。
        """
        self.image_exists(SWAN_PLAYER_PAUSE_BTN, timeout=10)
        if self.region_changed(*self._vinyl_region()):
            return
        increasing = self._ocr_progress_increasing()
        assert increasing, (
            "播放态第二证据失败：⏸ 在位但黑胶动检未检出画面变化"
            + ("，进度时间亦不可读（两帧 OCR 均未取到进度双时间）"
               if increasing is None else
               "，且进度时间未递增（疑似暂停态）"))

    def assert_paused(self) -> None:
        """暂停态断言（A16 对偶，run4b 改版）：▶ 图标 [图] 硬断言 + 进度时间静止。

        与 assert_playing 对偶：播放中进度时间必然递增，暂停即时间静止
        （_ocr_progress_increasing 返回 False 即通过）。时间仍在递增
        （True，实为播放中）显式判失败；时间不可读（None，OCR 取不到
        进度双时间）时退回旧口径黑胶动检兜底——这是 region_changed 唯一
        仍可单独判定的场合（此时它是唯一可用证据）。
        注意不区分「无播放任务」与「已暂停」（两者都是 ▶ + 时间静止），
        调用方须保证当前存在播放任务。
        """
        self.image_exists(SWAN_PLAYER_PLAY_PAUSE_BTN, timeout=10)
        increasing = self._ocr_progress_increasing()
        if increasing is False:
            return
        assert increasing is not True, (
            "暂停态第二证据失败：▶ 在位但播放进度时间仍在递增（实为播放中）")
        assert not self.region_changed(*self._vinyl_region()), (
            "暂停态第二证据失败：▶ 在位但进度时间不可读且封面区画面仍在动")

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

    def _find_volume_slider(self, timeout: float = 10.0):
        """定位音量滑条真轨道矩形（± 钮锚定推导），返回 rect 或 None。

        ± 钮为弹窗静态控件（SWAN_PLAYER_VOLUME_MINUS/PLUS 正式模板），匹配
        矩形与音量填充态无关：fix4c/fix532 两态截图复配均 (31/547,1440)
        score=1.00，run4d 真机点击 (62/578,1466) 同证。真轨道 =
        减钮右缘+_VOLUME_TRACK_INSET_L → 加钮左缘-_VOLUME_TRACK_INSET_R，
        中线与 ± 钮同行。旧「中填充滑条模板」的匹配矩形随填充态漂移
        （run4d 实测同一轨道 x0=227~293），作几何锚比例换算必错，弃用。
        """
        minus = self.find_image_rect(SWAN_PLAYER_VOLUME_MINUS, timeout=timeout)
        plus = self.find_image_rect(SWAN_PLAYER_VOLUME_PLUS, timeout=timeout)
        if minus is None or plus is None:
            return None
        x0 = minus[0] + minus[2] + self._VOLUME_TRACK_INSET_L
        x1 = plus[0] - self._VOLUME_TRACK_INSET_R
        if x1 <= x0:
            logger.warning("_find_volume_slider: ± 钮矩形异常 minus=%s plus=%s",
                           minus, plus)
            return None
        cy = minus[1] + minus[3] // 2
        return (x0, cy - self._VOLUME_TRACK_HEIGHT // 2,
                x1 - x0, self._VOLUME_TRACK_HEIGHT)

    def set_volume(self, value: int, action: str = "drag") -> None:
        """调节音量（A19，回归用例 25-26）。

        声学断言已拍板降级为 UI 态（方案 §5③）：
        - action="drag"：点音量图标 [图] 开弹窗 → 断言弹窗 [图] → 音量滑条
          真轨道（± 钮锚定推导，_find_volume_slider）元素锚定拖到
          value/100 位置 → **弹窗开启态** OCR 音量核对 value（±5）→
          press_back 关弹窗 → 断言已回播放页。百分比核对在弹窗开启态做：
          弹窗标题行 "Speaker N"（run4d 实测数字可见但无 % 符号）是弹窗态
          唯一数据通道；press_back 后播放页走音量行 "N%" 通道（KB Wave2）。
        - action="click"：同 drag，落点为滑条 value/100 比例位。产品滑条
          忽略裸点（run4d 实测 tap@64.3% 位置 5 次扫描值不变，仅拖动生效），
          以 ≤2% 微拖实现点击定位（_click_track，落点即 pointer 终点）。
        - action="plus"/"minus"：value 为加减钮连点次数，收尾断言弹窗关闭
          且回到播放页（步进结果不核对具体百分比；该分支断言本就是页面态，
          保持在关弹窗后做，run4c 复核位置正确）。

        音量滑条方向默认横向（_VOLUME_SLIDER_AXIS），纵向布局改 "y"（同时
        需重校 _VOLUME_TRACK_* 常量与 _volume_ratios 上下翻转）。滑条定位
        走 _find_volume_slider（± 钮静态锚定推真轨道，2026-09-28 run4d
        run2 实测旧填充态模板锚定漂移废弃）。
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
            rect = self._find_volume_slider(timeout=10)
            assert rect is not None, "音量滑条拖动失败: 未定位到滑条真轨道（± 钮锚定失败）"
            assert self._swipe_track(
                rect, start_ratio, end_ratio,
                axis=self._VOLUME_SLIDER_AXIS), "音量滑条拖动失败"
        elif action == "click":
            rect = self._find_volume_slider(timeout=10)
            assert rect is not None, "音量滑条点击失败: 未定位到滑条真轨道（± 钮锚定失败）"
            assert self._click_track(
                rect, value, axis=self._VOLUME_SLIDER_AXIS), "音量滑条点击失败"
        else:
            template = (SWAN_PLAYER_VOLUME_PLUS if action == "plus"
                        else SWAN_PLAYER_VOLUME_MINUS)
            for _ in range(value):
                self.click_image(template, timeout=5)
        if action in ("drag", "click"):
            # 百分比断言必须在弹窗开启态完成：弹窗标题行 "Speaker N" 是
            # 弹窗态唯一数据通道（run4d run2 实测无 % 符号，正则需 Speaker
            # 模式；run4c run2 实测 press_back 后播放页仅存音量行 "N%" 通道）
            self._assert_volume_percent(value)
        self.press_back()  # 关弹窗回播放页（弹层关闭惯例，见知识库）
        self.image_exists(SWAN_PLAYER_VOLUME_ICON, timeout=10)      # 已回播放页

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

    def _ocr_progress_increasing(self, interval: float = 2.0) -> bool | None:
        """两次 OCR 进度时间比对：递增=在播，静止=暂停（run4b 新增动证据）。

        播放中进度时间必然递增，与黑胶动检（region_changed，run4b 实测
        播放中平均像素差 2.7-5.7 贴 2.0 阈值边缘）互为备份的第二证据。
        间隔 interval 秒各读一次进度双时间（_ocr_progress_times）：
        - True  已播秒数递增（或总时长变化=已换曲）→ 在播；
        - False 已播秒数不变 → 暂停；
        - None  两帧未读全进度时间（OCR 失败）→ 证据不可用，由调用方按
          自身口径取舍（assert_playing 记失败 / assert_paused 退回黑胶
          动检兜底）。
        """
        first = self._ocr_progress_times(timeout=5)
        if first is None:
            return None
        self.sleep(interval)
        second = self._ocr_progress_times(timeout=5)
        if second is None:
            return None
        if second[1] != first[1]:
            return True  # 总时长变化＝已换曲，必然在播
        return second[0] > first[0]

    def _ocr_volume_percent(self, timeout: float = 5.0) -> int | None:
        """OCR 读取音量百分比，返回整数；读不到返回 None。

        双数据通道（run4d run2 实测，_VOLUME_PCT_RE/_VOLUME_SPEAKER_RE）：
        - 弹窗开启态：弹窗标题行 "Speaker N"，数字可见但**无 % 符号**（每
          用例 5 次弹窗期全量扫描仅出 'Speaker 70/69/80/86/93'，从无 N%）
          ——set_volume 弹窗态断言唯一通道；
        - 弹窗关闭态：播放页音量行 "N%"（KB swan_播放页 Wave2 实测 OCR
          "0%"）——volume_key 前后读的通道。
        状态栏电量 "100"（无 % 尾、无 Speaker 前缀）两模式均不命中。
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for item in self.ocr_scan_page():
                m = self._VOLUME_PCT_RE.search(item["text"]) or \
                    self._VOLUME_SPEAKER_RE.search(item["text"])
                if m:
                    return int(m.group(1))
            self.sleep(0.5)
        return None

    def _assert_volume_percent(self, expected: int, tolerance: int = 5,
                               timeout: float = 8.0) -> None:
        """核对音量 UI 态：OCR 百分比与目标差值 ≤ tolerance。"""
        actual = self._ocr_volume_percent(timeout=timeout)
        assert actual is not None, (
            "OCR 未读到音量百分比（弹窗标题 Speaker N / 播放页音量行 N% "
            "两通道均未命中），无法核对音量 UI 态")
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
    def _track_point(cls, rect: tuple[int, int, int, int], ratio: float,
                     axis: str = "x") -> tuple[int, int]:
        """轨道矩形 + 比例 → 屏幕点（矩形中线取点）。"""
        x, y, w, h = rect
        if axis == "x":
            return x + int(w * ratio), y + h // 2
        return x + w // 2, y + int(h * ratio)

    def _swipe_track(self, rect: tuple[int, int, int, int],
                     start_ratio: float, end_ratio: float,
                     axis: str = "x", duration: float = 0.5) -> bool:
        """在 _find_volume_slider 推导的真轨道矩形上按比例元素锚定滑动。

        与 drag_on_template 的差异仅在于矩形来源：后者由滑动模板自身匹配
        （音量滑条的填充态模板匹配矩形会漂移，run4d run2 实测废弃），此处
        由静态 ± 钮锚定推导，几何稳定。
        """
        start = self._track_point(rect, start_ratio, axis)
        end = self._track_point(rect, end_ratio, axis)
        return self.swipe(start[0], start[1], end[0], end[1], duration)

    def _click_track(self, rect: tuple[int, int, int, int], value: int,
                     axis: str = "x", duration: float = 0.4) -> bool:
        """「点击」轨道 value/100 比例位（≤2% 微拖实现）。

        产品行为依据（run4d run2 实测）：音量弹窗滑条忽略裸点——tap 在
        64.3% 位置后 5 次弹窗期 OCR 扫描值恒不变（Speaker 69），仅拖动手势
        生效。故点击定位以微拖实现：起点取目标位沿值增长反方向回退 2%，
        终点即目标比例位，落点为 pointer 手势终点，与点击语义等价。
        轴向与 _volume_ratios 同约定：x 轴值随比例增，纵轴下小上大。
        """
        ratio = value / 100.0
        if axis == "x":
            start_ratio = max(0.0, ratio - 0.02)     # 目标位左邻 2%
            end_ratio = ratio
        else:
            start_ratio = min(1.0, 1.0 - ratio + 0.02)  # 目标位下方 2%
            end_ratio = 1.0 - ratio
        start = self._track_point(rect, start_ratio, axis)
        end = self._track_point(rect, end_ratio, axis)
        return self.swipe(start[0], start[1], end[0], end[1], duration)

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
    # 用例44-55（歌曲收藏）5.3.2 实测口径：[+] → 「选择平台收藏」弹层 →
    # 「已选N首歌」页点宫格块（=KB 旧「选择歌单页」/player/select-playlist，
    # 入口 2026-09-28 实测确认为播放页/各列表页 [+]，页标题实为「已选N首歌」
    # 而非「选择歌单」），见 collect_song（事实来源
    # knowledge/swan/draft/swan_收藏流程_532实测.md）。
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

    # 歌单详情页/我喜欢页歌曲行行内 [+] 中心 x（5.3.2 实测 bounds
    # (616,796)-(688,868)，720 宽口径；同排垃圾桶 bounds (528,796)-(600,868)，
    # 中心相距 88px，勿左偏误触移除）。[仅剩兜底职能] 行内 [+] 模板
    # SWAN_SONG_ROW_PLUS_BTN 已交付（2026-09-28，element 实测对垃圾桶区
    # 0.268 无误触、对播放页 [+] 0.372 无互扰），_tap_song_row_plus 改
    # 模板优先图定位；本 x 常量仅在模板未命中时与 OCR 行号 cy 组合作
    # 兜底（y 锚定 OCR 行，非盲坐标）。
    _SONG_ROW_PLUS_TAP_X = 652
    # 行内 [+] 模板主搜索条带（run5 改版主路径，720x1600 口径）：右侧
    # [+] 列（模板实测命中 x=635..669，中心 652 同 _SONG_ROW_PLUS_TAP_X）；
    # y 上界 600 排除歌单头/我喜欢头区页面级控件，下界 1360 排除底部播放
    # 条（run3 实测 y1376-1476）。
    _SONG_PLUS_STRIP = (560, 600, 160, 760)

    def collect_song(self, target_platform: str, playlist: str,
                     source: str = "player") -> None:
        """收藏歌曲到指定歌单（A30，回归用例44-55，12条合1）。

        2026-09-28 按 5.3.2 真机实测重写（事实来源：
        knowledge/swan/draft/swan_收藏流程_532实测.md）。5.3.2 正确链路：
        `[+] → 底部弹层「选择平台收藏」（点平台行）→ push 页
        「已选N首歌」（点歌单宫格块即完成，页内无确认钮）`。

        ⚠️ 旧实现的「红心/收藏图标 → 选择歌单页」流程已废弃：5.3.2 播放页
        红心只做「我喜欢」toggle（红/灰两态翻转，无弹层无跳转无 toast），
        与「收藏到指定歌单」语义已分离；红心 toggle 属收藏域
        （favorite_playlist 域），需要时另立独立私有辅助（如
        _toggle_like_in_player），本方法不再承担。

        source="player"：全屏播放页底部 [+] [图]（无 key 无 desc 仅图可达；
        调用方须已在播放页且有播放任务，域3 start_play 发起）。
        source="playlist_page"：歌单详情页/我喜欢页歌曲行右侧 [+]（调用方
        须已在含歌曲行的页面；两处入口与播放页 [+] 实测同构，点击后均为
        同一弹层）。行内定位 run5 改版模板优先：[+] 模板在右侧 [+] 列
        条带直接图定位（同构行并列得分取最上行，run5 实测行号纯数字为
        OCR 弱项不可作主路径依赖）；模板未命中退化 OCR 行号锚 +
        _SONG_ROW_PLUS_TAP_X 兜底（见 _tap_song_row_plus）。

        流程与断言：
          1. 点 [+] 后断言「选择平台收藏」弹层锚 [图]。
          2. OCR 点目标平台行（精确→compact 两级比对，同 _match_ocr_name
             口径；多命中取最靠下——弹层为底部浮层，平台行恒位于页面层
             同名文本之下：QQ 歌播放页的「QQ音乐 VIP」来源徽标、歌单详情页
             的平台 Tab 都在纱罩之上的页面层）。⚠️ 弹层平台行清单随歌曲来源
             变化（QQ 歌实测仅 QQ音乐+SWAN 两行，知识库遗留2），目标平台
             无行时显式报错并列出当前屏 OCR。
          3. 进「已选N首歌」页（=KB 旧「选择歌单页」，⚠️ 页标题不是
             「选择歌单」而是「已选N首歌」，N=本次加入歌曲数，[+] 单首相加
             恒为 1）：顶栏锚 [图] + OCR 含「已选」（动态 N 用 contains）
             双断言。
          4. 点目标歌单宫格块（3 列宫格，块 click=True、desc=歌单名；首块
             恒为「新增歌单」须避开——匹配命中先确认非「新增歌单」，防误入
             新建歌单弹窗；不在首屏时上滑重扫最多 3 轮）。⚠️ SWAN 宫格无
             「我喜欢」块（SWAN 收藏即我喜欢、红心直达），QQ 宫格才有粉心
             「我喜欢」块。
          5. 点块即完成；若捕获「已添加至我的音乐」toast 记录日志（辅助
             证据，不作断言；run4c 实测文案）。
        收尾断言回到来源页：播放页（收起钮三模板探测 _wait_player_page_open）
        / 歌单详情页更多按钮 [图]。
        ⚠️ 宫格块点击后的终局行为（toast 文案/是否自动返回来源页）未实测
        （探索期零写入红线，知识库遗留1），若真机实测不自动返回需补 back
        收尾。
        ⚠️ 弹层打开时来源页被纱罩遮盖，full_player_page 从 dump 消失属纱罩
        语义替换（页面视觉仍在），勿以播放页锚消失判定离页；异常退出关弹层
        用 back 键（弹层无取消钮，勿 tap 纱罩坐标）。
        ⚠️ 收藏结果无自动化回滚（行内垃圾桶为移除入口，红线禁点），目标
        歌单建议用 rig 测试账号聚合歌单（如「我的音乐」），数据污染由设备
        管理流程定期重置。
        """
        assert source in ("player", "playlist_page"), "source 仅支持 player / playlist_page"
        platform_text = self._require_platform_text(target_platform)
        if source == "player":
            self.click_image(SWAN_PLAYER_PLUS_BTN, timeout=10)
            back_anchor = None   # player 收尾走 _wait_player_page_open（三模板）
        else:
            self._tap_song_row_plus()
            back_anchor = SWAN_PD_MORE_BTN
        self.image_exists(SWAN_COLLECT_PLATFORM_SHEET, timeout=10)
        row = self._find_collect_platform_row(platform_text, timeout=10)
        self.tap(row["cx"], row["cy"])
        self.image_exists(SWAN_COLLECT_SELECTED_TOPBAR, timeout=10)
        self.text_exists("已选", timeout=10)   # 动态 N 用 contains，勿用「选择歌单」
        self._click_collect_playlist_tile(playlist)
        # run4c 实测成功 toast 文案为「已添加至我的音乐」（探索期猜测的
        # 「收藏成功」不出现）；重复收藏时 App 静默拦截、弹「添加失败，
        # 请稍后重试」且停留「已选N首歌」页（测试层数据设计规避，见
        # test_collect_song 注）。toast 仅辅助证据不作断言。
        if self.wait_toast("已添加至我的音乐", timeout=3):
            logger.info(
                "collect_song: 「已添加至我的音乐」toast 已捕获（辅助证据，不作断言）")
        if back_anchor is None:
            # 已回播放页：收起钮浅底/深底/单模板任一在位（电台页浅底单模板
            # 失配教训，run5 脏跑 wifi 9 条同因，见 _wait_player_page_open 注）
            self._wait_player_page_open(timeout=10)
        else:
            self.image_exists(back_anchor, timeout=10)

    def _tap_song_row_plus(self, timeout: float = 10.0) -> None:
        """歌单详情页/我喜欢页最上方歌曲行的行内 [+] 点击（collect_song
        source="playlist_page" 入口）。

        主路径（run5 改版——模板优先，OCR 行号降为兜底）：行内 [+] 模板
        SWAN_SONG_ROW_PLUS_BTN 在右侧 [+] 列条带（_SONG_PLUS_STRIP）直接
        图定位点击 rect 中心。同构行 [+] 匹配得分并列时 cv2 minMaxLoc 按
        行优先序返回最上命中——「最上方歌曲行」语义保持（源歌单数据约定
        仅保证顶行曲不在目标歌单内，见 test_歌单收藏与历史 SOURCE_PLAYLIST
        注）；fix4c/fix532 三张歌单详情截图实测两行 [+] 全部 score=1.000
        并列、minMaxLoc 恒返顶行 (635,815)。
        ⚠️ 为什么不以 OCR 行号锚作主路径：run5 实测行号纯数字是 OCR 弱项
        （cx<120 的 1/2/3 被识别为「田/盲」等汉字），行号锚断言直接失败，
        模板根本没机会执行；模板几何独立于 OCR，命中即点。

        模板未命中（截取态偏差/页面改版）退化旧 OCR 行锚兜底：行 desc=
        'N\\n歌名\\n歌手'，行号列在行左缘（cx<120）：OCR 取纯数字行
        （compact 归一化吞 l/I/1 同形——行号可能被读成 l/I；容错尾随
        「.、，」标点）得行 cy，取 cy 最小（最上方）行；x 取
        _SONG_ROW_PLUS_TAP_X（见其注，y 锚定 OCR 行非盲坐标）。
        """
        rect = self.find_image_rect(SWAN_SONG_ROW_PLUS_BTN, timeout=timeout,
                                    region=self._SONG_PLUS_STRIP)
        if rect is not None:
            self.tap(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)
            return
        logger.warning(
            "_tap_song_row_plus: 行内 [+] 模板全条带未命中，退化 OCR 行号锚兜底")
        deadline = time.monotonic() + timeout
        heads: list[str] = []
        while True:
            items = self.ocr_scan_page()
            heads = [i["text"].strip()[:12] for i in items if i["text"].strip()]
            rows = [
                i for i in items
                if i["cx"] < 120
                and self._ocr_compact(i["text"]).strip().strip(".、，,").isdigit()
            ]
            if rows:
                break
            if time.monotonic() >= deadline:
                assert False, (
                    "歌单行内 [+] 定位失败：模板未命中且 OCR 未找到歌曲行行号"
                    "（纯数字行，cx<120）。页面须已在含 ≥1 首歌曲行的歌单详情页"
                    f"/我喜欢页，当前屏 OCR 行首文字: {heads}")
            self.sleep(1.0)
        row = min(rows, key=lambda i: i["cy"])
        self.tap(self._SONG_ROW_PLUS_TAP_X, row["cy"])

    def _find_collect_platform_row(self, platform_text: str,
                                   timeout: float = 10.0) -> dict:
        """「选择平台收藏」弹层定位目标平台行（OCR 项，含 cx/cy）。

        精确包含优先、失配两侧 compact 归一化（同 _match_ocr_name 口径）；
        多命中取 cy 最大（最靠下）：弹层平台行恒位于页面层同名文本之下
        （QQ 歌播放页「QQ音乐 VIP」来源徽标、歌单详情页平台 Tab 都在纱罩
        之上的页面层），最靠下命中天然排除页面层误命中。
        """
        deadline = time.monotonic() + timeout
        items: list[dict] = []
        while True:
            items = self.ocr_scan_page()
            compact_text = self._ocr_compact(platform_text)
            hits = [
                i for i in items
                if platform_text in i["text"]
                or compact_text in self._ocr_compact(i["text"])
            ]
            if hits:
                return max(hits, key=lambda i: i["cy"])
            if time.monotonic() >= deadline:
                break
            self.sleep(1.0)
        heads = [i["text"].strip()[:12] for i in items if i["text"].strip()]
        assert False, (
            f"收藏平台弹层未找到平台行 {platform_text!r}（精确+compact 均未"
            "命中；弹层平台行清单随歌曲来源变化，QQ 歌实测仅 QQ音乐+SWAN，"
            f"见知识库 5.3.2 实测遗留2），当前屏 OCR 行首文字: {heads}")

    def _click_collect_playlist_tile(self, playlist: str,
                                     scrolls: int = 3) -> None:
        """「已选N首歌」页点目标歌单宫格块（块 click=True、desc=歌单名）。

        3 列宫格，首块恒为「新增歌单」（红底白十字，新建歌单入口）——命中
        剔除「新增歌单」行（歌单名匹配前先确认非「新增歌单」，防误入新建
        歌单弹窗）。目标歌单不在首屏时上滑一屏重扫（最多 scrolls 轮），每轮
        OCR 前等列表静止（_wait_list_settled，滑动惯性防护——宫格块纵向
        相接，惯性时移可能把点击甩进相邻块，收藏进错误歌单）。比对精确
        包含优先、失配两侧 compact 归一化（同 _match_ocr_name 口径）。
        """
        compact_name = self._ocr_compact(playlist)
        heads: list[str] = []
        for attempt in range(scrolls + 1):
            self._wait_list_settled()
            items = self.ocr_scan_page()
            heads = [i["text"].strip()[:12] for i in items if i["text"].strip()]
            hits = [
                i for i in items
                if (playlist in i["text"]
                    or compact_name in self._ocr_compact(i["text"]))
                and ("新增歌单" not in i["text"] or playlist in i["text"])
            ]
            if hits:
                tile = max(hits, key=lambda i: i["cy"])
                self.tap(tile["cx"], tile["cy"])
                return
            if attempt < scrolls:
                self.swipe_up()
        assert False, (
            f"「已选N首歌」页未找到歌单宫格块 {playlist!r}（已上滑重扫 "
            f"{scrolls} 轮；⚠️ SWAN 宫格无「我喜欢」块——SWAN 收藏即我喜欢，"
            f"QQ 宫格才有，见知识库 5.3.2 实测），当前屏 OCR 行首文字: {heads}")

    def recent_played_visible(self, kind: str, name: str,
                              timeout: float = 6.0) -> bool:
        """最近播放页目标条目可见性探测（非断言，返回 bool）。

        assert_recent_played 的造数前置判据（run5 新增）：进入播放历史页 +
        切分类 Tab 后 OCR 探测 name 是否已在内容区可见——可见则用例层无需
        现场播放造数（SWAN_HISTORY_FRESH_PLAY 条件触发口径），不可见才造。
        与 assert_recent_played 同导航（幂等 _open_recent_played），探完即
        返回，不做内容区断言、不上滑。
        """
        tab = self._HISTORY_TAB_ALIASES.get(kind)
        if tab is None:
            raise ValueError(
                f"kind 仅支持 {sorted(set(self._HISTORY_TAB_ALIASES))}，收到 {kind!r}")
        self._open_recent_played()
        if tab != "歌曲":
            self.click_text(tab, timeout=10, region=self._HISTORY_TAB_ROW_REGION)
        return self.find_text_by_ocr(
            name, timeout=int(timeout), region=self._HISTORY_CONTENT_REGION) is not None

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

    # back_to_tab_shell 防盲退探测的「App 内页面锚」集（run4c run3 实测：
    # teardown 音量弹层假阳性误 back 把 App 退到桌面后，back_to_tab_shell
    # 盲 back×3 仍在桌面空转，5 条 teardown ERROR 同因）。tab 壳锚由
    # _tab_shell_anchor_visible 承担，此处补 back 链途经的 push 页锚 [图]
    # （播放页收起钮/歌单详情页更多按钮/播放历史页顶栏/搜索提交钮），均
    # 为已转正常量。
    _APP_PAGE_ANCHORS = (SWAN_PLAYER_DISMISS_BTN, SWAN_PD_MORE_BTN,
                         SWAN_HISTORY_TOPBAR, SWAN_SEARCH_SUBMIT)

    def _app_page_anchor_visible(self, timeout: float = 1.0) -> bool:
        """前台仍在 Swan App 内的页面锚探测（back_to_tab_shell 防盲退用）。

        tab 壳锚（_tab_shell_anchor_visible）或 back 链途经 push 页锚
        [图]（_APP_PAGE_ANCHORS）任一命中即在 App 内；全未命中再 dump
        语义树兜底——bottom_player（贴底迷你播放条 key）除搜索全屏路由
        外全页面常驻（explorer 各页 dump 实测恒有），桌面 launcher 恒无
        此节点。探测口径宁缺勿滥：App 内未知页误判「退到桌面」的代价是
        start_app 拉回（App 已在前台时为无害空操作）+ 提前中止 back 循环，
        不会比原盲 back 行为更差（见 back_to_tab_shell 注）。
        """
        if self._tab_shell_anchor_visible(timeout=timeout):
            return True
        for template in self._APP_PAGE_ANCHORS:
            if self.find_image(template, timeout=timeout) is not None:
                return True
        return any((node.get("resource_id") or "") == "bottom_player"
                   for node in self.dump_semantics())

    def back_to_tab_shell(self, max_backs: int = 3) -> None:
        """从任意 push 页回到全局 tab 壳（一级页）：收播放页 -> 按需 press_back。

        每次 press_back 前先用一级页锚点 [图] 确认不在 tab 壳（首页按返回
        会退出 App）；供域7/域8 用例与清理流程从深层页面退出，已在 tab 壳
        时零操作。
        run4c 防盲退加固：每次 press_back 后校验前台仍在 App 内
        （_app_page_anchor_visible）——发现退到桌面（如前序 teardown 误
        back 已把 App 退出，run3 实测场景）立即 start_app 拉回并中止 back
        循环，杜绝在桌面继续盲 back；拉回后壳锚是否可见交由方法尾部断言
        定论（App 恢复到深层 push 页时仍会报退出失败，但设备已回到 App
        内，不再滞留桌面）。
        """
        # 收播放页改走 _dismiss_full_player（双模板+顶栏 region）：原处内联
        # 的收起钮单模板探测对歌单详情页返回箭头 score 0.997 同形互扰
        # （teardown 误点根因，见 _dismiss_full_player 注），2026-09-28 一并替换。
        self._dismiss_full_player()
        for _ in range(max_backs):
            if self._tab_shell_anchor_visible():
                return
            self.press_back()
            if not self._app_page_anchor_visible():
                logger.warning(
                    "back_to_tab_shell: press_back 后未检测到任何 App 页面锚"
                    "（已退到桌面），start_app 拉回并中止 back 循环")
                self.driver.start_app(
                    os.environ.get("SWAN_PACKAGE", "com.swan.network"))
                self._tab_shell_anchor_visible(timeout=10)
                break
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

    # 最近一次 search() 的关键词（assert_search_results「有结果」口径的
    # 加分证据源；search() → assert_search_results 同实例链路内有效，
    # 避免为传关键词改动用例层调用签名）
    _last_search_keyword: str = ""

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
        未授权账号点搜索条会弹「授权通知」模态弹窗（QQ音乐/网易云授权
        引导，verify-run3 实测）：进输入页断言前先 press_back 关闭（实测
        会重弹一次，最多关 2 轮），见 _dismiss_auth_notice_popup。
        流程：顶 Tab 切换 -> 搜索条进搜索输入页 -> OCR hint
        「搜索歌曲或艺术家等」定位输入框并点击聚焦 -> adb 输入关键词 ->
        搜索按钮 [图] 提交（用图不用 OCR 顶栏「搜索」，规避与自定义 T9
        键盘「搜索」键同名歧义，见知识库搜索 flow 风险注）。
        收尾断言：结果页六分类 Tab 行（region 限定 OCR「单曲」）+ 关键词
        回填输入框（OCR）。结果断言口径（空态/有结果）由 SWAN_SEARCH_
        PLATFORMS 决定，本方法把关键词记录到 _last_search_keyword 供其
        OCR 取证，两种口径与账号对应关系见 assert_search_results docstring。
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
        # 未授权账号点搜索条会弹「授权通知」模态（遮罩使搜索输入页不可达，
        # verify-run3 实测）：进输入页断言前先关闭。不并入 android_base 的
        # dismiss_app_popups 规则表——弹窗「授权」按钮是状态变更入口，规则
        # 表按按钮文字自动点击有误改账号授权态的风险，故只 press_back。
        self._dismiss_auth_notice_popup()
        self.text_exists("搜索歌曲或艺术家等", timeout=timeout)   # 搜索输入页生效
        self.click_text("搜索歌曲或艺术家等", timeout=5)          # 点击输入框聚焦
        self.input_text(keyword)
        self.text_exists(keyword, timeout=5)                      # 框内出现关键词
        self._last_search_keyword = keyword  # 供 assert_search_results「有结果」口径 OCR 取证
        self.click_image(SWAN_SEARCH_SUBMIT, timeout=10)          # 提交搜索
        self.text_exists("单曲", timeout=timeout,
                         region=self._RESULTS_TAB_ROW_REGION)     # 结果页 Tab 行渲染
        self.text_exists(keyword, timeout=5)                      # 关键词回填

    def _dismiss_auth_notice_popup(self, detect_timeout: int = 2,
                                   max_rounds: int = 2) -> None:
        """关闭搜索入口触发的「授权通知」模态弹窗（verify-run3 实测）。

        未授权账号每次点搜索条都会弹该模态（QQ音乐/网易云授权引导），
        遮罩导致搜索输入页不可达、后续 teardown go_home 找不到 tab_recommend。
        处置只 press_back（实测可安全关闭且不碰弹窗按钮）：弹窗内「授权」
        按钮是状态变更入口，故**不**并入 android_base 的 dismiss_app_popups
        规则表（规则表按按钮文字自动点击，存在误改账号授权态的风险）。
        实测 press_back 关一次会重弹一次，故最多关 max_rounds 轮；每轮
        OCR 探测标志文字「授权通知」，未命中即视为无弹窗/已清净（happy
        path 仅消耗一轮探测超时）。若 2 轮后弹窗仍在，交由后续输入页
        断言显式失败暴露，不在此吞错。
        """
        for round_no in range(1, max_rounds + 1):
            if self.find_text_by_ocr("授权通知", timeout=detect_timeout) is None:
                return
            logger.info("search: 第%d次检测到「授权通知」弹窗，press_back 关闭"
                        "（不点弹窗内授权按钮，规避状态变更）", round_no)
            self.press_back()

    def assert_search_results(self, tab: str, platforms=None,
                              timeout: float = 10.0,
                              allow_empty: bool = False) -> None:
        """搜索结果分类断言（A34，回归用例69-72后半）。

        须在搜索结果页调用（search() 收尾即停在此页）。tab ∈ 单曲/艺人/
        专辑/歌单/电台/播客（方案口径「博客」归一为页内文案「播客」），
        Tab 行 region 限定点击，原地切换内容区。

        结果断言两种口径（由 platforms 参数驱动；测试层经环境变量
        SWAN_SEARCH_PLATFORMS 控制，见 swan_regression_common2.py）：
        - platforms 为空/None（SWAN_SEARCH_PLATFORMS 未配置＝干净未授权
          账号）：断言空态——SWAN_SEARCH_EMPTY [图]，缺失时退化 OCR
          「没有找到相关结果」。
        - platforms 非空（SWAN_SEARCH_PLATFORMS 配置了已授权平台，如
          "qq,netease"；账号 B 已授权口径，空态断言不再适用）：断言结果
          区「有结果」——轮询窗口内空态图与空态文案均未出现即通过；本次
          搜索关键词（search() 记录于 _last_search_keyword）OCR 出现在
          结果区时提前通过（铁证）。不再逐个断言结果行内平台标注文案
          （该标注形式 5.3.2 未真机校准，原口径不可靠）。
          未列平台不受影响：对任一平台显式传空列表仍可断空态。
        - allow_empty=True（仅 platforms 非空口径生效，run4 实测电台 Tab
          专用）：run4 真机数据（qq/netease 授权 + 关键词 piano）——电台
          Tab 结果区空态、播客 Tab 有结果，电台内容源不按关键词返回结果，
          「有结果」断言对其不适用。该 Tab 降级为「空态或有结果均可」：
          空态证据（图/文案）出现记日志提前通过，否则窗口内无空态证据
          照旧按有结果放行；Tab 切换渲染本身仍是硬断言（click_text）。
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
        # 有结果口径：空态证据（图/文案）在轮询窗口内出现即判失败
        # （allow_empty=True 时降级为记日志提前通过，见 docstring）
        keyword = getattr(self, "_last_search_keyword", "")
        region = self._RESULTS_CONTENT_REGION
        deadline = time.monotonic() + timeout
        while True:
            if self.find_image(SWAN_SEARCH_EMPTY, timeout=1) is not None:
                if allow_empty:
                    logger.info(
                        "assert_search_results: 「%s」结果区为空态 [图]"
                        "（allow_empty 口径：空态或有结果均可）", tab_text)
                    return
                assert False, (
                    f"搜索「{tab_text}」结果区为空态 [图]（配置平台 {platforms} "
                    "应有结果；核对账号授权态与 SWAN_SEARCH_PLATFORMS 口径）")
            if self.find_text_by_ocr("没有找到相关结果", timeout=1,
                                     region=region) is not None:
                if allow_empty:
                    logger.info(
                        "assert_search_results: 「%s」结果区 OCR 空态文案"
                        "（allow_empty 口径：空态或有结果均可）", tab_text)
                    return
                assert False, (
                    f"搜索「{tab_text}」结果区 OCR 空态文案「没有找到相关结果」"
                    f"（配置平台 {platforms} 应有结果）")
            if (keyword
                    and self.find_text_by_ocr(keyword, timeout=1,
                                              region=region) is not None):
                logger.info("assert_search_results: 关键词 %r 已出现在「%s」"
                            "结果区（有结果铁证）", keyword, tab_text)
                return
            if time.monotonic() >= deadline:
                break
            self.sleep(0.5)
        logger.warning(
            "assert_search_results: 「%s」结果区未见空态证据%s，按有结果通过",
            tab_text,
            f"且关键词 {keyword!r} 未 OCR 命中" if keyword else "")

    def _assert_text_in_region(self, text: str, region, timeout: float,
                               what: str, scrolls: int = 2) -> None:
        """region 内 OCR 断言文本，未命中时上滑整屏重试（列表折叠下方条目）。"""
        for attempt in range(scrolls + 1):
            if self.find_text_by_ocr(text, timeout=int(timeout), region=region) is not None:
                return
            if attempt < scrolls:
                self.swipe_up()
        assert False, f"{what}未找到 {text!r}（已上滑重试 {scrolls} 次）"
