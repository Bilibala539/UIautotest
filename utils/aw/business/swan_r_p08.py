"""Swan 回归 P08 包（M13 个人中心）新增业务方法 mixin。

tcbatch 批量转换产出；挂入 SwanBusiness MRO 的集成由大领导统一执行。
定位口径：OCR 文本优先（click_text/text_exists/find_text_by_ocr）；
图像模板仅用 image/image_name_mapping.py 已注册常量；
坐标点击/运行期语义键一律不用。
"""
from __future__ import annotations

import numpy as np

from image.image_name_mapping import (
    SWAN_FAV_FAMILY_GROUP_ROW,
    SWAN_FAV_MUSIC_GROUP_ROW,
    SWAN_ME_ACCOUNT_ENTRY,
    SWAN_ME_DEVICE_MANAGE_ROW,
    SWAN_ME_FAVORITES_ROW,
    SWAN_ME_FAMILY_MANAGE_ROW,
    SWAN_ME_SCAN_ICON,
    SWAN_ME_SOUND_QUALITY_ROW,
    SWAN_PERSON_LOGOUT_BTN,
    SWAN_PROFILE_EDIT_DONE,
    SWAN_SOUND_QUALITY_DONE_BUTTON,
)


class SwanRP08Mixin:
    """M13 个人中心域业务方法（P08 包新增）。"""

    # ---------- 导航 ----------

    def open_me_page(self) -> None:
        """确保登录态后切底部「我的」Tab（到位锚 收藏行 [图]，go_bottom_tab 内建断言）。"""
        self.user.ensure_logged_in_on_home()
        self.user.go_bottom_tab("我的")

    def open_person_info(self) -> None:
        """我的页顶卡用户区 [图] → 个人信息页（到位锚「退出登入」[图]）。"""
        self.user.click_image(SWAN_ME_ACCOUNT_ENTRY)
        self.user.image_exists(SWAN_PERSON_LOGOUT_BTN, timeout=10)

    def assert_on_person_info(self, timeout: int = 10) -> None:
        """断言当前在个人信息页（「退出登入」[图] 可见）。"""
        self.user.image_exists(SWAN_PERSON_LOGOUT_BTN, timeout=timeout)

    def back_to_me_page(self, timeout: int = 10) -> None:
        """返回键回我的页（到位锚 收藏行 [图]）。"""
        self.user.press_back()
        self.user.image_exists(SWAN_ME_FAVORITES_ROW, timeout=timeout)

    # ---------- 我的页行滚动与进入 ----------

    def me_row_scroll_until(self, text: str, max_swipes: int = 4) -> bool:
        """向下滚动直到 OCR 见到行文本；max_swipes 次后仍未见返回 False。"""
        for _ in range(max_swipes):
            if self.user.find_text_by_ocr(text, timeout=1) is not None:
                return True
            self.user.swipe_up(400)
        return self.user.find_text_by_ocr(text, timeout=1) is not None

    def me_row_image_scroll_until(self, template: str, max_swipes: int = 4) -> bool:
        """向下滚动直到行模板 [图] 命中（用于标题行/可点行重名的行）。"""
        for _ in range(max_swipes):
            if self.user.probe_image(template, timeout=1) is not None:
                return True
            self.user.swipe_up(400)
        return self.user.probe_image(template, timeout=1) is not None

    def open_me_row_image(self, template: str, max_swipes: int = 4) -> None:
        """滚动到我的页模板行 [图] 并点击（到位断言由调用方执行）。"""
        assert self.me_row_image_scroll_until(template, max_swipes), "我的页未滚动到目标行 [图]"
        self.user.click_image(template)

    def assert_me_rows_rendered(self, texts, max_swipes: int = 5) -> None:
        """逐行滚动断言我的页功能行全部渲染（三功能区冒烟）。"""
        for text in texts:
            assert self.me_row_scroll_until(text, max_swipes), f"我的页缺行「{text}」"

    def me_top_nickname(self) -> str:
        """OCR 读取我的页顶卡昵称（手机号文本块正上方最近文本块）。"""
        items = self.ocr_scan_page()
        target = None
        for it in items:
            if self.user.phone and self.user.phone in str(it.get("text", "")):
                target = it
                break
        assert target is not None, "我的页顶卡未 OCR 到手机号文本块"
        raw = str(target["text"])
        if raw.strip() != self.user.phone:
            # 昵称与手机号被 OCR 合并进同一文本块：剥出手机号即昵称
            merged = raw.replace(self.user.phone, "").strip()
            if merged:
                return merged
        best, best_dy = None, None
        for it in items:
            if it is target:
                continue
            dy = target["cy"] - it["cy"]
            if dy <= 4:
                continue
            if best_dy is None or dy < best_dy:
                best, best_dy = it, dy
        assert best is not None, "我的页顶卡未 OCR 到昵称文本块"
        return str(best["text"])

    def me_top_bar_text(self, text: str, timeout: int = 2) -> bool:
        """顶部 12% 区域 OCR 探测文本（毛玻璃标题栏渐显判定，排除底部 Tab 同名文案）。"""
        img = self.take_screenshot()
        if img is None:
            return False
        h, w = img.shape[:2]
        region = (0, 0, w, int(h * 0.12))
        return self.user.find_text_by_ocr(text, timeout=timeout, region=region) is not None

    # ---------- 通用可达/防截屏判据 ----------

    def assert_page_not_blank(self) -> None:
        """截图非空白（纯色空页像素方差≈0）：未探索页/WebView 的兜底可达判据。"""
        img = self.take_screenshot()
        assert img is not None, "截图失败（页面不可截）"
        assert float(img.std()) > 1.0, "页面疑似空白（截图像素方差过低）"

    def screen_capture_blocked(self) -> bool:
        """FLAG_SECURE 防截屏判据：截图返回 None 或近全黑（知识库实测口径）。"""
        img = self.take_screenshot()
        if img is None:
            return True
        return bool(np.mean(img) < 3.0)

    def assert_screen_capture_blocked(self) -> None:
        """断言当前页已进入防截屏态（修改密码页 FLAG_SECURE，反向判据）。"""
        assert self.screen_capture_blocked(), "页面未进入防截屏态（截图可读）"

    # ---------- 扫一扫 ----------

    def open_scan_page(self) -> None:
        """顶卡扫一扫图标 [图] → 扫码页（到位判据 OCR 标题「扫一扫」）。"""
        self.user.click_image(SWAN_ME_SCAN_ICON)
        self.user.text_exists("扫一扫", timeout=10)

    def handle_camera_permission(self, allow: bool) -> bool:
        """系统相机权限弹窗处置（ROM 文案变体轮询）；弹窗未出现返回 False。"""
        if allow:
            texts = ("允许", "仅在使用中允许", "使用应用时允许", "使用软件时允许",
                     "While using the app")
        else:
            texts = ("拒绝", "不允许", "禁止", "Don't allow")
        for text in texts:
            if self.user.find_text_by_ocr(text, timeout=1) is not None:
                self.user.click_text(text, timeout=2)
                return True
        return False

    # ---------- 音质设置弹层 ----------

    def open_quality_sheet(self) -> None:
        """我的页「音质设置」行 [图] → 底部弹层（判据 OCR 档位文案）。"""
        self.open_me_row_image(SWAN_ME_SOUND_QUALITY_ROW)
        self.user.assert_any_text(["流畅音质"], timeout=10)

    def assert_quality_tiers(self) -> None:
        """断言四档单选行全部渲染（流畅/标准/HQ/SQ）。"""
        for tier in ("流畅音质", "标准音质", "HQ高品质", "SQ无损音质"):
            self.user.text_exists(tier, timeout=3)

    def select_quality_tier(self, tier: str) -> None:
        """点击音质档位单选行（OCR 文案定位）。"""
        self.user.click_text(tier, timeout=5)

    def confirm_quality_sheet(self) -> None:
        """弹层右上角红字「完成」[图] 提交并关闭（关闭后档位行不可见）。"""
        self.user.click_image(SWAN_SOUND_QUALITY_DONE_BUTTON)
        self.user.text_not_exists("流畅音质", timeout=5)

    def close_quality_sheet_by_back(self) -> None:
        """back 键关闭弹层——蒙层无文本不可 OCR 定位，back 为等效免坐标替代。"""
        self.user.press_back()
        self.user.text_not_exists("流畅音质", timeout=5)

    # ---------- 资料编辑（个人信息页行） ----------

    def open_edit_nickname(self) -> None:
        """个人信息页「昵称」行 → 修改昵称页（到位判据 OCR 标题「修改昵称」）。"""
        self.user.click_text("昵称")
        self.user.text_exists("修改昵称", timeout=10)

    def focus_nickname_input(self, current: str) -> None:
        """点击预填当前昵称的输入框取得焦点（current 为运行时读取的昵称值）。"""
        self.user.click_text(current, timeout=5)

    def exit_edit_page_without_save(self) -> None:
        """不提交退出昵称编辑页，逐级回退稳定落到我的页。

        首 back 可能仅收起输入法键盘（Android 惯例），故按落点逐级判定：
        编辑页（标题「修改昵称」仍在）→ 再退；个人信息页（「注销账号」可见）→ 回我的页。
        绝不点「完成」，杜绝误保存。
        """
        self.user.press_back()
        self.user.press_back()
        if self.user.find_text_by_ocr("修改昵称", timeout=2) is not None:
            self.user.press_back()
        if self.user.find_text_by_ocr("注销账号", timeout=2) is not None:
            self.back_to_me_page()

    def open_edit_password(self) -> None:
        """个人信息页「密码」行 → 修改密码页（FLAG_SECURE：截图失效即到位判据）。"""
        self.user.click_text("密码")
        self.assert_screen_capture_blocked()

    def open_binding_manage_if_present(self) -> bool:
        """个人信息页「账号绑定管理」行条件进入（无绑定态该行隐藏）；未渲染返回 False。"""
        if self.user.find_text_by_ocr("账号绑定管理", timeout=2) is None:
            return False
        self.user.click_text("账号绑定管理")
        self.assert_page_not_blank()
        return True

    # ---------- 其它入口页 ----------

    def open_family_page(self) -> None:
        """「家庭管理」行 → 家庭页（到位判据 OCR「我的家庭」）。"""
        assert self.me_row_scroll_until("家庭管理"), f"我的页未滚动到行「家庭管理」"
        self.user.click_text("家庭管理")
        self.user.assert_any_text(["我的家庭"], timeout=10)

    def open_favorites_page(self) -> None:
        """「SWAN收藏」行 → 收藏页（到位锚 分组行 [图]，兜底 OCR 分组标题）。"""
        assert self.me_row_scroll_until("SWAN收藏"), f"我的页未滚动到行「SWAN收藏」"
        self.user.click_text("SWAN收藏")
        if self.user.probe_image(SWAN_FAV_MUSIC_GROUP_ROW, timeout=3) is None and \
                self.user.probe_image(SWAN_FAV_FAMILY_GROUP_ROW, timeout=3) is None:
            self.user.assert_any_text(["我的音乐", "我的家庭"], timeout=5)

    def about_version_text(self) -> str | None:
        """OCR 提取关于页版本行（含「版本」关键字的文本项；两行由框架记录留档）。"""
        for it in self.ocr_scan_page():
            if "版本" in str(it.get("text", "")):
                return str(it["text"])
        return None

    def open_help_page(self) -> None:
        """「帮助与反馈」行 → 帮助页（到位判据 OCR 入口行；行需滚动脱离播放条遮挡）。"""
        assert self.me_row_scroll_until("帮助与反馈"), f"我的页未滚动到行「帮助与反馈」"
        self.user.click_text("帮助与反馈")
        self.user.assert_any_text(["使用说明", "常见问题"], timeout=10)

    def open_local_music_page(self) -> bool:
        """「本地音乐」行 → 本地音乐库页壳；行未渲染（坑19 漂移）返回 False 交用例裁决。"""
        if not self.me_row_scroll_until("本地音乐"):
            return False
        self.user.click_text("本地音乐")
        self.assert_page_not_blank()
        return True

    def open_recharge_record(self) -> None:
        """「充值与消费记录」行 → 充值记录页（页未探索，空白断言兜底）。"""
        assert self.me_row_scroll_until("充值与消费记录"), f"我的页未滚动到行「充值与消费记录」"
        self.user.click_text("充值与消费记录")
        self.assert_page_not_blank()

    def open_device_setting(self) -> None:
        """「设备管理」行 [图]（标题行与可点行重名，OCR 有歧义走模板）→ 设备设置页。"""
        self.open_me_row_image(SWAN_ME_DEVICE_MANAGE_ROW)
        self.assert_page_not_blank()
