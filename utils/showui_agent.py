"""
ShowUI-2B 元素定位 Agent（Windows CUDA 版）

用途：从 UI 截图中通过自然语言描述自动定位元素坐标。
运行环境：独立 venv (.venv-showui, Python 3.12 + torch CUDA)
项目主环境(Python 3.9)不直接 import 本文件，通过 subprocess 调用。

用法：
    .venv-showui\\Scripts\\python.exe utils/showui_agent.py serve          # 启动常驻服务（推荐）
    .venv-showui\\Scripts\\python.exe utils/showui_agent.py locate <screenshot.png> "元素描述"
    .venv-showui\\Scripts\\python.exe utils/showui_agent.py ground <screenshot.png> "元素描述"
"""

import argparse
import json
import os
import re
import sys
import time

import torch
from PIL import Image

MODEL_PATH = os.path.expanduser(
    "~/.cache/huggingface/hub/models--showlab--ShowUI-2B"
)

# 允许通过环境变量覆盖模型路径
if os.environ.get("SHOWUI_MODEL_PATH"):
    MODEL_PATH = os.environ["SHOWUI_MODEL_PATH"]

_model = None
_processor = None


def _get_device():
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _get_dtype():
    if torch.cuda.is_available():
        return torch.float16
    return torch.float32


def _load_model():
    global _model
    if _model is not None:
        return _model

    from transformers import Qwen2VLForConditionalGeneration

    device = _get_device()
    dtype = _get_dtype()

    try:
        _model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_PATH,
            torch_dtype=dtype,
            device_map=device if device == "cuda" else None,
        )
    except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
        if "out of memory" in str(e).lower() or "CUDA" in str(e):
            print(
                json.dumps({"warning": "GPU显存不足，降级到CPU模式"}, ensure_ascii=False),
                file=sys.stderr,
            )
            torch.cuda.empty_cache()
            _model = Qwen2VLForConditionalGeneration.from_pretrained(
                MODEL_PATH,
                torch_dtype=torch.float32,
                device_map=None,
            )
            _model = _model.to("cpu")
        else:
            raise

    if device == "cpu" and not hasattr(_model, "_on_cpu_fallback"):
        _model = _model.to(device)
    _model.eval()
    return _model


def _load_processor():
    global _processor
    if _processor is not None:
        return _processor

    from transformers import AutoProcessor

    _processor = AutoProcessor.from_pretrained(MODEL_PATH)
    return _processor


def _parse_click_point(text, img_width, img_height):
    """解析 ShowUI 输出的归一化坐标点 (x, y) ∈ [0, 1]"""
    pattern = r"\[\s*([\d.]+)\s*,\s*([\d.]+)\s*\]"
    match = re.search(pattern, text)
    if not match:
        pattern2 = r"([\d.]+)\s*,\s*([\d.]+)"
        match = re.search(pattern2, text)
    if not match:
        return None

    nx, ny = float(match.group(1)), float(match.group(2))
    if nx > 1.0 or ny > 1.0:
        x, y = int(nx), int(ny)
    else:
        x = int(nx * img_width)
        y = int(ny * img_height)

    return {"x": x, "y": y}


def _center_to_bbox(cx, cy, img_width, img_height, padding=30):
    """从中心点扩展为 bbox，默认 padding 30px（适合中小型 UI 元素）"""
    x1 = max(0, cx - padding)
    y1 = max(0, cy - padding)
    x2 = min(img_width, cx + padding)
    y2 = min(img_height, cy + padding)
    return [x1, y1, x2, y2]


