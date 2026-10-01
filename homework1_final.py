from pathlib import Path
import os
import json
import re
import time
from collections import Counter
from dotenv import load_dotenv

from dataflow.pipeline import PipelineABC
from dataflow.utils.storage import FileStorage
from dataflow.serving import APILLMServing_request
from dataflow.operators.core_text import PromptedGenerator

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "input.json"
TEMP_BATCH_FILE = BASE_DIR / "temp_batch_input.json"
OUTPUT_FILE = BASE_DIR / "output_results_batch.json"
SUMMARY_FILE = BASE_DIR / "summary_report_batch.txt"
ALL_SUMMARIES_FILE = BASE_DIR / "all_summaries.txt"

CACHE_CANDIDATES = [
    BASE_DIR / "cache" / "dataflow_cache_step_step1.jsonl",
    BASE_DIR.parent / "cache" / "dataflow_cache_step_step1.jsonl",
]

BATCH_SIZE = 1
SLEEP_SECONDS = 15


# ================= 工具函数 =================
def shorten(text, max_len=120):
    if not isinstance(text, str):
        return ""
    text = text.replace("\n", " ").strip()
    return text if len(text) <= max_len else text[:max_len] + "..."


def parse_tagged_result(result_value):
    """
    支持解析以下格式：
    QUALITY: YES / PARTIAL / NO
    SCORE: 85
    REASON: ...
    SUMMARY: ...

    也兼容模型脏输出，例如：
    ...正文...
    </think>
    <answer>
    QUALITY: ...
    SCORE: ...
    REASON: ...
    SUMMARY: ...
    </answer>
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
    if answer_match:
        text = answer_match.group(1).strip()
    else:
        text = raw_text

    # 统一换行
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    quality_match = re.search(r"QUALITY\s*:\s*(YES|PARTIAL|NO)", text, flags=re.I)
    score_match = re.search(r"SCORE\s*:\s*(\d{1,3})", text, flags=re.I)
    reason_match = re.search(
        r"REASON\s*:\s*(.*?)(?=\nSUMMARY\s*:|\Z)",
        text,
        flags=re.I | re.S
    )
    summary_match = re.search(
        r"SUMMARY\s*:\s*(.*?)(?=\Z)",
        text,
        flags=re.I | re.S
    )

    if not quality_match:
        return None, "quality_not_found"
    if not score_match:
        return None, "score_not_found"
    if not reason_match:
        return None, "reason_not_found"
    if not summary_match:
        return None, "summary_not_found"

    score = int(score_match.group(1))
    score = max(0, min(100, score))

    reason = reason_match.group(1).strip()
    summary = summary_match.group(1).strip()

    # 清掉残留标签
    reason = re.sub(r"</?answer>", "", reason, flags=re.I).strip()
    reason = re.sub(r"</?think>", "", reason, flags=re.I).strip()
    summary = re.sub(r"</?answer>", "", summary, flags=re.I).strip()
    summary = re.sub(r"</?think>", "", summary, flags=re.I).strip()

    return {
        "quality": quality_match.group(1).strip().upper(),
        "score": score,
        "reason": reason,
        "summary": summary,
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
class BatchPipeline(PipelineABC):
    def __init__(self, input_file):
        super().__init__()

        self.storage = FileStorage(
            first_entry_file_name=str(input_file),
        )

        self.llm_serving = APILLMServing_request(
            api_url="https://open.bigmodel.cn/api/paas/v4/chat/completions",
            model_name="glm-4.5-air",
            max_workers=1,
            retry_attempts=1,
            request_timeout=300,
        )

        self.main_op = PromptedGenerator(
            llm_serving=self.llm_serving,
            system_prompt=(
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
                "SUMMARY: 100到200字摘要\n"
            )
        )

    def forward(self):
        self.main_op.run(
            storage=self.storage.step(),
            input_key="text",
            output_key="result"
        )


# ================= 执行批次 =================
def run_one_batch(batch_data):
    with open(TEMP_BATCH_FILE, "w", encoding="utf-8") as f:
        json.dump(batch_data, f, ensure_ascii=False, indent=2)

    clear_cache()

    pipeline = BatchPipeline(TEMP_BATCH_FILE)
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


# ================= 分析与导出 =================
def analyze_and_export(records):
    total = len(records)
    yes_count = 0
    partial_count = 0
    no_count = 0
    parse_fail_count = 0
    missing_result_count = 0

    fail_reasons = Counter()
    parsed_rows = []

    for item in records:
        raw_result = item.get("result")
        parsed, err = parse_tagged_result(raw_result)

        row = {
            "file_name": item.get("file_name"),
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

        if parsed["quality"] == "YES":
            yes_count += 1
        elif parsed["quality"] == "PARTIAL":
            partial_count += 1
        elif parsed["quality"] == "NO":
            no_count += 1

        parsed_rows.append(row)

    # 1) 保存结构化 JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(parsed_rows, f, ensure_ascii=False, indent=2)

    # 2) 保存摘要合集
    with open(ALL_SUMMARIES_FILE, "w", encoding="utf-8") as f:
        for row in parsed_rows:
            f.write(f"文件: {row['file_name']}\n")
            f.write(f"质量: {row['quality']}\n")
            f.write(f"评分: {row['score']}\n")
            if row["reason"]:
                f.write(f"理由: {row['reason']}\n")
            if row["summary"]:
                f.write(f"摘要: {row['summary']}\n")
            if not row["parse_ok"]:
                f.write(f"解析状态: 失败\n")
                f.write(f"原始输出预览: {row['raw_result_preview']}\n")
            f.write("=" * 50 + "\n")

    # 3) 保存统计报告
    report_lines = [
        "=" * 60,
        "【AI-Ready 数据生产线结果报告】",
        "=" * 60,
        f"总文档数：{total}",
        f"成功解析 result 的文档数：{total - parse_fail_count - missing_result_count}",
        f"没有 result 的文档数：{missing_result_count}",
        f"result 解析失败的文档数：{parse_fail_count}",
        f"QUALITY=YES 的文档数：{yes_count}",
        f"QUALITY=PARTIAL 的文档数：{partial_count}",
        f"QUALITY=NO 的文档数：{no_count}",
    ]

    if total > 0:
        report_lines.append(
            f"解析成功率：{(total - parse_fail_count - missing_result_count) / total * 100:.1f}%"
        )

    if fail_reasons:
        report_lines.append("")
        report_lines.append("【解析失败原因统计】")
        for reason, count in fail_reasons.most_common():
            report_lines.append(f"- {reason}: {count} 篇")

    report_lines.append("")
    report_lines.append("【样例预览】")
    shown = 0
    for row in parsed_rows:
        if row["parse_ok"]:
            report_lines.append("-" * 60)
            report_lines.append(f"文件名：{row['file_name']}")
            report_lines.append(f"质量：{row['quality']}")
            report_lines.append(f"评分：{row['score']}")
            report_lines.append(f"理由：{row['reason']}")
            report_lines.append(f"摘要：{shorten(row['summary'], 150)}")
            shown += 1
        if shown >= 5:
            break

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    # 4) 终端展示
    print("\n" + "=" * 60)
    print("【处理结果统计】")
    print("=" * 60)
    print(f"总文档数：{total}")
    print(f"成功解析 result 的文档数：{total - parse_fail_count - missing_result_count}")
    print(f"没有 result 的文档数：{missing_result_count}")
    print(f"result 解析失败的文档数：{parse_fail_count}")
    print(f"QUALITY=YES 的文档数：{yes_count}")
    print(f"QUALITY=PARTIAL 的文档数：{partial_count}")
    print(f"QUALITY=NO 的文档数：{no_count}")
    if total > 0:
        print(f"解析成功率：{(total - parse_fail_count - missing_result_count) / total * 100:.1f}%")

    if fail_reasons:
        print("\n【解析失败原因统计】")
        for reason, count in fail_reasons.most_common():
            print(f"- {reason}: {count} 篇")

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

    print(f"\n✓ 结构化结果已保存至：{OUTPUT_FILE}")
    print(f"✓ 统计报告已保存至：{SUMMARY_FILE}")
    print(f"✓ 摘要合集已保存至：{ALL_SUMMARIES_FILE}")


# ================= 主函数 =================
def main():
    if not INPUT_FILE.exists():
        print("❌ input.json 不存在")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_results = []

    for i in range(len(data)):
        print(f"\n处理第 {i+1} 条...")
        result = run_one_batch([data[i]])
        all_results.extend(result)

        if i < len(data) - 1:
            print(f"⏳ 等待 {SLEEP_SECONDS} 秒后开始下一条...")
            time.sleep(SLEEP_SECONDS)

    analyze_and_export(all_results)

    if TEMP_BATCH_FILE.exists():
        try:
            TEMP_BATCH_FILE.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    main()