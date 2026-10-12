"""步骤级证据采集(②证据规范) + AW 方法级 HTML 执行报告。

【一】步骤证据(StepEvidence)
每次操作(点击/滑动/输入)结束后截图,并在截图上标注操作位置:
  - 点击: 红圈 + 十字线标注点击点
  - 滑动: 起终点圆点 + 连线箭头
  - 输入: 文字标注输入内容(无坐标)

通过环境变量 EVIDENCE=1 启用(平台会话自动开启;日常探索/调试不开,
避免拖慢节奏)。证据保存到 output/evidence/<run_tag>/,目录由
EVIDENCE_DIR 或 DASHBOARD_RUN_ID 决定,与平台会话一一对应。

【二】AW 方法级 HTML 执行报告(AWMethodReporter)
每个 AW 业务方法执行时自动生成"建议报告"式单文件 HTML:
  - 每步骤操作前/后截图(复用定位命中帧,零额外截屏)
  - 红框标注操作元素位置 + 左上角红底白字中文标签;
    点击点红圈+十字线;滑动起终点箭头
  - 红框标注操作之后"验证生效"的图像识别/OCR 命中位置
  - 时间线布局,失败步骤红色高亮,图片 base64 内嵌,单文件双击即看

通过环境变量 AW_REPORT 控制,默认开启(用户拍板:每个 AW 方法必须配备),
AW_REPORT=0 / false / off / no 关闭。报告输出到
output/aw_reports/<用例stem>/<方法名>_<HHMMSS>_<状态>.html,
用例名从 PYTEST_CURRENT_TEST 自动解析,非 pytest 环境归档到 manual/。

证据与报告均为"只增不阻塞":采集/标注/渲染任何失败仅记日志,
绝不向用例抛异常。
"""
from __future__ import annotations

import base64
import functools
import html
import inspect
import logging
import os
from datetime import datetime

import cv2
import numpy as np

try:  # 中文标签渲染依赖 Pillow(requirements.txt 已含);缺失时退化为 ASCII 文字
    from PIL import Image, ImageDraw, ImageFont
    _PIL_OK = True
except Exception:  # noqa: BLE001 — 报告是辅助设施,缺库不阻塞
    _PIL_OK = False

logger = logging.getLogger(__name__)

# 标注颜色统一用红色(BGR)
_COLOR = (0, 0, 255)

# 中文标签字体候选(Windows → Linux → macOS),按平台依次探测
_CN_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
_CN_FONT_CACHE: dict = {}


def _evidence_root() -> str:
    base = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
    run_tag = os.environ.get("EVIDENCE_DIR") or os.environ.get("DASHBOARD_RUN_ID") \
        or datetime.now().strftime("manual_%Y%m%d")
    safe_tag = "".join(c if c not in '\\/:*?"<>|' else "_" for c in run_tag)
    return os.path.join(base, "output", "evidence", safe_tag)


def _cn_font(size: int):
    """加载中文字体(按字号缓存);找不到任何中文字体返回 None。"""
    if not _PIL_OK:
        return None
    cached = _CN_FONT_CACHE.get(size)
    if cached is not None:
        return cached or None
    for path in _CN_FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                _CN_FONT_CACHE[size] = font
                return font
            except Exception:  # noqa: BLE001 — 换下一个候选字体
                continue
    _CN_FONT_CACHE[size] = False  # 已探明无可用中文字体,不再重复探测
    return None


def _put_cn_text(img: np.ndarray, text: str, org: tuple[int, int],
                 color_bgr: tuple[int, int, int], size: int) -> None:
    """在 BGR 图上写文字,支持中文(PIL);无字体时退化为 ASCII 安全文字。"""
    font = _cn_font(size)
    if font is None:
        ascii_text = text.encode("ascii", "ignore").decode() or "R"
        cv2.putText(img, ascii_text, org, cv2.FONT_HERSHEY_SIMPLEX,
                    max(0.5, size / 24.0), color_bgr, 2, cv2.LINE_AA)
        return
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    fill = (color_bgr[2], color_bgr[1], color_bgr[0])
    ImageDraw.Draw(pil_img).text(org, text, font=font, fill=fill)
    img[:] = cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2BGR)


def _cn_text_width(text: str, size: int) -> int:
    """测量中文文字像素宽(用于标签条底色尺寸)。"""
    font = _cn_font(size)
    if font is None:
        return size * len(text)
    try:
        return int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(text, font=font))
    except Exception:  # noqa: BLE001 — 测量失败按字符数估算
        return size * len(text)


