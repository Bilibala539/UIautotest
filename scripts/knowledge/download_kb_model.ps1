# download_kb_model.ps1 — 从 modelscope 下载 embedding 模型到 .166 本地
$ErrorActionPreference = "Stop"
$dst = "E:\uiautotest\models\paraphrase-multilingual-MiniLM-L12-v2"
New-Item -ItemType Directory -Force -Path "$dst\1_Pooling" | Out-Null
$base = "https://modelscope.cn/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2/resolve/master"
$files = @(
    "config.json",
    "1_Pooling/config.json",
    "config_sentence_transformers.json",
    "modules.json",
    "sentence_bert_config.json",
    "special_tokens_map.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "sentencepiece.bpe.model",
    "unigram.json",
    "model.safetensors"
)
foreach ($f in $files) {
    $out = Join-Path $dst ($f -replace "/", "\")
    if ((Test-Path $out) -and ((Get-Item $out).Length -gt 0)) { Write-Output "SKIP $f"; continue }
    Write-Output "GET  $f"
    & curl.exe -sL --retry 3 --max-time 1800 -o $out "$base/$f"
    if (-not (Test-Path $out) -or (Get-Item $out).Length -eq 0) { Write-Output "FAIL $f"; exit 1 }
}
Write-Output "DONE"
Get-ChildItem $dst -Recurse -File | ForEach-Object { Write-Output ("{0,12}  {1}" -f $_.Length, $_.FullName.Replace("$dst\","")) }
