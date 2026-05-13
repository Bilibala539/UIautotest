#!/bin/bash
# POPO UIAutotest 结果上报脚本（Mac / Linux）
# 用法：./run.sh
cd "$(dirname "$0")"

SERVER="http://10.220.28.125/reports"

# ── 1. 下载上报组件 ───────────────────────────────
if [ ! -f report_uploader.py ]; then
    echo "📥 下载上报组件..."
    curl -sSf "$SERVER/report_uploader.py" -o report_uploader.py \
        || { echo "❌ 下载失败，请确认能访问 $SERVER"; exit 1; }
fi

# ── 2. 安装依赖 ───────────────────────────────────
python3 -c "import paramiko, scp" 2>/dev/null \
    || pip3 install paramiko scp -q

# ── 3. 首次配置（只问一次）────────────────────────
if [ ! -f .run_config ]; then
    echo ""
    echo "首次配置（只需输入一次）："
    read -p "  平台名称（如 iOS / Mac / Web）: " _P
    read -p "  项目名称（如 POPO-iOS）:        " _N
    printf 'UPLOADER_PLATFORM="%s"\nUPLOADER_PROJECT="%s"\n' "$_P" "$_N" > .run_config
fi
source .run_config
export UPLOADER_PLATFORM UPLOADER_PROJECT

# ── 4. 自动修改 pytest.ini，让 PyCharm/agent 也能上报 ──
python3 - <<'EOF'
import os, re

for ini in ("pytest.ini", "setup.cfg", "pyproject.toml"):
    if not os.path.isfile(ini):
        continue
    txt = open(ini, encoding="utf-8").read()
    if "report_uploader" in txt:
        break                          # 已配置，跳过
    if re.search(r"addopts\s*=", txt):
        txt = re.sub(r"(addopts\s*=\s*)", r"\1-p report_uploader ", txt, count=1)
    else:
        txt += "\naddopts = -p report_uploader\n"
    open(ini, "w", encoding="utf-8").write(txt)
    print(f"✅ 已更新 {ini}（PyCharm / agent 运行也会自动上报）")
    break
EOF

# ── 5. 跑测试，结束后自动上报 ─────────────────────
echo ""
echo "▶  平台：$UPLOADER_PLATFORM  项目：$UPLOADER_PROJECT"
echo "▶  执行：pytest ${1:-tests/}"
echo ""
pytest "${1:-tests/}" -v -p report_uploader

echo ""
echo "✅ 完成 → http://10.220.28.125/reports/allure-report/history.html"
