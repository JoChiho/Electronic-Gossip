"""占卜记录 Markdown 导出（纯逻辑）。"""

from __future__ import annotations

from bagua.yao_texts import format_yao_texts_block


def _format_hexagram_markdown(hexagram: dict) -> list[str]:
    name = hexagram.get("name", "未知卦")
    lines = [
        f"### {name}",
        "",
        f"- 上卦：{hexagram.get('upper_trigram', '')}",
        f"- 下卦：{hexagram.get('lower_trigram', '')}",
    ]
    yaos = hexagram.get("yaos") or []
    if yaos:
        lines += ["", "**六爻（自下而上）**", ""]
        for yao in yaos:
            graphic = "阳" if yao.get("is_yang") else "阴"
            label = yao.get("label", "")
            pos = yao.get("position", "")
            extra = " · 变爻" if yao.get("is_changing") else ""
            lines.append(f"- 第{pos}爻 {label}（{graphic}{extra}）")
    changing = hexagram.get("changing_positions") or []
    if changing:
        lines.append("")
        lines.append(f"- 变爻位置：第 {', '.join(str(p) for p in changing)} 爻")
    changed = hexagram.get("changed_hexagram")
    if changed:
        lines += [
            "",
            f"**之卦**：{changed.get('name', '')}（"
            f"{changed.get('upper_trigram', '')} / {changed.get('lower_trigram', '')}）",
        ]
    highlights = set(hexagram.get("changing_positions") or [])
    yao_md = format_yao_texts_block(name, highlight_positions=highlights)
    if yao_md:
        lines += ["", "**爻辞（《周易》）**", ""]
        for row in yao_md[1:]:
            lines.append(row.strip().replace(" ★", "（变爻）"))
    return lines


def record_to_markdown(data: dict) -> str:
    """将单条 JSON 记录转为 Markdown 文本。"""
    hexagram = data.get("hexagram") or {}
    name = hexagram.get("name", "未知卦")
    question = (data.get("question") or "").strip() or "（未填写）"
    bazi = (data.get("bazi") or "").strip() or "（未提供）"

    lines = [
        f"# 占卜记录 · {name}",
        "",
        "## 概览",
        "",
        f"- **保存时间**：{data.get('saved_at', '')}",
        f"- **起卦时间**：{data.get('divination_time', '')}",
        f"- **起卦方法**：{data.get('method', '')}",
        f"- **时区**：{data.get('timezone', '')}",
        f"- **问题**：{question}",
        f"- **八字**：{bazi}",
        f"- **出生时间**：{data.get('birth_datetime', '') or '（未提供）'}",
        "",
        "## 卦象",
        "",
        *_format_hexagram_markdown(hexagram),
        "",
        "## AI 解读提示词",
        "",
        "```",
        (data.get("prompt") or "").strip(),
        "```",
        "",
    ]
    return "\n".join(lines)


def records_to_markdown(records: list[dict]) -> str:
    """多条记录合并为一份 Markdown（`---` 分隔）。"""
    if not records:
        return "# 占卜记录导出\n\n（无记录）\n"
    parts = [record_to_markdown(item) for item in records]
    header = f"# bagua 占卜记录导出\n\n共 {len(records)} 条记录。\n\n---\n\n"
    return header + "\n---\n\n".join(parts)