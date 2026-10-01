"""
homework1_final.py

基于 DataFlow-Agent 的论文质量评估流水线：
读取 input.json，逐条调用 GLM 大模型按统一规则评分并生成摘要，
最终输出结构化 JSON、摘要合集与统计报告。

用法：
    python homework1_final.py                     # 使用默认参数运行完整流程
    python homework1_final.py --batch-size 5      # 每批 5 条（注意 API 限流）
    python homework1_final.py --input 其他.json --output 结果.json

依赖：
    - dataflow-agent（OpenDataLab DataFlow-Agent，pip 包名 dataflow-agent）
      注意：不要 pip install dataflow，那是另一个同名无关的包。
    - python-dotenv
    - .env 中配置 DF_API_KEY
"""

import argparse
import json
import os
import re
import sys
import time
import uuid
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_FILE = BASE_DIR / "input.json"
DEFAULT_OUTPUT_FILE = BASE_DIR / "output_results_batch.json"
DEFAULT_SUMMARY_FILE = BASE_DIR / "summary_report_batch.txt"
DEFAULT_ALL_SUMMARIES_FILE = BASE_DIR / "all_summaries.txt"

CACHE_CANDIDATES = [
    BASE_DIR / "cache" / "dataflow_cache_step_step1.jsonl",
    BASE_DIR.parent / "cache" / "dataflow_cache_step_step1.jsonl",
]

DEFAULT_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
DEFAULT_MODEL = "glm-4.5-air"

# 原评分体系（5 个维度，总分 100），与报告口径保持一致
SYSTEM_PROMPT = (
    "你是一名金融与金融科技论文质量评估助手。\n"
    "请对文本进行评分并分类。\n\n"

    "评分规则（总分100）：\n"
    "1. 方法与识别（0-25）：DID、回归、理论模型、因果识别。\n"
    "2. 可复用信息（0-25）：变量、机制、样本、结果。\n"
    "3. 金融相关（0-20）：风险、投资、银行、创新、市场机制。\n"
    "4. 噪声控制（0-15）：无目录、无乱码、无封面、无教学题目。\n"
    "5. 学术贡献（0-15）：有机制、有假说、有明确贡献。\n\n"

    "判定规则：\n"
    "score >= 80 为 YES\n"
    "60 <= score < 80 为 PARTIAL\n"
    "score < 60 为 NO\n\n"

    "以下情况通常判为 NO：练习题、教材、目录、封面、版权页、政策宣传、无模型或无方法的描述性文本。\n\n"

    "必须严格按以下格式输出，不能添加任何其他内容：\n"
    "QUALITY: YES 或 PARTIAL 或 NO\n"
    "SCORE: 0-100之间的整数\n"
    "REASON: 一句话说明理由\n"
    "SUMMARY: 100到200字摘要"
)


# ================= 依赖加载（懒加载，便于无 dataflow 环境也能用辅助功能） =================
def build_batch_pipeline_class(model_name, api_url, max_workers, retry_attempts):
    """动态导入 dataflow 并构建 Pipeline 类（保持与原代码一致的调用方式）。"""
    try:
        from dataflow.pipeline import PipelineABC
        from dataflow.utils.storage import FileStorage
        from dataflow.serving import APILLMServing_request
        from dataflow.operators.core_text import PromptedGenerator
    except ImportError:
        sys.exit(
            "❌ 未找到 DataFlow-Agent 依赖。\n"
            "   请执行: pip install dataflow-agent\n"
            "   注意包名是 dataflow-agent（提供 import dataflow），\n"
            "   不要安装 pypi 上同名的 dataflow，那是无关包。"
        )

    class BatchPipeline(PipelineABC):
        def __init__(self, input_file):
            super().__init__()

            self.storage = FileStorage(
                first_entry_file_name=str(input_file),
            )

            self.llm_serving = APILLMServing_request(
                api_url=api_url,
                model_name=model_name,
                max_workers=max_workers,
                retry_attempts=retry_attempts,
                request_timeout=300,
            )

            self.main_op = PromptedGenerator(
                llm_serving=self.llm_serving,
                system_prompt=SYSTEM_PROMPT,
            )

        def forward(self):
            self.main_op.run(
                storage=self.storage.step(),
                input_key="text",
                output_key="result"
            )

    return BatchPipeline


# ================= 工具函数 =================
def shorten(text, max_len=120):
    if not isinstance(text, str):
        return ""
    text = text.replace("\n", " ").strip()
    return text if len(text) <= max_len else text[:max_len] + "..."


