"""Render a detailed Swan trace log as a readable Markdown report."""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


LINE_PATTERN = re.compile(r"^(?P<wall>\S+\s+\S+)\s+(?P<level>\w+)\s+(?P<message>.*)$")
ELAPSED_PATTERN = re.compile(r"elapsed=(?P<value>[0-9.]+)s")
STEP_START_PATTERN = re.compile(r"STEP_START name=(?P<name>.+?) elapsed=(?P<elapsed>[0-9.]+)s")
STEP_END_PATTERN = re.compile(
    r"STEP_END name=(?P<name>.+?) elapsed=(?P<elapsed>[0-9.]+)s duration=(?P<duration>[0-9.]+)s"
)


@dataclass
class Event:
    wall: str
    elapsed: float
    kind: str
    detail: str


def _elapsed(message: str) -> float | None:
    match = ELAPSED_PATTERN.search(message)
    return float(match.group("value")) if match else None


def _event_kind(message: str) -> str | None:
    token = message.split(" ", 1)[0]
    known = {
        "TRACE_START", "TRACE_END", "STEP_START", "STEP_END", "UI_TREE",
        "UI_HINT", "UI_HINT_MISSING", "SCREENSHOT", "OCR_REGION", "OCR_SCAN",
        "OCR_ASSERT_SCAN", "OCR_TIMEOUT", "OCR_TAP", "OCR_ASSERT_WAIT",
        "SEMANTIC_TAP", "CONTENT_DESC_CANDIDATES", "INPUT_START", "INPUT_END",
        "PRECONDITION", "RECORD_START", "RECORD_STOP", "RECORD_SAVED",
        "RECORD_NATIVE_UNAVAILABLE", "RECORD_FALLBACK_START", "RECORD_FALLBACK_FRAMES",
        "RECORD_FALLBACK_FAILED",
    }
    return token if token in known else None


def parse_events(log_path: str | Path) -> tuple[list[Event], int]:
    events: list[Event] = []
    tick_count = 0
    last_elapsed = 0.0
    for line in Path(log_path).read_text(encoding="utf-8", errors="replace").splitlines():
        match = LINE_PATTERN.match(line.strip())
        if not match:
            continue
        message = match.group("message")
        if message.startswith("TRACE_TICK"):
            tick_count += 1
            continue
        kind = _event_kind(message)
        elapsed = _elapsed(message)
        if kind is None:
            continue
        if elapsed is None:
            elapsed = 0.0 if kind == "TRACE_START" else last_elapsed
        last_elapsed = elapsed
        events.append(Event(match.group("wall"), elapsed, kind, message))
    return events, tick_count


def _duration(value: float) -> str:
    return f"{value:.3f}s"


def _short_detail(event: Event) -> str:
    detail = event.detail
    for prefix in (
        "STEP_START ", "STEP_END ", "SCREENSHOT ", "UI_TREE ", "OCR_REGION ",
        "OCR_SCAN ", "OCR_ASSERT_SCAN ", "OCR_TAP ", "SEMANTIC_TAP ",
        "INPUT_START ", "INPUT_END ", "RECORD_",
    ):
        if detail.startswith(prefix):
            return detail[len(prefix):]
    return detail


def render_markdown(log_path: str | Path, output_path: str | Path) -> Path:
    events, tick_count = parse_events(log_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    starts: dict[str, Event] = {}
    stages: list[tuple[str, float, float, float]] = []
    for event in events:
        start_match = STEP_START_PATTERN.match(event.detail)
        end_match = STEP_END_PATTERN.match(event.detail)
        if start_match:
            starts[start_match.group("name")] = event
        elif end_match:
            name = end_match.group("name")
            stages.append((name, starts.get(name, event).elapsed, event.elapsed, float(end_match.group("duration"))))

    trace_start = next((event for event in events if event.kind == "TRACE_START"), None)
    trace_end = next((event for event in reversed(events) if event.kind == "TRACE_END"), None)
    total_elapsed = trace_end.elapsed if trace_end else (events[-1].elapsed if events else 0.0)
    screenshots = sum(event.kind == "SCREENSHOT" for event in events)
    ocr_scans = sum(event.kind in {"OCR_SCAN", "OCR_ASSERT_SCAN"} for event in events)
    ocr_taps = sum(event.kind == "OCR_TAP" for event in events)
    semantic_taps = sum(event.kind == "SEMANTIC_TAP" for event in events)
    record_saved = next((event for event in reversed(events) if event.kind == "RECORD_SAVED"), None)

    key_events = [
        event for event in events
        if event.kind not in {"UI_HINT", "UI_TREE", "SCREENSHOT", "OCR_SCAN", "OCR_ASSERT_SCAN", "OCR_ASSERT_WAIT"}
    ]
    waits: list[tuple[float, float, str]] = []
    for previous, current in zip(key_events, key_events[1:]):
        gap = current.elapsed - previous.elapsed
        if gap >= 0.8:
            waits.append((previous.elapsed, current.elapsed, previous.kind))

    lines = [
        "# Swan UI 视觉执行报告",
        "",
        f"- 原始日志：`{Path(log_path).name}`",
        f"- 开始时间：`{trace_start.wall if trace_start else '-'}`",
        f"- 总耗时：`{_duration(total_elapsed)}`",
        f"- 50ms 心跳：`{tick_count}` 次（报告不逐条展开）",
        f"- 截图：`{screenshots}` 张；OCR 扫描：`{ocr_scans}` 次；OCR 点击：`{ocr_taps}` 次；语义 bounds 点击：`{semantic_taps}` 次",
        f"- 录屏：`{_short_detail(record_saved) if record_saved else '未记录'}`",
        "",
        "## 阶段耗时",
        "",
        "| 阶段 | 开始 | 结束 | 耗时 |",
        "|---|---:|---:|---:|",
    ]
    for name, started, ended, duration in stages:
        lines.append(f"| `{name}` | {started:.3f}s | {ended:.3f}s | {_duration(duration)} |")

    lines.extend(["", "## 关键时间线", "", "| 相对时间 | 类型 | 详情 |", "|---:|---|---|"])
    for event in key_events:
        lines.append(f"| {event.elapsed:.3f}s | `{event.kind}` | `{_short_detail(event).replace('|', '\\|')}` |")

    lines.extend(["", "## 明显等待区间", ""])
    if waits:
        lines.extend(["以下区间没有关键操作事件，通常对应 ADB、页面动画、网络请求或 OCR 处理：", "", "| 起点 | 终点 | 间隔 | 起点事件 |", "|---:|---:|---:|---|"])
        for started, ended, kind in waits:
            lines.append(f"| {started:.3f}s | {ended:.3f}s | {_duration(ended - started)} | `{kind}` |")
    else:
        lines.append("未发现超过 0.8 秒的明显等待区间。")

    lines.extend(["", "## 原始日志查看建议", "", "50ms 心跳用于精确定位调度间隔；阅读执行过程时优先看“阶段耗时”和“关键时间线”，需要深入时再回到原始日志搜索对应相对时间。", ""])
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Swan trace log to Markdown")
    parser.add_argument("log", help="detailed trace log path")
    parser.add_argument("--output", help="Markdown output path")
    args = parser.parse_args()
    log_path = Path(args.log)
    output_path = Path(args.output) if args.output else log_path.with_suffix(".md")
    print(render_markdown(log_path, output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
