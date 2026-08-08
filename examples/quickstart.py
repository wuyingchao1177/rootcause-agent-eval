#!/usr/bin/env python3
"""评测快速示例：不依赖任何数据集，验证评测链路可运行。

用法: python3 examples/quickstart.py
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "eval"))

from score import evaluate_results


def main():
    # 1) 构造一个假的 RCAEval 结果目录（2 个 case）
    with tempfile.TemporaryDirectory() as d:
        cases = {
            "adservice_cpu_1": ["adservice_cpu", "cartservice_mem"],   # AC@1 命中
            "cartservice_mem_1": ["adservice_cpu", "cartservice_mem"],  # AC@3 命中（第 2 位）
        }
        for name, ranks in cases.items():
            json.dump({"0": ranks}, open(os.path.join(d, f"{name}.json"), "w"))

        sc = evaluate_results(d)
        print("=== 计分链路示例 ===")
        print(f"case 数: {sc['n']}")
        print(f"AC@1: {sc['AC@1']:.2f}  AC@3: {sc['AC@3']:.2f}  Avg@5: {sc['Avg@5']:.2f}")

    # 2) 内置压缩器冒烟
    from log_compressor import build_analysis_view
    log = ["2026-01-01 00:00:%02d [svc] %s" % (i % 60,
           "ERROR RedisTimeoutException boom" if i % 7 == 0 else "INFO ok") for i in range(200)]
    view = build_analysis_view(log)
    print(f"\n=== 压缩器冒烟 ===")
    print(f"200 行 → {len(view):,} chars 分析视图")
    print(view[:300] + ("..." if len(view) > 300 else ""))

    print("\n链路 OK。正式评测需要数据（见 scripts/download_datasets.sh）。")


if __name__ == "__main__":
    main()
