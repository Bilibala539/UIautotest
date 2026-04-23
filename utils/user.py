"""
用户和设备定义模块
提供PPUser和PPDevice类用于测试用户和设备管理

支持 MuMu 和 PC 两个平台，通过 platform 参数切换。
用户通过 user.aw.xxx() 方式调用AW方法。
"""
import logging
import time
from typing import Optional

from image.image_name_mapping import *
from utils.aw import create_aw, AWHelper
from utils.aw.search_region import *

logger = logging.getLogger(__name__)


class PPDevice:
    """MuMu模拟器设备类"""

    def __init__(self, device_port: int = 7555, instance_id: int = 0):
        """
        初始化MuMu模拟器设备

        Args:
            device_port: ADB连接端口，默认7555
            instance_id: 模拟器实例编号，默认0
        """
        self.device_port = device_port
        self.instance_id = instance_id
        self.device_serial = f"127.0.0.1:{device_port}"

        # 设备窗口信息（由devices.py设置）
        self.pos = (0, 0)
        self.size = (540, 960)
        self.window_name = ""
        self.is_ready = False

    @property
    def adb_address(self) -> str:
        """获取设备的ADB地址"""
        return self.device_serial

    def __repr__(self):
        return f"PPDevice(port={self.device_port}, instance={self.instance_id})"


