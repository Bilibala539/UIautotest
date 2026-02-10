"""
测试数据管理模块
提供用户数据的模板定义和动态加载机制
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserData:
    """
    用户数据模板类
    定义用户信息的标准结构
    """
    uid: str  # 用户唯一标识
    username: str  # 用户名/邮箱/手机号
    password: str  # 登录密码
    name: str  # 中文姓名
    name_en: str  # 英文姓名
    phone: str  # 手机号
    email: str  # 邮箱地址
    role: str  # 用户角色 (admin/user/guest)
    status: str  # 账号状态 (active/inactive)
    department: str  # 所属部门
    company: str  # 所属公司
    created_at: str  # 创建时间
    last_login: str  # 最后登录时间
    permissions: List[str]  # 权限列表
    metadata: Dict[str, Any]  # 其他元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserData':
        """从字典创建用户对象"""
        # 确保必需字段存在
        required_fields = ['uid', 'username', 'password', 'name', 'name_en']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必需字段: {field}")

        # 处理可选字段，提供默认值
        defaults = {
            'phone': '',
            'email': '',
            'role': 'user',
            'status': 'active',
            'department': '',
            'company': '',
            'created_at': '',
            'last_login': '',
            'permissions': [],
            'metadata': {}
        }

        # 合并数据和默认值
        merged_data = {**defaults, **data}

        # 确保列表类型字段正确
        if not isinstance(merged_data['permissions'], list):
            merged_data['permissions'] = []
        if not isinstance(merged_data['metadata'], dict):
            merged_data['metadata'] = {}

        return cls(**merged_data)


class TestDataManager:
    """
    测试数据管理器
    负责从外部文件加载用户数据并在需要时实例化
    """

    def __init__(self, data_file_path: str = "config/test_users.json"):
        """
        初始化数据管理器

        Args:
            data_file_path: 用户数据文件路径
        """
        self.data_file_path = data_file_path
        self._users_cache: Optional[List[UserData]] = None
        self._users_dict: Optional[Dict[str, UserData]] = None

    def _load_users_from_file(self) -> List[UserData]:
        """
        从JSON文件加载用户数据

        Returns:
            List[UserData]: 用户对象列表

        Raises:
            FileNotFoundError: 数据文件不存在
            ValueError: 数据格式无效
            json.JSONDecodeError: JSON解析失败
        """
        if not os.path.exists(self.data_file_path):
            # 如果文件不存在，创建示例文件
            self._create_sample_data_file()
            logger.warning(f"用户数据文件不存在，已创建示例文件: {self.data_file_path}")

        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            if not isinstance(raw_data, list):
                raise ValueError("用户数据文件必须包含用户对象数组")

            users = []
            for i, user_data in enumerate(raw_data):
                try:
                    user_obj = UserData.from_dict(user_data)
                    users.append(user_obj)
                except (ValueError, TypeError) as e:
                    logger.warning(f"跳过无效用户数据 (索引 {i}): {e}")
                    continue

            if not users:
                logger.warning("用户数据文件中没有有效的用户数据")

            return users

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise ValueError(f"用户数据文件格式无效: {self.data_file_path}")
        except Exception as e:
            logger.error(f"加载用户数据失败: {e}")
            raise

    def _create_sample_data_file(self):
        """创建示例用户数据文件"""
        sample_users = [
            {
                "uid": "U001",
                "username": "testuser001@example.com",
                "password": "SecurePass123!",
                "name": "张三",
                "name_en": "Zhang San",
                "phone": "13800138001",
                "email": "testuser001@example.com",
                "role": "user",
                "status": "active",
                "department": "技术部",
                "company": "测试公司",
                "created_at": "2024-01-01T00:00:00Z",
                "last_login": "2026-02-10T10:00:00Z",
                "permissions": ["read", "write"],
                "metadata": {
                    "test_environment": "staging",
                    "account_type": "automated_test"
                }
            },
            {
                "uid": "U002",
                "username": "admin@example.com",
                "password": "AdminPass456!",
                "name": "李四",
                "name_en": "Li Si",
                "phone": "13800138002",
                "email": "admin@example.com",
                "role": "admin",
                "status": "active",
                "department": "管理部",
                "company": "测试公司",
                "created_at": "2024-01-01T00:00:00Z",
                "last_login": "2026-02-10T10:00:00Z",
                "permissions": ["read", "write", "delete", "admin"],
                "metadata": {
                    "test_environment": "production",
                    "account_type": "admin_test"
                }
            },
            {
                "uid": "U003",
                "username": "guest@example.com",
                "password": "GuestPass789!",
                "name": "王五",
                "name_en": "Wang Wu",
                "phone": "13800138003",
                "email": "guest@example.com",
                "role": "guest",
                "status": "active",
                "department": "访客",
                "company": "外部合作方",
                "created_at": "2024-01-01T00:00:00Z",
                "last_login": "2026-02-10T10:00:00Z",
                "permissions": ["read"],
                "metadata": {
                    "test_environment": "demo",
                    "account_type": "guest_test"
                }
            }
        ]

        # 确保目录存在
        os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)

        with open(self.data_file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_users, f, ensure_ascii=False, indent=2)

        logger.info(f"已创建示例用户数据文件: {self.data_file_path}")

    def get_all_users(self) -> List[UserData]:
        """获取所有用户（带缓存）"""
        if self._users_cache is None:
            self._users_cache = self._load_users_from_file()
        return self._users_cache.copy()

    def get_user_by_uid(self, uid: str) -> Optional[UserData]:
        """根据UID获取用户"""
        if self._users_dict is None:
            users = self.get_all_users()
            self._users_dict = {user.uid: user for user in users}
        return self._users_dict.get(uid)

    def get_users_by_role(self, role: str) -> List[UserData]:
        """根据角色获取用户"""
        users = self.get_all_users()
        return [user for user in users if user.role == role]

    def get_active_users(self) -> List[UserData]:
        """获取活跃用户"""
        users = self.get_all_users()
        return [user for user in users if user.status == "active"]

    def get_random_user(self, role: Optional[str] = None, status: Optional[str] = None) -> Optional[UserData]:
        """
        获取随机用户

        Args:
            role: 可选的角色过滤
            status: 可选的状态过滤

        Returns:
            UserData: 随机用户对象，如果没有符合条件的用户返回None
        """
        import random

        users = self.get_all_users()

        if role:
            users = [user for user in users if user.role == role]
        if status:
            users = [user for user in users if user.status == status]

        if not users:
            return None

        return random.choice(users)

    def reload_data(self):
        """重新加载数据（清除缓存）"""
        self._users_cache = None
        self._users_dict = None
        logger.info("用户数据缓存已清除")


# 全局数据管理器实例
_test_data_manager = TestDataManager()


# 便捷函数
def get_all_test_users() -> List[UserData]:
    """获取所有测试用户"""
    return _test_data_manager.get_all_users()


def get_test_user_by_uid(uid: str) -> Optional[UserData]:
    """根据UID获取测试用户"""
    return _test_data_manager.get_user_by_uid(uid)


def get_test_users_by_role(role: str) -> List[UserData]:
    """根据角色获取测试用户"""
    return _test_data_manager.get_users_by_role(role)


def get_active_test_users() -> List[UserData]:
    """获取活跃测试用户"""
    return _test_data_manager.get_active_users()


def get_random_test_user(role: Optional[str] = None, status: Optional[str] = None) -> Optional[UserData]:
    """获取随机测试用户"""
    return _test_data_manager.get_random_user(role, status)


def reload_test_data():
    """重新加载测试数据"""
    _test_data_manager.reload_data()
