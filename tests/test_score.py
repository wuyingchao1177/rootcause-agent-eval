"""score.py 计分逻辑单元测试（AC@1 / AC@3 / Avg@5）。"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eval"))

from score import evaluate_results


def _make_result_dir(cases):
    d = tempfile.mkdtemp()
    for name, ranks in cases.items():
        # 文件名前缀 = 根因服务
        json.dump({"0": ranks}, open(os.path.join(d, f"{name}.json"), "w"))
    return d


class TestEvaluateResults:
    def test_ac1_hit(self):
        # root=adservice，ranks[0]=adservice_cpu → AC@1 命中
        d = _make_result_dir({"adservice_cpu_1": ["adservice_cpu", "cartservice_mem"]})
        sc = evaluate_results(d)
        assert sc["AC@1"] == 1.0
        assert sc["n"] == 1

    def test_ac1_miss_ac3_hit(self):
        d = _make_result_dir({"cartservice_mem_1": ["adservice_cpu", "cartservice_mem", "frontend_cpu"]})
        sc = evaluate_results(d)
        assert sc["AC@1"] == 0.0
        assert sc["AC@3"] == 1.0
        assert sc["Avg@5"] == 0.5  # 第 2 位命中 → 1/2

    def test_avg5_rank_position(self):
        d = _make_result_dir({"frontend_delay_1": ["adservice_cpu", "cartservice_mem", "frontend_cpu"]})
        sc = evaluate_results(d)
        assert sc["Avg@5"] == 1.0 / 3.0  # 第 3 位命中 → 1/3

    def test_no_result(self):
        assert evaluate_results("/nonexistent_dir") is None

    def test_error_entry_skipped(self):
        d = tempfile.mkdtemp()
        json.dump({"error": "boom"}, open(os.path.join(d, "x_cpu_1.json"), "w"))
        assert evaluate_results(d) is None
