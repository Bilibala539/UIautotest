"""
MuMu (Android) 端业务方法

包含 MuMu 模拟器上 POPO 应用的完整业务操作流程。
UI 流程、检查图片、操作步骤均为 Android 端专属。
"""
import logging
import subprocess
import time

from image.image_name_mapping import *
from utils.aw.business.common import CommonBusiness
from utils.aw.driver.base_driver import BasePlatformDriver
from utils.aw.search_region import Normal

logger = logging.getLogger(__name__)

POPO_PACKAGE = "com.netease.popo"
POPO_ACTIVITY = "com.netease.popo.MainActivity"


def _get_adb_path() -> str:
    from utils.devices import ADB_PATH
    return ADB_PATH


class MuMuBusiness(CommonBusiness):
    """
    MuMu (Android) 端业务类

    继承链: MuMuBusiness → CommonBusiness → AWBase
    """

    def __init__(self, driver: BasePlatformDriver):
        super().__init__(driver)
        from utils.devices import get_device_port_by_instance
        self._device_port = get_device_port_by_instance(driver.instance_id)
        self._device_serial = f"127.0.0.1:{self._device_port}"

    # ==================== ADB 命令 ====================

    def _run_adb_command(self, *args) -> bool:
        """执行ADB命令"""
        cmd = [_get_adb_path(), "-s", self._device_serial] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error(f"❌ ADB命令超时: {' '.join(cmd)}")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ ADB命令失败: {e.stderr.decode()}")
            return False

    # ==================== 应用控制 ====================

    def start_app(self):
        """点击 MuMu 桌面上的 POPO 图标启动应用"""
        self.click_image(HOME_POPO_LOGO)

    def stop_app(self, package: str = POPO_PACKAGE) -> bool:
        """停止应用"""
        logger.info(f"📱 正在停止应用 {package}...")
        self._run_adb_command("shell", "am", "force-stop", package)
        time.sleep(0.5)
        logger.info("✅ 应用已停止")
        return True

    def restart_app(self) -> bool:
        """重启应用"""
        self.stop_app()
        time.sleep(1)
        self.start_app()
        return True

    def clear_app_data(self, package: str = POPO_PACKAGE) -> bool:
        """清除应用数据"""
        logger.info(f"🗑️ 正在清除应用数据 {package}...")
        self._run_adb_command("shell", "pm", "clear", package)
        time.sleep(1)
        logger.info("✅ 应用数据已清除")
        return True

    def page_ctrl(self):
        pass

    # ==================== 登录 / 退登 ====================

    def login(self, uid: str, password: str):
        """
        MuMu 端登录流程

        步骤:
        1. 点击桌面 POPO 图标启动应用
        2. 等待登录页面
        3. 点击邮箱 Tab
        4. 输入邮箱
        5. 输入密码
        6. 勾选协议
        7. 点击登录按钮
        8. 处理弹窗
        """
        logger.info(f"🔐 [MuMu] 开始登录: {uid}")

        self.start_app()
        self.sleep(2)

        self.image_exists(LOGIN_POPO_TEXT, timeout=5)
        logger.info("📱 检测到登录页面")

        self.click_text("邮箱", timeout=3)
        self.sleep(0.5)

        try:
            self.click_text("输入邮箱", timeout=5)
            self.sleep(0.5)
            self.input_text(str(uid))
            self.click_text("邮箱", timeout=5, dx=50, dy=180)
        except:
            self.text_exists("grp", region=Normal.HALF_UP)

        if self.click_text("输入密码", timeout=5):
            self.sleep(0.3)
            self.input_text(str(password))

        try:
            self.click_image(LOGIN_READ_CENTER_FALSE)
            self.sleep(0.3)
            self.click_image(LOGIN_ENTER)
            self.sleep(1.5)
            self.image_exists(MESSAGE_TAB_BLUE, timeout=10)
        except:
            self.image_exists(LOGIN_READ_CENTER_TRUE)
            self.click_image(LOGIN_ENTER)
            self.sleep(1.5)
            self.image_exists(MESSAGE_TAB_BLUE, timeout=10)

        self.pop_not_allowed()
        logger.info(f"✅ [MuMu] 登录成功: {uid}")

    def logout(self) -> bool:
        """MuMu 端退出登录流程"""
        logger.info("🚪 [MuMu] 开始退出登录")
        try:
            self.click_image(MESSAGE_TAB_BLUE)
        except:
            self.click_image(MESSAGE_TAB_GRUE)

        self.click_image(MESSAGE_TAB_MSG_TEXT, dx=-70)
        time.sleep(0.3)
        self.click_text("设置", region=Normal.HALF_DOWN)
        time.sleep(0.3)
        self.click_image(SETTINGS_LOGOUT)
        time.sleep(0.3)
        self.click_image(SETTINGS_LOGOUT_CONFIRM)
        time.sleep(1.5)
        self.image_exists(LOGIN_POPO_TEXT)
        logger.info("✅ [MuMu] 退出登录成功")
        return True

    # ==================== 弹窗处理 ====================

    def pop_not_allowed(self):
        self.pop_is_exisit(isallow=False)

    def pop_allowed(self):
        self.pop_is_exisit(isallow=True)

    def pop_is_exisit(self, isallow=False):
        try:
            self.image_exists(POPO_POP)
            time.sleep(0.5)
            if not isallow:
                self.click_image(POPO_POP_CANCEL)
                logger.info("弹窗已关闭")
        except:
            logger.info("未发现弹窗")

    # ==================== 群组相关 ====================

    def create_team(self):
        """创建群组"""
        username = "grp.popoqa"
        self.click_image(SESSIONLIST_PLUS_BUTTON)
        time.sleep(5)
        self.click_image(SESSIONLIST_PLUS_BUTTON_CREATETEAM)
        time.sleep(0.3)
        self.image_exists(SELECT_TITLE_ADD_TEAM_MUNBER)
        self.click_image(SELECT_SEARCH)
        self.input_text(str(username))
        time.sleep(1)

        self.click_image(SELECT_CIRCLE, region=Normal.HALF_UP)
        time.sleep(0.3)
        self.image_exists(SELECT_CIRCLE_BLUE, region=Normal.HALF_UP)
        self.click_image(SELECT_OK_BLUE, region=Normal.HALF_DOWN)

        try:
            self.text_exists(text="选择已有群组", region=Normal.HALF_UP)
            self.click_image(CREATE_NEW_TEAM, region=Normal.HALF_DOWN)
        except:
            pass

        self.text_exists(text="发起群聊", region=Normal.HALF_UP)
        self.text_exists(text="并邀请", region=Normal.HALF_UP)
        self.text_exists(text="加入群聊", region=Normal.HALF_UP)
        return True

    def delete_team(self):
        pass

    # ==================== 消息操作相关 ====================

    def recall_message(self, message_text: str) -> bool:
        """
        撤回消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"撤回"，
        在确认弹窗中点击"确定"完成撤回。

        前置条件:
        - 当前页面为聊天页面 (chat_page)
        - 目标消息为自己发送的消息
        - 消息发送时间在24小时内

        步骤:
        1. 通过OCR定位消息文字
        2. 长按消息体(1.5秒)
        3. 弹出操作菜单（底部浮动面板）
        4. 点击"撤回"选项
        5. 在确认弹窗中点击"确定"
        6. 验证撤回成功（出现"你撤回了一条消息"提示）

        探索来源: explorer_output/records/exploration_record_recall_message.md

        Args:
            message_text: 要撤回的消息文字内容

        Returns:
            bool: 撤回是否成功
        """
        logger.info(f"🔄 [MuMu] 撤回消息: '{message_text}'")

        # 1. 定位消息文字并长按
        self.long_press_text(message_text)
        y = self.find_text_by_ocr(message_text)[1]
        time.sleep(1)

        # 2. 点击弹出菜单中的"撤回"
        self.click_text("撤回", region=Normal.HALF_DOWN)
        time.sleep(1)

        # 3. 判断是否存在撤回确认弹窗
        try:
            if self.image_exists(MSG_RECELL_POP):
                self.click_text("确定")
        except:
            pass

        # 4. 验证撤回成功
        self.find_text_by_ocr("你撤回了一条消息", timeout=5, region=(0, (920 - y), 540, (880 - y)))

        logger.info(f"✅ [MuMu] 消息撤回成功: '{message_text}'")
        return True

    # ==================== 发消息相关 ====================

    def send_message(self, recipient: str, message: str, isback):
        """
        发送消息（支持P2P消息和群组消息）

        根据 recipient 自动判断是发送给个人还是群组：
        - 如果 recipient 是纯数字，则认为是群号，给群组发消息
        - 否则认为是人，给人发消息

        步骤:
        1. 从消息页面点击搜索按钮进入搜索页
        2. 搜索收件人（支持账号、昵称）
        3. 切换到对应Tab（联系人Tab或群组Tab）
        4. 点击搜索结果
        5. 进入聊天页面后，点击输入框
        6. 输入消息内容
        7. 点击发送按钮
        8. 验证消息发送成功（发送按钮恢复为+号）
        9. 返回消息页面

        探索来源: explorer_output/records/exploration_record_send_message.md

        Args:
            recipient: 收件人账号或关键词（如 '12345' 表示群组，'zhangsan' 表示个人）
            message: 要发送的消息内容
        """
        # 判断是否为群组：纯数字为群号
        if message is None:
            message = self.random_digits()
        is_group = recipient.isdigit()

        if is_group:
            msg_type = "群组"
        else:
            msg_type = "P2P"

        # 1. 打开搜索页面
        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        self.image_exists(SEARCH_EMPTY)

        # 2. 输入搜索关键词
        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(str(recipient))
        time.sleep(1)

        # 3. 切换到对应Tab
        if is_group:
            self.click_text("群组", region=Normal.HALF_UP)
        else:
            self.click_text("联系人", region=Normal.HALF_UP)
        time.sleep(2)

        # 4. 点击搜索结果中的联系人/群组（用完整邮箱匹配，避免点到搜索框里的文字）
        recipient_email = f"{recipient}@corp.netease.com" if "@" not in recipient else recipient
        self.click_text(recipient_email, timeout=10)
        time.sleep(1)

        # 5. 验证进入聊天页面（通过输入框占位符文字判断）
        self.text_exists("发送给", region=Normal.HALF_DOWN)
        logger.info(f"📱 已进入{msg_type}聊天页面")

        # 6. 点击输入框（通过占位符文字定位）
        self.click_text("发送给", region=Normal.HALF_DOWN)
        time.sleep(0.3)

        # 7. 输入消息内容
        self.input_text(str(message))
        time.sleep(0.5)

        # 8. 点击发送按钮
        self.click_image(CHAT_SEND_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 9. 验证发送成功：发送按钮恢复为+号
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        logger.info(f"✅ [MuMu] 消息发送成功: '{message}' -> {recipient}")
        if isback:
            # 10. 返回消息页面
            self.press_back()
            time.sleep(0.5)
            self.image_exists(MESSAGE_TAB_BLUE)

        return message

    # ==================== 侧边栏相关 ====================

    def open_sidebar(self):
        """
        打开侧边栏

        步骤:
        1. 确保在消息Tab页
        2. 点击左上角消息文案左侧的头像区域
        3. 等待侧边栏内容出现（通过图片断言确认）

        探索来源: explorer_output/screenshots/step7_sidebar.png
        """
        logger.info("📋 [MuMu] 打开侧边栏")
        self.click_image(MESSAGE_TAB_MSG_TEXT, dx=-70)
        time.sleep(0.5)
        self.image_exists(SIDEBAR_SETTINGS_BUTTON, region=Normal.HALF_DOWN)
        logger.info("✅ 侧边栏已打开")

    def close_sidebar(self):
        """
        关闭侧边栏

        通过按返回键关闭侧边栏，回到消息列表页
        """
        logger.info("📋 [MuMu] 关闭侧边栏")
        self.press_back()
        time.sleep(0.5)

    def view_my_profile(self) -> dict:
        """
        查看我的个人资料

        步骤:
        1. 打开侧边栏
        2. 点击用户名进入个人资料页
        3. 通过 find_text_by_ocr 逐字段采集个人信息
        4. 向上滑动查看更多字段（岗位、组织架构、办公位置）
        5. 返回消息列表页

        探索来源:
        - explorer_output/screenshots/step7_sidebar.png (侧边栏)
        - explorer_output/screenshots/step8_profile.png (个人资料页上半)
        - explorer_output/screenshots/step9_profile_scroll.png (个人资料页下半)

        Returns:
            dict: 个人资料信息，包含以下字段:
                - nickname_cn: 中文昵称
                - nickname_en: 英文昵称
                - nickname_jp: 日文昵称
                - signature: 个性签名
                - account: 账号邮箱
                - phone: 手机号
                - position: 岗位名称
                - organization: 组织架构
                - office_location: 办公位置
        """
        logger.info("👤 [MuMu] 查看个人资料")

        # 1. 打开侧边栏
        self.open_sidebar()

        # 2. 在侧边栏中点击用户名区域进入个人资料页
        self.image_exists(SIDEBAR_MY_COLLECTION)
        # 用户名在侧边栏顶部头像下方，相对"我的收藏"向上偏移点击
        self.click_image(SIDEBAR_MY_COLLECTION, dx=0, dy=-180)
        time.sleep(1.5)

        # 3. 通过 find_text_by_ocr 确认进入个人资料页
        self.find_text_by_ocr("个性签名", timeout=5)
        self.find_text_by_ocr("中文昵称", timeout=3)
        logger.info("📱 已进入个人资料页")

        # 4. 逐字段采集个人信息
        profile = self._extract_profile_fields()

        # 5. 返回消息列表
        self.press_back()
        time.sleep(0.5)
        self.press_back()
        time.sleep(0.5)

        logger.info(f"✅ 个人资料采集完成: {profile}")
        return profile

    def _extract_profile_fields(self) -> dict:
        """
        从个人资料页通过 find_text_by_ocr 逐字段提取信息

        利用 find_text_by_ocr 在页面中查找字段标签，
        字段值在标签坐标下方约25~30px处，通过偏移坐标读取。

        Returns:
            dict: 个人资料字段
        """
        profile = {}

        # 第一屏字段
        first_screen_fields = [
            ("个性签名", "signature"),
            ("中文昵称", "nickname_cn"),
            ("英文昵称", "nickname_en"),
            ("日文昵称", "nickname_jp"),
            ("账号", "account"),
            ("手机号", "phone"),
        ]

        for label, key in first_screen_fields:
            pos = self.find_text_by_ocr(label, timeout=3)
            if pos:
                profile[key] = pos
                logger.info(f"📋 找到字段 '{label}' @ {pos}")

        # 向上滑动看第二屏：岗位名称、组织架构、办公位置
        self.swipe_up(300)
        time.sleep(0.5)

        second_screen_fields = [
            ("岗位名称", "position"),
            ("组织架构", "organization"),
            ("办公位置", "office_location"),
        ]

        for label, key in second_screen_fields:
            pos = self.find_text_by_ocr(label, timeout=3)
            if pos:
                profile[key] = pos
                logger.info(f"📋 找到字段 '{label}' @ {pos}")

        return profile

    def open_my_collection(self):
        """
        打开「我的收藏」

        步骤: 打开侧边栏 → 点击"我的收藏"图片
        """
        logger.info("⭐ [MuMu] 打开我的收藏")
        self.open_sidebar()
        self.click_image(SIDEBAR_MY_COLLECTION, region=Normal.HALF_DOWN)
        time.sleep(1)

    def open_device_management(self):
        """
        打开「登录设备管理」

        步骤: 打开侧边栏 → 点击"登录设备管理"图片
        """
        logger.info("📱 [MuMu] 打开登录设备管理")
        self.open_sidebar()
        self.click_image(SIDEBAR_DEVICE_MANAGEMENT, region=Normal.HALF_DOWN)
        time.sleep(1)

    def open_settings(self):
        """
        打开「设置」页面

        步骤: 打开侧边栏 → 点击"设置"图片
        """
        logger.info("⚙️ [MuMu] 打开设置页面")
        self.open_sidebar()
        self.click_image(SIDEBAR_SETTINGS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

    # ==================== 搜索相关 ====================
    def search(self, tab, text, isclose=True):
        """创建群组"""

        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        self.image_exists(SEARCH_EMPTY)

        # tab左滑翻页
        if tab in ["云空间", "任务", "应用"]:
            self.swipe_left(self.text_exists("日程"), 230)
        img_name = f"搜索页面-{tab}tab.png"
        img_name_miss = f"搜索页面-{tab}tab-未选中.png"
        if tab == "全部":
            pass
        else:
            logger.info(f"tab是：{tab}")
            self.click_image(os.path.join(path, img_name_miss))
        self.image_exists(img_name, region=Normal.HALF_UP)
        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(str(text))
        if isclose:
            # 点击取消按钮，退出搜索页面
            self.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)
