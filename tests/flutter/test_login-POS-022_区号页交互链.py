# CASE-ID: login-POS-022
"""Swan 回归·会话与登录:区号页交互链 跳段/回填/复位(login-POS-022 可自动化面)。

步骤→AW 映射:
1. 填手机号(为步骤 9 保留面前置) → 进区号页(open_area_page);
2. 热门区呈现:中国行 [图] + 「中国香港」「中国澳门」「中国台湾」[OCR];
   索引条呈现:index_bar_letters 单字母 OCR 探针(≥3 个);
3. 滚动遍历(swipe_up 距离式滑动 ×≤60)+ 行语义抽查(滚动页 OCR 恒有 +NNN
   区号行,行=国家名+区号两段式);
4. 滚动定位 +998 行(乌兹别克斯坦)点击 → 自动返回登录页 + 区号回填 +998;
5. 重进区号页点中国行([图]) → +86 复位 + 手机号保留([OCR] 完整号码仍在)。
注(回填/缺口面,登记 report):S4 行总数=235 需 area-rows-all.txt 清单核对;
S5 索引条拖拽跳段需索引条模板(drag_on_template 依赖注册模板,OCR 无法给矩形);
S6/S7 穿透选中存疑记录面(NEG-011 承载);S10/S11 断网兜底需系统级飞行模式
控制(框架无此通道)。
cleanup: 区号已复位 +86(步骤 5);手机号由冷启动模型清空。
"""
from __future__ import annotations

import re

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_AREA_CODE_CHINA_ROW
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestAreaPageInteractionChain(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_area_page_interaction_chain(self) -> None:
        # 步骤 1-2:进区号页,热门区 + 索引条呈现
        self.userA.ensure_fresh_sms_form()
        self.userA.fill_phone_number(self.userA.phone)
        self.userA.open_area_page("+86")
        assert self.userA.find_image(SWAN_AREA_CODE_CHINA_ROW, timeout=5) is not None, (
            "热门区中国行未呈现")
        assert self.userA.find_text_by_ocr("中国香港", timeout=3) is not None, (
            "热门区中国香港行未呈现")
        assert self.userA.find_text_by_ocr("中国澳门", timeout=3) is not None, (
            "热门区中国澳门行未呈现")
        assert self.userA.find_text_by_ocr("中国台湾", timeout=3) is not None, (
            "热门区中国台湾行未呈现")
        letters = self.userA.index_bar_letters(timeout=5)
        assert len(letters) >= 3, f"索引条单字母 OCR 探针不足(索引条未呈现?): {letters}"
        # 步骤 3-4:滚动遍历 + 行语义抽查 + 定位 +998 行
        found_998 = False
        for _ in range(60):
            if self.userA.find_text_by_ocr("+998", timeout=2) is not None:
                found_998 = True
                break
            page_codes = [
                item.get("text", "") for item in self.userA.ocr_scan_page()
                if re.search(r"\+\d{3}", item.get("text", ""))
            ]
            assert page_codes, "滚动页无任何区号行(行=国家名+区号语义缺失)"
            self.userA.swipe_up()
        assert found_998, "滚动 60 次未定位到 +998 行(乌兹别克斯坦)"
        self.userA.click_text("+998", timeout=10)
        assert self.userA.find_text_by_ocr("选择归属地", timeout=5) is None, (
            "点击 +998 行后未自动返回登录页")
        assert self.userA.find_text_by_ocr("+998", timeout=5) is not None, (
            "+998 行选中后区号未回填")
        # 步骤 5:重进区号页复位中国 +86,手机号保留
        self.userA.open_area_page("+998")
        self.userA.select_china_area_row()
        assert self.userA.find_text_by_ocr("+86", timeout=5) is not None, (
            "中国行选中后区号未恢复 +86")
        assert self.userA.find_text_by_ocr(self.userA.phone, timeout=5) is not None, (
            "区号往返后手机号被清空")