def score_to_quality(score):
    if score >= 80:
        return "YES"
    if score >= 60:
        return "PARTIAL"
    return "NO"


def parse_tagged_result(result_value):
    """
    支持解析以下格式：
    QUALITY: YES / PARTIAL / NO
    SCORE: 85
    REASON: ...
    SUMMARY: ...

    兼容模型脏输出（如带 <answer>/<think> 标签、标签顺序颠倒等）。
    """
    if result_value is None:
        return None, "missing_result"

    if not isinstance(result_value, str):
        return None, "result_not_string"

    raw_text = result_value.strip()
    if not raw_text:
        return None, "empty_result"

    # 优先截取 <answer>...</answer>
    answer_match = re.search(r"<answer>(.*?)</answer>", raw_text, flags=re.I | re.S)
    text = answer_match.group(1) if answer_match else raw_text

    # 统一换行
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    # 按标签切分：先定位 QUALITY/SCORE/REASON/SUMMARY 四个标签的位置，
    # 再按位置顺序切片，兼容模型调换标签顺序的情况。
    label_pattern = re.compile(r"(QUALITY|SCORE|REASON|SUMMARY)\s*:", re.I)
    matches = list(label_pattern.finditer(text))

    fields = {}
    for idx, m in enumerate(matches):
        key = m.group(1).upper()
        if key in fields:  # 同一标签出现多次时只取第一次
            continue
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        fields[key] = text[m.end():end].strip()

    if "QUALITY" not in fields:
        return None, "quality_not_found"
    if "SCORE" not in fields:
        return None, "score_not_found"
    if "REASON" not in fields:
        return None, "reason_not_found"
    if "SUMMARY" not in fields:
        return None, "summary_not_found"

    quality_match = re.search(r"YES|PARTIAL|NO", fields["QUALITY"], flags=re.I)
    if not quality_match:
        return None, "quality_not_found"

    score_match = re.search(r"\d{1,3}", fields["SCORE"])
    if not score_match:
        return None, "score_not_found"
    score = max(0, min(100, int(score_match.group(0))))

    # 清掉残留标签
    def _clean(s):
        s = re.sub(r"</?answer>", "", s, flags=re.I)
        s = re.sub(r"</?think>", "", s, flags=re.I)
        return s.strip()

    return {
        "quality": quality_match.group(0).upper(),
        "score": score,
        "reason": _clean(fields["REASON"]),
        "summary": _clean(fields["SUMMARY"]),
    }, None


def find_cache_file():
    for path in CACHE_CANDIDATES:
        if path.exists():
            return path
    return None


def clear_cache():
    for path in CACHE_CANDIDATES:
        if path.exists():
            try:
                path.unlink()
            except Exception:
                pass


# ================= Pipeline =================
def run_one_batch(batch_data, args):
    """对一批数据运行 Pipeline，返回缓存中的结果列表。"""
    temp_batch_file = BASE_DIR / f".tmp_batch_{uuid.uuid4().hex[:8]}.json"
    try:
        with open(temp_batch_file, "w", encoding="utf-8") as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)

        clear_cache()

        BatchPipeline = build_batch_pipeline_class(
            model_name=args.model,
            api_url=args.api_url,
            max_workers=args.max_workers,
            retry_attempts=args.retry_attempts,
        )

        pipeline = BatchPipeline(temp_batch_file)
        pipeline.compile()
        pipeline.forward()

        cache_file = find_cache_file()
        if not cache_file:
            return []

        results = []
        with open(cache_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))

        return results
    finally:
        if temp_batch_file.exists():
            try:
                temp_batch_file.unlink()
            except Exception:
                pass


def is_failed_record(record):
    """判断一条结果是否解析失败或缺失，需要重试。"""
    if record is None:
        return True
    parsed, _ = parse_tagged_result(record.get("result"))
    return parsed is None


