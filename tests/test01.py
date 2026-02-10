"""
用户实例化和日志输出验证测试用例
验证用户数据管理器能否正确加载和实例化用户对象
"""

import pytest
import logging
from config.test_data import (
    get_random_test_user,
    get_test_user_by_uid,
    get_all_test_users,
    UserData
)

logger = logging.getLogger(__name__)


class TestUserInstantiation:
    """用户实例化功能测试类"""

    def test_random_user_instantiation(self):
        """
        测试随机用户实例化功能
        验证能够成功加载并实例化随机用户对象
        """
        logger.info("开始测试随机用户实例化")

        # 获取随机用户
        user = get_random_test_user()

        # 验证用户对象不为空
        assert user is not None, "随机用户获取失败，返回None"
        logger.info(f"成功获取随机用户: {user.name} (UID: {user.uid})")

        # 验证用户对象类型
        assert isinstance(user, UserData), f"用户对象类型错误，期望UserData，实际: {type(user)}"
        logger.debug(f"用户对象类型验证通过: {type(user)}")

        # 验证必需字段存在且非空
        required_fields = ['uid', 'username', 'password', 'name', 'name_en']
        for field in required_fields:
            field_value = getattr(user, field)
            assert field_value, f"用户字段 '{field}' 为空或缺失"
            logger.debug(f"字段 '{field}' 验证通过: {field_value}")

        logger.info("随机用户实例化测试通过")

    def test_specific_user_instantiation(self):
        """
        测试特定用户实例化功能
        验证能够通过UID精确获取用户对象
        """
        logger.info("开始测试特定用户实例化")

        # 尝试获取第一个示例用户 (U001)
        user = get_test_user_by_uid("U001")

        if user is None:
            pytest.skip("测试数据中不存在UID为'U001'的用户")

        # 验证用户信息
        assert user.uid == "U001", f"UID不匹配，期望'U001'，实际: {user.uid}"
        assert user.name == "张三", f"中文姓名不匹配，期望'张三'，实际: {user.name}"
        assert user.name_en == "Zhang San", f"英文姓名不匹配，期望'Zhang San'，实际: {user.name_en}"

        logger.info(f"成功验证特定用户: {user.name} ({user.username})")
        logger.debug(f"用户完整信息: {user.to_dict()}")

        logger.info("特定用户实例化测试通过")

    def test_user_data_structure(self):
        """
        测试用户数据结构完整性
        验证所有用户都包含完整的数据结构
        """
        logger.info("开始测试用户数据结构完整性")

        all_users = get_all_test_users()

        if not all_users:
            pytest.skip("测试数据中没有用户数据")

        logger.info(f"共加载 {len(all_users)} 个用户进行验证")

        for user in all_users:
            # 验证基本字段类型
            assert isinstance(user.uid, str), f"UID应为字符串类型，实际: {type(user.uid)}"
            assert isinstance(user.username, str), f"用户名应为字符串类型，实际: {type(user.username)}"
            assert isinstance(user.password, str), f"密码应为字符串类型，实际: {type(user.password)}"
            assert isinstance(user.name, str), f"中文姓名应为字符串类型，实际: {type(user.name)}"
            assert isinstance(user.name_en, str), f"英文姓名应为字符串类型，实际: {type(user.name_en)}"

            # 验证列表和字典字段
            assert isinstance(user.permissions, list), f"权限应为列表类型，实际: {type(user.permissions)}"
            assert isinstance(user.metadata, dict), f"元数据应为字典类型，实际: {type(user.metadata)}"

            # 验证角色和状态字段的有效值
            valid_roles = {"admin", "user", "guest"}
            assert user.role in valid_roles, f"无效的角色值: {user.role}，有效值: {valid_roles}"

            valid_statuses = {"active", "inactive"}
            assert user.status in valid_statuses, f"无效的状态值: {user.status}，有效值: {valid_statuses}"

            logger.debug(f"用户 {user.uid} 数据结构验证通过")

        logger.info("所有用户数据结构验证通过")

    def test_user_to_dict_conversion(self):
        """
        测试用户对象与字典的相互转换
        验证to_dict()方法和from_dict()方法的正确性
        """
        logger.info("开始测试用户对象与字典转换")

        original_user = get_random_test_user()

        if original_user is None:
            pytest.skip("没有可用的测试用户")

        # 转换为字典
        user_dict = original_user.to_dict()
        logger.debug(f"用户对象转字典结果: {user_dict}")

        # 从字典重新创建用户对象
        recreated_user = UserData.from_dict(user_dict)

        # 验证两个对象内容一致
        assert original_user.uid == recreated_user.uid, "UID不一致"
        assert original_user.username == recreated_user.username, "用户名不一致"
        assert original_user.name == recreated_user.name, "中文姓名不一致"
        assert original_user.name_en == recreated_user.name_en, "英文姓名不一致"
        assert original_user.role == recreated_user.role, "角色不一致"
        assert original_user.status == recreated_user.status, "状态不一致"
        assert original_user.permissions == recreated_user.permissions, "权限列表不一致"
        assert original_user.metadata == recreated_user.metadata, "元数据不一致"

        logger.info("用户对象与字典转换测试通过")

    def test_logging_output_verification(self, caplog):
        """
        测试日志输出功能
        验证测试过程中的日志记录是否正常工作
        """
        logger.info("开始测试日志输出验证")

        # 执行一些操作来产生日志
        user = get_random_test_user()
        if user:
            logger.info(f"测试日志: 当前用户为 {user.name}")
            logger.debug(f"测试调试日志: 用户UID为 {user.uid}")

        # 验证日志是否被正确捕获
        assert len(caplog.records) > 0, "未捕获到任何日志记录"

        # 验证包含特定的日志消息
        log_messages = [record.getMessage() for record in caplog.records]
        has_info_log = any("测试日志:" in msg for msg in log_messages)
        has_debug_log = any("测试调试日志:" in msg for msg in log_messages)

        assert has_info_log or user is None, "未找到预期的信息级别日志"

        logger.info(f"日志输出验证完成，共捕获 {len(caplog.records)} 条日志记录")