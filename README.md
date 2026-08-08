# RootCause Agent 评测工程 (Evaluation Project)

可复现的横向评测基准工程：评测 **token 高效的根因定位（RCA）方案** 在准确率（召回率）与 token 压缩率
两个维度上的水平，覆盖业界标准数据集（LogDx-CI / RCAEval）与官方 baseline。
配套被测项目：[rootcause-agent](https://github.com/wuyingchao1177/rootcause-agent)（独立仓库）。

> 评测规范遵循 `rootcause-agent/docs/evaluation-spec.md`（对标 LogDx-CI / RCAEval / FSE 可复现性清单）。

## 评测覆盖

| 评测 | 数据集 | case 数 | 指标 | 脚本 |
|---|---|---|---|---|
| LogDx-CI 信号召回 + 压缩率 | LogDx-CI（FSE 2025） | 35 | 信号召回率 + token 压缩率 | `eval/logdx_eval.py` |
| RCAEval 指标型定位 | RCAEval RE1（re1ob/re1ss） | 250 | AC@1/AC@3/Avg@5 | `eval/rcaeval_metric.py` |
| RCAEval 多源定位 | RCAEval RE2/RE3 | 271 | AC@1 | `eval/rcaeval_multisource.py` |
| RCAEval 官方 baseline | RCAEval 全系 | 431 | AC@1/AC@3/Avg@5 | `eval/baseline_runner.py` + `eval/score.py` |

## 快速开始（零数据冒烟）

```bash
pip install -e .[dev]
python3 examples/quickstart.py      # 计分链路 + 压缩器冒烟（无需数据集）
python3 -m pytest tests/ -q         # 单元测试
```

## 数据准备

```bash
bash scripts/download_datasets.sh   # 下载 RCAEval（Zenodo）+ LogDx-CI（GitHub）+ RCAEval 官方框架
```

或手动：
- RCAEval：https://zenodo.org/records/14590730 （RE1-OB/RE1-SS/RE2-OB/RE2-SS.zip；RE3 用 HF phamquiluan/RCAEval parquet）
- LogDx-CI：`git clone https://github.com/eyuansu62/LogDx.git`

## 运行评测

```bash
# 1. LogDx-CI（静态确定性评分；--bm25-weak/--noise-limit 为压缩率最优档）
export LOGDX_CI_ROOT=data/LogDx
python3 eval/logdx_eval.py --logdx-root data/LogDx
python3 eval/logdx_eval.py --logdx-root data/LogDx --bm25-weak 100 --noise-limit 90   # 召回不变，压缩 +0.34%

# 2. RCAEval 指标型（ours）
python3 eval/rcaeval_metric.py --data-dir data/RE1-OB/RE1-OB --out results/ours_re1ob.json
python3 eval/rcaeval_metric.py --data-dir data/RE1-SS/RE1-SS --out results/ours_re1ss.json

# 3. RCAEval 多源（ours，RE2/RE3）
python3 eval/rcaeval_multisource.py --data-dir data/RE2-OB/RE2-OB --out results/ours_re2ob.json

# 4. RCAEval 官方 baseline（需 RCAEval 官方框架）
python3 eval/baseline_runner.py --rcaeval-dir data/RCAEval --dataset re1-ob
python3 eval/score.py --result-dir data/RCAEval/output/results
```

> LLM 定位需要 `DEEPSEEK_API_KEY`（或其它 OpenAI 兼容 key）。`--ours-root` 可指向被测产品代码，
> 缺省使用本仓库内置的压缩器快照（自包含）。

## 复现结果对照

见 [results/README.md](results/README.md) —— 关键数字：LogDx-CI 0.9296（压缩 94.94%）、
re1ob 94.4%、re1ss 96.8%、re2ob 100.0%、re2ss 92.2%、RE3 95.6%（全部第一）。

## 项目结构

```
rootcause-agent-eval/
├── eval/                      # 评测核心（自包含：内置压缩器快照）
│   ├── logdx_eval.py          # LogDx-CI 评测
│   ├── rcaeval_metric.py      # RCAEval 指标型
│   ├── rcaeval_multisource.py # RCAEval 多源
│   ├── baseline_runner.py     # 官方 baseline 跑批
│   ├── score.py               # AC@1/AC@3/Avg@5 计分
│   ├── log_compressor.py      # 压缩器快照（复刻自 rootcause-agent，MIT）
│   └── relevance.py           # BM25 零依赖复刻
├── scripts/download_datasets.sh
├── examples/quickstart.py
├── tests/                     # 单元测试（计分/摘要/压缩器）
├── results/                   # 复现对照说明
└── .github/workflows/ci.yml   # CI（pytest × 3.10/3.12 + 冒烟）
```

## 评测规范（对标业界）

- **双指标必报**：准确率/召回率 + token 压缩率，分别排名（防"自嗨"）
- **真实能力**：竞品必须真实运行（禁止降级/截断冒充），不可运行如实标注
- **公平性**：同一 LLM、同一判分协议、统一 token 预算；共享摘要对所有方法一致
- **防泄漏**：评测集不用于调参；压缩器参数在 LogDx-CI 上回归、定位能力在 RE3 上验证
- **确定性优先**：静态评测（LogDx-CI）零波动；LLM 判分多次运行报告波动

## License

MIT License — 详见 [LICENSE](LICENSE)。压缩器快照（eval/log_compressor.py、eval/relevance.py）
复刻自 rootcause-agent（同 MIT）。