# ================= 执行与重试 =================
def run_all_batches(data, args):
    """分批执行全部数据；对失败条目自动重试 args.max_retries 轮。"""
    results_by_key = {}

    def key_of(item, idx):
        return item.get("file_name") or f"#{idx}"

    pending = [(key_of(item, i), item) for i, item in enumerate(data)]

    for round_idx in range(args.max_retries + 1):
        if round_idx > 0:
            print(f"\n===== 第 {round_idx} 轮重试：{len(pending)} 条失败条目 =====")
            if args.sleep > 0:
                print(f"⏳ 等待 {args.sleep} 秒后开始重试...")
                time.sleep(args.sleep)

        next_pending = []
        for i in range(0, len(pending), args.batch_size):
            batch = pending[i:i + args.batch_size]
            print(f"\n处理第 {i + 1}-{i + len(batch)} 条（共 {len(pending)} 条）...")

            try:
                batch_results = run_one_batch([item for _, item in batch], args)
            except Exception as e:
                print(f"⚠️ 本批次执行出错：{e}")
                batch_results = []

            by_name = {}
            for r in batch_results:
                by_name.setdefault(r.get("file_name"), []).append(r)

            for key, item in batch:
                matched = by_name.get(item.get("file_name"))
                record = matched[0] if matched else None
                if is_failed_record(record):
                    next_pending.append((key, item))
                else:
                    results_by_key[key] = record

        pending = next_pending
        if not pending:
            break

    # 最终仍失败的条目也保留占位，保证输出条目数与输入一致
    for key, item in pending:
        results_by_key[key] = None

    # 按原始输入顺序返回
    ordered = []
    for i, item in enumerate(data):
        ordered.append(results_by_key.get(key_of(item, i)))
    return ordered


# ================= 分析与导出 =================
def build_report(stats):
    lines = [
        "=" * 60,
        "【AI-Ready 数据生产线结果报告】",
        "=" * 60,
        f"总文档数：{stats['total']}",
        f"成功解析 result 的文档数：{stats['parsed']}",
        f"没有 result 的文档数：{stats['missing']}",
        f"result 解析失败的文档数：{stats['parse_fail']}",
        f"QUALITY=YES 的文档数：{stats['yes']}",
        f"QUALITY=PARTIAL 的文档数：{stats['partial']}",
        f"QUALITY=NO 的文档数：{stats['no']}",
    ]

    if stats["total"] > 0:
        lines.append(f"解析成功率：{stats['parsed'] / stats['total'] * 100:.1f}%")

    if stats["mismatch"] > 0:
        lines.append(f"质量判定与分数不一致的文档数：{stats['mismatch']}")

    if stats["fail_reasons"]:
        lines.append("")
        lines.append("【解析失败原因统计】")
        for reason, count in stats["fail_reasons"].most_common():
            lines.append(f"- {reason}: {count} 篇")

    lines.append("")
    lines.append("【样例预览】")
    shown = 0
    for row in stats["rows"]:
        if row["parse_ok"]:
            lines.append("-" * 60)
            lines.append(f"文件名：{row['file_name']}")
            lines.append(f"质量：{row['quality']}")
            lines.append(f"评分：{row['score']}")
            lines.append(f"理由：{row['reason']}")
            lines.append(f"摘要：{shorten(row['summary'], 150)}")
            shown += 1
        if shown >= 5:
            break

    return lines


