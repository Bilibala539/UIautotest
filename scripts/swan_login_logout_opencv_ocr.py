"""Use screenshot, OpenCV and OCR to exercise Swan login and logout."""
from __future__ import annotations

import argparse
import logging
import os
import re
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ElementTree
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.aw.base.flutter_base import FlutterBaseAW
from utils.aw.driver.android_driver import AndroidAdbDriver


LOGGER = logging.getLogger("swan_vision")
BOUNDS_PATTERN = re.compile(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]")


@dataclass(frozen=True)
class UiHint:
    resource_id: str
    content_desc: str
    bounds: tuple[int, int, int, int]

    @property
    def center(self) -> tuple[int, int]:
        x1, y1, x2, y2 = self.bounds
        return (x1 + x2) // 2, (y1 + y2) // 2


def parse_bounds(value: str) -> tuple[int, int, int, int] | None:
    match = BOUNDS_PATTERN.fullmatch(value.strip())
    if not match:
        return None
    return tuple(int(item) for item in match.groups())


def parse_ui_hints(xml_data: str) -> list[UiHint]:
    root = ElementTree.fromstring(xml_data)
    hints: list[UiHint] = []
    for node in root.iter("node"):
        bounds = parse_bounds(node.attrib.get("bounds", ""))
        if bounds is None:
            continue
        hints.append(
            UiHint(
                resource_id=node.attrib.get("resource-id", ""),
                content_desc=node.attrib.get("content-desc", ""),
                bounds=bounds,
            )
        )
    return hints


