"""
generate_report.py

从评估结果生成自包含的交互式 HTML 报告：
  - 统计卡片：总数、成功率、各质量判定数量、平均分
  - 图表：质量占比环形图、评分分布直方图（matplotlib 生成，内嵌 base64，离线可看）
  - 交互表格：按质量判定筛选、关键词搜索、点击表头排序、展开查看摘要/理由

用法：
    python generate_report.py                    # 生成 report.html
    python generate_report.py --charts-dir charts  # 同时把图表 PNG 保存到 charts/
"""

import argparse
import base64
import html
import io
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

QUALITY_ORDER = {"YES": 0, "PARTIAL": 1, "NO": 2}


def make_console_output_safe():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(errors="replace")
            except Exception:
                pass


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="生成交互式 HTML 评估报告")
    parser.add_argument("--input", default=str(BASE_DIR / "output_results_batch.json"),
                        help="评估结果 JSON（默认：./output_results_batch.json）")
    parser.add_argument("--output", default=str(BASE_DIR / "report.html"),
                        help="HTML 报告输出路径（默认：./report.html）")
    parser.add_argument("--charts-dir", default=None,
                        help="可选：同时将图表 PNG 保存到该目录")
    return parser.parse_args(argv)


def compute_stats(rows):
    total = len(rows)
    parsed = [r for r in rows if r.get("parse_ok")]
    failed = total - len(parsed)
    scores = [r["score"] for r in parsed if isinstance(r.get("score"), int)]
    quality_counts = {"YES": 0, "PARTIAL": 0, "NO": 0}
    for r in parsed:
        if r.get("quality") in quality_counts:
            quality_counts[r["quality"]] += 1
    return {
        "total": total,
        "parsed": len(parsed),
        "failed": failed,
        "success_rate": (len(parsed) / total * 100) if total else 0,
        "quality_counts": quality_counts,
        "avg_score": sum(scores) / len(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "scores": scores,
    }


def make_charts(stats, charts_dir=None):
    """生成质量占比环形图与评分分布直方图，返回 {名称: base64}。"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
        plt.rcParams["axes.unicode_minus"] = False
    except ImportError:
        print("未安装 matplotlib，跳过图表生成（表格与统计不受影响）")
        return {}

    images = {}
    colors = {"YES": "#2ea44f", "PARTIAL": "#e6a23c", "NO": "#d73a49"}

    # 环形图
    counts = stats["quality_counts"]
    labels = [k for k in ("YES", "PARTIAL", "NO") if counts[k] > 0]
    values = [counts[k] for k in labels]
    fig, ax = plt.subplots(figsize=(4.2, 3.2), dpi=110)
    ax.pie(
        values, labels=[f"{k} ({v})" for k, v in zip(labels, values)],
        colors=[colors[k] for k in labels], startangle=90,
        wedgeprops={"width": 0.45, "edgecolor": "white"},
    )
    ax.set_title("质量判定占比")
    fig.tight_layout()
    images["donut"] = _fig_to_base64(fig)
    if charts_dir:
        _save_png(fig, charts_dir, "quality_donut.png")
    plt.close(fig)

    # 评分直方图
    if stats["scores"]:
        fig, ax = plt.subplots(figsize=(5.4, 3.2), dpi=110)
        bins = range(0, 101, 10)
        ax.hist(stats["scores"], bins=bins, color="#4a7ebb", edgecolor="white")
        ax.axvline(stats["avg_score"], color="#d73a49", linestyle="--",
                   label=f"平均 {stats['avg_score']:.1f}")
        ax.set_xlabel("评分"); ax.set_ylabel("文献数量")
        ax.set_title("评分分布"); ax.legend()
        fig.tight_layout()
        images["hist"] = _fig_to_base64(fig)
        if charts_dir:
            _save_png(fig, charts_dir, "score_hist.png")
        plt.close(fig)

    return images


def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _save_png(fig, charts_dir, name):
    d = Path(charts_dir)
    d.mkdir(parents=True, exist_ok=True)
    fig.savefig(d / name, format="png")
    print(f"[OK] 图表已保存：{d / name}")


def build_rows_html(rows):
    parts = []
    for r in sorted(rows, key=lambda x: (
            QUALITY_ORDER.get(x.get("quality"), 9),
            -(x.get("score") or 0))):
        name = html.escape(str(r.get("file_name") or "-"))
        quality = r.get("quality") or "失败"
        score = r.get("score") if r.get("score") is not None else "-"
        reason = html.escape(str(r.get("reason") or ""))
        summary = html.escape(str(r.get("summary") or ""))
        preview = html.escape(str(r.get("raw_result_preview") or ""))
        mismatch = " ⚠" if r.get("quality_score_mismatch") else ""
        detail = summary or preview
        detail_label = "摘要" if summary else "原始输出预览"

        parts.append(f"""
        <tr data-quality="{html.escape(quality)}"
            data-search="{(name + ' ' + reason + ' ' + summary).lower()}">
            <td class="name" title="{name}">{name}</td>
            <td><span class="badge q-{html.escape(quality)}">{html.escape(quality)}{mismatch}</span></td>
            <td class="num">{score}</td>
            <td class="reason">{reason}</td>
            <td><details><summary>查看{detail_label}</summary><p>{detail}</p></details></td>
        </tr>""")
    return "\n".join(parts)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI-Ready 数据生产线 · 评估报告</title>
<style>
:root {{ --yes:#2ea44f; --partial:#e6a23c; --no:#d73a49; --ink:#24292f; }}
* {{ box-sizing: border-box; }}
body {{ font-family: "Microsoft YaHei", "Segoe UI", sans-serif; margin: 0;
       background:#f6f8fa; color: var(--ink); }}
header {{ background:#24292f; color:#fff; padding:24px 32px; }}
header h1 {{ margin:0 0 6px; font-size:22px; }}
header p {{ margin:0; opacity:.75; font-size:13px; }}
main {{ max-width:1200px; margin:0 auto; padding:24px; }}
.cards {{ display:flex; flex-wrap:wrap; gap:14px; margin-bottom:20px; }}
.card {{ background:#fff; border:1px solid #e1e4e8; border-radius:8px;
        padding:14px 20px; min-width:130px; flex:1; }}
.card .v {{ font-size:26px; font-weight:700; }}
.card .k {{ font-size:12px; color:#6a737d; margin-top:2px; }}
.charts {{ display:flex; flex-wrap:wrap; gap:14px; margin-bottom:20px; }}
.charts figure {{ background:#fff; border:1px solid #e1e4e8; border-radius:8px;
                 padding:10px; margin:0; }}
.toolbar {{ display:flex; gap:10px; margin-bottom:12px; flex-wrap:wrap; }}
.toolbar input, .toolbar select {{ padding:8px 10px; border:1px solid #d1d5da;
        border-radius:6px; font-size:14px; }}
.toolbar input {{ flex:1; min-width:220px; }}
table {{ width:100%; border-collapse:collapse; background:#fff;
        border:1px solid #e1e4e8; border-radius:8px; overflow:hidden; }}
th, td {{ text-align:left; padding:10px 12px; border-bottom:1px solid #e1e4e8;
         font-size:13.5px; vertical-align:top; }}
th {{ background:#fafbfc; cursor:pointer; user-select:none; white-space:nowrap; }}
th:hover {{ background:#f0f2f5; }}
tr:hover td {{ background:#f6f8fa; }}
td.name {{ max-width:340px; word-break:break-all; }}
td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
td.reason {{ max-width:300px; }}
.badge {{ display:inline-block; padding:2px 10px; border-radius:12px;
         color:#fff; font-size:12px; }}
.q-YES {{ background: var(--yes); }} .q-PARTIAL {{ background: var(--partial); }}
.q-NO {{ background: var(--no); }} .q-失败 {{ background:#6a737d; }}
details summary {{ cursor:pointer; color:#0366d6; }}
details p {{ white-space:pre-wrap; margin:8px 0 0; max-width:520px; }}
footer {{ text-align:center; color:#6a737d; font-size:12px; padding:20px; }}
</style>
</head>
<body>
<header>
    <h1>AI-Ready 数据生产线 · 评估报告</h1>
    <p>MinerU + DataFlow-Agent + GLM · 生成于 {generated_at} · 共 {total} 篇文献</p>
</header>
<main>
    <section class="cards">
        <div class="card"><div class="v">{total}</div><div class="k">总文档数</div></div>
        <div class="card"><div class="v">{success_rate:.1f}%</div><div class="k">解析成功率</div></div>
        <div class="card"><div class="v" style="color:var(--yes)">{yes}</div><div class="k">YES（高质量）</div></div>
        <div class="card"><div class="v" style="color:var(--partial)">{partial}</div><div class="k">PARTIAL</div></div>
        <div class="card"><div class="v" style="color:var(--no)">{no}</div><div class="k">NO（已过滤）</div></div>
        <div class="card"><div class="v">{avg_score:.1f}</div><div class="k">平均评分</div></div>
    </section>

    <section class="charts">
        {donut_figure}
        {hist_figure}
    </section>

    <div class="toolbar">
        <input id="search" type="search" placeholder="搜索文件名 / 理由 / 摘要关键词…">
        <select id="filter">
            <option value="">全部</option>
            <option value="YES">仅 YES</option>
            <option value="PARTIAL">仅 PARTIAL</option>
            <option value="NO">仅 NO</option>
            <option value="失败">仅解析失败</option>
        </select>
    </div>

    <table id="result-table">
        <thead>
        <tr>
            <th onclick="sortBy(0,'text')">文件名 ↕</th>
            <th onclick="sortBy(1,'quality')">判定 ↕</th>
            <th onclick="sortBy(2,'num')">评分 ↕</th>
            <th>理由</th>
            <th>详情</th>
        </tr>
        </thead>
        <tbody>
        {rows}
        </tbody>
    </table>
</main>
<footer>由 generate_report.py 自动生成 · 数据文件：output_results_batch.json</footer>
<script>
const QUALITY_RANK = {{YES:0, PARTIAL:1, NO:2, "失败":3}};
function applyFilter() {{
    const q = document.getElementById('filter').value;
    const s = document.getElementById('search').value.trim().toLowerCase();
    document.querySelectorAll('#result-table tbody tr').forEach(tr => {{
        const okQ = !q || tr.dataset.quality === q;
        const okS = !s || tr.dataset.search.includes(s);
        tr.style.display = (okQ && okS) ? '' : 'none';
    }});
}}
document.getElementById('filter').addEventListener('change', applyFilter);
document.getElementById('search').addEventListener('input', applyFilter);

let sortCol = 2, sortAsc = true;
function cellVal(tr, col) {{ return tr.children[col].innerText.trim(); }}
function sortBy(col, type) {{
    sortAsc = (sortCol === col) ? !sortAsc : true;
    sortCol = col;
    const tbody = document.querySelector('#result-table tbody');
    [...tbody.rows].sort((a, b) => {{
        let va = cellVal(a, col), vb = cellVal(b, col), r;
        if (type === 'num') r = (parseFloat(va) || -1) - (parseFloat(vb) || -1);
        else if (type === 'quality') r = (QUALITY_RANK[va.replace(' ⚠','')] ?? 9) - (QUALITY_RANK[vb.replace(' ⚠','')] ?? 9);
        else r = va.localeCompare(vb, 'zh');
        return sortAsc ? r : -r;
    }}).forEach(tr => tbody.appendChild(tr));
}}
</script>
</body>
</html>
"""


def build_html(rows, stats, images):
    from datetime import datetime
    donut_figure = (f'<figure><img src="data:image/png;base64,{images["donut"]}" '
                    f'alt="质量判定占比"></figure>') if "donut" in images else ""
    hist_figure = (f'<figure><img src="data:image/png;base64,{images["hist"]}" '
                   f'alt="评分分布"></figure>') if "hist" in images else ""
    qc = stats["quality_counts"]
    return PAGE_TEMPLATE.format(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        total=stats["total"],
        success_rate=stats["success_rate"],
        yes=qc["YES"], partial=qc["PARTIAL"], no=qc["NO"],
        avg_score=stats["avg_score"],
        donut_figure=donut_figure,
        hist_figure=hist_figure,
        rows=build_rows_html(rows),
    )


def main(argv=None):
    make_console_output_safe()
    args = parse_args(argv)

    with open(args.input, "r", encoding="utf-8") as f:
        rows = json.load(f)

    stats = compute_stats(rows)
    images = make_charts(stats, args.charts_dir)
    page = build_html(rows, stats, images)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[OK] HTML 报告已生成：{args.output}")


if __name__ == "__main__":
    main()
