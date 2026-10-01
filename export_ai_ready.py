"""
export_ai_ready.py

从评估结果中筛选高质量文献，导出为 AI-Ready 语料：
  - corpus.jsonl：每行一篇，字段含 text / summary / quality / score，可直接用于模型微调或 RAG
  - markdown/：每篇一个 Markdown 文件，含元信息、摘要与正文，便于人工阅读与检索

用法：
    python export_ai_ready.py                          # 仅导出 QUALITY=YES 的文献
    python export_ai_ready.py --include-partial        # YES 和 PARTIAL 都导出
    python export_ai_ready.py --min-score 85           # 分数 >= 85
    python export_ai_ready.py --formats jsonl          # 只导出 JSONL
"""

import argparse
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def make_console_output_safe():
    """Windows GBK 控制台无法编码部分符号时自动降级为 ?，避免 UnicodeEncodeError。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(errors="replace")
            except Exception:
                pass

QUALITY_RANK = {"YES": 2, "PARTIAL": 1, "NO": 0}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="从评估结果导出 AI-Ready 语料库"
    )
    parser.add_argument("--input", default=str(BASE_DIR / "output_results_batch.json"),
                        help="评估结果 JSON（默认：./output_results_batch.json）")
    parser.add_argument("--texts", default=str(BASE_DIR / "input.json"),
                        help="原始文档文本 JSON（默认：./input.json）")
    parser.add_argument("--output-dir", default=str(BASE_DIR / "ai_ready_corpus"),
                        help="语料输出目录（默认：./ai_ready_corpus）")
    parser.add_argument("--include-partial", action="store_true",
                        help="同时导出 PARTIAL 文献（默认仅导出 YES）")
    parser.add_argument("--min-score", type=int, default=None,
                        help="最低分数要求（可选，与质量判定同时生效）")
    parser.add_argument("--formats", nargs="+", choices=["jsonl", "md", "csv"],
                        default=["jsonl", "md"],
                        help="导出格式（默认：jsonl md；csv 为评估结果表，可用 Excel 打开）")
    return parser.parse_args(argv)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_stem(name, max_len=60):
    """把文件名转成适合作为文件名的形式。"""
    stem = re.sub(r"\.json$", "", name or "untitled", flags=re.I)
    stem = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", stem)
    stem = re.sub(r"_+", "_", stem).strip("_")
    return stem[:max_len] or "untitled"


def select_rows(rows, include_partial, min_score):
    min_rank = QUALITY_RANK["PARTIAL" if include_partial else "YES"]
    selected = []
    for row in rows:
        if not row.get("parse_ok"):
            continue
        if QUALITY_RANK.get(row.get("quality"), -1) < min_rank:
            continue
        if min_score is not None and (row.get("score") or 0) < min_score:
            continue
        selected.append(row)
    return selected


def export_jsonl(selected, texts_by_name, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        for row in selected:
            text = texts_by_name.get(row["file_name"], "")
            record = {
                "file_name": row["file_name"],
                "quality": row["quality"],
                "score": row["score"],
                "summary": row["summary"],
                "reason": row["reason"],
                "text": text,
                "metadata": {
                    "source": "MinerU + DataFlow-Agent pipeline",
                    "language": "zh" if re.search(r"[\u4e00-\u9fff]", text[:500]) else "en",
                    "text_chars": len(text),
                },
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def export_csv(selected, out_file):
    """导出评估结果表（utf-8-sig 带 BOM，Excel 打开不乱码）。"""
    import csv
    with open(out_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file_name", "quality", "score", "reason", "summary"])
        for row in selected:
            writer.writerow([
                row.get("file_name"),
                row.get("quality"),
                row.get("score"),
                row.get("reason"),
                row.get("summary"),
            ])


def export_markdown(selected, texts_by_name, md_dir):
    md_dir.mkdir(parents=True, exist_ok=True)
    used = set()
    for row in selected:
        stem = safe_stem(row["file_name"])
        filename, i = stem, 2
        while filename.lower() in used:
            filename = f"{stem}_{i}"
            i += 1
        used.add(filename.lower())

        text = texts_by_name.get(row["file_name"], "")
        lines = [
            f"# {filename}",
            "",
            f"- 质量判定：{row['quality']}",
            f"- 评分：{row['score']}",
            f"- 理由：{row['reason']}",
            "",
            "## 摘要",
            "",
            row["summary"] or "",
            "",
            "## 正文",
            "",
            text,
            "",
        ]
        with open(md_dir / f"{filename}.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def main(argv=None):
    make_console_output_safe()
    args = parse_args(argv)

    rows = load_json(args.input)
    texts = load_json(args.texts)
    texts_by_name = {t.get("file_name"): t.get("text", "") for t in texts}

    selected = select_rows(rows, args.include_partial, args.min_score)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if "jsonl" in args.formats:
        jsonl_file = out_dir / "corpus.jsonl"
        export_jsonl(selected, texts_by_name, jsonl_file)
        print(f"[OK] JSONL 语料已导出：{jsonl_file}（{len(selected)} 篇）")

    if "csv" in args.formats:
        csv_file = out_dir / "corpus_eval.csv"
        export_csv(selected, csv_file)
        print(f"[OK] CSV 结果表已导出：{csv_file}（{len(selected)} 篇）")

    if "md" in args.formats:
        md_dir = out_dir / "markdown"
        export_markdown(selected, texts_by_name, md_dir)
        print(f"[OK] Markdown 语料已导出：{md_dir}（{len(selected)} 篇）")

    skipped = len(rows) - len(selected)
    print(f"共 {len(rows)} 篇评估结果，导出 {len(selected)} 篇，过滤 {skipped} 篇")


if __name__ == "__main__":
    main()