class SwanVisionAutomation:
    def __init__(
        self,
        serial: str | None = None,
        package: str = "com.swan.network",
        output_dir: str | Path | None = None,
        timeout: float = 12.0,
        trace_interval_ms: int = 50,
    ) -> None:
        self.driver = AndroidAdbDriver(serial=serial)
        self.aw = FlutterBaseAW(self.driver)
        self.package = package
        self.timeout = timeout
        self.trace_interval = max(10, trace_interval_ms) / 1000.0
        self.output_dir = Path(output_dir or PROJECT_ROOT / "output" / "swan_vision")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._capture_index = 0
        self._stage = "initializing"
        self._trace_started = time.monotonic()
        self._heartbeat_stop = threading.Event()
        self._heartbeat_thread: threading.Thread | None = None
        self._record_stop = threading.Event()
        self._record_thread: threading.Thread | None = None
        self._recording_mode = "none"

    @contextmanager
    def step(self, name: str):
        previous_stage = self._stage
        started = time.monotonic()
        self._stage = name
        LOGGER.info("STEP_START name=%s elapsed=%.3fs", name, started - self._trace_started)
        try:
            yield
        finally:
            ended = time.monotonic()
            LOGGER.info(
                "STEP_END name=%s elapsed=%.3fs duration=%.3fs",
                name,
                ended - self._trace_started,
                ended - started,
            )
            self._stage = previous_stage

    def start_trace(self) -> None:
        self._trace_started = time.monotonic()
        self._heartbeat_stop.clear()

        def heartbeat() -> None:
            tick = 0
            while not self._heartbeat_stop.wait(self.trace_interval):
                tick += 1
                LOGGER.info(
                    "TRACE_TICK tick=%d elapsed=%.6fs stage=%s screenshots=%d",
                    tick,
                    time.monotonic() - self._trace_started,
                    self._stage,
                    self._capture_index,
                )

        self._heartbeat_thread = threading.Thread(target=heartbeat, name="swan-trace", daemon=True)
        self._heartbeat_thread.start()
        LOGGER.info("TRACE_START serial=%s package=%s output_dir=%s interval_ms=%d", self.driver.serial, self.package, self.output_dir, int(self.trace_interval * 1000))

    def stop_trace(self) -> None:
        self._heartbeat_stop.set()
        if self._heartbeat_thread is not None:
            self._heartbeat_thread.join(timeout=2)
        LOGGER.info("TRACE_END elapsed=%.3fs screenshots=%d", time.monotonic() - self._trace_started, self._capture_index)

    def start_recording(
        self,
        remote_path: str = "/sdcard/swan_vision_run.mp4",
        time_limit: int = 180,
        local_path: str | Path | None = None,
    ) -> None:
        command = [
            self.driver.adb_path,
            *(["-s", self.driver.serial] if self.driver.serial else []),
            "shell",
            "screenrecord",
            "--time-limit",
            str(time_limit),
            remote_path,
        ]
        LOGGER.info("RECORD_START remote=%s", remote_path)
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        time.sleep(0.5)
        if process.poll() is not None:
            LOGGER.warning("RECORD_NATIVE_UNAVAILABLE code=%s; using ADB screenshot fallback", process.returncode)
            if local_path is None:
                raise RuntimeError("local_path is required for screenshot recording fallback")
            self._start_screenshot_recording(Path(local_path))
            return
        self._record_process = process
        self._record_remote_path = remote_path
        self._recording_mode = "native"

    def _start_screenshot_recording(self, local_path: Path, fps: float = 5.0) -> None:
        self._record_stop.clear()

        def record_frames() -> None:
            writer = None
            frame_count = 0
            next_frame = time.monotonic()
            recording_started = time.monotonic()
            try:
                while not self._record_stop.is_set():
                    now = time.monotonic()
                    if now < next_frame:
                        time.sleep(min(0.02, next_frame - now))
                        continue
                    frame = self.driver.take_screenshot()
                    if frame is not None:
                        if writer is None:
                            height, width = frame.shape[:2]
                            writer = cv2.VideoWriter(
                                str(local_path),
                                cv2.VideoWriter_fourcc(*"mp4v"),
                                fps,
                                (width, height),
                            )
                            if not writer.isOpened():
                                raise RuntimeError(f"Unable to open OpenCV video writer: {local_path}")
                        target_count = max(1, int((time.monotonic() - recording_started) * fps))
                        repeat_count = max(1, target_count - frame_count)
                        for _ in range(repeat_count):
                            writer.write(frame)
                        frame_count += repeat_count
                    next_frame += 1.0 / fps
            except Exception:
                LOGGER.exception("RECORD_FALLBACK_FAILED")
            finally:
                if writer is not None:
                    writer.release()
                LOGGER.info("RECORD_FALLBACK_FRAMES count=%d", frame_count)

        local_path.parent.mkdir(parents=True, exist_ok=True)
        self._record_thread = threading.Thread(target=record_frames, name="swan-record", daemon=True)
        self._record_thread.start()
        self._recording_mode = "screenshot"
        self._record_local_path = local_path
        LOGGER.info("RECORD_FALLBACK_START path=%s fps=%.1f", local_path, fps)

    def stop_recording(self, local_path: str | Path) -> Path:
        if self._recording_mode == "screenshot":
            self._record_stop.set()
            if self._record_thread is not None:
                self._record_thread.join(timeout=10)
            local_file = Path(local_path)
            if not local_file.exists() or local_file.stat().st_size == 0:
                raise RuntimeError(f"Screenshot recording produced no video: {local_file}")
            LOGGER.info("RECORD_SAVED path=%s size=%d mode=screenshot", local_file, local_file.stat().st_size)
            return local_file
        remote_path = getattr(self, "_record_remote_path", "/sdcard/swan_vision_run.mp4")
        process = getattr(self, "_record_process", None)
        LOGGER.info("RECORD_STOP remote=%s", remote_path)
        self.driver._run("shell", "sh", "-c", "kill -INT $(pidof screenrecord)", check=False)
        if process is not None:
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=3)
        local_file = Path(local_path)
        local_file.parent.mkdir(parents=True, exist_ok=True)
        pull = self.driver._run("pull", remote_path, str(local_file), check=False)
        if pull.returncode != 0 or not local_file.exists() or local_file.stat().st_size == 0:
            raise RuntimeError(
                f"Unable to pull screen recording to {local_file}: "
                f"{pull.stderr.decode('utf-8', errors='replace').strip()}"
            )
        self.driver._run("shell", "rm", "-f", remote_path, check=False)
        LOGGER.info("RECORD_SAVED path=%s size=%d mode=native", local_file, local_file.stat().st_size)
        return local_file

    def _dump_hints(self) -> list[UiHint]:
        self._stage = "ui_tree_dump"
        started = time.monotonic()
        self.driver._run(
            "shell",
            "uiautomator",
            "dump",
            "/sdcard/swan_vision_window.xml",
            check=False,
        )
        result = self.driver._run("shell", "cat", "/sdcard/swan_vision_window.xml")
        hints = parse_ui_hints(result.stdout.decode("utf-8", errors="replace"))
        LOGGER.info("UI_TREE duration=%.3fs nodes=%d", time.monotonic() - started, len(hints))
        return hints

    def _find_hint(self, resource_id: str) -> UiHint | None:
        candidates = self._dump_hints()
        for hint in candidates:
            if hint.resource_id == resource_id or hint.resource_id.endswith(f"/{resource_id}"):
                LOGGER.info("UI_HINT resource_id=%s content_desc=%r bounds=%s", resource_id, hint.content_desc, hint.bounds)
                return hint
        LOGGER.info("UI_HINT_MISSING resource_id=%s", resource_id)
        return None

    def _require_hint(self, resource_id: str) -> UiHint:
        hint = self._find_hint(resource_id)
        if hint is None:
            raise RuntimeError(f"UI semantic node not found: {resource_id}")
        return hint

    def _region_for_hint(self, hint: UiHint, padding: int = 12) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = hint.bounds
        window = self.driver.get_window_rect(refresh=True)
        width, height = (window[2], window[3]) if window else (x2, y2)
        left = max(0, x1 - padding)
        top = max(0, y1 - padding)
        right = min(width, x2 + padding)
        bottom = min(height, y2 + padding)
        return left, top, max(1, right - left), max(1, bottom - top)

    def _capture(self, label: str):
        self._stage = f"screenshot:{label}"
        started = time.monotonic()
        self._capture_index += 1
        safe_label = re.sub(r"[^0-9A-Za-z_.-]+", "_", label).strip("_") or "screen"
        path = self.output_dir / f"{self._capture_index:03d}_{safe_label}.png"
        image = self.aw.take_screenshot(save_path=str(path))
        if image is None:
            raise RuntimeError(f"Unable to capture Android screenshot: {path}")
        if image.ndim != 3 or image.shape[0] == 0 or image.shape[1] == 0:
            raise RuntimeError(f"Invalid screenshot image: {path}")
        LOGGER.info("SCREENSHOT label=%s path=%s shape=%s duration=%.3fs", label, path, image.shape, time.monotonic() - started)
        return image

    def wait_for_any_text(self, texts: Iterable[str], timeout: float | None = None) -> str:
        """Wait for one expected text using the shared AW OCR implementation."""
        expected = tuple(texts)
        deadline = time.monotonic() + (timeout if timeout is not None else self.timeout)
        self._stage = "wait_for_text"
        while time.monotonic() < deadline:
            for text in expected:
                if self.aw.find_text_by_ocr(text, timeout=1) is not None:
                    LOGGER.info("TEXT_ASSERTION_PASSED text=%s", text)
                    return text
            time.sleep(0.5)
        raise AssertionError(f"Text assertion failed; expected one of {expected}")

    def click_accessibility(self, resource_id: str) -> None:
        """Log a semantic node and delegate its click to AWBase."""
        with self.step(f"click_accessibility:{resource_id}"):
            hint = self._require_hint(resource_id)
            LOGGER.info("SEMANTIC_TAP resource_id=%s center=%s content_desc=%r bounds=%s", resource_id, hint.center, hint.content_desc, hint.bounds)
            self.aw.click_accessibility(resource_id)

    def click_text(self, text: str, resource_id: str | None = None) -> None:
        """Limit OCR to a semantic region, then delegate to AWBase.click_text."""
        with self.step(f"click_text:{text}"):
            region = None
            if resource_id:
                hint = self._require_hint(resource_id)
                padding = 96 if resource_id.startswith("tab_") else 12
                region = self._region_for_hint(hint, padding=padding)
                LOGGER.info("TEXT_REGION text=%s resource_id=%s region=%s padding=%d", text, resource_id, region, padding)
            self.aw.click_text(text, timeout=int(self.timeout), region=region)

    def login(self, phone: str, password: str) -> None:
        with self.step("login"):
            if self._find_hint("login_password_field") is None:
                self.click_text("密码登入", resource_id="login_use_password_button")
            self.click_accessibility("login_phone_field")
            LOGGER.info("INPUT_START field=phone length=%d", len(phone))
            self.aw.input_text(phone)
            LOGGER.info("INPUT_END field=phone")
            self.click_accessibility("login_password_field")
            LOGGER.info("INPUT_START field=password length=%d", len(password))
            self.aw.input_text(password)
            LOGGER.info("INPUT_END field=password")
            self.aw.press_back()
            self.click_accessibility("login_agreement_checkbox")
            self.click_accessibility("login_submit_button")
            self.wait_for_any_text(("推荐", "首页"))

    def logout(self) -> None:
        with self.step("logout"):
            self.click_accessibility("tab_me")
            self.click_accessibility("me_user_profile_entry")
            self.click_accessibility("person_info_logout_button")
            self.wait_for_any_text(("密码登入", "验证码登入", "登入后就可畅享音乐世界"))

    def run(self, phone: str, password: str) -> None:
        with self.step("run"):
            if self._find_hint("login_page") is None:
                LOGGER.info("PRECONDITION state=logged_in action=logout")
                self.logout()
            self.login(phone, password)
            self.logout()


