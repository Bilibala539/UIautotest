#!/bin/sh
# KB 双层索引自动同步钩子(由 post-commit / post-merge 调用)
# 动作:KB 相关文件有变更时,重建 backlinks + 增量 embedding;
#       索引产物有 diff 则自动 commit(用 KB_INDEX_HOOK 防递归)。
# 环境变量:KB_DIFF_BASE 控制变更检测基准(post-merge 传 ORIG_HEAD)。

[ "$KB_INDEX_HOOK" = "1" ] && exit 0
export KB_INDEX_HOOK=1

cd /e/uiautotest || exit 0
[ -x .venv/Scripts/python.exe ] || exit 0

export UIAUTOTEST_KNOWLEDGE_DIR=knowledge/swan
export UIAUTOTEST_CHROMA_DIR=knowledge/swan/.chroma_db
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export UIAUTOTEST_EMBEDDING_MODEL='E:\uiautotest\models\paraphrase-multilingual-MiniLM-L12-v2'
[ -n "$KB_DIFF_BASE" ] && export KB_DIFF_BASE

PY=.venv/Scripts/python.exe
"$PY" scripts/knowledge/auto_update.py --knowledge-dir knowledge/swan --chroma-dir knowledge/swan/.chroma_db || exit 0

# 索引产物有变更则自动提交(含生成器写回 pages/digest 的时间戳;防递归由 KB_INDEX_HOOK 保证)
if ! git diff --quiet -- knowledge/swan 2>/dev/null; then
    git add knowledge/swan
    git commit -m "chore(kb): 自动同步双层索引(backlinks+chroma)" -q
fi
