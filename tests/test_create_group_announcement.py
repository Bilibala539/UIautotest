"""
测试用例: 创建群组并设置群公告
"""
from time import sleep

import pytest

from image.image_name_mapping import MESSAGE_TAB_MSG_TEXT


class TestCreateGroupAndSetAnnouncement:
    """测试创建群组并设置群公告功能"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_create_group_and_set_announcement(self):
        """
        测试场景: 创建群组并设置群公告为"1234"

        步骤:
        1. 点击添加按钮(+)，弹出功能菜单
        2. 点击"创建群组"，进入添加群成员页面
        3. 选择2个联系人
        4. 点击确定按钮
        5. 如果出现"选择已有群组"页面，点击"创建新的群组"
        6. 进入群聊页面后，点击群名称进入群设置
        7. 点击群公告
        8. 输入"1234"
        9. 点击确认并选择"发送到群聊"
        10. 验证群公告设置成功
        11. 退出群组

        预期结果: 群组创建成功，群公告显示为"1234"
        """
        # ========== 步骤1: 点击添加按钮 ==========
        print("步骤1: 点击添加按钮(+)")
        # 通过消息文案定位，向右偏移到添加按钮位置
        self.userA.aw.click_image(MESSAGE_TAB_MSG_TEXT, dx=400)
        sleep(1)

        # ========== 步骤2: 点击创建群组 ==========
        print("步骤2: 点击创建群组")
        self.userA.aw.click_text("创建群组")
        sleep(1.5)

        # ========== 步骤3: 选择联系人 ==========
        print("步骤3: 选择联系人")
        # 点击第一个联系人（在"会话"文字下方）
        self.userA.aw.click_text("会话", dy=180)
        sleep(0.5)
        
        # 点击第二个联系人（在第一个联系人下方）
        self.userA.aw.click_text("会话", dy=280)
        sleep(0.5)

        # ========== 步骤4: 点击确定 ==========
        print("步骤4: 点击确定按钮")
        self.userA.aw.click_text("确定")
        sleep(2)

        # ========== 步骤5: 处理"选择已有群组"页面（如果出现） ==========
        if self.userA.aw.text_exists("选择已有群组", timeout=2):
            print("步骤5: 检测到已有群组页面，点击创建新的群组")
            self.userA.aw.click_text("创建新的群组")
            sleep(2)
        else:
            print("步骤5: 直接创建成功，跳过")
        
        # ========== 步骤6: 进入群设置 ==========
        print("步骤6: 点击群名称进入群设置")
        # 点击"名群成员"文字上方的群名称
        self.userA.aw.click_text("名群成员", dy=-30)
        sleep(1.5)

        # ========== 步骤7: 点击群公告 ==========
        print("步骤7: 点击群公告")
        self.userA.aw.click_text("群公告")
        sleep(1.5)

        # ========== 步骤8: 输入群公告内容 ==========
        print("步骤8: 点击输入框并输入1234")
        self.userA.aw.click_text("输入群公告内容")
        sleep(0.5)
        self.userA.aw.input_text("1234")
        sleep(1)

        # ========== 步骤9: 保存群公告 ==========
        print("步骤9: 点击确认按钮")
        # 点击"群公告"文字右侧的确认按钮
        self.userA.aw.click_text("群公告", dx=200)
        sleep(1)
        
        print("步骤9: 选择发送到群聊")
        self.userA.aw.click_text("发送到群聊")
        sleep(2)

        # ========== 步骤10: 断言验证 ==========
        print("步骤10: 验证群公告设置成功")
        
        # 断言: 验证"1234"在页面中存在
        # find_text_by_ocr找不到会直接assert False，用于断言"存在"
        self.userA.aw.find_text_by_ocr("1234", timeout=5)
        print("✅ 断言通过: 群公告成功设置为'1234'")

        # ========== 步骤11: 退出群组（业务流程的一部分） ==========
        print("步骤11: 退出群组")
        
        # 向下滑动找到退出群组
        self.userA.aw.swipe(270, 800, 270, 300)
        sleep(0.5)
        
        # 点击退出群组
        self.userA.aw.click_text("退出群组")
        sleep(1)
        
        # 点击转让并退出
        self.userA.aw.click_text("转让并退出")
        sleep(1)
        
        # 选择新群主（点击"转让群主"下方的第一个联系人）
        self.userA.aw.click_text("转让群主", dy=150)
        sleep(1)
        
        # 确认转让
        self.userA.aw.click_text("确定")
        sleep(2)
        
        print("步骤11: 群组已退出")

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        self.userA.logout()
