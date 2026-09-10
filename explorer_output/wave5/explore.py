"""Wave 5 AI/Vision/视频域探索 runner（enrich-kb 模式）。

用法: python explore.py <cmd> [args...]

cmd:
  state [name]      截图 + dump 语义树 + OCR 全量（一站式）
  dump [name]       dump 语义树（可读表格，存 wave5/dumps/）
  ocr [name]        OCR 全量扫描
  shot <name>       截图到 explorer_output/wave5/
  ck <key>          click_accessibility(key)
  ct <text>         click_text(OCR 文案)
  ci <CONST>        click_image(image_name_mapping 常量名)
  ie <CONST>        image_exists(常量) 只断言不点
  keys              列出当前页全部 resource_id（去重）
  back              press_back
  home              go_home（tab_recommend）
  start / stop      启动 / 强停 App
  swipe up|down [n] 滑动 n 次（默认 1）
  raw [x1 y1 x2 y2] 区域内全部原始节点
  tap <x> <y>       探索专用：点窗口坐标（仅无语义图标探测，知识库不落坐标）
  sleep <sec>       等待
"""
import os
import sys
import logging

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
logging.basicConfig(level=logging.WARNING)

sys.path.insert(0, r"E:\UIAutotest")

from dotenv import load_dotenv

load_dotenv(r"E:\UIAutotest\.env")
load_dotenv(r"E:\UIAutotest\.env.local")
os.environ.setdefault("PLATFORM", "flutter")
os.environ.setdefault("ANDROID_DEVICE_SERIAL", "c0614b6a")

from utils.aw.driver.flutter_driver import FlutterAndroidDriver
from utils.user import SwanUser
import image.image_name_mapping as imgmap

u = SwanUser(driver=FlutterAndroidDriver())
b = u.aw
PACKAGE = os.environ.get("SWAN_PACKAGE", "com.swan.network").strip()
BASE = r"E:\UIAutotest\explorer_output\wave5"
DUMP_DIR = os.path.join(BASE, "dumps")


def shot(name):
    p = b.screenshot_for_explore(filename=name, subdir="wave5")
    print(f"[SHOT] {p}")
    return p


def dump_nodes():
    for attempt in range(3):
        nodes = b.dump_semantics()
        seen0 = set()
        rows0 = []
        for n in nodes:
            rid0 = (n["resource_id"] or "").split("/")[-1]
            if rid0 or n["text"] or n["content_desc"] or n["clickable"]:
                k0 = (rid0, n["text"], n["content_desc"], n["bounds"])
                if k0 not in seen0:
                    seen0.add(k0)
                    rows0.append(n)
        if len(rows0) >= 3:
            break
        b.sleep(1.5)  # dump 瞬时失败（动画中），重试
    seen = set()
    rows = []
    for n in nodes:
        rid = (n["resource_id"] or "").split("/")[-1]
        text = n["text"] or ""
        desc = n["content_desc"] or ""
        if not (rid or text or desc or n["clickable"]):
            continue
        key = (rid, text, desc, n["bounds"])
        if key in seen:
            continue
        seen.add(key)
        rows.append((n["clickable"], rid, text, desc, n["bounds"]))
    return rows


def print_dump(name=None):
    rows = dump_nodes()
    print(f"[DUMP] {len(rows)} 个有效节点")
    for click, rid, text, desc, box in rows:
        bstr = f"[{box[0]},{box[1]}][{box[2]},{box[3]}]" if box else "?"
        print(f"{'*' if click else ' '} {rid:<48} text={text!r:<24} desc={desc!r:<24} {bstr}")
    if name:
        os.makedirs(DUMP_DIR, exist_ok=True)
        path = os.path.join(DUMP_DIR, f"{name}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# dump {name}\n")
            for click, rid, text, desc, box in rows:
                bstr = f"[{box[0]},{box[1]}][{box[2]},{box[3]}]" if box else "?"
                f.write(f"{'*' if click else ' '} {rid}\ttext={text!r}\tdesc={desc!r}\t{bstr}\n")
        print(f"[DUMP] saved -> {path}")


