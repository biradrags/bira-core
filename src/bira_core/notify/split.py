def split_message(text: str, limit: int = 4096, *, numbering: bool = True) -> list[str]:
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
    if numbering and len(parts) > 1:
        total = len(parts)
        parts = [f"[{i + 1}/{total}] {part}" for i, part in enumerate(parts)]
    return parts
