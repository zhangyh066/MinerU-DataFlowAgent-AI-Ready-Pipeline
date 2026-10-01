"""
convert_mineru_jsons.py

将 mineru_outputs/ 目录下 MinerU 解析输出的 JSON 文件批量转换为
DataFlow-Agent 所需的 input.json（[{"file_name": ..., "text": ...}, ...]）。

用法：
    python convert_mineru_jsons.py
    python convert_mineru_jsons.py --input-dir mineru_outputs --output input.json
"""

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


# ===== 1) 文本清洗函数 =====
def clean_text(text: str) -> str:
    """
    清理 MinerU 导出文本中的常见脏字符与异常 Unicode。
    """
    if not isinstance(text, str):
        return ""

    # Unicode 规范化，尽量统一字符形式
    text = unicodedata.normalize("NFKC", text)

    # 替换常见特殊空白
    text = text.replace("\u00A0", " ")   # 不换行空格
    text = text.replace("\u3000", " ")   # 全角空格
    text = text.replace("\t", " ")

    # 去掉零宽字符 / BOM
    text = text.replace("\u200B", "")
    text = text.replace("\u200C", "")
    text = text.replace("\u200D", "")
    text = text.replace("\uFEFF", "")

    # 去掉大多数不可见控制字符，但保留换行
    text = "".join(
        ch for ch in text
        if ch == "\n" or unicodedata.category(ch)[0] != "C"
    )

    # 合并多余空格
    text = re.sub(r"[ ]{2,}", " ", text)

    # 合并过多空行
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 去掉每行首尾空白，并删除空行
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    return text.strip()


def content_fingerprint(text: str) -> str:
    """生成归一化文本的指纹，用于检测内容完全重复的文档。"""
    normalized = re.sub(r"\s+", "", text)
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


# ===== 2) 提取 block/line/span 风格文本 =====
def extract_from_blocks(blocks, texts):
    if not isinstance(blocks, list):
        return

    for block in blocks:
        if not isinstance(block, dict):
            continue

        # 顶层 content（若 block 自带 content，通常已包含其下所有 span 文本）
        block_content = block.get("content", "")
        if isinstance(block_content, str) and block_content.strip():
            cleaned = clean_text(block_content)
            if cleaned:
                texts.append(cleaned)
                continue  # 有 content 时不再重复拼接 lines/spans

        # lines -> spans -> content
        lines = block.get("lines", [])
        if isinstance(lines, list):
            for line in lines:
                if not isinstance(line, dict):
                    continue

                spans = line.get("spans", [])
                if not isinstance(spans, list):
                    continue

                line_parts = []
                for span in spans:
                    if not isinstance(span, dict):
                        continue

                    span_text = span.get("content", "")
                    if isinstance(span_text, str) and span_text.strip():
                        cleaned_span = clean_text(span_text)
                        if cleaned_span:
                            line_parts.append(cleaned_span)

                if line_parts:
                    line_text = "".join(line_parts).strip()
                    if line_text:
                        texts.append(line_text)


# ===== 3) 提取 content_list / list 风格文本 =====
def extract_from_content_list(items, texts):
    if not isinstance(items, list):
        return

    for item in items:
        if isinstance(item, str):
            cleaned = clean_text(item)
            if cleaned:
                texts.append(cleaned)
            continue

        if not isinstance(item, dict):
            continue

        item_type = item.get("type", "")

        # 普通文本
        item_text = item.get("text", "")
        if isinstance(item_text, str) and item_text.strip():
            cleaned = clean_text(item_text)
            if cleaned:
                texts.append(cleaned)

        # 表格
        if item_type == "table":
            table_body = item.get("table_body", "")
            if isinstance(table_body, str) and table_body.strip():
                cleaned = clean_text(table_body)
                if cleaned:
                    texts.append(cleaned)

        # 兼容其他字段
        item_content = item.get("content", "")
        if isinstance(item_content, str) and item_content.strip():
            cleaned = clean_text(item_content)
            if cleaned:
                texts.append(cleaned)


# ===== 4) 从单个 JSON 提取正文 =====
def extract_text_from_mineru_json(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = []

    # 情况 A：标准 MinerU dict 结构
    if isinstance(data, dict):
        pdf_info = data.get("pdf_info", [])
        if isinstance(pdf_info, list):
            for page in pdf_info:
                if not isinstance(page, dict):
                    continue

                # 兼容两种结构：preproc_blocks / para_blocks
                blocks = page.get("preproc_blocks", [])
                if not blocks:
                    blocks = page.get("para_blocks", [])

                extract_from_blocks(blocks, texts)

        # 兼容 {"content_list": [...]}
        content_list = data.get("content_list", [])
        extract_from_content_list(content_list, texts)

    # 情况 B：最外层直接是 list（content_list 风格导出文件）
    elif isinstance(data, list):
        extract_from_content_list(data, texts)

    full_text = "\n".join(texts)
    full_text = clean_text(full_text)

    return full_text


# ===== 5) 主程序：批量转换 =====
def parse_args():
    parser = argparse.ArgumentParser(
        description="将 MinerU 输出的 JSON 批量转换为 input.json"
    )
    parser.add_argument(
        "--input-dir", default=str(BASE_DIR / "mineru_outputs"),
        help="MinerU JSON 文件所在目录（默认：./mineru_outputs）",
    )
    parser.add_argument(
        "--output", default=str(BASE_DIR / "input.json"),
        help="输出文件路径（默认：./input.json）",
    )
    parser.add_argument(
        "--pattern", default="*.json",
        help="文件名匹配模式（默认：*.json）",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_file = Path(args.output)

    if not input_dir.exists():
        raise FileNotFoundError(f"找不到文件夹：{input_dir}")

    json_files = sorted(input_dir.glob(args.pattern))
    if not json_files:
        raise FileNotFoundError(f"在 {input_dir} 中没有找到匹配 {args.pattern} 的文件")

    output_data = []
    seen_hashes = {}
    skipped_empty = []
    skipped_dupes = []

    for json_file in json_files:
        try:
            text = extract_text_from_mineru_json(json_file)

            if not text:
                skipped_empty.append(json_file.name)
                print(f"[跳过] {json_file.name} 提取结果为空")
                continue

            fp = content_fingerprint(text)
            if fp in seen_hashes:
                skipped_dupes.append((json_file.name, seen_hashes[fp]))
                print(f"[跳过] {json_file.name} 与 {seen_hashes[fp]} 内容重复")
                continue
            seen_hashes[fp] = json_file.name

            output_data.append({
                "file_name": json_file.name,
                "text": text
            })

            print(f"[成功] {json_file.name} -> 提取 {len(text)} 个字符")

        except Exception as e:
            print(f"[报错] {json_file.name}: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n全部完成：共扫描 {len(json_files)} 个文件")
    print(f"  成功写入：{len(output_data)} 条")
    if skipped_empty:
        print(f"  空文本跳过：{len(skipped_empty)} 条")
    if skipped_dupes:
        print(f"  重复内容跳过：{len(skipped_dupes)} 条")
    print(f"输出文件：{output_file}")


if __name__ == "__main__":
    main()
