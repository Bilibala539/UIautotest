"""
测试数据管理
包含账号池、测试数据等
"""

# 账号池 - 用于随机登录
ACCOUNT_POOL = [
    {
        "username": "testuser001@example.com",
        "password": "Password123!",
        "display_name": "Test User 001"
    },
    {
        "username": "testuser002@example.com",
        "password": "Password456!",
        "display_name": "Test User 002"
    },
    {
        "username": "testuser003@example.com",
        "password": "Password789!",
        "display_name": "Test User 003"
    },
    {
        "username": "testuser004@example.com",
        "password": "SecurePass123!",
        "display_name": "Test User 004"
    },
    {
        "username": "testuser005@example.com",
        "password": "MySecurePass456!",
        "display_name": "Test User 005"
    }
]

# 测试数据常量
TEST_DATA = {
    "valid_email_domains": ["@example.com", "@test.com"],
    "invalid_passwords": ["123", "abc", "short"],
    "valid_usernames": ["user123", "test_user", "demo_account"],
    "search_keywords": ["test", "demo", "sample"]
}