def locate(screenshot_path, element_desc, bbox_padding=30):
    """
    定位元素，返回 center + bbox。

    Args:
        screenshot_path: 截图文件路径
        element_desc: 元素的自然语言描述
        bbox_padding: 中心点向外扩展的像素数（默认30）

    Returns:
        dict: {"status": "ok", "center": [x, y], "bbox": [x1, y1, x2, y2], "confidence": float, "raw_output": str}
    """
    if not os.path.isfile(screenshot_path):
        return {"status": "error", "message": f"截图文件不存在: {screenshot_path}"}

    img = Image.open(screenshot_path)
    img_width, img_height = img.size

    model = _load_model()
    processor = _load_processor()

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": screenshot_path,
                    "min_pixels": 256 * 28 * 28,
                    "max_pixels": 1344 * 28 * 28,
                },
                {"type": "text", "text": element_desc},
            ],
        }
    ]

    from qwen_vl_utils import process_vision_info

    text_input = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    image_inputs, video_inputs = process_vision_info(messages)

    inputs = processor(
        text=[text_input],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )

    device = _get_device()
    inputs = inputs.to(device)

    t0 = time.time()
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=16)

    input_len = inputs["input_ids"].shape[1]
    generated_ids = output_ids[:, input_len:]
    raw_output = processor.batch_decode(
        generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
    )[0]
    inference_time = time.time() - t0

    point = _parse_click_point(raw_output, img_width, img_height)
    if point is None:
        return {
            "status": "error",
            "message": "无法从模型输出中解析坐标",
            "raw_output": raw_output,
            "inference_time_s": round(inference_time, 2),
        }

    cx, cy = point["x"], point["y"]
    bbox = _center_to_bbox(cx, cy, img_width, img_height, padding=bbox_padding)

    return {
        "status": "ok",
        "center": [cx, cy],
        "bbox": bbox,
        "confidence": 0.9,
        "raw_output": raw_output,
        "inference_time_s": round(inference_time, 2),
        "device": device,
    }


def ground(screenshot_path, element_desc, output_dir=None, bbox_padding=30):
    """
    定位 + 裁剪一步到位（兼容 Mac 版行为）。

    Returns:
        dict: locate 结果 + crop 路径
    """
    result = locate(screenshot_path, element_desc, bbox_padding=bbox_padding)
    if result["status"] != "ok":
        return result

    if output_dir is None:
        output_dir = os.path.join(os.environ.get("TEMP", "/tmp"), "showui_crops")
    os.makedirs(output_dir, exist_ok=True)

    img = Image.open(screenshot_path)
    x1, y1, x2, y2 = result["bbox"]
    cropped = img.crop((x1, y1, x2, y2))

    safe_name = re.sub(r'[\\/:*?"<>|\s]', "_", element_desc)[:40]
    crop_path = os.path.join(output_dir, f"showui_{safe_name}.png")
    cropped.save(crop_path)

    latest_path = os.path.join(output_dir, "latest.png")
    cropped.save(latest_path)

    result["crop"] = crop_path
    result["latest"] = latest_path
    return result


def _call_server(endpoint, screenshot_path, element_desc, bbox_padding=30, output_dir=None):
    """向常驻服务发送请求（模型已预加载，响应快）"""
    import urllib.request
    import urllib.error

    payload = {
        "screenshot": screenshot_path,
        "description": element_desc,
        "padding": bbox_padding,
    }
    if output_dir:
        payload["output_dir"] = output_dir

    url = f"http://127.0.0.1:7860/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError:
        return None


def _server_available():
    """检测常驻服务是否在运行"""
    import urllib.request
    import urllib.error

    try:
        with urllib.request.urlopen("http://127.0.0.1:7860/health", timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def serve(host="127.0.0.1", port=7860):
    """启动常驻 HTTP 服务，模型只加载一次，后续请求直接推理（~3-5s/次）"""
    from http.server import HTTPServer, BaseHTTPRequestHandler

    print(f"正在加载模型到 {_get_device()}...", flush=True)
    _load_model()
    _load_processor()
    print(f"模型加载完成，服务监听 {host}:{port}", flush=True)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length).decode("utf-8"))

            screenshot = body["screenshot"]
            description = body["description"]
            padding = body.get("padding", 30)
            output_dir = body.get("output_dir")

            if self.path == "/locate":
                result = locate(screenshot, description, bbox_padding=padding)
            elif self.path == "/ground":
                result = ground(screenshot, description, output_dir=output_dir, bbox_padding=padding)
            else:
                result = {"status": "error", "message": f"未知端点: {self.path}"}

            response = json.dumps(result, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"ok")
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            print(f"[ShowUI] {args[0]}", flush=True)

    server = HTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()