def main() -> int:
    parser = argparse.ArgumentParser(description="Swan login/logout using OpenCV and OCR")
    parser.add_argument("--serial", default=os.environ.get("ANDROID_DEVICE_SERIAL"))
    parser.add_argument("--package", default=os.environ.get("SWAN_PACKAGE", "com.swan.network"))
    parser.add_argument("--output-dir", default=os.environ.get("SWAN_VISION_OUTPUT"))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("SWAN_VISION_TIMEOUT", "12")))
    parser.add_argument("--trace-interval-ms", type=int, default=int(os.environ.get("SWAN_TRACE_INTERVAL_MS", "50")))
    parser.add_argument("--trace-log", default=os.environ.get("SWAN_TRACE_LOG"))
    parser.add_argument("--recording", default=os.environ.get("SWAN_RECORDING"))
    parser.add_argument("--no-record", action="store_true", help="disable Android screen recording")
    args = parser.parse_args()

    phone = os.environ.get("SWAN_PHONE", "").strip()
    password = os.environ.get("SWAN_PASSWORD", "")
    if not phone or not password:
        parser.error("set SWAN_PHONE and SWAN_PASSWORD environment variables")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    automation = None
    file_handler = None
    recording_started = False
    try:
        automation = SwanVisionAutomation(
            serial=args.serial,
            package=args.package,
            output_dir=args.output_dir,
            timeout=args.timeout,
            trace_interval_ms=args.trace_interval_ms,
        )
        stamp = time.strftime("%Y%m%d_%H%M%S")
        trace_path = Path(args.trace_log) if args.trace_log else automation.output_dir / f"run_{stamp}.log"
        recording_path = Path(args.recording) if args.recording else automation.output_dir / f"run_{stamp}.mp4"
        file_handler = logging.FileHandler(trace_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"))
        LOGGER.addHandler(file_handler)
        LOGGER.setLevel(logging.INFO)
        automation.start_trace()
        if not args.no_record:
            automation.start_recording(local_path=recording_path)
            recording_started = True
        automation.run(phone, password)
    except Exception:
        if automation is not None:
            LOGGER.exception("Swan OpenCV/OCR flow failed stage=%s", automation._stage)
        else:
            LOGGER.exception("Swan OpenCV/OCR flow failed")
        return 1
    finally:
        if automation is not None:
            if recording_started:
                try:
                    automation.stop_recording(recording_path)
                except Exception:
                    LOGGER.exception("RECORD_SAVE_FAILED")
            automation.stop_trace()
        if file_handler is not None:
            LOGGER.removeHandler(file_handler)
            file_handler.close()
    LOGGER.info("Swan login/logout flow passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
