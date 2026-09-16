# UIAutotest 知识库

本目录是与 `docs/` 平级的知识库入口，按客户端平台隔离内容。

## 知识库分区

| 平台 | 知识库路径 | 状态 |
|---|---|---|
| TidyTree Web | `explorer_output/knowledge/` | 已有 Web 页面和流程知识 |
| TidyTree Android | `knowledge/android/` | 已建立骨架，等待真机探索录入 |

两个知识库是独立的 Obsidian-style vault：页面、导航图、反向链接、审计状态和后续向量索引不得混用。跨平台对照时，在文档中显式标注 `Web` 或 `Android`，不要复用相同的 `page_id`。

Android 知识库的入口说明见 `knowledge/android/README.md`。

## 同事上手（git 拉取后环境搭建）

知识库内容（页面文档、app_map、向量索引 `*/.chroma_db`）已随仓库上传，拉取后只需补齐运行环境：

1. **克隆路径必须是 `E:\UIAutotest`** —— `.mcp.json` 中各 MCP 服务的 `command`/`cwd`/环境变量写死了该绝对路径；装到其他位置需自行修改 `.mcp.json`。
2. 创建 venv 并安装依赖（先 CPU 版 torch，再其余依赖，避免拉取 CUDA 大包）：
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   pip install -r requirements.txt -r requirements_kb.txt
   ```
3. 下载嵌入模型（约 500MB，走 ModelScope 国内源）：
   ```bash
   python scripts/download_embedding_model.py --verify
   ```
   模型不入 git（`.gitignore` 排除 `models/`），只下载 sentence-transformers 实际需要的文件。
4. 重启 Claude Code，即可使用 `knowledge_graph_swan` / `vector_kb_swan` 等 MCP。向量索引无需重建；若增删了知识文档，按 `knowledge/swan/CONTRIBUTING.md` 里的 embedding_pipeline 重新生成。

注：`knowledge/web` 与 `knowledge/android` 尚未生成向量索引（`.chroma_db`），对应 `vector_kb_*` 服务需先在本地跑一次 embedding_pipeline 才可用；Swan 知识库已就绪。
