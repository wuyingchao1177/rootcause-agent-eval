"""内置压缩器快照 + 指标摘要单元测试（保证评测链路自包含可用）。"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eval"))

from log_compressor import compress_log, build_analysis_view, _signal_level
from relevance import BM25Scorer


class TestCompressorSnapshot:
    def test_reduction(self):
        lines = [f"2026-01-01 00:00:{i % 60:02d} [svc{i % 2}] "
                 + ("ERROR boom" if i % 7 == 0 else "INFO ok") for i in range(200)]
        c = compress_log(lines)
        assert c["reduced_lines"] < c["original_lines"]

    def test_signal_levels(self):
        assert _signal_level("ERROR exception thrown") == 0
        assert _signal_level("INFO heartbeat") == 2

    def test_analysis_view(self):
        lines = ["2026-01-01 00:00:00 [frontend] ERROR boom", "2026-01-01 00:00:01 [frontend] INFO ok"] * 5
        view = build_analysis_view(lines)
        assert "[服务级错误分布]" in view
        assert "[业务错误日志(高价值)]" in view

    def test_bm25(self):
        scorer = BM25Scorer()
        scores = scorer.score_batch(["ERROR connection refused", "INFO ok"], "error refused")
        assert scores[0]["score"] > scores[1]["score"]


class TestMetricSummary:
    def test_summary_detects_anomaly(self):
        sys.path.insert(0, str(Path(__file__).parent.parent / "eval"))
        from rcaeval_metric import summarize_metrics_csv
        import pandas as pd
        import numpy as np

        with tempfile.TemporaryDirectory() as d:
            csv = os.path.join(d, "metrics.csv")
            t = list(range(100))
            df = pd.DataFrame({
                "time": t,
                "adservice_cpu": [1.0] * 50 + [3.0] * 50,   # 注入后 3x
                "cartservice_cpu": [1.0] * 100,
            })
            df.to_csv(csv, index=False)
            summary = summarize_metrics_csv(csv, "50")  # inject at t=50
            assert "adservice_cpu" in summary
            assert "cartservice_cpu" not in summary

    def test_empty_window(self):
        sys.path.insert(0, str(Path(__file__).parent.parent / "eval"))
        from rcaeval_metric import summarize_metrics_csv
        import pandas as pd
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            csv = os.path.join(d, "metrics.csv")
            pd.DataFrame({"time": [1, 2], "a_cpu": [1.0, 1.0]}).to_csv(csv, index=False)
            assert summarize_metrics_csv(csv, "100") == "[指标窗口异常]"
