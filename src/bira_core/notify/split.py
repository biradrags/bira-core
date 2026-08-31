"""Plain-text message splitter with numbering."""

_MAX_RENUMBER_PASSES = 4


def split_message(text: str, limit: int = 4096, *, numbering: bool = True) -> list[str]:
    """Plain text; с parse_mode=HTML не сочетать."""
    if len(text) <= limit:
        return [text]
    effective = limit
    if numbering:
        effective = limit - len("[99/99] ")
    parts = _split_raw(text, effective)
    if numbering and len(parts) > 1:
        # Префикс растёт вместе с разрядностью номера, а от него зависит бюджет
        # куска: пересчитываем до стабильной пары (бюджет, число частей).
        for _ in range(_MAX_RENUMBER_PASSES):
            total = len(parts)
            prefix_len = len(f"[{total}/{total}] ")
            parts = _split_raw(text, limit - prefix_len)
            if len(parts) == total:
                break
        total = len(parts)
        parts = [f"[{i + 1}/{total}] {part}" for i, part in enumerate(parts)]
    return parts


def _split_raw(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    buffer: list[str] = []
    size = 0
    for line in text.split("\n"):
        if len(line) > limit:
            if buffer:
                parts.append("\n".join(buffer))
                buffer, size = [], 0
            for i in range(0, len(line), limit):
                parts.append(line[i : i + limit])
            continue
        line_size = len(line) + 1
        if size + line_size > limit and buffer:
            parts.append("\n".join(buffer))
            buffer, size = [], 0
        buffer.append(line)
        size += line_size
    if buffer:
        parts.append("\n".join(buffer))
    return parts
