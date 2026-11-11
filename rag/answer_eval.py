"""端到端答案质量评审：人工语义标签 + 可自动检查的引用、拒答、延迟和成本。"""

import json
import math
import re
from pathlib import Path

_REVIEW_FIELDS = ("answer_correct", "citation_correct", "faithful")
_CITATION_RE = re.compile(r"\[(\d+)\]")


def _ratio(values):
    valid = [value for value in values if value is not None]
    return {
        "reviewed": len(valid),
        "passed": sum(valid),
        "rate": sum(valid) / len(valid) * 100 if valid else None,
    }


def _percent(value):
    return "待评审" if value is None else f"{value:.1f}%"


def _average(values):
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else None


def _p95(values):
    values = sorted(value for value in values if value is not None)
    if not values:
        return None
    return values[math.ceil(len(values) * 0.95) - 1]


def _validate_item(item, index):
    where = f"第 {index} 条"
    if not isinstance(item.get("question"), str) or not item["question"].strip():
        raise ValueError(f"{where}缺少 question")
    if not isinstance(item.get("answer"), str) or not item["answer"].strip():
        raise ValueError(f"{where}尚未填写实际 answer；模板不能直接作为评测结果")
    if not isinstance(item.get("should_refuse"), bool):
        raise ValueError(f"{where}的 should_refuse 必须是 true/false")
    if not isinstance(item.get("sources", []), list):
        raise ValueError(f"{where}的 sources 必须是数组")
    for field in _REVIEW_FIELDS:
        if item.get(field) is not None and not isinstance(item.get(field), bool):
            raise ValueError(f"{where}的 {field} 必须为 true/false/null")
    for field in ("latency_ms", "cost"):
        value = item.get(field)
        if value is not None and (not isinstance(value, (int, float)) or value < 0):
            raise ValueError(f"{where}的 {field} 必须是非负数字或 null")


def evaluate_answers(path):
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    items = payload.get("items") if isinstance(payload, dict) else payload
    if not isinstance(items, list) or not items:
        raise ValueError("评测文件必须包含非空 items 数组")
    for index, item in enumerate(items, 1):
        _validate_item(item, index)

    rows = []
    for item in items:
        citations = [int(value) for value in _CITATION_RE.findall(item["answer"])]
        source_count = len(item.get("sources", []))
        refused = "资料中未提及" in item["answer"]
        should_refuse = item["should_refuse"]
        rows.append({
            **item,
            "refused": refused,
            "refusal_correct": refused == should_refuse,
            "citation_present": bool(citations) if not should_refuse else None,
            "citation_valid": (
                bool(citations)
                and source_count > 0
                and all(1 <= value <= source_count for value in citations)
            ) if not should_refuse else None,
        })

    costs = [item.get("cost") for item in rows if item.get("cost") is not None]
    return {
        "n": len(rows),
        "answer_correct": _ratio([item.get("answer_correct") for item in rows]),
        "citation_correct": _ratio([item.get("citation_correct") for item in rows]),
        "faithful": _ratio([item.get("faithful") for item in rows]),
        "refusal": _ratio([item["refusal_correct"] for item in rows]),
        "citation_present": _ratio([item["citation_present"] for item in rows]),
        "citation_valid": _ratio([item["citation_valid"] for item in rows]),
        "latency_avg": _average([item.get("latency_ms") for item in rows]),
        "latency_p95": _p95([item.get("latency_ms") for item in rows]),
        "cost_avg": _average(costs),
        "cost_total": sum(costs) if costs else None,
        "rows": rows,
    }


def render_answer_report(summary, source):
    lines = [
        "# 答案质量人工评审报告",
        "",
        f"- 输入：`{source}`",
        f"- 样本数：{summary['n']}",
        "- 答案正确性、引用语义正确性和事实一致性来自人工评审；程序不代替人工填充这些标签。",
        "",
        "| 指标 | 通过/有效样本 | 比例 |",
        "| --- | ---: | ---: |",
    ]
    for key, label in (
        ("answer_correct", "答案正确率（人工）"),
        ("citation_correct", "引用语义正确率（人工）"),
        ("faithful", "事实一致率（人工）"),
        ("refusal", "拒答决策正确率"),
        ("citation_present", "非拒答答案引用覆盖率"),
        ("citation_valid", "引用编号格式有效率"),
    ):
        metric = summary[key]
        lines.append(
            f"| {label} | {metric['passed']}/{metric['reviewed']} | "
            f"{_percent(metric['rate'])} |")

    lines += ["", "## 延迟与成本", ""]
    if summary["latency_avg"] is None:
        lines.append("- 尚未填写延迟数据。")
    else:
        lines.append(f"- 平均延迟：{summary['latency_avg']:.0f} ms")
        lines.append(f"- P95 延迟（最近秩口径）：{summary['latency_p95']:.0f} ms")
    if summary["cost_avg"] is None:
        lines.append("- 尚未填写成本数据。")
    else:
        lines.append(f"- 单次平均成本：{summary['cost_avg']:.6f}")
        lines.append(f"- 已记录样本总成本：{summary['cost_total']:.6f}")

    lines += [
        "",
        "## 口径限制",
        "",
        "1. 各人工指标使用各自已评审样本作为分母，未评审的 null 不计为正确或错误。",
        "2. 引用编号格式有效不代表引用内容真的支持答案，必须结合人工 citation_correct。",
        "3. 拒答以答案包含“资料中未提及”为程序判据，应结合人工复核检查误拒和漏拒。",
        "4. 延迟和成本只汇总实际填写的样本；报告不能替代更大规模、跨题型的回归评测。",
        "",
        "## 逐题复核",
        "",
        "| 问题 | 拒答正确 | 引用格式有效 | 答案正确 | 引用语义正确 | 事实一致 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    def mark(value):
        return "待评审" if value is None else ("是" if value else "否")

    for item in summary["rows"]:
        question = item["question"].replace("|", "\\|")
        lines.append(
            f"| {question} | {mark(item['refusal_correct'])} | "
            f"{mark(item['citation_valid'])} | {mark(item.get('answer_correct'))} | "
            f"{mark(item.get('citation_correct'))} | {mark(item.get('faithful'))} |")
    return "\n".join(lines) + "\n"


def write_answer_report(input_path, output_path):
    summary = evaluate_answers(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_answer_report(summary, input_path), encoding="utf-8")
    return output_path
