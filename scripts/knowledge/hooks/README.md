# KB 双层索引自动同步钩子(部署包)

git 钩子是**机器本地文件**(不进 git),本目录是部署源。任何要在本机承担"索引重建"职责的机器,按下面步骤部署一次即可。

## 部署(Windows + Git for Windows)

1. 前置:venv 里 `pip install chromadb sentence-transformers`;embedding 模型放到
   `E:\uiautotest\models\paraphrase-multilingual-MiniLM-L12-v2`
   (用本目录上级的 `download_kb_model.ps1` 下载;hf-mirror 已失效,脚本走 modelscope)
2. 拷贝三个文件到 `.git\hooks\`:`kb_auto_update.sh`、`post-commit`、`post-merge`
3. 确认脚本里的路径与本机一致(仓库根 `/e/uiautotest`、模型路径、venv 位置)
4. 验证:手动跑一次 `"C:\Program Files\Git\bin\sh.exe" .git\hooks\post-commit`,应输出
   auto_update 摘要且工作区不残留未提交变更

## 行为

- post-commit:以 HEAD~1 为基准检测变更;post-merge(git pull 后):以 ORIG_HEAD 为基准
- KB(`knowledge/swan`)有变更 → 重建 backlinks + 增量 embedding → 索引产物自动 commit
  (`chore(kb): 自动同步双层索引`,含生成器写回 pages/digest 的时间戳)
- `KB_INDEX_HOOK=1` 环境变量防止递归;auto_update.py 支持 `KB_DIFF_BASE` 覆盖 diff 基准
- ⚠ auto_update.py 默认指向 web 库,钩子里已显式传
  `--knowledge-dir knowledge/swan --chroma-dir knowledge/swan/.chroma_db`,改动钩子时别丢这两个参数
