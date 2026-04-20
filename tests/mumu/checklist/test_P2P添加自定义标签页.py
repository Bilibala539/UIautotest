"""
测试用例: P2P会话成员添加自定义标签页
探索来源: AI自主探索POPO App生成
探索补全: 通过自主探索发现P2P设置→标签页→+号→添加链接的完整路径
"""
from conftest import BaseTest


class TestP2PAddCustomTabPage(BaseTest):
    """P2P会话成员添加自定义标签页测试类"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_add_custom_tab_page(self):
        """
        测试场景: P2P会话中添加自定义标签页
        预期结果: 标签页成功添加，标签页列表中显示新增的标签页

        操作路径: 消息列表→搜索联系人→进入P2P聊天→设置→标签页→+→添加链接
        """
        tab_name = "自动化测试标签页"
        result = self.userA.add_custom_tab_page(
            recipient="grp.popoqa50",
            tab_name=tab_name,
            link_url="https://www.163.com"
        )
        assert result, "添加自定义标签页应该成功"

    def teardown(self):
        """测试后清理 - 删除新添加的标签页"""
        try:
            self.userA.remove_custom_tab_page("grp.popoqa50", "自动化测试标签页")
        except Exception:
            pass
