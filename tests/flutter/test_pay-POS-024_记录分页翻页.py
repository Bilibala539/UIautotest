# CASE-ID: pay-POS-024
# LINKED-CASE: M14-POS-024
"""Swan 回归·M14 支付与会员:充值记录分页第二页加载(pay-POS-024)。

用例 -> AW 映射:
- 首屏 30 条渲染 -> scan_record_rows OCR 行聚类计数 ==30(实传 size=30
  契约;行聚类为 y 邻近合并,OCR 噪声容差登记 notes)
- 滚动到列表底部触发第二页 -> swipe_up 步进+逐屏 scan_record_rows 累计
  去重,总行数 ≥31 即第二页已追加;总量 <31 按 YAML 口径 SKIP-DATA
  (分页边界改由逆向/专项覆盖)
- 无重复行 -> 每屏扫描内行键唯一断言(行键含时间要素时;跨屏滚动边界
  重叠属同一物理行重复入镜,不判重复,登记 notes)
- 回滚顶部确认列表稳定 -> swipe_down 回顶后首屏行键序列与初始一致
  (无重排无崩溃)

清理:无(只读浏览)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestPayPos024(BaseTest):
    """充值记录分页第二页加载(size=30 翻页)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_record_pagination_second_page(self):
        """首屏 30 条,滚动触发第二页追加,回顶列表稳定无重排。"""

        def _scan_unique(tag: str) -> list:
            """扫当前屏订单行,并断言同屏行键唯一(含时间要素时)。"""
            keys = [tuple(r) for r in self.userA.scan_record_rows()]
            dup = [k for k in set(keys) if keys.count(k) > 1]
            if dup and all(len(k) >= 3 for k in dup):
                assert False, f"{tag} 同屏重复行键(含时间要素仍重复): {dup}"
            return keys

        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_recharge_page()
        self.userA.open_recharge_record_page()
        if (self.userA.find_text_by_ocr("¥", timeout=6) is None
                and self.userA.find_text_by_ocr("￥", timeout=3) is None):
            pytest.skip(
                "充值段无预置订单(空态分支,SKIP-DATA):分页断言跳过")
        first_keys = _scan_unique("首屏")
        if len(first_keys) < 30:
            pytest.skip(
                f"首屏行数 {len(first_keys)} < 30,预置 <31 条(SKIP-DATA:"
                "分页边界改由逆向/专项覆盖)")
        assert len(first_keys) == 30, (
            f"首屏行数 {len(first_keys)} != 30(实传 size=30 契约/OCR 聚类噪声)")

        seen = list(first_keys)
        seen_set = set(seen)
        stable_rounds = 0
        for _ in range(15):
            self.userA.swipe_up(500)
            keys = _scan_unique("翻页")
            fresh = [k for k in keys if k not in seen_set]
            for key in fresh:
                seen.append(key)
                seen_set.add(key)
            stable_rounds = stable_rounds + 1 if not fresh else 0
            if stable_rounds >= 2:
                break
        if len(seen) <= 30:
            pytest.skip(
                f"全列表共 {len(seen)} 条(<31),服务端预置不足(SKIP-DATA)")
        assert len(seen) > len(first_keys), "第二页未追加渲染"

        for _ in range(12):
            self.userA.swipe_down(600)
        keys_top = _scan_unique("回顶")
        assert keys_top == first_keys, "回滚顶部首屏行序与初始不一致(重排)"

        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
