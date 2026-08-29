"""Plain-text message splitter with numbering."""


def split_message(text: str, limit: int = 4096, *, numbering: bool = True) -> list[str]:
    """Plain text; с parse_mode=HTML не сочетать."""
    if len(text) <= limit:
        return [text]
    effective = limit
    if numbering:
        effective = limit - len("[99/99] ")
    parts = _split_raw(text, effective)
    if numbering and len(parts) > 1:
        while True:
            total = len(parts)
            prefix_len = len(f"[{total}/{total}] ")
            new_effective = limit - prefix_len
            new_parts = _split_raw(text, new_effective)
            if len(new_parts) == total:
                break
            parts = new_parts
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
