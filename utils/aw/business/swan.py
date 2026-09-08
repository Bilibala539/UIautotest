"""Swan 项目业务方法（flutter 端）。

页面控件 key 约定（accessibility resource_id）与既有用例
``tests/flutter/test_swan_login_logout.py`` 保持一致。
"""
from __future__ import annotations

import logging

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
    # ⚠️ 尚未实机验证（需走到密码登入页后按 dump 修正）
    KEY_PASSWORD_FIELD = "login_password_field"

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

    def login_with_password(self, phone: str, password: str) -> None:
        """密码登录，从任意初始状态开始，最终停在首页。"""
        if not self.accessibility_exists(self.KEY_PASSWORD_FIELD):
            self.click_accessibility(self.KEY_USE_PASSWORD_BUTTON)
        self.click_accessibility(self.KEY_PHONE_FIELD)
        self.input_text(phone)
        self.click_accessibility(self.KEY_PASSWORD_FIELD)
        self.input_text(password)
        self.press_back()
        self.click_accessibility(self.KEY_AGREEMENT)
        self.click_accessibility(self.KEY_SUBMIT)
        assert self.wait_accessibility(self.KEY_TAB_ME, timeout=20), "登录后未进入首页"

    def login_by_sms(self, phone: str, wait_code: float = 60.0) -> None:
        """验证码登录：输入手机号 → 下一步（自动发送验证码）→ 平台取码 → 填码自动提交。

        实测（2026-09-08）：点"下一步"后 App 自动发送验证码并跳到验证码输入页，
        没有"获取验证码"按钮；验证码 4 位，填满第 4 位自动提交进首页。
        """
        # 已在首页视为已登录
        if self.accessibility_exists(self.KEY_TAB_ME):
            logger.info("已在首页，跳过登录")
            return
        self.click_accessibility(self.KEY_PHONE_FIELD)
        self.input_text(phone)
        self.click_accessibility(self.KEY_AGREEMENT)
        # 下一步触发验证码发送，之后网关才能从开发接口取到本次验证码
        self.click_accessibility(self.KEY_SUBMIT)
        code = self._fetch_sms_code(phone, wait=wait_code)
        self.click_accessibility(self.KEY_CODE_FIELD)
        self.input_text(code)
        assert self.wait_accessibility(self.KEY_TAB_ME, timeout=20), "登录后未进入首页"

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
