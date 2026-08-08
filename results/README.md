# 复现结果对照

本目录存放评测结果文件（.json 被 gitignore，只保留对照说明）。
完整结果见主仓库 docs/evaluation.md；复现方法见根 README。

## 关键复现数字（实测）

| 评测 | 结果 | 命令 |
|---|---|---|
| LogDx-CI 信号召回 | 0.9296（压缩 94.94%） | `python3 eval/logdx_eval.py --logdx-root data/LogDx` |
| LogDx-CI 最优档 | 0.9296（压缩 95.28%） | `... --bm25-weak 100 --noise-limit 90` |
| re1ob ours AC@1 | 94.4%（125 case） | `python3 eval/rcaeval_metric.py --data-dir data/RE1-OB/RE1-OB` |
| re1ss ours AC@1 | 96.8%（125 case） | `python3 eval/rcaeval_metric.py --data-dir data/RE1-SS/RE1-SS` |
| re2ob ours AC@1 | 100.0%（91 case） | `python3 eval/rcaeval_multisource.py --data-dir data/RE2-OB/RE2-OB` |
| re2ss ours AC@1 | 92.2%（90 case） | `python3 eval/rcaeval_multisource.py --data-dir data/RE2-SS/RE2-SS` |
| RE3 ours AC@1 | 95.6%（90 case） | 多源评测（RE3 parquet，见 README） |
| baro baseline | AC@1 0.736（re1ob） | `cd data/RCAEval && python3 main.py --method baro --dataset re1-ob` |

## 双指标说明

- LogDx-CI：静态确定性评分（信号召回率 + token 压缩率），零波动
- RCAEval：AC@1/AC@3/Avg@5（官方 Evaluator 口径），LLM 判分有 ±1-2 case 波动
- 压缩率口径：token 估算 `len(chars)//2`，基准为原始日志全量（多源场景为三源全量）
