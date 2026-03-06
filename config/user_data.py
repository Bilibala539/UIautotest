import json
import random
from typing import Optional, List, Tuple, Dict
from pathlib import Path

JSON_FILE_PATH = "users_info.json"


class User:
    def __init__(self, uid: str, password: str, name: str, name_en: str, name_jp: str, phone: str, role: str,
                 department: str):
        self.uid = uid
        self.password = password
        self.name = name
        self.name_en = name_en
        self.name_jp = name_jp
        self.phone = phone
        self.role = role
        self.department = department

    def __repr__(self):
        return f"UserData(uid='{self.uid}', name='{self.name}', department='{self.department}')"


class UserManager:
    def __init__(self, json_path: str = JSON_FILE_PATH):
        self._users: Optional[Dict[str, User]] = None
        self._user_list: Optional[List[User]] = None
        self._json_path = json_path

    def _load_users(self):
        if self._users is not None:
            return  # 已加载，避免重复读取

        with open(self._json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self._users = {}
        self._user_list = []
        for item in data:
            user = User(**item)
            self._users[user.uid] = user
            self._user_list.append(user)

    def get_user_by_uid(self, uid: str) -> Optional[User]:
        self._load_users()
        return self._users.get(uid)

    def get_one_random_userinfo(self):
        self._load_users()
        if not self._user_list:
            return None
        return random.choice(self._user_list)

    def get_two_random_userinfo(self) -> Optional[Tuple[User, User]]:
        self._load_users()
        if len(self._user_list) < 2:
            return None
        return tuple(random.sample(self._user_list, 2))

# if __name__ == "__main__":
#     manager = UserManager("users_info.json")
#
#     # 1. 按 UID 查询
#     user1 = manager.get_user_by_uid("zhang.wei@company.com")
#     print("按 UID 查询:", user1)
#
#     # 2. 随机一个用户
#     rand_user = manager.get_random_userinfo()
#     print("随机用户:", rand_user)
#
#     # 3. 随机两个不同用户
#     two_users = manager.get_two_random_userinfo()
#     print("两个随机不同用户:", two_users)
