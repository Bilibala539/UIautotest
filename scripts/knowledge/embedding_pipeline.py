"""
Embedding Pipeline — 知识库向量化

将 pages/*.md + tests/*.py + docs/*.md 做 chunking + embedding，存入 ChromaDB。

用法:
  python scripts/knowledge/embedding_pipeline.py              # 全量构建
  python scripts/knowledge/embedding_pipeline.py --incremental # 增量更新（基于文件修改时间）
  python scripts/knowledge/embedding_pipeline.py --query "会话分组"  # 测试查询

存储位置: .chroma_db/ (本地持久化)
"""

import os
import sys
import re
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

PROJ_ROOT = Path(__file__).parent.parent.parent
KNOWLEDGE_DIR = Path(os.environ.get("UIAUTOTEST_KNOWLEDGE_DIR", PROJ_ROOT / "knowledge/web"))
if not KNOWLEDGE_DIR.is_absolute():
    KNOWLEDGE_DIR = PROJ_ROOT / KNOWLEDGE_DIR
CHROMA_DIR = Path(os.environ.get("UIAUTOTEST_CHROMA_DIR", PROJ_ROOT / ".chroma_db"))
if not CHROMA_DIR.is_absolute():
    CHROMA_DIR = PROJ_ROOT / CHROMA_DIR
STATE_FILE = CHROMA_DIR / "index_state.json"

SCAN_CONFIGS = [
    {
        "name": "knowledge_pages",
        "path": KNOWLEDGE_DIR / "pages",
        "glob": "*.md",
        "chunk_size": 500,
        "overlap": 50,
    },
    {
        "name": "knowledge_digest",
        "path": KNOWLEDGE_DIR / "digest",
        "glob": "**/*.md",
        "chunk_size": 500,
        "overlap": 50,
    },
    {
        "name": "test_cases",
        "path": PROJ_ROOT / "tests",
        "glob": "**/*.py",
        "chunk_size": 800,
        "overlap": 100,
    },
    {
        "name": "docs",
        "path": PROJ_ROOT / "docs",
        "glob": "*.md",
        "chunk_size": 600,
        "overlap": 80,
    },
]


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """将文本按段落/标题分块，保持语义完整性"""
    # 剥掉 YAML frontmatter，避免污染语义索引
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)

    # 按标题或双换行分割
    sections = re.split(r'\n(?=## |\n\n)', text)

    chunks = []
    current_chunk = ""

    for section in sections:
        if len(current_chunk) + len(section) <= chunk_size:
            current_chunk += section + "\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            # 保留 overlap
            if overlap > 0 and current_chunk:
                current_chunk = current_chunk[-overlap:] + section + "\n"
            else:
                current_chunk = section + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # 如果没有分块成功，整个文本作为一块
    if not chunks and text.strip():
        chunks = [text.strip()]

    return chunks


def compute_file_hash(filepath: Path) -> str:
    """计算文件 MD5"""
    return hashlib.md5(filepath.read_bytes()).hexdigest()


def build_index(incremental: bool = False):
    """构建/更新向量索引"""
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    print("初始化 ChromaDB...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # 使用多语言模型（支持中文）
    embed_fn = SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

    collection = client.get_or_create_collection(
        name="knowledge_base",
        embedding_function=embed_fn,
        metadata={"description": "UIAutotest 知识库向量索引"},
    )

    # 加载上次索引状态
    state = {}
    if incremental and STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))

    total_chunks = 0
    total_files = 0
    skipped = 0

    for config in SCAN_CONFIGS:
        scan_path = config["path"]
        if not scan_path.exists():
            print(f"  [skip] 目录不存在: {scan_path}")
            continue

        files = list(scan_path.glob(config["glob"]))
        print(f"\n扫描 {config['name']}: {len(files)} 个文件")

        for filepath in files:
            # __pycache__ 跳过
            if "__pycache__" in str(filepath):
                continue

            file_hash = compute_file_hash(filepath)
            rel_path = str(filepath.relative_to(PROJ_ROOT))

            # 增量模式：跳过未变更的文件
            if incremental and state.get(rel_path) == file_hash:
                skipped += 1
                continue

            # 读取并分块
            try:
                content = filepath.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            chunks = chunk_text(content, config["chunk_size"], config["overlap"])

            if not chunks:
                continue

            # 删除该文件的旧 chunks
            try:
                existing = collection.get(where={"source_file": rel_path})
                if existing["ids"]:
                    collection.delete(ids=existing["ids"])
            except Exception:
                pass

            # 添加新 chunks
            ids = [f"{rel_path}::{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "source_file": rel_path,
                    "source_type": config["name"],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }
                for i in range(len(chunks))
            ]

            collection.add(
                ids=ids,
                documents=chunks,
                metadatas=metadatas,
            )

            total_files += 1
            total_chunks += len(chunks)
            state[rel_path] = file_hash

            print(f"  [+] {rel_path}: {len(chunks)} chunks")

    # 保存状态
    CHROMA_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"索引构建完成:")
    print(f"  文件数: {total_files}")
    print(f"  分块数: {total_chunks}")
    print(f"  跳过(未变更): {skipped}")
    print(f"  集合总数: {collection.count()}")
    print(f"  存储位置: {CHROMA_DIR}")

    return collection


def query_index(query: str, n_results: int = 5):
    """测试查询"""
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embed_fn = SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

    collection = client.get_collection(
        name="knowledge_base",
        embedding_function=embed_fn,
    )

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    print(f"\n查询: '{query}'")
    print(f"{'='*60}")

    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )):
        print(f"\n[{i+1}] 相似度: {1-dist:.3f} | 来源: {meta['source_file']}")
        print(f"    类型: {meta['source_type']} | chunk {meta['chunk_index']+1}/{meta['total_chunks']}")
        print(f"    内容: {doc[:150]}...")


def main():
    parser = argparse.ArgumentParser(description="知识库 Embedding Pipeline")
    parser.add_argument("--incremental", action="store_true", help="增量更新")
    parser.add_argument("--query", type=str, help="测试查询")
    parser.add_argument("--knowledge-dir", type=str, help="知识库目录（默认 Web 知识库）")
    parser.add_argument("--chroma-dir", type=str, help="向量数据库目录（默认 .chroma_db）")
    args = parser.parse_args()

    global KNOWLEDGE_DIR, CHROMA_DIR, STATE_FILE, SCAN_CONFIGS
    if args.knowledge_dir:
        KNOWLEDGE_DIR = Path(args.knowledge_dir)
        if not KNOWLEDGE_DIR.is_absolute():
            KNOWLEDGE_DIR = PROJ_ROOT / KNOWLEDGE_DIR
    if args.chroma_dir:
        CHROMA_DIR = Path(args.chroma_dir)
        if not CHROMA_DIR.is_absolute():
            CHROMA_DIR = PROJ_ROOT / CHROMA_DIR
        STATE_FILE = CHROMA_DIR / "index_state.json"
    SCAN_CONFIGS[0]["path"] = KNOWLEDGE_DIR / "pages"
    SCAN_CONFIGS[1]["path"] = KNOWLEDGE_DIR / "digest"

    if args.query:
        query_index(args.query)
    else:
        build_index(incremental=args.incremental)


if __name__ == "__main__":
    main()