def analyze_and_export(records, args):
    total = len(records)
    yes_count = 0
    partial_count = 0
    no_count = 0
    parse_fail_count = 0
    missing_result_count = 0
    mismatch_count = 0

    fail_reasons = Counter()
    parsed_rows = []

    for item in records:
        raw_result = item.get("result") if isinstance(item, dict) else None
        parsed, err = parse_tagged_result(raw_result)

        row = {
            "file_name": item.get("file_name") if isinstance(item, dict) else None,
            "quality": None,
            "score": None,
            "reason": None,
            "summary": None,
            "parse_ok": parsed is not None,
            "raw_result_preview": shorten(raw_result, 200) if isinstance(raw_result, str) else None
        }

        if raw_result is None:
            missing_result_count += 1
            fail_reasons["missing_result"] += 1
            parsed_rows.append(row)
            continue

        if parsed is None:
            parse_fail_count += 1
            fail_reasons[err] += 1
            parsed_rows.append(row)
            continue

        row["quality"] = parsed["quality"]
        row["score"] = parsed["score"]
        row["reason"] = parsed["reason"]
        row["summary"] = parsed["summary"]

        # 校验质量判定与分数是否自洽（score>=80→YES, 60-79→PARTIAL, <60→NO）
        if score_to_quality(parsed["score"]) != parsed["quality"]:
            row["quality_score_mismatch"] = True
            mismatch_count += 1

        if parsed["quality"] == "YES":
            yes_count += 1
        elif parsed["quality"] == "PARTIAL":
            partial_count += 1
        elif parsed["quality"] == "NO":
            no_count += 1

        parsed_rows.append(row)

    # 1) 保存结构化 JSON
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(parsed_rows, f, ensure_ascii=False, indent=2)

    # 2) 保存摘要合集
    with open(args.summaries, "w", encoding="utf-8") as f:
        for row in parsed_rows:
            f.write(f"文件: {row['file_name']}\n")
            f.write(f"质量: {row['quality']}\n")
            f.write(f"评分: {row['score']}\n")
            if row["reason"]:
                f.write(f"理由: {row['reason']}\n")
            if row["summary"]:
                f.write(f"摘要: {row['summary']}\n")
            if row.get("quality_score_mismatch"):
                f.write("注意: 质量判定与分数不一致\n")
            if not row["parse_ok"]:
                f.write(f"解析状态: 失败\n")
                f.write(f"原始输出预览: {row['raw_result_preview']}\n")
            f.write("=" * 50 + "\n")

    # 3) 保存并打印统计报告
    stats = {
        "total": total,
        "parsed": total - parse_fail_count - missing_result_count,
        "missing": missing_result_count,
        "parse_fail": parse_fail_count,
        "yes": yes_count,
        "partial": partial_count,
        "no": no_count,
        "mismatch": mismatch_count,
        "fail_reasons": fail_reasons,
        "rows": parsed_rows,
    }
    report_lines = build_report(stats)

    with open(args.report, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("\n" + "\n".join(report_lines))

    print("\n===== 样例展示 =====")
    shown = 0
    for row in parsed_rows:
        if row["parse_ok"]:
            print("-" * 40)
            print("文件:", row["file_name"])
            print("质量:", row["quality"])
            print("评分:", row["score"])
            print("理由:", row["reason"])
            print("摘要:", shorten(row["summary"], 100))
            shown += 1
        if shown >= 3:
            break

    print(f"\n✓ 结构化结果已保存至：{args.output}")
    print(f"✓ 统计报告已保存至：{args.report}")
    print(f"✓ 摘要合集已保存至：{args.summaries}")


# ================= 主函数 =================
def make_console_output_safe():
    """Windows GBK 控制台无法编码 ✓ 等符号时自动降级为 ?，避免 UnicodeEncodeError。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(errors="replace")
            except Exception:
                pass


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="基于 DataFlow-Agent + GLM 的论文质量评估流水线"
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT_FILE),
                        help="输入 JSON（默认：./input.json）")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_FILE),
                        help="结构化结果输出路径（默认：./output_results_batch.json）")
    parser.add_argument("--report", default=str(DEFAULT_SUMMARY_FILE),
                        help="统计报告输出路径（默认：./summary_report_batch.txt）")
    parser.add_argument("--summaries", default=str(DEFAULT_ALL_SUMMARIES_FILE),
                        help="摘要合集输出路径（默认：./all_summaries.txt）")
    parser.add_argument("--batch-size", type=int, default=1,
                        help="每批处理的文档数（默认：1，注意 API 限流）")
    parser.add_argument("--sleep", type=int, default=15,
                        help="批次之间的等待秒数（默认：15）")
    parser.add_argument("--max-retries", type=int, default=1,
                        help="失败条目自动重试轮数（默认：1）")
    parser.add_argument("--model", default=os.getenv("MODEL_NAME", DEFAULT_MODEL),
                        help=f"模型名（默认：{DEFAULT_MODEL}，可用 MODEL_NAME 环境变量覆盖）")
    parser.add_argument("--api-url", default=os.getenv("API_URL", DEFAULT_API_URL),
                        help="OpenAI 兼容的 chat completions 接口地址")
    parser.add_argument("--max-workers", type=int, default=1,
                        help="并发请求数（默认：1）")
    parser.add_argument("--retry-attempts", type=int, default=1,
                        help="单条请求的重试次数（默认：1）")
    return parser.parse_args(argv)


def main(argv=None):
    make_console_output_safe()
    args = parse_args(argv)

    input_file = Path(args.input)
    if not input_file.exists():
        print(f"❌ 输入文件不存在：{input_file}")
        sys.exit(1)

    if not os.getenv("DF_API_KEY"):
        print("❌ 未检测到 DF_API_KEY，请在 .env 文件中配置（参考 .env.example）")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or not data:
        print("❌ 输入文件应为非空的 JSON 数组")
        sys.exit(1)

    print(f"共 {len(data)} 条待处理文档，模型：{args.model}")

    records = run_all_batches(data, args)
    analyze_and_export(records, args)


if __name__ == "__main__":
    main()
