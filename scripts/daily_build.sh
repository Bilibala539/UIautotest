#!/bin/bash
# 每日定时打包(2026-09-22):凌晨触发 dev 分支测试服+正式服各一包。
# 走平台 POST /api/builds 统一入口——与手动打包/同链路校验/登记完全一致;
# Jenkins swan-audio-build concurrentBuild=false 自动串行,总耗时约 2×构建时长。
# 环境变量:PLATFORM_URL(默认 http://127.0.0.1:8080)、DAILY_BUILD_NOTES(默认 daily)、
#          DRY_RUN=1 只打印不真发(自测用)。
set -u
PLATFORM_URL="${PLATFORM_URL:-http://127.0.0.1:8080}"
NOTES="${DAILY_BUILD_NOTES:-daily}"
status=0
for st in test formal; do
    echo "[daily-build] $(date '+%F %T') trigger dev/$st"
    if [ "${DRY_RUN:-0}" = "1" ]; then
        echo "[daily-build] DRY_RUN: POST $PLATFORM_URL/api/builds {branch:dev,server_type:$st,notes:$NOTES}"
        continue
    fi
    resp_file=$(mktemp)
    code=$(curl -s -m 30 -o "$resp_file" -w '%{http_code}' -X POST \
        -H 'Content-Type: application/json' \
        -d "{\"branch\":\"dev\",\"server_type\":\"$st\",\"notes\":\"$NOTES\"}" \
        "$PLATFORM_URL/api/builds")
    echo "[daily-build] http=$code body=$(cat "$resp_file")"
    rm -f "$resp_file"
    if [ "$code" != "200" ]; then
        echo "[daily-build] dev/$st 触发失败(http=$code)"
        status=1
    fi
done
exit $status
