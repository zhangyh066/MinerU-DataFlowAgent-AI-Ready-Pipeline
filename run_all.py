"""
run_all.py

一键流水线：依次执行 转换 → 评估 → 语料导出 → HTML 报告。
把新的 MinerU 输出 JSON 放进 mineru_outputs/ 后直接运行本脚本即可增量更新：
评估缓存会自动跳过内容未变化的文档。

用法：
    python run_all.py
    python run_all.py --skip-eval          # 不调用 API，只重建导出与报告
    python run_all.py --batch-size 5 --sleep 5
    python run_all.py --include-partial --charts-dir charts
"""

import argparse
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def make_console_output_safe():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(errors="replace")
            except Exception:
                pass


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="一键运行完整流水线")
    parser.add_argument("--skip-eval", action="store_true",
                        help="跳过评估步骤（不调用 API，基于已有结果重建导出与报告）")
    parser.add_argument("--batch-size", type=int, default=None, help="每批文档数")
    parser.add_argument("--sleep", type=int, default=None, help="批间等待秒数")
    parser.add_argument("--max-retries", type=int, default=None, help="失败重试轮数")
    parser.add_argument("--no-cache", action="store_true", help="忽略评估缓存")
    parser.add_argument("--include-partial", action="store_true",
                        help="语料导出时包含 PARTIAL 文献")
    parser.add_argument("--min-score", type=int, default=None, help="语料导出最低分")
    parser.add_argument("--charts-dir", default=None, help="同时保存图表 PNG 到该目录")
    return parser.parse_args(argv)


def run_step(title, cmd):
    print("\n" + "=" * 60)
    print(f"【{title}】")
    print("=" * 60)
    print(">", " ".join(cmd))
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"\n步骤失败（退出码 {result.returncode}）：{title}")
        sys.exit(result.returncode)


def main(argv=None):
    make_console_output_safe()
    args = parse_args(argv)
    py = sys.executable

    run_step("1/4 转换 MinerU JSON", [py, "convert_mineru_jsons.py"])

    if not args.skip_eval:
        eval_cmd = [py, "homework1_final.py"]
        if args.batch_size is not None:
            eval_cmd += ["--batch-size", str(args.batch_size)]
        if args.sleep is not None:
            eval_cmd += ["--sleep", str(args.sleep)]
        if args.max_retries is not None:
            eval_cmd += ["--max-retries", str(args.max_retries)]
        if args.no_cache:
            eval_cmd.append("--no-cache")
        run_step("2/4 大模型批量评估", eval_cmd)
    else:
        print("\n已跳过评估步骤（--skip-eval）")

    export_cmd = [py, "export_ai_ready.py", "--formats", "jsonl", "md", "csv"]
    if args.include_partial:
        export_cmd.append("--include-partial")
    if args.min_score is not None:
        export_cmd += ["--min-score", str(args.min_score)]
    run_step("3/4 导出 AI-Ready 语料", export_cmd)

    report_cmd = [py, "generate_report.py"]
    if args.charts_dir:
        report_cmd += ["--charts-dir", args.charts_dir]
    run_step("4/4 生成 HTML 报告", report_cmd)

    print("\n全部完成")
    print("  - 评估结果：output_results_batch.json")
    print("  - 语料库：  ai_ready_corpus/")
    print("  - 报告：    report.html")


if __name__ == "__main__":
    main()
