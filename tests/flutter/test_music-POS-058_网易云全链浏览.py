# CASE-ID: music-POS-058
"""Swan 回归·M07 网易云:授权后内容浏览全链(music-POS-058)。

步骤→AW 映射(7.3 网易云四页族链,已授权账号全程只读浏览):
  1. 平台 Tab→网易云主页 → open_platform_home("netease")(已授权,无
     授权弹层误弹→assert_no_auth_error)
  2. 每日推荐双 Tab+风格面板(POS-017 链)→ click 每日推荐→断言双 Tab
     →切风格推荐→断言曲风族→条件返回主页
  3. 歌单分类→子 Tab 首项「流行」(POS-018/021 链,KB region 限定裸词)
     →标题透传断言→条件返回主页(两级栈兜底)
  4. 我的歌单(POS-023 自适应入口,字面探测→自建歌单卡兜底,空态合法)
  5. 逐级返回至平台 Tab → back_to_platform_page(条件返回,根级禁盲返)

cleanup: 无(全程只读浏览);框架每用例冷启动。
B 标定说明:复用网易云主页/分类页知识库锚,无新增模板需求;服务端
内容轮换致区块缺失时以显式断言暴露。
"""

from __future__ import annotations

from conftest import BaseTest


class TestMusicPos058NeteaseFullChain(BaseTest):
    """已授权账号平台入口→内容族→个人数据页全链浏览闭环可用。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_full_browse_chain(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:进网易云主页(已授权,无授权弹层误弹)
        self.userA.open_platform_home("netease")
        self.userA.assert_no_auth_error()
        # 步骤 2:每日推荐双 Tab + 风格面板(POS-017 链)
        self.userA.click_text("每日推荐", timeout=8)
        self.userA.assert_any_text(["默认推荐", "风格推荐"])
        self.userA.click_text("风格推荐", timeout=6)
        self.userA.assert_any_text(["流行", "民谣", "摇滚", "电子", "曲风"])
        self.userA.press_back()  # 子级页 1 次返回主页(KB 实测)
        assert self.userA.find_text_by_ocr("每日推荐", timeout=6) is not None, (
            "风格面板返回后未回到网易云主页(返回栈异常)")
        # 步骤 3:歌单分类 → 子 Tab 首项「流行」→ 返回(POS-018/021 链)
        self.userA.click_text("歌单", timeout=8, region=(0, 300, 160, 1312))
        self.userA.click_text("流行", timeout=8)
        assert self.userA.find_text_by_ocr("流行", timeout=10) is not None, (
            "分类详情标题未渲染入参「流行」(参数透传失效或页面未打开)")
        self.userA.press_back()  # 子 Tab 切换非压栈,1 次即回主页
        if self.userA.find_text_by_ocr("每日推荐", timeout=3) is None:
            self.userA.press_back()  # 分类详情→分类页 两级栈兜底
        assert self.userA.find_text_by_ocr("每日推荐", timeout=6) is not None, (
            "歌单分类返回后未回到网易云主页(返回栈异常)")
        # 步骤 4:我的歌单(自适应入口,空态为合法态)
        self.userA.scroll_to_text("用户收藏")
        if self.userA.find_text_by_ocr("我的歌单", timeout=3) is not None:
            self.userA.click_text("我的歌单", timeout=4)
        else:
            self.userA.click_text("自建歌单", timeout=5)
        self.userA.assert_any_text(["自建歌单", "我的歌单", "歌单"])
        self.userA.assert_no_auth_error()
        # 步骤 5:逐级返回至平台 Tab
        self.userA.back_to_platform_page()
        self.userA.assert_no_auth_error()
