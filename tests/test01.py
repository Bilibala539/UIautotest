"""
用户实例化和日志输出验证 - 简单版本
每个文件只包含一个test方法，并包含setup()和teardown()
"""

import pytest
import logging
from config.user_data import get_random_test_user, UserData

logger = logging.getLogger(__name__)

class TestUserInstantiationSimple:
    """用户实例化简单验证测试类"""

    def setup(self):
        """
        测试方法执行前的初始化
        """
        logger.info("=" * 50)
        logger.info("开始执行用户实例化测试的setup")
        self.test_user = None
        logger.info("setup完成")
        logger.info("=" * 50)



    def test_user_instantiation_and_logging(self):
        """
        测试用户实例化和日志输出能力
        验证能够成功加载随机用户并正确记录日志
        """
        logger.info("【测试开始】验证用户实例化和日志输出功能")

        # 获取随机用户
        self.test_protected_user = get_random_test_user()

        # 验证用户对象不为空
        assert self.test_protected_user is not None, "随机用户获取失败，返回None"
        logger.info(f"✅ 成功获取随机用户: {self.test_protected_user.name} (UID: {self.test_protected_user.uid})")

        # 验证用户对象类型
        assert isinstance(self.test_protected_user, UserData), f"用户对象类型错误，期望UserData，实际: {type(self.test_protected_user)}"
        logger.debug(f"✅ 用户对象类型验证通过: {type(self.test_protected_user)}")

        # 验证必需字段存在且非空
        required_fields = ['uid', 'username', 'password', 'name', 'name_en']
        for field in required_fields:
            field_value = getattr(self.test_protected_user, field)
            assert field_value, f"用户字段 '{field}' 为空或缺失"
            logger.debug(f"✅ 字段 '{field}' 验证通过: {field_value}")

        # 验证日志输出功能 - 记录用户详细信息
        user_info = {
            'uid': self.test_protected_user.uid,
            'name': self.test_protected_user.name,
            'name_en': self.test_protected_user.name_en,
            'role': self.test_protected_user.role,
            'status': self.test_protected_user.status,
            'email': self.test_protected_user.email
        }
        logger.info(f"📋 用户详细信息: {user_info}")

        # 将用户赋值给实例变量，以便teardown中使用
        self.test_user = self.test_protected_user

        logger.info("【测试通过】用户实例化和日志输出功能验证成功")

    def teardown(self):
        """
        测试方法执行后的清理工作
        """
        logger.info("=" * 50)
        logger.info("开始执行用户实例化测试的teardown")

        if self.test_user:
            logger.info(f"清理用户数据: {self.test_user.name} (UID: {self.test_user.uid})")
            # 这里可以添加实际的清理逻辑，比如登出、删除临时数据等
            self.test_user = None

        logger.info("teardown完成")
        logger.info("=" * 50)