class PPUser:
    """
    测试用户类
    
    支持 MuMu 和 PC 两个平台，通过 platform 参数切换。
    通过 user.aw 属性访问所有AW方法。
    
    使用示例:
        # MuMu 端
        user = PPUser(uid="test@example.com", password="123456",
                      device=device, platform="mumu")
        
        # PC 端
        user = PPUser(uid="test@example.com", password="123456",
                      platform="pc")
        
        # 调用方式完全一致
        user.aw.click_text("登录")
        user.aw.login(user.uid, user.password)
    """

    def __init__(self, uid: str, password: str,
                 device: Optional[PPDevice] = None,
                 platform: str = "mumu",
                 env: str = "test3",
                 name: str = "", name_en: str = "", name_jp: str = "",
                 phone: str = "", role: str = "", department: str = "",
                 need_login: bool = True):
        """
        初始化测试用户

        Args:
            uid: 用户ID/邮箱
            password: 密码
            device: 关联的MuMu模拟器设备 (platform='mumu' 时必传)
            platform: 平台类型 ('mumu' 或 'pc')
            env: 测试环境
            name: 中文名
            name_en: 英文名
            name_jp: 日文名
            phone: 手机号
            role: 账号类型
            department: 部门
            need_login: 是否需要登录
        """
        self.uid = uid
        self.password = password
        self.name = name
        self.name_en = name_en
        self.name_jp = name_jp
        self.phone = phone
        self.role = role
        self.department = department
        self.device = device
        self.platform = platform
        self.env = env
        self.need_login = need_login
        self._logged_in = False

        # AW 实例延迟初始化
        self._aw: Optional[AWHelper] = None

    @property
    def aw(self) -> AWHelper:
        """
        获取AW实例

        根据 platform 自动选择对应的驱动和业务类:
        - platform='mumu': MuMuDriver + MuMuBusiness
        - platform='pc': PCDriver + PCBusiness

        Returns:
            MuMuBusiness 或 PCBusiness 实例
        """
        if self._aw is None:
            if self.platform == "mumu":
                assert self.device is not None, "MuMu 平台必须指定 device"
                self._aw = create_aw(platform="mumu", instance_id=self.device.instance_id)
            elif self.platform == "pc":
                self._aw = create_aw(platform="pc")
            else:
                raise ValueError(f"不支持的平台: {self.platform}")
        return self._aw

    def login(self) -> bool:
        """
        执行用户登录

        完成登录流程后 POPO 已在消息列表页，无需再调用 open_app()。
        完成登录后标记 _logged_in = True。
        """
        logger.info(f"🔐 {self.uid} 正在登录 (平台: {self.platform})")
        self.aw.login(self.uid, self.password)
        self._logged_in = True
        logger.info(f"✅ {self.uid} 登录成功")

    def logout(self) -> bool:
        """
        执行用户退出登录

        内部会自动确保回到消息列表页（处理深层页面/桌面等场景），
        无需提前调用 open_app()。
        """
        logger.info(f"🚪 {self.uid} 正在退出登录")

        result = self.aw.logout()

        if result:
            self._logged_in = False
            logger.info(f"✅ {self.uid} 已退出登录")

        return result

    def open_app(self):
        """
        启动 POPO 并等待进入消息列表首页（已登录状态下）

        每个用例的 setup 阶段调用。
        前置条件: 用户已完成 Session 级登录，force-stop 不清除登录态。
        """
        logger.info(f"📱 {self.uid} 启动 POPO")
        self.aw.open_app()

    def close_app(self):
        """
        关闭 POPO 应用（force-stop，保持登录态）

        每个用例的 teardown 阶段调用。
        """
        logger.info(f"📱 {self.uid} 关闭 POPO")
        self.aw.close_app()

    @property
    def is_logged_in(self) -> bool:
        """检查用户是否已登录"""
        return self._logged_in

    # ==================== 便捷业务方法 ====================

    def open_session_group_panel(self) -> bool:
        """打开会话分组弹窗"""
        return self.aw.open_session_group_panel()

    def close_session_group_panel(self) -> bool:
        """关闭会话分组弹窗（点击蒙层区域）"""
        return self.aw.close_session_group_panel()

    def open_session_group_manage(self) -> bool:
        """进入分组管理页面"""
        return self.aw.open_session_group_manage()

    def enable_hidden_session_group(self, group_name: str = "群组") -> bool:
        """启用一个隐藏的会话分组"""
        return self.aw.enable_hidden_session_group(group_name)

    def disable_session_group(self, group_name: str = "群组") -> bool:
        """将一个展示的会话分组移到隐藏区域"""
        return self.aw.disable_session_group(group_name)

    def create_team(self) -> bool:
        """创建群组"""
        return self.aw.create_team()

    def delete_team(self) -> bool:
        """解散群组"""
        return self.aw.delete_team()

    def send_message(self, recipient: str, message=None, isback=True):
        """
        发送P2P消息

        通过搜索联系人进入聊天页面，输入消息并发送。

        Args:
            recipient: 收件人账号关键词（如 'grp.popoqa50'）
            message: 要发送的消息内容，默认 '自动化测试消息'

        """

        return self.aw.send_message(recipient=recipient, message=message, isback=isback)

    def send_file(self, recipient="grp.popoqa50", file_name="text"):
        """
        发送文件
        Args:
            recipient: 接收方
            file_name: text\video

        """
        self.aw.send_file(recipient=recipient, file_name=file_name)
        if file_name is "text":
            self.image_exists(MSG_FILE_JSON)
        elif file_name is "video":
            self.image_exists(MSG_FILE_VIDEO)
        return

    def recall_message(self, message_text=None, is_good=False):
        """
        撤回消息

        在当前聊天页面，长按指定消息体并撤回。
        前置条件: 当前在聊天页面，消息为自己发送且在24小时内。

        Args:
            message_text: 要撤回的消息文字内容

        Returns:
            bool: 撤回是否成功
        """
        if message_text:
            return self.aw.recall_message(message_text)
        if is_good:
            return self.aw.recall_good()

    def reply_message(self, message_text: str, reply_content: str) -> bool:
        """回复消息"""
        return self.aw.reply_message(message_text, reply_content)

    def copy_message(self, message_text: str) -> bool:
        """复制消息"""
        return self.aw.copy_message(message_text)

    def multi_select_message(self, message_text: str) -> bool:
        """进入多选模式"""
        return self.aw.multi_select_message(message_text)

    def translate_message(self, message_text: str) -> bool:
        """翻译消息"""
        return self.aw.translate_message(message_text)

    def favorite_message(self, message_text: str) -> bool:
        """收藏消息"""
        return self.aw.favorite_message(message_text)

    def open_sidebar(self):
        """打开侧边栏"""
        return self.aw.open_sidebar()

    def view_my_profile(self) -> dict:
        """
        查看我的个人资料，返回OCR采集到的个人信息字典

        Returns:
            dict: 包含 nickname_cn, nickname_en, nickname_jp,
                  signature, account, phone, position,
                  organization, office_location 等字段
        """
        return self.aw.view_my_profile()

    def open_my_collection(self):
        """打开我的收藏"""
        return self.aw.open_my_collection()

    def open_settings(self):
        """打开设置页面"""
        return self.aw.open_settings()

    def open_message_settings(self):
        """打开消息设置页面"""
        return self.aw.open_message_settings()

    def close_message_settings(self):
        """从消息设置页面返回消息列表页"""
        return self.aw.close_message_settings()

    def set_message_switch(self, switch_name: str, target_state: bool) -> bool:
        """
        设置消息设置页面中指定开关的状态

        前置条件: 当前已在消息设置页面

        Args:
            switch_name: 开关名称（如 "连续播放语音消息"）
            target_state: 目标状态 True=开启, False=关闭

        Returns:
            bool: 操作是否成功
        """
        return self.aw.set_message_switch(switch_name, target_state)

    def get_message_switch_state(self, switch_name: str) -> bool:
        """
        获取消息设置页面中指定开关的当前状态

        前置条件: 当前已在消息设置页面

        Args:
            switch_name: 开关名称

        Returns:
            bool: True=开启, False=关闭
        """
        return self.aw.get_message_switch_state(switch_name)

    def toggle_message_switch(self, switch_name: str) -> bool:
        """
        切换消息设置中的开关（完整流程: 进入→切换→返回）

        Args:
            switch_name: 开关名称

        Returns:
            bool: 切换后的新状态
        """
        return self.aw.toggle_message_switch(switch_name)

    # ==================== 图片编辑相关 ====================

    def send_image_from_album(self, recipient: str) -> bool:
        """从相册选图并直接发送"""
        return self.aw.send_image_from_album(recipient)

    def select_edit_send_image_from_album(self, recipient: str) -> bool:
        """从相册选图 → 进入预览 → 编辑 → 完成 → 发送"""
        return self.aw.select_edit_send_image_from_album(recipient)

    def edit_image_from_chat_message(self, RECIPIENT) -> bool:
        """长按聊天中的图片消息 → 点击编辑图片 → 完成"""
        return self.aw.edit_image_from_chat_message(RECIPIENT=RECIPIENT)

    def select_edit_with_tools_send_image(self, recipient: str) -> bool:
        """从相册选图 → 使用画笔工具编辑 → 完成 → 发送"""
        return self.aw.select_edit_with_tools_send_image(recipient)

    def search(self, tab="全部", text="", isclose=True):
        """大搜"""
        return self.aw.search(tab=tab, text=text, isclose=isclose)

    def search_all(self, tab="全部", text=""):
        """搜全部"""
        self.aw.search(tab, text)

    def search_people(self, text="王英", isgoin=False):
        """搜人"""
        self.aw.search(tab="联系人", text=text, isclose=False)
        # 具体例子-搜索 王英
        if text in ["王英", "wangying43", "wy"]:
            self.aw.image_exists(SEARCH_WANGYING_BLUE)
            self.aw.image_exists(SEARCH_WANGYING_HEAD)
            self.text_exists("效率工程部", region=Normal.HALF_UP)
            self.text_exists("技术质量中心", region=Normal.HALF_UP)
            self.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)
        if isgoin:
            time.sleep(5)
            self.click_text(text, timeout=10, region=Search.RESULT_LIST)
            # self.image_exists(MSG_P2P_UNDER_BOTTON)

    def search_group(self, text="测试测试", isgoin=False):
        """搜群"""
        self.aw.search(tab="群", text=text, isclose=False)
        # 具体例子-搜索 测试
        if text is "测试测试":
            self.aw.image_exists(SEARCH_CESHI_BLUE)
            self.aw.image_exists(SEARCH_TAB3_BOTTON)
        self.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)
        if isgoin:
            self.click_text(text, region=Search.RESULT_LIST)
            self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

    def search_msg(self, tab="消息", text=""):
        """搜消息"""
        self.aw.search(tab, text, isclose=False)
        # 具体例子-搜索 测试
        if text is "123":
            self.aw.image_exists(SEARCH_123_BLUE)
            self.aw.image_exists(SEARCH_TAB4_BOTTON)
        self.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def search_fuwuhao(self, tab="消息", text=""):
        """搜服务号"""
        self.aw.search(tab, text)

    def search_xiaochengxu(self, tab="日程", text=""):
        """搜小程序"""
        self.aw.search(tab, text)

    def search_cloude(self, tab="云空间", text=""):
        """搜云空间"""
        self.aw.search(tab, text)

    def search_mession(self, tab="任务", text=""):
        """搜任务"""
        self.aw.search(tab, text)

    def search_app(self, tab="应用", text=""):
        """搜应用"""
        self.aw.search(tab, text)

    # ==================== 富文本（扩展编辑）相关 ====================

    def send_rich_text_message(self, recipient: str, message: str,
                                format_type: str) -> bool:
        """
        发送富文本格式消息（加粗/斜体/下划线/删除线/字体颜色）

        Args:
            recipient: 收件人账号
            message: 消息文本内容
            format_type: 格式类型 ('bold'/'underline'/'strikethrough'/'font_color')
        """
        return self.aw.send_rich_text_message(recipient, message, format_type)

    def send_markdown_message(self, recipient: str, text: str,
                               markdown_type: str, **kwargs) -> bool:
        """
        发送 Markdown 格式消息（统一入口）

        Args:
            recipient: 收件人账号
            text: 消息文本内容
            markdown_type: Markdown 语法类型
                - 'hyperlink': 超链接，额外参数 url
                - 'quote': 引用块
                - 'inline_code': 行内代码
                - 'code_block': 代码块，额外参数 language
                - 'background_color': 背景色高亮
            **kwargs: 额外参数（如 url, language）
        """
        return self.aw.send_markdown_message(recipient, text, markdown_type, **kwargs)

    # 向下兼容的快捷方法
    def send_hyperlink_message(self, recipient: str, text: str,
                                url: str = "https://www.163.com") -> bool:
        """发送超链接消息"""
        return self.aw.send_hyperlink_message(recipient, text, url)

    def send_quote_message(self, recipient: str, text: str) -> bool:
        """发送引用块消息"""
        return self.aw.send_quote_message(recipient, text)

    def send_inline_code_message(self, recipient: str, text: str) -> bool:
        """发送行内代码消息"""
        return self.aw.send_inline_code_message(recipient, text)

    def send_code_block_message(self, recipient: str, text: str,
                                 language: str = "") -> bool:
        """发送代码块消息"""
        return self.aw.send_code_block_message(recipient, text, language)

    def send_background_color_message(self, recipient: str, text: str) -> bool:
        """发送带背景色的消息"""
        return self.aw.send_background_color_message(recipient, text)

    # ==================== 日历相关 ====================

    def view_calendar(self) -> bool:
        """查看日历页面"""
        return self.aw.view_calendar()

    def create_calendar_book(self, name: str) -> bool:
        """创建日历本"""
        return self.aw.create_calendar_book(name)

    def modify_calendar_book(self, name: str, new_name: str) -> bool:
        """修改日历本名称"""
        return self.aw.modify_calendar_book(name, new_name)

    def delete_calendar_book(self, name: str) -> bool:
        """删除日历本"""
        return self.aw.delete_calendar_book(name)

    def subscribe_calendar_book(self, keyword: str) -> bool:
        """订阅日历本"""
        return self.aw.subscribe_calendar_book(keyword)

    def unsubscribe_calendar_book(self, name: str) -> bool:
        """退订日历本"""
        return self.aw.unsubscribe_calendar_book(name)

    # ==================== 群组管理相关 ====================

    def search_chat_content(self, group_identifier: str, keyword: str) -> bool:
        """搜索群聊天内容"""
        return self.aw.search_chat_content(group_identifier, keyword)

    def set_group_announcement(self, group_identifier: str, content: str) -> bool:
        """设置群公告"""
        return self.aw.set_group_announcement(group_identifier, content)

    def exit_group(self, group_identifier: str) -> bool:
        """退出群组"""
        return self.aw.exit_group(group_identifier)

    def delete_message(self, message_text: str) -> bool:
        """删除消息"""
        return self.aw.delete_message(message_text)

    def pin_message(self, message_text: str) -> bool:
        """Pin消息（置顶消息）"""
        return self.aw.pin_message(message_text)

    def view_message_history_cloud_docs(self, group_identifier: str) -> bool:
        """查看消息历史-云文档"""
        return self.aw.view_message_history_cloud_docs(group_identifier)

    def search_message_history(self, group_identifier: str, keyword: str = "UI") -> bool:
        """搜索消息历史-云文档"""
        return self.aw.search_message_history(group_identifier, keyword)

    def add_custom_tab_page(self, recipient: str, tab_name: str = "测试标签页", link_url: str = "https://www.163.com") -> bool:
        """P2P会话添加自定义标签页"""
        return self.aw.add_custom_tab_page(recipient, tab_name, link_url)

    def remove_custom_tab_page(self, recipient: str, tab_name: str) -> bool:
        """P2P会话删除自定义标签页"""
        return self.aw.remove_custom_tab_page(recipient, tab_name)

    def merge_forward_message(self, message_text: str, forward_to: str = "grp.popoqa50") -> bool:
        """
        合并转发消息

        在当前聊天页面长按消息 → 多选 → 合并转发 → 选择联系人，
        验证合并消息卡片出现。

        Args:
            message_text: 要合并转发的消息文字
            forward_to: 转发接收人账号
        """
        return self.aw.merge_forward_message(message_text, forward_to)

    def copy_image_to_input_and_send(self, recipient: str) -> bool:
        """
        长按聊天中的图片→复制→粘贴到输入框→发送

        Args:
            recipient: 收件人账号
        """
        return self.aw.copy_image_to_input_and_send(recipient)

    def add_elife_to_floating_window(self) -> bool:
        """
        将易生活页面加入浮窗

        从消息列表页导航到易生活→右上角更多→浮窗。
        """
        return self.aw.add_elife_to_floating_window()

    def merge_forward_images_and_swipe(self, recipient: str = "grp.popoqa50") -> bool:
        """
        发送多张图片→合并转发→进入合并消息详情→图片查看器中左右滑动

        Args:
            recipient: 收件人账号
        """
        return self.aw.merge_forward_images_and_swipe(recipient)

    def screenshot_and_share(self, recipient: str = "grp.popoqa50") -> bool:
        """
        在聊天页面触发系统截图并通过POPO分享给指定联系人

        Args:
            recipient: 收件人账号
        """
        return self.aw.screenshot_and_share(recipient)

    def share_image_from_external(self, recipient: str = "grp.popoqa50") -> bool:
        """
        从系统相册分享图片到POPO并发送给指定联系人

        Args:
            recipient: 收件人账号
        """
        return self.aw.share_image_from_external(recipient)

    # ==================== 断言方法 ====================
    def click_image(self, image_name: str, threshold: float = 0.8,
                    timeout: int = 10, dx: int = 0, dy: int = 0, region=Normal.ALL) -> bool:
        """点击图片"""
        return self.aw.click_image(image_name, threshold, timeout, dx, dy, region)

    def image_exists(self, template_name: str, threshold: float = 0.8,
                     timeout: int = 5,
                     region=Normal.ALL):
        """断言图片存在"""
        return self.aw.image_exists(template_name, threshold, timeout, region)

    def click_text(self, text: str, timeout: int = 10,
                   dx: int = 0, dy: int = 0, region=Normal.ALL) -> bool:
        """点击文字"""
        return self.aw.click_text(text, timeout, dx, dy, region=region)

    def text_exists(self, text: str, timeout: int = 5,
                    region=Normal.ALL):
        """断言文字存在"""
        return self.aw.text_exists(text, timeout, region)

    def input_text(self, text: str) -> bool:
        """输入文本"""
        return self.aw.input_text(text)

    def tap(self, x: int, y: int, dx: int = 0, dy: int = 0) -> bool:
        """点击坐标"""
        return self.aw.tap(x, y, dx, dy)

    def wait_and_click_text(self, text: str, timeout: int = 10) -> bool:
        """等待文字出现并点击"""
        if self.aw.text_exists(text, timeout):
            return self.aw.click_text(text)
        return False

    def wait_and_click_image(self, image_name: str, timeout: int = 10) -> bool:
        """等待图片出现并点击"""
        if self.aw.find_image(image_name, timeout=timeout):
            return self.aw.click_image(image_name)
        return False

    def __repr__(self):
        return f"PPUser(uid='{self.uid}', platform='{self.platform}', device={self.device})"


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # MuMu 端示例
    device = PPDevice(device_port=16384, instance_id=0)
    user_mumu = PPUser(
        uid="test@example.com",
        password="password123",
        device=device,
        platform="mumu",
        env="test03"
    )
    print(user_mumu)
    print(f"AW Helper: {user_mumu.aw}")

    # PC 端示例
    user_pc = PPUser(
        uid="test@example.com",
        password="password123",
        platform="pc",
        env="test03"
    )
    print(user_pc)
    print(f"AW Helper: {user_pc.aw}")