def print_ocr(name=None):
    items = b.ocr_scan_page()
    lines = [f"[OCR] {len(items)} 项"]
    for i in items:
        lines.append(f"  {i['text']!r} @({i['cx']},{i['cy']}) bbox={i['bbox']} conf={i['confidence']:.2f}")
    print("\n".join(lines))
    if name:
        os.makedirs(DUMP_DIR, exist_ok=True)
        with open(os.path.join(DUMP_DIR, f"{name}_ocr.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def get_img(const_name):
    v = getattr(imgmap, const_name, None)
    if v is None:
        print(f"[ERR] 常量不存在: {const_name}")
        sys.exit(2)
    return v


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "state"
    args = sys.argv[2:]
    if cmd == "state":
        name = args[0] if args else "state"
        shot(f"{name}.png")
        print_dump(name)
        print_ocr(name)
    elif cmd == "dump":
        print_dump(args[0] if args else None)
    elif cmd == "ocr":
        print_ocr(args[0] if args else None)
    elif cmd == "shot":
        shot(args[0] if args else "shot.png")
    elif cmd == "ck":
        b.click_accessibility(args[0])
        b.sleep(1.5)
        print(f"[CK] clicked {args[0]}")
    elif cmd == "ct":
        b.click_text(args[0])
        b.sleep(1.5)
        print(f"[CT] clicked text {args[0]}")
    elif cmd == "ci":
        b.click_image(get_img(args[0]))
        b.sleep(1.5)
        print(f"[CI] clicked image {args[0]}")
    elif cmd == "ie":
        r = b.image_exists(get_img(args[0]))
        print(f"[IE] {args[0]} exists={r}")
    elif cmd == "keys":
        ids = []
        for n in b.dump_semantics():
            rid = (n["resource_id"] or "").split("/")[-1]
            if rid and rid not in ids:
                ids.append(rid)
        print(f"[KEYS] {len(ids)} 个")
        for rid in ids:
            print(f"  {rid}")
    elif cmd == "back":
        b.press_back()
        b.sleep(1.5)
        print("[BACK]")
    elif cmd == "home":
        b.go_home()
        print("[HOME]")
    elif cmd == "start":
        b.driver.start_app(PACKAGE)
        b.sleep(5)
        print("[START]")
    elif cmd == "stop":
        b.driver.stop_app(PACKAGE)
        print("[STOP]")
    elif cmd == "swipe":
        direction = args[0] if args else "up"
        n = int(args[1]) if len(args) > 1 else 1
        for _ in range(n):
            if direction == "up":
                b.swipe_up(400)
            else:
                b.swipe_down(400)
            b.sleep(0.8)
        print(f"[SWIPE] {direction} x{n}")
    elif cmd == "raw":
        if len(args) >= 4:
            x1, y1, x2, y2 = map(int, args[:4])
        else:
            x1, y1, x2, y2 = 0, 0, 720, 1600
        for n in b.dump_semantics():
            box = n["bounds"]
            if not box:
                continue
            if box[0] >= x2 or box[2] <= x1 or box[1] >= y2 or box[3] <= y1:
                continue
            rid = (n["resource_id"] or "").split("/")[-1]
            print(f"{'*' if n['clickable'] else ' '} {n['class_name']:<28} {rid:<40} "
                  f"desc={n['content_desc']!r} [{box[0]},{box[1]}][{box[2]},{box[3]}]")
    elif cmd == "tap":
        # 探索专用：点窗口坐标（仅用于无语义图标探测，知识库不落坐标）
        b.tap(int(args[0]), int(args[1]))
        b.sleep(1.5)
        print(f"[TAP] ({args[0]},{args[1]})")
    elif cmd == "sleep":
        b.sleep(float(args[0]))
        print("[SLEEP] done")
    else:
        print(f"未知命令: {cmd}")
        sys.exit(2)


if __name__ == "__main__":
    main()
