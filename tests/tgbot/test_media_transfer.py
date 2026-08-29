from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Message

from bira_core.tgbot.media_transfer import (
    download_file_for_transfer,
    extract_content,
    get_media_label,
    transfer_message,
)


def test_extract_content_text() -> None:
    message = MagicMock(spec=Message)
    message.text = "hello"
    message.sticker = None
    message.contact = None
    message.location = None
    message.voice = None
    message.video_note = None
    message.video = None
    message.photo = None
    message.document = None
    message.audio = None
    message.animation = None

    assert extract_content(message) == "hello"


@pytest.mark.asyncio
async def test_download_file_for_transfer_uses_basename() -> None:
    bot = AsyncMock()
    bot.get_file.return_value.file_path = "photos/file.jpg"
    bot.download_file = AsyncMock()

    async with download_file_for_transfer(
        bot,
        "file_id",
        100,
        "../../../etc/passwd",
    ) as path:
        assert path is not None
        assert path.name == "passwd"
        assert ".." not in str(path)


@pytest.mark.asyncio
async def test_transfer_message_skips_oversized_file() -> None:
    src = MagicMock(spec=Message)
    src.contact = None
    src.location = None
    src.photo = [MagicMock(file_id="p", file_size=30 * 1024 * 1024)]
    src.video = None
    src.document = None
    src.audio = None
    src.voice = None
    src.video_note = None
    src.animation = None
    src.sticker = None
    src.html_text = None
    src.text = None

    result = await transfer_message(src, AsyncMock(), AsyncMock(), 1)

    assert result.skipped is True


def test_get_media_label_photo() -> None:
    message = MagicMock(spec=Message)
    message.contact = None
    message.photo = [MagicMock()]
    message.caption = "cap"
    message.video = None
    message.document = None
    message.audio = None
    message.voice = None
    message.video_note = None
    message.animation = None
    message.sticker = None
    message.text = None
    message.sticker = None

    assert get_media_label(message) == "[photo] cap"
