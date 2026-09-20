# -*- coding: utf-8 -*-
"""竞品视觉采集:公开页面 -> 整页/首屏截图 + 计算样式 JSON
用法:
    python scripts/design_shot.py <url> <名称> [输出目录]
输出(默认 docs/竞品截图/auto/<名称>/):
    viewport.png  首屏 1440x900
    fullpage.png  整页(高最多 12000px)
    styles.json   采样元素计算样式(色值/字号/圆角/间距/阴影) + 全页色板 Top25
仅限公开可访问页面;登录墙内页面请人工截图。
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 采样这些选择器的计算样式(每类最多 8 个,总采样去重后上限 200)
SELECTORS = [
    "body", "h1", "h2", "h3", "h4", "a", "button", "input", "table", "th", "td",
    '[class*="btn"]', '[class*="button"]', '[class*="badge"]', '[class*="tag"]',
    '[class*="chip"]', '[class*="card"]', '[class*="drawer"]', '[class*="modal"]',
    '[class*="table"]', '[class*="row"]', '[class*="item"]',
]
PROPS = [
    "background-color", "color", "font-size", "font-weight", "font-family",
    "border-radius", "padding", "margin", "border", "box-shadow",
    "line-height", "letter-spacing", "height",
]
# 全页色板统计的属性
PALETTE_PROPS = ["background-color", "color", "border-top-color"]

COLLECT_JS = """
const PROPS = %s, PALETTE_PROPS = %s, SELECTORS = %s;
function clsOf(el){
  const c = el.className;
  if (typeof c !== 'string') return '';
  return c.slice(0, 60);
}
function pick(el, sel){
  const cs = getComputedStyle(el);
  const o = {sel, tag: el.tagName.toLowerCase(), cls: clsOf(el),
             text: (el.textContent || '').trim().slice(0, 40)};
  for (const p of PROPS) o[p] = cs.getPropertyValue(p);
  return o;
}
const seen = new Set(), sample = [];
for (const sel of SELECTORS){
  let els;
  try { els = document.querySelectorAll(sel); } catch (e) { continue; }
  for (let i = 0; i < els.length && i < 8; i++){
    const o = pick(els[i], sel);
    const key = sel + '|' + o['background-color'] + '|' + o.color + '|' + o['font-size'] + '|' + o['border-radius'];
    if (seen.has(key)) continue;
    seen.add(key); sample.push(o);
  }
  if (sample.length > 200) break;
}
const cnt = {};
document.querySelectorAll('*').forEach(el => {
  const cs = getComputedStyle(el);
  for (const p of PALETTE_PROPS){
    const v = cs.getPropertyValue(p);
    if (v && v !== 'rgba(0, 0, 0, 0)'){
      const k = p + ' ' + v;
      cnt[k] = (cnt[k] || 0) + 1;
    }
  }
});
const palette = Object.entries(cnt).sort((a, b) => b[1] - a[1]).slice(0, 25)
  .map(([k, n]) => ({prop_color: k, count: n}));
return {url: location.href, title: document.title, viewport: {w: innerWidth, h: innerHeight},
        page_height: document.body.scrollHeight, sample, palette};
""" % (json.dumps(PROPS), json.dumps(PALETTE_PROPS), json.dumps(SELECTORS))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    url, name = sys.argv[1], sys.argv[2]
    out_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "docs" / "竞品截图" / "auto" / name
    out_dir.mkdir(parents=True, exist_ok=True)

    from selenium import webdriver
    from selenium.webdriver.edge.options import Options as EdgeOptions

    opts = EdgeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1440,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--hide-scrollbars")
    opts.add_argument("--log-level=3")
    driver = webdriver.Edge(options=opts)
    try:
        driver.set_page_load_timeout(45)
        driver.get(url)
        time.sleep(3)  # 等字体/图表等异步资源

        # 首屏
        driver.get_screenshot_as_file(str(out_dir / "viewport.png"))

        # 滚到底触发懒加载,再回顶部
        total = driver.execute_script("return document.body.scrollHeight")
        for y in range(0, total, 1200):
            driver.execute_script(f"window.scrollTo(0, {y})")
            time.sleep(0.15)
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(0.5)

        # 整页:窗口拉高后截(上限 12000)
        full_h = min(driver.execute_script("return document.body.scrollHeight"), 12000)
        driver.set_window_size(1440, full_h)
        time.sleep(1)
        driver.get_screenshot_as_file(str(out_dir / "fullpage.png"))

        # 恢复窗口再采样式,避免拉高窗口影响 lazy 渲染判定
        data = driver.execute_script(COLLECT_JS)
        (out_dir / "styles.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

        print(f"OK page_height={data['page_height']} 输出目录={out_dir}")
        print("palette 前 10:")
        for item in data["palette"][:10]:
            print(f"  {item['prop_color']}  x{item['count']}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