def _aw_report_enabled() -> bool:
    """AW_REPORT 默认开启(用户拍板:每个 AW 方法必须配备执行报告)。"""
    return os.environ.get("AW_REPORT", "1").strip().lower() not in {"0", "false", "off", "no"}


def _case_stem_from_pytest() -> str:
    """从 PYTEST_CURRENT_TEST 提取用例文件名 stem 作报告归档目录。

    形如 "tests/flutter/test_xxx.py::TestXxx::test_yyy (call)" → "test_xxx"。
    非 pytest 环境(探索脚本/手工驱动)返回 "manual"。
    """
    current = os.environ.get("PYTEST_CURRENT_TEST", "")
    node = current.split(" (")[0]
    path = node.split("::")[0] if node else ""
    if path:
        return os.path.splitext(os.path.basename(path))[0]
    return "manual"


def _safe_name(name: str, limit: int = 80) -> str:
    cleaned = "".join(c if c not in '\\/:*?"<>| ' else "_" for c in str(name))
    return cleaned[:limit] or "unnamed"


class StepEvidence:
    """会话级步骤证据记录器。disabled 时所有方法是 no-op。"""

    def __init__(self) -> None:
        self.enabled = os.environ.get("EVIDENCE", "").strip() in {"1", "true", "True", "on"}
        self.root = _evidence_root()
        self._counter = 0
        if self.enabled:
            os.makedirs(self.root, exist_ok=True)
            logger.info(f"🖼️ 步骤证据已启用: {self.root}")

    def _next_path(self, op: str) -> str:
        self._counter += 1
        ts = datetime.now().strftime("%H%M%S")
        return os.path.join(self.root, f"{self._counter:03d}_{op}_{ts}.png")

    @staticmethod
    def _annotate_point(img: np.ndarray, point: tuple[int, int]) -> np.ndarray:
        x, y = int(point[0]), int(point[1])
        cv2.circle(img, (x, y), 28, _COLOR, 3)
        cv2.line(img, (x - 40, y), (x + 40, y), _COLOR, 2)
        cv2.line(img, (x, y - 40), (x, y + 40), _COLOR, 2)
        return img

    @staticmethod
    def _annotate_swipe(img: np.ndarray, start: tuple[int, int], end: tuple[int, int]) -> np.ndarray:
        sx, sy = int(start[0]), int(start[1])
        ex, ey = int(end[0]), int(end[1])
        cv2.arrowedLine(img, (sx, sy), (ex, ey), _COLOR, 3, tipLength=0.15)
        cv2.circle(img, (sx, sy), 14, _COLOR, 3)
        cv2.circle(img, (ex, ey), 14, _COLOR, 3)
        return img

    @staticmethod
    def _annotate_label(img: np.ndarray, text: str) -> np.ndarray:
        h, w = img.shape[:2]
        cv2.rectangle(img, (0, h - 56), (w, h), (30, 30, 30), -1)
        cv2.putText(img, text, (12, h - 18), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)
        return img

    def record(self, aw, op: str, point=None, start=None, end=None,
               detail: str = "") -> None:
        """截图并标注当前操作。aw 需提供 take_screenshot()。

        证据只增不阻塞:截图/标注任何失败仅记日志,不向用例抛异常
        (证据缺失不算用例失败,但会在日志中留痕)。
        """
        if not self.enabled:
            return
        try:
            save_path = self._next_path(op)
            img = aw.take_screenshot()  # take_screenshot 自带 HTML 日志内嵌
            if img is None:
                logger.warning(f"⚠️ 证据截图失败({op}),本步骤无截图")
                return
            if point is not None:
                img = self._annotate_point(img, point)
            if start is not None and end is not None:
                img = self._annotate_swipe(img, start, end)
            if detail:
                img = self._annotate_label(img, detail[:60])
            success, buf = cv2.imencode(".png", img)
            if success:
                buf.tofile(save_path)
                logger.info(f"🖼️ 步骤证据[{op}]: {save_path}")
        except Exception as error:  # noqa: BLE001 — 证据失败绝不影响用例
            logger.warning(f"⚠️ 步骤证据采集异常({op}): {error}")


# 模块级单例:AWBase 直接引用
step_evidence = StepEvidence()