def _auto_start_server():
    """自动在后台拉起 ShowUI 服务进程，等待就绪后返回 True"""
    import subprocess
    import urllib.request
    import urllib.error

    python_exe = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".venv-showui", "Scripts", "python.exe"
    )
    if not os.path.isfile(python_exe):
        python_exe = sys.executable

    script_path = os.path.abspath(__file__)

    print(
        json.dumps({"info": "ShowUI 服务未运行，正在自动启动..."}, ensure_ascii=False),
        file=sys.stderr,
    )

    CREATE_NO_WINDOW = 0x08000000
    subprocess.Popen(
        [python_exe, script_path, "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_NO_WINDOW,
    )

    for _ in range(60):
        time.sleep(3)
        try:
            with urllib.request.urlopen("http://127.0.0.1:7860/health", timeout=2) as resp:
                if resp.status == 200:
                    print(
                        json.dumps({"info": "ShowUI 服务已就绪"}, ensure_ascii=False),
                        file=sys.stderr,
                    )
                    return True
        except (urllib.error.URLError, OSError):
            continue

    print(
        json.dumps({"warning": "ShowUI 服务启动超时（3分钟）"}, ensure_ascii=False),
        file=sys.stderr,
    )
    return False


def main():
    parser = argparse.ArgumentParser(
        description="ShowUI-2B 元素定位 Agent"
    )
    subparsers = parser.add_subparsers(dest="command")

    loc_parser = subparsers.add_parser(
        "locate", help="定位元素坐标（不裁剪）"
    )
    loc_parser.add_argument("screenshot", help="截图文件路径")
    loc_parser.add_argument("description", help="元素自然语言描述")
    loc_parser.add_argument(
        "--padding", type=int, default=30, help="bbox 扩展像素（默认30）"
    )

    gnd_parser = subparsers.add_parser(
        "ground", help="定位 + 裁剪（兼容 Mac 版）"
    )
    gnd_parser.add_argument("screenshot", help="截图文件路径")
    gnd_parser.add_argument("description", help="元素自然语言描述")
    gnd_parser.add_argument(
        "--padding", type=int, default=30, help="bbox 扩展像素（默认30）"
    )
    gnd_parser.add_argument("--output-dir", default=None, help="裁剪输出目录")

    srv_parser = subparsers.add_parser(
        "serve", help="启动常驻服务（模型预加载）"
    )
    srv_parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    srv_parser.add_argument("--port", type=int, default=7860, help="监听端口")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "serve":
        serve(host=args.host, port=args.port)
        return

    # locate / ground：检测服务 → 没有就自动拉起 → 走 HTTP
    if not _server_available():
        _auto_start_server()

    if args.command == "locate":
        if _server_available():
            result = _call_server("locate", args.screenshot, args.description, args.padding)
            if result:
                print(json.dumps(result, ensure_ascii=False))
                sys.exit(0 if result.get("status") == "ok" else 1)
        result = locate(args.screenshot, args.description, bbox_padding=args.padding)
    elif args.command == "ground":
        if _server_available():
            result = _call_server("ground", args.screenshot, args.description, args.padding, args.output_dir)
            if result:
                print(json.dumps(result, ensure_ascii=False))
                sys.exit(0 if result.get("status") == "ok" else 1)
        result = ground(
            args.screenshot,
            args.description,
            output_dir=args.output_dir,
            bbox_padding=args.padding,
        )
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get("status") == "ok" else 1)


if __name__ == "__main__":
    main()
