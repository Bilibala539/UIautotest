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
        self.click_image(HOME_POPO_LOGO, timeout=20)

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

        if self.click_text("密码", timeout=5):
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
        for i in range(5):
            logger.info(f"第{i}次按返回键")
            self.press_back()
            time.sleep(0.5)
            try:
                if self.image_exists(MESSAGE_TAB_BLUE, timeout=1):
                    logger.info(f"跳出返回循环")
                    break
            except:
                pass
        else:
            raise AssertionError("❌ 返回消息页面失败：连续5次未找到 MESSAGE_TAB_BLUE")
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

    def recall_message(self, message_text: str):
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
        y = self.find_text_by_ocr(message_text)[1]
        time.sleep(1)
        # 1. 定位消息文字并长按
        self.long_press_text(message_text)
        time.sleep(1)

        # 2. 点击弹出菜单中的"撤回"
        self.click_text("撤回")
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

    def reply_message(self, message_text: str, reply_content: str) -> bool:
        """
        回复消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"回复"，
        输入回复内容后发送。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 点击弹出菜单中的"回复"
        3. 验证引用栏出现
        4. 输入回复内容
        5. 点击发送按钮
        6. 验证发送成功（发送按钮恢复为+号）

        探索来源: explorer_output/screenshots/longpress_step3_reply_clicked.png

        Args:
            message_text: 要回复的目标消息文字
            reply_content: 回复内容

        Returns:
            bool: 回复是否成功
        """
        logger.info(f"💬 [MuMu] 回复消息: '{message_text}' -> '{reply_content}'")

        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        self.click_text("回复", region=Normal.HALF_DOWN)
        time.sleep(1)

        self.image_exists(CHAT_REPLY_QUOTE_BAR, region=Normal.HALF_DOWN)

        self.input_text(str(reply_content))
        time.sleep(0.5)

        self.click_image(CHAT_SEND_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info(f"✅ [MuMu] 回复消息成功")
        return True

    def copy_message(self, message_text: str) -> bool:
        """
        复制消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"复制"，
        消息文字内容复制到剪贴板。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 点击弹出菜单中的"复制"
        3. 验证"复制成功"toast出现

        探索来源: explorer_output/screenshots/longpress_step6_copy_done.png

        Args:
            message_text: 要复制的消息文字

        Returns:
            bool: 复制是否成功
        """
        logger.info(f"📋 [MuMu] 复制消息: '{message_text}'")

        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        self.click_text("复制", region=Normal.HALF_DOWN)
        time.sleep(1)

        self.image_exists(CHAT_COPY_SUCCESS_TOAST)

        logger.info(f"✅ [MuMu] 消息复制成功")
        return True

    def multi_select_message(self, message_text: str) -> bool:
        """
        进入多选模式

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"多选"，
        进入多选模式，验证后按返回键退出多选模式。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 点击弹出菜单中的"多选"
        3. 验证进入多选模式（标题栏出现"已选中"）
        4. 按返回键退出多选模式

        探索来源: explorer_output/screenshots/longpress_step8_multiselect.png

        Args:
            message_text: 要多选的消息文字

        Returns:
            bool: 多选模式进入和退出是否成功
        """
        logger.info(f"☑️ [MuMu] 多选消息: '{message_text}'")

        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        self.click_text("多选", region=Normal.HALF_DOWN)
        time.sleep(1)

        self.image_exists(CHAT_MULTI_SELECT_TITLE, region=Normal.HALF_UP)

        self.press_back()
        time.sleep(0.5)

        logger.info(f"✅ [MuMu] 多选模式进入和退出成功")
        return True

    def translate_message(self, message_text: str) -> bool:
        """
        翻译消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"翻译"，
        消息气泡下方出现翻译结果。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 点击弹出菜单中的"翻译"
        3. 验证翻译结果出现

        探索来源: explorer_output/screenshots/longpress_step10_translate.png

        Args:
            message_text: 要翻译的消息文字

        Returns:
            bool: 翻译是否成功
        """
        logger.info(f"🌐 [MuMu] 翻译消息: '{message_text}'")

        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        self.click_text("翻译", region=Normal.HALF_DOWN)
        time.sleep(2)

        self.image_exists(CHAT_TRANSLATE_RESULT, region=Normal.HALF_DOWN)

        logger.info(f"✅ [MuMu] 消息翻译成功")
        return True

    def favorite_message(self, message_text: str) -> bool:
        """
        收藏消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"收藏"，
        出现"已收藏"提示。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 点击弹出菜单中的"收藏"
        3. 验证"已收藏"提示出现

        探索来源: explorer_output/screenshots/longpress_step11_favorite.png

        Args:
            message_text: 要收藏的消息文字

        Returns:
            bool: 收藏是否成功
        """
        logger.info(f"⭐ [MuMu] 收藏消息: '{message_text}'")

        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        self.click_text("收藏", region=Normal.HALF_DOWN)
        time.sleep(2)

        self.image_exists(CHAT_FAVORITE_TOAST)

        # 关闭收藏成功弹窗（首次收藏会弹出引导弹窗）
        know_pos = self.find_text_by_ocr("知道啦", timeout=3)
        if know_pos:
            self.tap(know_pos[0], know_pos[1])
            time.sleep(0.5)

        logger.info(f"✅ [MuMu] 消息收藏成功")
        return True

    def recall_good(self):
        """
            撤回赞消息
        """
        x, y = self.find_image(MSG_MESSAGE_GOOD, timeout=15)
        self.long_press(x, y, duration=1.3)
        self.click_text("撤回")
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
            # 10. 返回消息页面，最多按5次返回键直到找到 MESSAGE_TAB_BLUE
            for i in range(5):
                self.press_back()
                time.sleep(0.5)
                try:
                    self.image_exists(MESSAGE_TAB_BLUE, timeout=1)
                    break
                except:
                    logger.warning(f"⚠️ 第{i + 1}次未找到消息Tab，继续返回...")
            else:
                raise AssertionError("❌ 返回消息页面失败：连续5次未找到 MESSAGE_TAB_BLUE")

        return message

    def send_file(self, recipient, file_name):
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
        self.click_text(recipient_email)
        time.sleep(1)
        self.click_image(CHAT_PLUS_BUTTON)
        self.click_image(CHAT_PLUS_FILE)
        self.click_image(FILE_SELECT_MORE)
        self.image_exists(FILE_SELECT_MORE_OPENICON)
        self.click_text("共享文件夹")
        self.click_image(FILE_SELECT_MORE_SEARCH)
        self.input_text(file_name)
        time.sleep(1)
        self.click_text(file_name, region=Normal.HALF_DOWN)
        logger.info(f"Normal.CENTER_POP:{Normal.CENTER_POP}")
        # self.text_exists(text="确定要将文件发送给", region=Normal.CENTER_POP)
        self.click_image(POPO_POP_OK)
        pass

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

    # ==================== 消息设置相关 ====================

    # 消息设置页面中的所有开关项（完整列表）
    MSG_SETTINGS_SWITCHES = [
        "AI智能识别快捷指令",
        "AI智能识别任务",
        "双击会话背景发送语音",
        "连续播放语音消息",
        "语音消息自动转换出文字",
        "语音消息转文字自动使用AI整理",
        "文件自动下载",
        "消息气泡聚合显示",
        "分享转发时需再次确认",
        "启用表情联想",
        "表情添加至默认分组",
    ]

    def open_message_settings(self):
        """
        从消息页面进入 设置→消息 设置页面

        步骤:
        1. 打开侧边栏
        2. 点击设置（图片识别）
        3. 点击消息入口（图片识别）
        4. 验证进入消息设置页面（图片识别）

        探索来源: explorer_output/screenshots/msg_settings_step0_focused.png
        """
        logger.info("⚙️ [MuMu] 打开消息设置页面")
        self.open_settings()
        self.click_image(SETTINGS_MESSAGE_ENTRY)
        time.sleep(0.5)
        self.image_exists(MSG_SETTINGS_TITLE, timeout=5, region=Normal.HALF_UP)
        logger.info("✅ 已进入消息设置页面")

    def close_message_settings(self):
        """
        从消息设置页面返回到消息列表页

        步骤:
        1. 按返回键 → 设置页
        2. 按返回键 → 侧边栏
        3. 按返回键 → 消息页
        """
        logger.info("🔙 [MuMu] 关闭消息设置页面")
        self.press_back()
        time.sleep(0.3)
        self.press_back()
        time.sleep(0.3)
        self.press_back()
        time.sleep(0.5)

    def _scroll_to_switch(self, switch_name: str) -> bool:
        """
        滚动消息设置页面直到目标开关可见

        消息设置页面有多屏内容，需要滑动才能看到所有开关。
        先尝试当前屏查找，找不到则向上滑动查找。

        Args:
            switch_name: 开关标题文字

        Returns:
            bool: 是否找到目标开关
        """
        # 先在当前屏查找
        pos = self.find_text_by_ocr(switch_name, timeout=2)
        if pos:
            return True

        # 向上滑动查找（最多滑3次）
        for i in range(3):
            self.swipe_up(350)
            time.sleep(0.5)
            pos = self.find_text_by_ocr(switch_name, timeout=2)
            if pos:
                return True

        logger.warning(f"⚠️ 滑动后仍未找到开关: {switch_name}")
        return False

    def set_message_switch(self, switch_name: str, target_state: bool) -> bool:
        """
        设置消息设置页面中指定开关的状态

        前置条件: 当前已在消息设置页面

        步骤:
        1. 滑动页面使目标开关可见
        2. 检测当前开关状态
        3. 如果与目标不一致则点击切换
        4. 验证切换成功

        探索来源: explorer_output/screenshots/msg_settings_analysis.png

        Args:
            switch_name: 开关名称（如 "连续播放语音消息"）
            target_state: 目标状态 True=开启, False=关闭

        Returns:
            bool: 操作是否成功
        """
        state_text = "开启" if target_state else "关闭"
        logger.info(f"🔧 [MuMu] 设置开关 '{switch_name}' → {state_text}")

        # 滚动到目标开关位置
        assert self._scroll_to_switch(switch_name), f"未找到开关 '{switch_name}'"

        # 切换开关
        result = self.toggle_switch(switch_name, target_state)
        assert result, f"开关 '{switch_name}' 切换到{state_text}失败"

        logger.info(f"✅ [MuMu] 开关 '{switch_name}' 已设置为{state_text}")
        return True

    def get_message_switch_state(self, switch_name: str) -> bool:
        """
        获取消息设置页面中指定开关的当前状态

        前置条件: 当前已在消息设置页面

        Args:
            switch_name: 开关名称

        Returns:
            bool: True=开启, False=关闭
        """
        logger.info(f"🔍 [MuMu] 查询开关状态: '{switch_name}'")
        self._scroll_to_switch(switch_name)
        return self.is_switch_on(switch_name)

    def toggle_message_switch(self, switch_name: str) -> bool:
        """
        切换消息设置页面中指定开关（开→关 或 关→开）

        完整流程: 消息页 → 侧边栏 → 设置 → 消息设置 → 切换开关 → 返回消息页

        Args:
            switch_name: 开关名称

        Returns:
            bool: 切换后的新状态 True=开启, False=关闭
        """
        logger.info(f"🔄 [MuMu] 切换消息设置开关: '{switch_name}'")

        self.open_message_settings()

        self._scroll_to_switch(switch_name)
        old_state = self.is_switch_on(switch_name)
        new_state = not old_state
        self.set_message_switch(switch_name, new_state)

        self.close_message_settings()

        state_text = "开启" if new_state else "关闭"
        logger.info(f"✅ [MuMu] 开关 '{switch_name}' 已切换为{state_text}")
        return new_state

    # ==================== 图片编辑相关 ====================

    def _enter_chat_page(self, recipient: str) -> None:
        """
        搜索联系人/群组，进入聊天页（复用 send_message 前半部分逻辑）

        Args:
            recipient: 收件人账号或群号
        """
        is_group = recipient.isdigit()
        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        self.image_exists(SEARCH_EMPTY)

        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(str(recipient))
        time.sleep(1)

        if is_group:
            self.click_text("群组", region=Normal.HALF_UP)
        else:
            self.click_text("联系人", region=Normal.HALF_UP)
        time.sleep(2)

        recipient_email = f"{recipient}@corp.netease.com" if "@" not in recipient else recipient
        self.click_text(recipient_email, timeout=10)
        time.sleep(1)

        self.text_exists("发送给", region=Normal.HALF_DOWN)
        logger.info(f"[MuMu] 已进入聊天页: {recipient}")

    def send_image_from_album(self, recipient: str) -> bool:
        """
        从相册选图并发送（不进行编辑）

        步骤:
        1. 通过搜索进入联系人聊天页
        2. 点击 + 号打开更多面板
        3. 点击"相册"
        4. 点击第一张图片选中
        5. 点击"发送"按钮发送

        探索来源: explorer_output/screenshots/edit_img_plus_panel.png

        Args:
            recipient: 收件人账号

        Returns:
            bool: 是否发送成功
        """
        logger.info(f"[MuMu] 从相册发送图片给: {recipient}")

        self._enter_chat_page(recipient)

        # 打开 + 面板
        self.click_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 点击相册
        self.click_image(CHAT_PLUS_ALBUM, region=Normal.HALF_DOWN)
        time.sleep(2)

        # 点击第一张图片（相册网格第一行第一个位置，y≈200, x≈70）
        self.tap(70, 200)
        time.sleep(1)

        # 点击发送
        self.click_text("发送", region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)

        # 验证发送成功：回到聊天页，+ 按钮可见
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info("[MuMu] 图片发送成功")
        return True

    def select_edit_send_image_from_album(self, recipient: str) -> bool:
        """
        从相册选图 → 进入预览 → 点击"编辑" → 在编辑器中完成 → 发送

        步骤:
        1. 进入联系人聊天页
        2. 点击 + → 相册
        3. 点击第一张图片，直接进入带"编辑"按钮的预览页
        4. 点击"编辑"按钮进入图片编辑器
        5. 验证编辑器底部工具栏出现
        6. 点击"完成"退出编辑器
        7. 点击"发送"按钮发送编辑后的图片

        探索来源:
        - edit_img_after_done.png（预览页含编辑/发送按钮）
        - edit_img_editor_page.png（编辑器页面）

        Args:
            recipient: 收件人账号

        Returns:
            bool: 是否成功完成编辑并发送
        """
        logger.info(f"[MuMu] 从相册选图编辑后发送给: {recipient}")

        self._enter_chat_page(recipient)

        # 打开 + 面板
        self.click_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 点击相册
        self.click_image(CHAT_PLUS_ALBUM, region=Normal.HALF_DOWN)
        time.sleep(2)

        # 点击第一张图片 → 直接进入预览页（有"编辑"按钮）
        self.tap(70, 200)
        time.sleep(1.5)

        # 点击"编辑"进入编辑器（点击图片后直接出现编辑按钮，无需额外点"预览"）
        self.click_image(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1.5)

        # 验证已进入编辑器（底部工具栏出现）
        self.image_exists(IMAGE_EDITOR_TOOLBAR, region=Normal.HALF_DOWN, timeout=8)
        logger.info("[MuMu] 已进入图片编辑器")

        # 点击"完成"退出编辑器
        self.click_image(IMAGE_EDITOR_DONE_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1)

        # 验证返回预览页（"编辑"按钮重新出现）
        self.image_exists(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=5)

        # 点击"发送"发送图片
        self.click_image(ALBUM_PREVIEW_SEND_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)

        # 验证发送成功：回到聊天页
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info("[MuMu] 相册选图编辑后发送成功")
        return True

    def edit_image_from_chat_message(self, RECIPIENT) -> bool:
        """
        长按聊天中最近发送的图片消息 → 点击"编辑图片" → 在编辑器中完成

        前置条件:
        - 当前页面为聊天页（chat_page）
        - 聊天中已有图片消息

        步骤:
        1. 长按已发送的图片消息气泡
        2. 点击弹出菜单中的"编辑图片"
        3. 验证进入图片编辑器（底部工具栏出现）
        4. 点击"完成"完成编辑

        探索来源:
        - edit_longpress_step1_menu.png（长按菜单含编辑图片选项）
        - edit_img_editor_page.png（编辑器页面）

        Returns:
            bool: 是否成功完成编辑
        """
        logger.info("[MuMu] 长按图片消息进行编辑")

        # 长按已发送的图片消息气泡
        self.long_press_image(CHAT_SENT_IMAGE_BUBBLE, duration=1.5)
        time.sleep(1)

        # 点击"编辑图片"（长按菜单中的文字选项，用 OCR 定位）
        self.click_text("编辑图片", region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1.5)

        # 验证进入图片编辑器
        self.image_exists(IMAGE_EDITOR_TOOLBAR, region=Normal.HALF_DOWN, timeout=8)
        logger.info("[MuMu] 已进入图片编辑器（从长按菜单）")

        self.click_image(IMAGE_EDITOR_PEN_BUTTON, region=Normal.HALF_DOWN)

        # 在图片中画一个 H 图案，范围在左上角(125,200)到右下角(400,750)内
        # H 的左竖线：从 (125, 200) 向下到 (125, 750)
        self.swipe(125, 200, 125, 750, duration=0.5)
        time.sleep(0.3)
        # H 的右竖线：从 (400, 200) 向下到 (400, 750)
        self.swipe(400, 200, 400, 750, duration=0.5)
        time.sleep(0.3)
        # H 的中间横线：从 (125, 475) 向右到 (400, 475)
        self.swipe(125, 475, 400, 475, duration=0.5)
        self.image_exists(IMAGE_EDITOR_H)
        assert False
        time.sleep(0.3)

        # 点击"完成"退出编辑器
        self.click_image(IMAGE_EDITOR_DONE_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1)

        # 在更多操作弹窗中选择“发送给同事或群组”
        self.text_exists("发送给同事或群组")
        self.click_image(IMAGE_EDITOR_FORWARD, region=Normal.HALF_DOWN)

        # 在选人组建的输入框中搜索接收者
        self.click_text("搜索", region=Normal.HALF_UP)
        self.input_text(RECIPIENT)

        # 点击关闭按钮下方308xp的第一个匹配结果，并且验证已发送提示
        self.click_image(SELECT_CANCEL, dy=308)
        self.image_exists(TOAST_SENDED)
        self.press_back()

        # 验证刚刚发送了带有H的图片
        self.image_exists(TOAST_SENDED)

        # 验证已返回聊天页（+ 按钮可见）
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info("[MuMu] 长按图片编辑完成")
        return True

    def select_edit_with_tools_send_image(self, recipient: str) -> bool:
        """
        从相册选图 → 编辑器中使用画笔工具编辑 → 完成 → 发送

        与 select_edit_send_image_from_album 的区别：
        本方法会在编辑器中使用画笔工具实际绘制，验证工具操作正常。

        步骤:
        1. 进入联系人聊天页
        2. 点击 + → 相册 → 选图 → 预览 → 编辑
        3. 进入编辑器后，在图片中心画一笔（使用画笔工具）
        4. 点击"完成"
        5. 点击"发送"

        探索来源: edit_img_editor_page.png（画笔工具坐标 x≈60, y≈870）

        Args:
            recipient: 收件人账号

        Returns:
            bool: 是否成功
        """
        logger.info(f"[MuMu] 从相册选图，使用工具编辑后发送给: {recipient}")

        self._enter_chat_page(recipient)

        # 打开 + 面板
        self.click_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 点击相册
        self.click_image(CHAT_PLUS_ALBUM, region=Normal.HALF_DOWN)
        time.sleep(2)

        # 点击第一张图片 → 直接进入预览页（有"编辑"按钮）
        self.tap(70, 200)
        time.sleep(1.5)

        # 点击"编辑"进入编辑器（点击图片后直接出现编辑按钮，无需额外点"预览"）
        self.click_image(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1.5)

        # 验证已进入编辑器
        self.image_exists(IMAGE_EDITOR_TOOLBAR, region=Normal.HALF_DOWN, timeout=8)

        # 在图片中心绘制一笔（画笔工具已默认激活，或可 click_text("T", region=HALF_DOWN) 激活）
        # 直接在图片区域滑动，产生绘制效果
        self.swipe(150, 400, 380, 400, duration=0.5)
        time.sleep(0.5)
        # 点击"完成"
        self.click_image(IMAGE_EDITOR_DONE_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1)

        # 验证返回预览页
        self.image_exists(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=5)

        # 点击"发送"
        self.click_image(ALBUM_PREVIEW_SEND_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)

        # 验证发送成功
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info("[MuMu] 使用工具编辑后发送成功")
        return True

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