# ==================== AW 方法级 HTML 执行报告 ====================

_AW_REPORT_KIND_ZH = {
    "locate": "定位",
    "action": "操作",
    "verify": "生效验证",
    "note": "信息",
}

_REPORT_STYLE = """
*{box-sizing:border-box}
body{font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;margin:0;background:#f3f4f6;color:#111827}
header{background:#fff;border-bottom:4px solid #10b981;padding:18px 28px}
header.fail{border-bottom-color:#ef4444;background:#fff7f7}
h1{margin:0;font-size:20px}
.meta{display:grid;grid-template-columns:max-content 1fr;gap:5px 16px;font-size:13px;margin:12px 0 0}
.meta dt{color:#6b7280;white-space:nowrap}
.meta dd{margin:0;word-break:break-all}
.meta code{background:#f3f4f6;padding:1px 6px;border-radius:4px;font-size:12px}
.banner{max-width:1060px;margin:16px auto 0;padding:10px 16px;background:#fee2e2;color:#991b1b;border-radius:8px;font-size:13px}
.timeline{max-width:1060px;margin:24px auto;padding-left:34px;border-left:2px solid #d1d5db}
.step{position:relative;background:#fff;border:1px solid #e5e7eb;border-left:4px solid #9ca3af;border-radius:8px;padding:12px 16px;margin-bottom:16px}
.step::before{content:"";position:absolute;left:-41px;top:16px;width:12px;height:12px;border-radius:50%;background:#9ca3af;border:2px solid #fff;box-shadow:0 0 0 1px #d1d5db}
.step.locate{border-left-color:#3b82f6}.step.locate::before{background:#3b82f6}
.step.action{border-left-color:#f59e0b}.step.action::before{background:#f59e0b}
.step.verify{border-left-color:#10b981}.step.verify::before{background:#10b981}
.step.note{border-left-color:#9ca3af}
.step.bad{border-color:#ef4444;background:#fef2f2}.step.bad::before{background:#ef4444}
.head{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.idx{font-weight:700;color:#6b7280;font-size:13px}
.badge{padding:2px 10px;border-radius:10px;color:#fff;font-size:12px}
.badge.locate{background:#3b82f6}.badge.action{background:#f59e0b}
.badge.verify{background:#10b981}.badge.note{background:#6b7280}
.act{font-weight:600}
.lbl{color:#374151;font-size:13px;word-break:break-all}
.ts{margin-left:auto;color:#9ca3af;font-size:12px;white-space:nowrap}
.imgs{display:flex;gap:14px;flex-wrap:wrap;margin-top:10px}
figure{margin:0;flex:1 1 240px;max-width:500px}
figure img{width:100%;display:block;border:1px solid #e5e7eb;border-radius:4px}
figcaption{font-size:12px;color:#6b7280;margin-top:4px}
.noimg{margin-top:10px;color:#9ca3af;font-size:12.5px;font-style:italic}
.notes{font-size:12.5px;color:#374151;margin-top:8px;line-height:1.7}
.err{margin-top:8px;padding:8px 12px;background:#fee2e2;border-radius:6px;color:#991b1b;font-size:12.5px;font-family:Consolas,monospace;white-space:pre-wrap;word-break:break-all}
footer{max-width:1060px;margin:0 auto;padding:0 28px 30px;color:#9ca3af;font-size:12px}
.ok-txt{color:#059669;font-weight:600}.fail-txt{color:#dc2626;font-weight:600}
"""


