#!/usr/bin/env bash
# 数据准备：下载 RCAEval（Zenodo 官方源）与 LogDx-CI（GitHub）
# 用法: bash scripts/download_datasets.sh [目标目录，默认 ./data]
set -e
DATA_DIR="${1:-data}"
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

echo "=== 1. RCAEval 数据（Zenodo records/14590730）==="
# RE1-OB（Online Boutique，125 case）
if [ ! -f RE1-OB.zip ]; then
  curl -fL --retry 5 --retry-delay 5 -C - -m 3600 \
    "https://zenodo.org/records/14590730/files/RE1-OB.zip?download=1" -o RE1-OB.zip
fi
unzip -q -o RE1-OB.zip -d RE1-OB 2>/dev/null || true

# RE1-SS（Sock Shop，125 case）
if [ ! -f RE1-SS.zip ]; then
  curl -fL --retry 5 --retry-delay 5 -C - -m 3600 \
    "https://zenodo.org/records/14590730/files/RE1-SS.zip?download=1" -o RE1-SS.zip
fi
unzip -q -o RE1-SS.zip -d RE1-SS 2>/dev/null || true

# RE2-OB / RE2-SS（多源，含 logs/traces）
for ds in RE2-OB RE2-SS; do
  if [ ! -f "$ds.zip" ]; then
    echo "下载 $ds（约 1.2GB / 246MB，可能较慢）..."
    curl -fL --retry 8 --retry-delay 10 -C - -m 7200 \
      "https://zenodo.org/records/14590730/files/$ds.zip?download=1" -o "$ds.zip"
  fi
  unzip -q -o "$ds.zip" -d "$ds" 2>/dev/null || true
done

# RE3（HF parquet 格式，多源代码级故障）
if [ ! -d RE3 ]; then
  echo "RE3 请从 HF 下载: https://huggingface.co/datasets/phamquiluan/RCAEval"
  echo "（或使用 RCAEval 官方 main.py 的 download_re3 系列函数）"
fi

echo "=== 2. LogDx-CI（GitHub）==="
if [ ! -d LogDx ]; then
  git clone -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=30 \
    https://github.com/eyuansu62/LogDx.git
fi

echo "=== 3. RCAEval 官方框架（官方 baseline 用）==="
if [ ! -d RCAEval ]; then
  git clone -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=30 \
    https://github.com/phamquiluan/RCAEval.git
  pip install causal-learn  # circa 依赖（包名 causal-learn）
fi

echo "完成。数据就位后："
echo "  LogDx-CI:  export LOGDX_CI_ROOT=$DATA_DIR/LogDx"
echo "  RCAEval 指标型:  python3 eval/rcaeval_metric.py --data-dir $DATA_DIR/RE1-OB/RE1-OB"
echo "  RCAEval 官方 baseline: cd $DATA_DIR/RCAEval && python3 main.py --method baro --dataset re1-ob"
