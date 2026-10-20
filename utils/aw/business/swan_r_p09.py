"""Swan 回归 P09 包 mixin(M14 支付与会员 + M15 帮助与反馈)。

批量转换批次 TCBATCH1(2026-10-20)新增包级业务方法,服务 wt-P09 包全部
转换用例(pay-*/help-*)。集成说明:本文件为纯 mixin,由集成方统一挂入
SwanBusiness MRO 后 userA 方可直调(tcbatch_check.py 按此口径静态检查);
严禁自行修改 utils/aw/business/swan.py 等存量文件。

方法口径:本 mixin 只编排基础 AW 层操作(OCR 点击/断言/滑动/输入),
跨页导航(底部/顶部 Tab、设备页)由用例层先经既有业务方法完成——方法
docstring 均标注所在页面前置。定位锚出处:knowledge/swan/pages/swan_平台页、
swan_我的页、swan_帮助与反馈页、swan_关于与升级页、swan_AI对话页 实测;
充值页/充值记录页/权益中心 H5 为未探索页,细粒度锚登记于
package_report.json template_needs。
"""
from __future__ import annotations


class SwanRP09Mixin:
    """M14 支付与会员 + M15 帮助与反馈 包级业务方法(仅新增,不改存量)。"""

    def _assert_any_anchor(self, texts, timeout: int = 10) -> str:
        """OCR 断言任一文案出现,返回命中文案(包内 assert_any_text 等价)。"""
        for text in texts:
            if self.find_text_by_ocr(text, timeout=1) is not None:
                return text
        assert False, f"OCR 均未找到任一文案: {list(texts)}"

    # ---------- 我的页行入口(M14/M15 共用前置) ----------

    def open_me_row(self, row: str) -> None:
        """我的页点击功能行(权益中心/帮助与反馈/关于与升级等)。

        前置:调用方已 go_bottom_tab("我的") 停在我的页。底部播放条遮挡
        下半区行项(知识库 swan_我的页:帮助与反馈未滚动时被 bottom_player
        遮挡)——先直接 OCR 点,不可见则上滑后再点,至多两轮。
        """
        if self.find_text_by_ocr(row, timeout=4) is not None:
            self.click_text(row, timeout=4)
            return
        self.swipe_up()
        if self.find_text_by_ocr(row, timeout=4) is not None:
            self.click_text(row, timeout=4)
            return
        self.swipe_up()
        self.click_text(row, timeout=6)

    # ---------- M14 充值/记录域 ----------

    def open_recharge_page(self) -> None:
        """平台页充值入口 -> /me/recharge(M14-POS-001 入口链)。

        前置:调用方已 go_bottom_tab("平台") 停在平台页。VIP 卡片右侧
        「充值」按钮 [OCR](知识库 swan_平台页);注意下方副标题「充值购买
        便可购买更多服务哦」含同词,OCR 读取顺序自上而下先命中按钮,残余
        混淆风险由充值按钮 region 模板承接(template_needs)。到位断言:
        充值页余额区/渠道区/标题文案任一可见(细锚登记 template_needs)。
        """
        self.click_text("充值", timeout=10)
        self._assert_any_anchor(("余额", "充值", "微信", "支付宝"), timeout=10)

    def open_recharge_record_page(self) -> None:
        """充值页「记录」入口 -> /me/recharge-record(M14-POS-002 入口链)。

        前置:已在充值页。到位断言:双段切换器「消费」段文案 [OCR]
        (YAML 14.2 双段口径)。
        """
        self.click_text("记录", timeout=10)
        self.text_exists("消费", timeout=10)

    def select_recharge_tier(self, amount: str) -> None:
        """充值页点选金额档位(选中为本地态,不发起任何支付)。

        amount 传页面展示金额(如 "¥30");¥ 字形存在 ¥/￥ 两种 OCR 变体,
        先探测命中变体再点击返回值(运行时数据直传,禁中间常量)。
        """
        label = self._assert_any_anchor((amount, amount.replace("¥", "￥")),
                                        timeout=10)
        self.click_text(label, timeout=5)

    def assert_recharge_tiers_visible(self) -> None:
        """充值页六档金额(10/20/30/60/100/200)文案全部可见。

        ¥ 字形 OCR 变体(¥/￥)兼容;缺档即断言失败(M14-NEG-001/POS-005)。
        """
        for amount in ("10", "20", "30", "60", "100", "200"):
            self._assert_any_anchor((f"¥{amount}", f"￥{amount}"), timeout=8)

    def set_record_status_filter(self, current: str, target: str) -> None:
        """充值记录页状态筛选:点入口(文案=当前筛选态)->选目标态->联动列表。

        充值段右上角状态筛选入口默认文案「全部」(M14-POS-009);部分形态
        选后需点「确定」提交(M14-NEG-013),运行时探测到才点,无则跳过。
        收尾断言:入口文案更新为目标态。
        """
        self.click_text(current, timeout=8)
        self.click_text(target, timeout=8)
        if self.find_text_by_ocr("确定", timeout=2) is not None:
            self.click_text("确定", timeout=4)
        self.text_exists(target, timeout=8)

    # ---------- M14 月筛选滚轮(ADD1 补转) ----------

    def open_month_filter_dialog(self) -> None:
        """充值记录页打开月筛选弹层(右上第二筛选入口,yyyy-MM 双轮)。

        前置:已在充值记录页充值段。入口默认文案未探索,按候选序探测:
        「月份」占位 / 当前值 yyyy-MM 前缀;全部未命中即断言失败(入口锚
        登记 template_needs)。到位断言:「重置」或「确认」按钮任一可见。
        """
        for candidate in ("月份", "2026-", "2025-"):
            if self.find_text_by_ocr(candidate, timeout=3) is not None:
                self.click_text(candidate, timeout=6)
                break
        else:
            assert False, (
                "月筛选入口未命中候选(月份/2026-/2025-)[OCR],"
                "入口锚需按 template_needs 校准")
        for anchor in ("重置", "确认", "确定"):
            if self.find_text_by_ocr(anchor, timeout=3) is not None:
                return
        assert False, "月筛选弹层未打开(重置/确认锚均未见)[OCR]"

    def _wheel_scan_items(self) -> list:
        """OCR 全量扫描当前弹层,返回 (text, cx, cy) 三元组列表。"""
        return [(i["text"], i["cx"], i["cy"])
                for i in self.ocr_scan_page() if i["text"].strip()]

    def select_month_in_wheel(self, year: int, month: int) -> None:
        """月筛选双轮选定 yyyy-MM 并使其落入中央选中槽(不点确认)。

        坑 8:弹层每次打开重定位当前年月——以当前月值(运行时时钟)的
        y 坐标为中央槽基准,对目标年/月值做「OCR 定位->同列纵向 swipe
        到槽位」的步进滚动(坐标全部来自运行时 OCR,无硬编码)。月份
        字形按 两位数字/N月 两种候选探测。
        """
        from datetime import datetime

        current_month = datetime.now().month
        slot_cy = None
        for text, cx, cy in self._wheel_scan_items():
            if text in (f"{current_month:02d}", f"{current_month}月"):
                slot_cy = cy
                break
        assert slot_cy is not None, (
            f"弹层未定位到当前月 {current_month}(中央槽基准不可得)[OCR]")

        def _wheel_step(target_texts, column_hint_x=None):
            """单步:找到目标值并纵向滚向槽位;返回是否已对准。"""
            for _ in range(14):
                for text, cx, cy in self._wheel_scan_items():
                    if text in target_texts and (
                            column_hint_x is None
                            or abs(cx - column_hint_x) <= 120):
                        if abs(cy - slot_cy) <= 20:
                            return True
                        self.swipe(cx, cy, cx, slot_cy)
                        break
                else:
                    return False
            return False

        year_texts = (str(year), f"{year}年")
        year_x = None
        for text, cx, cy in self._wheel_scan_items():
            if text in year_texts:
                year_x = cx
                break
        if year_x is not None:
            assert _wheel_step(year_texts, year_x), \
                f"年份轮未滚动到 {year}[OCR]"
        month_texts = (f"{month:02d}", f"{month}月")
        assert _wheel_step(month_texts), f"月份轮未滚动到 {month}[OCR]"

    def confirm_month_filter(self) -> None:
        """月筛选弹层点确认提交(确认钮字形变体确认/确定运行时探测)。"""
        for label in ("确认", "确定"):
            if self.find_text_by_ocr(label, timeout=4) is not None:
                self.click_text(label, timeout=6)
                return
        assert False, "月筛选弹层确认钮未命中(确认/确定)[OCR]"

    def reset_month_filter(self) -> None:
        """月筛选弹层点「重置」(month=null 语义分支,坑 8)。"""
        self.click_text("重置", timeout=8)

    def assert_month_filter_dialog_closed(self) -> None:
        """断言月筛选弹层已关闭(重置/确认锚消失)。"""
        assert (self.find_text_by_ocr("重置", timeout=2) is None
                and self.find_text_by_ocr("确认", timeout=2) is None), \
            "月筛选弹层未关闭(重置/确认锚仍在)[OCR]"

    def assert_month_filter_entry_value(self, year: int, month: int) -> None:
        """断言月筛选入口文案更新为所选年月(确认生效的 UI 联动证据)。

        入口文案字形未探索,按 yyyy-MM 主变体 + 「yyyy年m月」OCR 变体
        探测(入口文案更新态登记 template_needs);任一命中即通过。
        """
        variants = (f"{year}-{month:02d}", f"{year}年{month}月",
                    f"{year}年{month:02d}月")
        for text in variants:
            if self.find_text_by_ocr(text, timeout=2) is not None:
                return
        assert False, (f"月筛选入口文案未更新为 {year}-{month:02d}"
                       f"(变体 {list(variants)} 均未命中)[OCR]")

    def assert_month_filter_entry_unset(self, year: int, month: int) -> None:
        """断言月筛选入口无所选年月残留(重置/关闭=null 的 UI 证据)。"""
        for text in (f"{year}-{month:02d}", f"{year}年{month}月"):
            assert self.find_text_by_ocr(text, timeout=2) is None, \
                f"月筛选入口仍残留 {text}(null 语义未保持)[OCR]"

    def _wheel_grid_step(self, column_hint_x: int, slot_cy: int) -> int:
        """以同列相邻可视项 y 差的最小值估计滚轮一格步距(运行时 OCR)。"""
        ys = sorted(cy for text, cx, cy in self._wheel_scan_items()
                    if abs(cx - column_hint_x) <= 120)
        gaps = [b - a for a, b in zip(ys, ys[1:]) if b - a > 8]
        return max(24, min(gaps)) if gaps else 80

    def _wheel_align(self, target_texts, column_hint_x: int,
                     slot_cy: int, rounds: int = 3) -> bool:
        """目标值可见即拖入中央选中槽(±20px);不可见返回 False。

        同列约束 ±120px 防跨列误命中;拖入后重扫复核(至多 rounds 轮)。
        """
        for _ in range(rounds):
            for text, cx, cy in self._wheel_scan_items():
                if text in target_texts and abs(cx - column_hint_x) <= 120:
                    if abs(cy - slot_cy) <= 20:
                        return True
                    self.swipe(cx, cy, cx, slot_cy)
                    break
            else:
                return False
        return False

    def _wheel_seek(self, target_texts, column_hint_x: int,
                    slot_cy: int, max_steps: int = 13) -> bool:
        """滚轮列步进搜索:目标不可见时先向下、再向上逐格滚动扫描。

        格距取同列相邻项 y 差(_wheel_grid_step),swipe 坐标全部来自
        运行时 OCR 推导,无硬编码;双向覆盖月轮 1~12 全序与年轮近段。
        """
        if self._wheel_align(target_texts, column_hint_x, slot_cy):
            return True
        step = self._wheel_grid_step(column_hint_x, slot_cy)
        moved = 0
        for _ in range(max_steps):
            moved += 1
            self.swipe(column_hint_x, slot_cy + step, column_hint_x, slot_cy)
            if self._wheel_align(target_texts, column_hint_x, slot_cy):
                return True
        for _ in range(moved):
            self.swipe(column_hint_x, slot_cy - step, column_hint_x, slot_cy)
        for _ in range(max_steps):
            self.swipe(column_hint_x, slot_cy - step, column_hint_x, slot_cy)
            if self._wheel_align(target_texts, column_hint_x, slot_cy):
                return True
        return self._wheel_align(target_texts, column_hint_x, slot_cy)

    def scroll_wheel_to_value(self, year: int, month: int) -> None:
        """月筛选双轮滚动选定 yyyy-MM(含远格目标;选定≠提交)。

        坑 8 前提:弹层打开即定位当前年月,以当前月值(运行时时钟)y 为
        中央选中槽基准、当前年值 x 为年份列锚。目标值可见即一步对准
        (_wheel_align),不可见(远格,如目标月与当前月差超过滚轮可视
        窗口)时经 _wheel_seek 先下后上逐格滚动搜索;坐标全部来自运行时
        OCR 推导。年份轮与月份轮分开步进(同列约束防跨列误命中)。
        提交由调用方 confirm_month_filter()/reset_month_filter()/
        press_back 承担(pay-NEG-016 远格 2026-01 主用户)。
        """
        from datetime import datetime

        current_month = datetime.now().month
        slot_cy = None
        for text, cx, cy in self._wheel_scan_items():
            if text in (f"{current_month:02d}", f"{current_month}月"):
                slot_cy = cy
                break
        assert slot_cy is not None, (
            f"弹层未定位到当前月 {current_month}(中央槽基准不可得)[OCR]")
        now_year = datetime.now().year
        year_x = None
        for text, cx, cy in self._wheel_scan_items():
            if text in (str(now_year), f"{now_year}年"):
                year_x = cx
                break
        assert year_x is not None, "弹层未定位到年份列(当前年锚不可得)[OCR]"
        if year != now_year:
            assert self._wheel_seek((str(year), f"{year}年"),
                                    year_x, slot_cy), \
                f"年份轮未滚动到 {year}[OCR]"
        month_x = None
        for text, cx, cy in self._wheel_scan_items():
            if text in (f"{current_month:02d}", f"{current_month}月"):
                month_x = cx
                break
        assert month_x is not None, "弹层未定位到月份列(当前月锚不可得)[OCR]"
        assert self._wheel_seek((f"{month:02d}", f"{month}月"),
                                month_x, slot_cy), \
            f"月份轮未滚动到 {month}[OCR]"

    # ---------- M14 记录列表/详情(ADD1 补转) ----------

    def scan_record_rows(self) -> list:
        """充值记录页当前屏订单行扫描:OCR 全量 + y 聚类成行。

        返回行元组列表[(text, ...), ...](按 y 自上而下),仅保留含 ¥/
        ￥ 金额的行;同屏重复行不做去重(重复行断言由调用方承担)。
        """
        items = sorted(self.ocr_scan_page(), key=lambda i: i["cy"])
        rows = []
        for item in items:
            if not item["text"].strip():
                continue
            if rows and abs(item["cy"] - rows[-1][0]) <= 14:
                rows[-1][1].append(item["text"])
            else:
                rows.append([item["cy"], [item["text"]]])
        return [tuple(texts) for _, texts in rows
                if "¥" in "".join(texts) or "￥" in "".join(texts)]

    def open_record_detail_first_row(self) -> tuple:
        """充值记录页点首行进详情,返回首行行键(金额/时间/状态 OCR 聚类)。

        前置:调用方已经 probe 确认列表非空(SKIP-DATA 口径)。到位判据:
        段切换器「消费」锚消失(已离开列表页);详情页首屏锚未探索,行要素
        一致性比对登记 template_needs(坑 5:详情=列表内存缓存无 HTTP,
        深链步骤断言归执行层)。
        """
        rows = self.scan_record_rows()
        assert rows, "充值记录页首屏未扫到订单行[OCR]"
        first_key = rows[0]
        self.click_text("¥" if any("¥" in t for t in first_key) else "￥",
                        timeout=8)
        self.text_not_exists("消费", timeout=10)
        return first_key

    def open_rights_center(self) -> None:
        """我的页「权益中心」行 -> /me/rights-center(M14-POS-003 入口链)。

        前置:调用方已停在我的页。到位断言:标题「权益中心」[OCR];H5
        首屏细锚未探索,登记 template_needs(行文本与页标题同词的假阳性
        残余风险一并登记)。
        """
        self.open_me_row("权益中心")
        self.text_exists("权益中心", timeout=15)

    def open_recharge_via_ai(self) -> None:
        """AI 域对话触发余额不足(不进充值页,提示与入口由调用方断言)。

        前置:调用方已 go_top_tab("AI") 停在首页 AI 顶 Tab。链路:角色卡
        「小薇」-> 输入框(OCR"发送消息")-> ASCII 消息 -> enter 键发送
        (知识库 swan_AI对话页;中文经 adb 不可达,发送按钮无文案图标以
        enter 承接)。余额不足提示与提示内充值入口文案未探索,登记
        template_needs;账号余额非 0 时门不触发,由调用方按 SKIP-DATA 口径
        skip。
        """
        self.click_text("小薇", timeout=10)
        self._assert_any_anchor(("内容由AI生成", "我是你的好朋友"), timeout=15)
        self.click_text("发送消息", timeout=10)
        self.input_text("hi")
        self.press_key("enter")

    def open_how_to_connect_page(self) -> None:
        """添加设备页「如何配网」-> /me/how-to-connect(M15-POS-007)。

        前置:调用方已经 open_device_page() 进入设备页。链路:「添加设备」
        ->「如何配网」[OCR]。添加设备入口与配网 H5 首屏锚未探索,登记
        template_needs;到位判据交给调用方
        (YAML 步骤 3 以页内「可适配音箱型号」动作入口续链)。
        """
        self.click_text("添加设备", timeout=10)
        self.click_text("如何配网", timeout=10)

    # ---------- M15 帮助与反馈域 ----------

    def open_help_feedback_page(self) -> None:
        """我的页「帮助与反馈」行 -> /me/help-feedback(M15-POS-001 入口链)。

        前置:调用方已 go_bottom_tab("我的") 停在我的页。到位断言:标题
        「帮助与反馈」[OCR](知识库 swan_帮助与反馈页)。
        """
        self.open_me_row("帮助与反馈")
        self.text_exists("帮助与反馈", timeout=10)

    def assert_help_rows_in_order(self) -> None:
        """帮助入口页固定 4 行自上而下顺序断言(M15-POS-001 步骤 3)。

        可适配音箱型号/使用说明/用户反馈/常见问题逐行 OCR 取 y 坐标,
        要求严格按序排列。
        """
        rows = ("可适配音箱型号", "使用说明", "用户反馈", "常见问题")
        ys = []
        for row in rows:
            pos = self.find_text_by_ocr(row, timeout=8)
            assert pos is not None, f"帮助入口页缺少行锚「{row}」[OCR]"
            ys.append(pos[1])
        assert ys == sorted(ys), (
            f"帮助入口页 4 行顺序错误,y 序列 {ys}(期望 型号/说明/反馈/问题 递增)")

    def open_about_page(self) -> None:
        """我的页「关于与升级」行 -> /me/about(M15-POS-012 入口链)。

        前置:调用方已 go_bottom_tab("我的") 停在我的页。到位断言:标题
        「关于与升级」[OCR](知识库 swan_关于与升级页)。
        """
        self.open_me_row("关于与升级")
        self.text_exists("关于与升级", timeout=10)

    def open_feedback_h5(self) -> None:
        """帮助入口页「用户反馈」行 -> /me/feedback 全屏 H5(M15-POS-008/009)。

        前置:已在帮助与反馈入口页。全屏容器无原生标题栏,H5 首屏文案
        未探索(登记 template_needs);到位判据:帮助入口页四行锚消失
        (已离开列表页)。
        """
        self.click_text("用户反馈", timeout=10)
        self.text_not_exists("可适配音箱型号", timeout=10)