class AWMethodReporter:
    """AW 方法级 HTML 执行报告器。

    生命周期:begin() → record_step()/record_action()/record_verify() ×N → finish()。
    enabled=False(AW_REPORT=0)时所有方法为 no-op;任何异常只记日志,
    绝不影响用例执行("证据只增不阻塞")。

    与 AWBase 的协作(零额外截屏):
      - cache_hit(img, rect, template_name):AWBase._find_image_rect_impl 命中时
        把现成帧与矩形交给报告器,作为"最近帧"供后续 action/verify 复用;
        若上一步操作还没等到"操作后帧",当前帧即补为其 after。
      - record_action/record_verify/record_note/record_fail:AWBase 挂钩便捷入口。
    """

    def __init__(self) -> None:
        self.enabled = _aw_report_enabled()
        self.method_name: str = ""
        self.args_repr: str = ""
        self.case_name: str = ""
        self.started_at: datetime | None = None
        self.steps: list[dict] = []
        # 最近一次定位命中缓存(AWBase 挂钩复用,不重复截屏)
        self.last_frame: np.ndarray | None = None
        self.last_rect: tuple[int, int, int, int] | None = None
        self.last_template: str | None = None
        self._pending_action: dict | None = None  # 待补"操作后帧"的步骤
        self._counter = 0
        self._begun = False
        self._finished = False
        self._dir: str | None = None

    # ---------- 生命周期 ----------

    def begin(self, method_name: str, args_repr: str = "",
              case_name: str | None = None) -> None:
        """开始记录一个 AW 方法。case_name 供手工驱动时显式指定归档目录。"""
        if not self.enabled:
            return
        try:
            self.method_name = method_name
            self.args_repr = (args_repr or "")[:200]
            self.started_at = datetime.now()
            self.steps = []
            self._counter = 0
            self._pending_action = None
            self.last_frame = None
            self.last_rect = None
            self.last_template = None
            self._begun = True
            self._finished = False
            self.case_name = case_name or _case_stem_from_pytest()
            base = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self._dir = os.path.join(base, "output", "aw_reports", _safe_name(self.case_name))
            os.makedirs(self._dir, exist_ok=True)
            logger.info(f"📄 AW 方法报告开始: {method_name} → {self._dir}")
        except Exception as error:  # noqa: BLE001 — 报告失败绝不影响用例
            self._dir = None
            logger.warning(f"⚠️ AW 方法报告 begin 异常({method_name}): {error}")

    def record_step(self, kind: str, label: str, action: str | None = None,
                    rects=None, img: np.ndarray | None = None,
                    point: tuple[int, int] | None = None,
                    swipe: tuple[tuple[int, int], tuple[int, int]] | None = None,
                    ok: bool = True, error: str | None = None) -> None:
        """记录一个步骤。

        Args:
            kind:   "locate"定位 / "action"操作 / "verify"生效验证 / "note"信息
            label:  模板名 / OCR 文本 / 说明文字
            action: 操作方式文字(点击/长按/滑动/输入)
            rects:  [(x, y, w, h, 标签)] 红框列表,标签显示在框左上角红底白字
            img:    本步骤截图帧(None 则无图;action 步骤默认复用最近缓存帧)
            point:  点击点坐标 → 红圈+十字线
            swipe:  ((sx, sy), (ex, ey)) → 起终点箭头
            ok:     False 时卡片红色高亮
            error:  失败/异常消息
        """
        if not self.active():
            return
        try:
            if img is not None:
                self._absorb_frame(img)  # 当前帧先补给上一步"操作后帧"
            self._counter += 1
            step = {
                "idx": self._counter,
                "kind": kind if kind in _AW_REPORT_KIND_ZH else "note",
                "label": label or "",
                "action": action or "",
                "ts": datetime.now().strftime("%H:%M:%S"),
                "rects": [tuple(r) for r in rects] if rects else [],
                "point": tuple(point) if point is not None else None,
                "swipe": (tuple(swipe[0]), tuple(swipe[1])) if swipe is not None else None,
                "ok": ok,
                "error": error or "",
                "before_png": self._annotate_frame(img, rects, point, swipe) if img is not None else None,
                "after_png": None,
            }
            if kind == "action" and ok:
                self._pending_action = step  # 操作后帧由下一次定位/验证自然产生
            self.steps.append(step)
        except Exception as err:  # noqa: BLE001 — 报告失败绝不影响用例
            logger.warning(f"⚠️ AW 报告步骤记录异常({label}): {err}")

    def finish(self, status: str = "ok", error: str | None = None) -> str | None:
        """结束记录并渲染单文件 HTML。返回报告路径,失败返回 None。"""
        if not self.enabled or not self._begun or self._finished:
            return None
        self._finished = True
        try:
            html_str = self._render_html(status, error)
            if self._dir is None:
                return None
            fname = f"{_safe_name(self.method_name)}_{datetime.now():%H%M%S}_{status}.html"
            path = os.path.join(self._dir, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_str)
            logger.info(f"📄 AW 方法报告[{self.method_name}] {status}: {path}")
            return path
        except Exception as err:  # noqa: BLE001 — 渲染失败绝不影响用例
            logger.warning(f"⚠️ AW 方法报告渲染失败({self.method_name}): {err}")
            return None

    # ---------- AWBase 挂钩便捷入口 ----------

    def active(self) -> bool:
        """报告器是否正在记录(挂钩调用前先判此,未 begin 时不产生任何记录)。"""
        return bool(self.enabled and self._begun and not self._finished)

    def cache_hit(self, img: np.ndarray, rect: tuple[int, int, int, int],
                  template_name: str) -> None:
        """AWBase._find_image_rect_impl 命中时上交现成帧与矩形(不新增截屏)。

        当前帧同时承担两个职责:补上一步操作的 after + 缓存为最近帧
        (后续 action 的 before / verify 的标注底图)。
        """
        if not self.active() or img is None:
            return
        try:
            self._absorb_frame(img)
            self.last_frame = img
            self.last_rect = tuple(rect)
            self.last_template = template_name
        except Exception as err:  # noqa: BLE001 — 报告失败绝不影响用例
            logger.warning(f"⚠️ AW 报告 cache_hit 异常({template_name}): {err}")

    def rect_for(self, template_name: str) -> tuple[int, int, int, int] | None:
        """取指定模板最近一次命中矩形(模板名不匹配则返回 None,避免错框)。"""
        if self.last_template == template_name and self.last_rect is not None:
            return self.last_rect
        return None

    def record_action(self, action: str, label: str = "",
                      point: tuple[int, int] | None = None,
                      rect: tuple[int, int, int, int] | None = None,
                      swipe: tuple[tuple[int, int], tuple[int, int]] | None = None,
                      img: np.ndarray | None = None) -> None:
        """记录操作步骤(点击/长按/滑动/输入),复用最近缓存帧为操作前截图。

        rect(命中矩形)优先;无 rect 有 point 时框选点位周围 40px 方框。
        """
        if not self.active():
            return
        frame = img if img is not None else self.last_frame
        rects = []
        if rect is not None:
            rects.append((rect[0], rect[1], rect[2], rect[3],
                          f"{action} · {label}" if label else action))
        elif point is not None:
            rects.append((int(point[0]) - 20, int(point[1]) - 20, 40, 40,
                          f"{action} · {label}" if label else action))
        self.record_step("action", label=label or action, action=action,
                         rects=rects, img=frame, point=point, swipe=swipe)

    def record_verify(self, label: str,
                      rect: tuple[int, int, int, int] | None = None,
                      img: np.ndarray | None = None, tag: str = "") -> None:
        """记录"操作之后验证生效"的图像识别/OCR 命中(红框=命中位置)。"""
        if not self.active():
            return
        try:
            frame = img if img is not None else self.last_frame
            if frame is not None:
                self._absorb_frame(frame)
                self.last_frame = frame
            if rect is not None:
                self.last_rect = tuple(rect)
            self.last_template = label
            hit_label = f"{'[' + tag + '] ' if tag else ''}验证命中 · {label}"
            rects = [(rect[0], rect[1], rect[2], rect[3], hit_label)] if rect else []
            self.record_step("verify", label=label, rects=rects, img=frame)
        except Exception as err:  # noqa: BLE001 — 报告失败绝不影响用例
            logger.warning(f"⚠️ AW 报告 record_verify 异常({label}): {err}")

    def record_note(self, text: str) -> None:
        """记录信息性文字(无截图)。"""
        self.record_step("note", label=text)

    def record_fail(self, kind: str, label: str, error: str) -> None:
        """记录失败步骤(卡片红色高亮);附最近帧原图便于看失败时页面状态。"""
        if not self.active():
            return
        frame = None
        try:
            frame = self.last_frame if self.last_frame is not None else None
        except Exception:  # noqa: BLE001 — 取帧失败按无图处理
            frame = None
        self.record_step(kind, label=label, img=frame, ok=False, error=error)

    # ---------- 内部实现 ----------

    def _absorb_frame(self, img: np.ndarray) -> None:
        """把当前帧补给待填"操作后帧"的 action 步骤(幂等)。"""
        if self._pending_action is None:
            return
        if self._pending_action.get("after_png") is None:
            self._pending_action["after_png"] = self._encode_png(img)
        self._pending_action = None

    @staticmethod
    def _encode_png(img: np.ndarray) -> bytes | None:
        try:
            success, buf = cv2.imencode(".png", img)
            return buf.tobytes() if success else None
        except Exception:  # noqa: BLE001 — 编码失败按无图处理
            return None

    @staticmethod
    def _annotate_frame(img: np.ndarray, rects=None,
                        point: tuple[int, int] | None = None,
                        swipe: tuple[tuple[int, int], tuple[int, int]] | None = None) -> bytes | None:
        """在帧副本上标注(红框+中文标签/红圈十字线/滑动箭头)并编码 PNG。"""
        canvas = img.copy()
        h, w = canvas.shape[:2]
        for rect in (rects or []):
            try:
                rx, ry, rw, rh = (int(max(0, rect[0])), int(max(0, rect[1])),
                                  int(rect[2]), int(rect[3]))
                x2, y2 = min(w, rx + rw), min(h, ry + rh)
                if x2 <= rx or y2 <= ry:
                    continue
                cv2.rectangle(canvas, (rx, ry), (x2, y2), _COLOR, 3)
                label = str(rect[4]) if len(rect) > 4 and rect[4] else ""
                if label:
                    fs = max(15, int(h / 42))          # 标签字号随帧高自适应
                    pad = max(3, fs // 5)
                    tw = _cn_text_width(label, fs)
                    tag_y = ry - (fs + 2 * pad)
                    tag_y = tag_y if tag_y >= 0 else ry
                    cv2.rectangle(canvas, (rx, tag_y), (rx + tw + 2 * pad, tag_y + fs + 2 * pad),
                                  _COLOR, -1)
                    _put_cn_text(canvas, label, (rx + pad, tag_y + pad), (255, 255, 255), fs)
            except Exception as err:  # noqa: BLE001 — 单框失败不影响其余标注
                logger.debug(f"红框标注失败: {err}")
        if point is not None:
            StepEvidence._annotate_point(canvas, point)
        if swipe is not None:
            StepEvidence._annotate_swipe(canvas, swipe[0], swipe[1])
        return AWMethodReporter._encode_png(canvas)

    # ---------- HTML 渲染 ----------

    def _render_html(self, status: str, error: str | None) -> str:
        ok = status == "ok"
        esc = html.escape
        icon = "✅" if ok else "❌"
        started = self.started_at.strftime("%Y-%m-%d %H:%M:%S") if self.started_at else "-"
        dur = f"{(datetime.now() - self.started_at).total_seconds():.1f} 秒" \
            if self.started_at else "-"
        meta_rows = "".join(
            f"<dt>{esc(k)}</dt><dd>{v}</dd>" for k, v in [
                ("方法", esc(self.method_name or "-")),
                ("参数", f"<code>{esc(self.args_repr) or '-'}</code>"),
                ("用例", esc(self.case_name or "-")),
                ("开始时间", esc(started)),
                ("总耗时", esc(dur)),
                ("步骤数", str(len(self.steps))),
                ("结论", f'<span class="{"ok-txt" if ok else "fail-txt"}">'
                         f'{icon} {"成功" if ok else "失败"}</span>'),
            ]
        )
        err_banner = ""
        if not ok and error:
            err_banner = (f'<div class="banner">❌ 异常信息:'
                          f'<code>{esc(error)}</code></div>')
        cards = "".join(self._step_card(step) for step in self.steps)
        return (
            '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            f'<title>AW 执行报告 · {esc(self.method_name)}</title>'
            f'<style>{_REPORT_STYLE}</style></head><body>'
            f'<header class="{"" if ok else "fail"}">'
            f'<h1>{icon} AW 方法执行报告 · {esc(self.method_name)}</h1>'
            f'<dl class="meta">{meta_rows}</dl></header>'
            f'{err_banner}<div class="timeline">{cards}</div>'
            f'<footer>Swan 自动化测试 · AWMethodReporter · '
            f'生成于 {datetime.now():%Y-%m-%d %H:%M:%S}</footer></body></html>'
        )

    @staticmethod
    def _step_card(step: dict) -> str:
        esc = html.escape
        kind = step["kind"]
        zh = _AW_REPORT_KIND_ZH.get(kind, kind)
        card_cls = "bad" if not step["ok"] else kind

        head = (f'<div class="head"><span class="idx">#{step["idx"]}</span>'
                f'<span class="badge {esc(kind)}">{esc(zh)}</span>'
                + (f'<span class="act">{esc(step["action"])}</span>' if step["action"] else "")
                + f'<span class="lbl">{esc(step["label"])}</span>'
                + f'<span class="ts">{esc(step["ts"])}</span></div>')

        figures = []
        if step["before_png"]:
            cap = {
                "locate": "定位 · 红框=命中/目标位置",
                "action": f"{step['action'] or '操作'}前 · 红框=操作位置",
                "verify": "验证识别 · 红框=命中位置",
                "note": "信息",
            }.get(kind, "截图")
            b64 = base64.b64encode(step["before_png"]).decode("ascii")
            figures.append(f'<figure><figcaption>{esc(cap)}</figcaption>'
                           f'<img src="data:image/png;base64,{b64}"></figure>')
        if step["after_png"]:
            b64 = base64.b64encode(step["after_png"]).decode("ascii")
            figures.append(f'<figure><figcaption>操作后（下一步定位帧）</figcaption>'
                           f'<img src="data:image/png;base64,{b64}"></figure>')
        elif kind == "action" and step["ok"] and step["before_png"]:
            figures.append('<figure><figcaption>操作后帧未采集'
                           '（方法在下次定位前结束）</figcaption></figure>')
        img_html = f'<div class="imgs">{"".join(figures)}</div>' if figures \
            else '<div class="noimg">（本步骤无截图帧）</div>'

        notes = [f"红框{i}：{esc(r[4])}" for i, r in enumerate(step["rects"], 1)
                 if len(r) > 4 and r[4]]
        if step["point"]:
            notes.append(f"红圈：{esc(step['action'] or '操作')}点 "
                         f"({step['point'][0]}, {step['point'][1]})")
        if step["swipe"]:
            (sx, sy), (ex, ey) = step["swipe"]
            notes.append(f"箭头：({sx},{sy}) → ({ex},{ey})")
        note_html = f'<div class="notes">{"　·　".join(notes)}</div>' if notes else ""

        err_html = f'<div class="err">❌ {esc(step["error"])}</div>' if step["error"] else ""
        return (f'<section class="step {esc(card_cls)}">{head}{img_html}'
                f'{note_html}{err_html}</section>')


def _format_args_repr(method, args: tuple, kwargs: dict) -> str:
    """格式化方法实参 repr(截断 200 字),用于报告头部参数展示。"""
    try:
        sig = inspect.signature(method)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        joined = ", ".join(f"{name}={value!r}" for name, value in bound.arguments.items()
                           if name != "self")
    except Exception:  # noqa: BLE001 — 参数解析失败不阻塞
        joined = "<参数解析失败>"
    return joined if len(joined) <= 200 else joined[:197] + "..."


def _aw_method_report(method):
    """AW 业务方法执行报告装饰器。

    嵌套语义(一次顶层业务方法调用 = 一份完整 HTML 报告,不产生碎片文件):
      - 顶层调用(当前无活跃报告器): begin(方法名, 实参 repr 截断 200 字) →
        正常返回 finish("ok");异常 finish("fail", error) 后原样 re-raise。
      - 嵌套调用(外层报告器活跃): 不另建报告,降级为把子方法的进入/完成/
        失败作为 note 步骤记入外层报告;方法体内部经 AWBase 挂钩产生的
        定位/操作/验证步骤自然归档进同一份外层报告。
    报告生成全程只增不阻塞。
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        outer = getattr(self, "_method_reporter", None)
        if isinstance(outer, AWMethodReporter) and outer.active():
            # 嵌套调用:降级记录到外层报告(内层 AWBase 挂钩同样落外层)
            args_repr = _format_args_repr(method, (self, *args), kwargs)
            outer.record_note(f"子方法 {method.__name__}({args_repr}) 开始")
            try:
                result = method(self, *args, **kwargs)
            except Exception as error:
                outer.record_fail("note", f"子方法 {method.__name__} 失败",
                                  repr(error))
                raise
            outer.record_note(f"子方法 {method.__name__} 完成")
            return result
        reporter = AWMethodReporter()
        self._method_reporter = reporter
        try:
            # self 是 wrapper 的独立参数,须拼回 args 供 sig.bind;repr 时按名过滤
            reporter.begin(method.__name__,
                           _format_args_repr(method, (self, *args), kwargs))
            result = method(self, *args, **kwargs)
        except Exception as error:
            reporter.finish("fail", error=repr(error))
            raise
        else:
            reporter.finish("ok")
            return result
        finally:
            self._method_reporter = outer
    return wrapper
