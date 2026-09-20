"""Swan 项目业务方法（flutter 端）。

页面控件 key 约定（accessibility resource_id）与既有用例
``tests/flutter/test_swan_login_logout.py`` 保持一致。
"""
from __future__ import annotations

import logging
import os

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
