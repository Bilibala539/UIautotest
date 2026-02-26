"""
测试数据管理模块
提供用户数据的模板定义和动态加载机制
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

import pytest

logger = logging.getLogger(__name__)


@dataclass
class UserData:
    """
    用户数据模板类
    """
    uid: str  # 登录邮箱
    password: str  # 登录密码

    name: str  # 中文姓名
    name_en: str  # 英文姓名
    name_jp: str  # 日文姓名
    phone: str  # 手机号
    role: str  # 账号类型(外包/正职...)
    department: str  # 所属部门

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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserData':
        """从字典创建用户对象（严格校验必需字段）"""
        required = ["uid", "username", "password", "name", "name_en"]
        for field in required:
            if field not in data:
                raise ValueError(f"缺少必需字段: {field}")
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class UserManager:
    """
    精简用户管理器
    仅负责加载用户数据和登录验证
    """

    def __init__(self, data_file_path: str = "config/users_info.json"):
        self.data_file_path = data_file_path
        self._users: Optional[Dict[str, UserData]] = None  # username -> UserData

    def _load_users(self) -> Dict[str, UserData]:
        """从 JSON 文件加载用户"""
        try:
            with open("config/users_info.json", 'r', encoding='utf-8') as f:
                raw_list = json.load(f)

            if not isinstance(raw_list, list):
                raise ValueError("用户数据必须是列表")

            users = {}
            for item in raw_list:
                try:
                    user = UserData.from_dict(item)
                    users[user.username] = user
                except Exception as e:
                    logger.warning(f"跳过无效用户: {e}")
            return users

        except (json.JSONDecodeError, ValueError, OSError) as e:
            logger.error(f"加载用户数据失败: {e}")
            raise RuntimeError("无法加载用户数据") from e



    def get_user_by_username(self, uid):
        """按用户名获取用户"""
        if self._users is None:
            self._users = self._load_users()
        return self._users.get(uid)



def test_login():
    print(f"123132213321312132{UserManager.get_user_by_username(UserManager(),'zhang.wei@company.com')}")