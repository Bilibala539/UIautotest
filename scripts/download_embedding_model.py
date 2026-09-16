"""从 ModelScope 下载知识库向量检索所需的嵌入模型。

只下载 sentence-transformers 实际用到的文件（safetensors + 配置/分词，约 500MB），
排除仓库里的 onnx/openvino/tf_model.h5/pytorch_model.bin 等冗余格式（约 4GB）。

用法（在项目根目录）：
    python scripts/download_embedding_model.py
可选参数：
    --model-id   ModelScope 模型 id（默认 sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2）
    --target     下载目标目录（默认 <项目>/models/paraphrase-multilingual-MiniLM-L12-v2，
                 与 .mcp.json 的 UIAUTOTEST_EMBEDDING_MODEL 保持一致）
    --verify     下载后加载模型试算一条向量
"""
import argparse
from pathlib import Path

MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_TARGET = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "paraphrase-multilingual-MiniLM-L12-v2"
)

# sentence-transformers 加载所需的最小文件集
KEEP = [
    "config.json",
    "config_sentence_transformers.json",
    "configuration.json",
    "modules.json",
    "sentence_bert_config.json",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "sentencepiece.bpe.model",
    "unigram.json",
    "model.safetensors",
    "1_Pooling/config.json",
]


def download(target: Path, model_id: str) -> None:
    try:
        from modelscope import snapshot_download
    except ImportError:
        raise SystemExit("缺少 modelscope，请先执行：pip install modelscope")
    snapshot_download(model_id, local_dir=str(target), allow_patterns=KEEP)
    print(f"模型已下载到：{target}")


def verify(target: Path) -> None:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(str(target))
    vec = model.encode(["测试一句话"])
    print(f"验证通过：向量维度 {vec.shape}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", default=MODEL_ID)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--verify", action="store_true", help="下载后试算一条向量")
    args = parser.parse_args()

    download(args.target, args.model_id)
    if args.verify:
        verify(args.target)


if __name__ == "__main__":
    main()
