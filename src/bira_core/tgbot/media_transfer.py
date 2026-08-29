from __future__ import annotations

import logging
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, Message

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024


def extract_content(message: Message) -> str | None:
    if message.text:
        return message.text
    if message.sticker:
        return f"[sticker: {message.sticker.emoji or ''}]"
    if message.contact:
        phone = message.contact.phone_number or ""
        name = (
            " ".join(
                filter(None, [message.contact.first_name, message.contact.last_name])
            )
            or ""
        )
        return f"[contact: {phone}, {name}]" if name else f"[contact: {phone}]"
    if message.location:
        return f"[location: {message.location.latitude}, {message.location.longitude}]"
    if message.voice:
        return "[voice]"
    if message.video_note:
        return "[video_note]"
    if message.video:
        return f"[video] {message.caption or ''}"
    if message.photo:
        return f"[photo] {message.caption or ''}"
    if message.document:
        return f"[document: {message.document.file_name or ''}] {message.caption or ''}"
    if message.audio:
        return f"[audio: {message.audio.title or message.audio.file_name or ''}] {message.caption or ''}"
    if message.animation:
        return f"[animation] {message.caption or ''}"
    return None


@dataclass
class TransferResult:
    sent: Message | None = None
    skipped: bool = False
    error: str | None = None
    raw_exc: BaseException | None = None


@asynccontextmanager
async def download_file_for_transfer(
    src_bot: Bot,
    file_id: str,
    file_size: int | None,
    filename: str | None = None,
) -> AsyncIterator[Path | None]:
    if file_size is None or file_size > MAX_FILE_SIZE:
        yield None
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        safe_name = Path(filename).name if filename else ""
        if safe_name in ("", ".", ".."):
            safe_name = "file"
        tmp_path = Path(tmp_dir) / safe_name
        path_result: Path | None = None
        try:
            file_info = await src_bot.get_file(file_id)
            file_path = file_info.file_path
            if file_path is None:
                path_result = None
            elif file_path.startswith("/"):
                logger.debug(
                    "local Bot API path detected, skipping download",
                    extra={"path": file_path},
                )
                path_result = None
            else:
                await src_bot.download_file(file_path, tmp_path)
                path_result = tmp_path
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "failed to download file",
                extra={"file_id": file_id, "err": f"{type(e).__name__}: {e}"},
            )
            path_result = None
        yield path_result


async def transfer_message(
    src_message: Message,
    src_bot: Bot,
    dst_bot: Bot,
    dst_chat_id: int,
    dst_thread_id: int | None = None,
    business_connection_id: str | None = None,
) -> TransferResult:
    try:
        if src_message.contact:
            return TransferResult(skipped=True)

        if src_message.location:
            loc = src_message.location
            sent = await dst_bot.send_location(
                chat_id=dst_chat_id,
                message_thread_id=dst_thread_id,
                latitude=loc.latitude,
                longitude=loc.longitude,
                business_connection_id=business_connection_id,
            )
            return TransferResult(sent=sent)

        if src_message.photo:
            photo = src_message.photo[-1]
            async with download_file_for_transfer(
                src_bot, photo.file_id, photo.file_size, "photo.jpg"
            ) as path:
                if path:
                    sent = await dst_bot.send_photo(
                        chat_id=dst_chat_id,
                        message_thread_id=dst_thread_id,
                        photo=FSInputFile(path),
                        caption=src_message.caption,
                        business_connection_id=business_connection_id,
                    )
                    return TransferResult(sent=sent)
            return TransferResult(skipped=True)

        if src_message.video:
            v = src_message.video
            async with download_file_for_transfer(
                src_bot, v.file_id, v.file_size, v.file_name or "video.mp4"
            ) as path:
                if path:
                    sent = await dst_bot.send_video(
                        chat_id=dst_chat_id,
                        message_thread_id=dst_thread_id,
                        video=FSInputFile(path),
                        caption=src_message.caption,
                        business_connection_id=business_connection_id,
                    )
                    return TransferResult(sent=sent)
            return TransferResult(skipped=True)

        if src_message.document:
            d = src_message.document
            async with download_file_for_transfer(
                src_bot, d.file_id, d.file_size, d.file_name or "document"
            ) as path:
                if path:
                    sent = await dst_bot.send_document(
                        chat_id=dst_chat_id,
                        message_thread_id=dst_thread_id,
                        document=FSInputFile(path, filename=d.file_name),
                        caption=src_message.caption,
                        business_connection_id=business_connection_id,
                    )
                    return TransferResult(sent=sent)
            return TransferResult(skipped=True)

        if src_message.audio:
            a = src_message.audio
            async with download_file_for_transfer(
                src_bot, a.file_id, a.file_size, a.file_name or "audio.mp3"
            ) as path:
                if path:
                    sent = await dst_bot.send_audio(
                        chat_id=dst_chat_id,
                        message_thread_id=dst_thread_id,
                        audio=FSInputFile(path, filename=a.file_name),
                        caption=src_message.caption,
                        business_connection_id=business_connection_id,
                    )
                    return TransferResult(sent=sent)
            return TransferResult(skipped=True)

        if src_message.voice:
            voice = src_message.voice
            async with download_file_for_transfer(
                src_bot, voice.file_id, voice.file_size, "voice.ogg"
            ) as path:
                if path:
                    sent = await dst_bot.send_voice(
                        chat_id=dst_chat_id,
                        message_thread_id=dst_thread_id,
                        voice=FSInputFile(path),
                        business_connection_id=business_connection_id,
                    )
                    return TransferResult(sent=sent)
            return TransferResult(skipped=True)

        if src_message.video_note:
            vn = src_message.video_note
            async with download_file_for_transfer(
                src_bot, vn.file_id, vn.file_size, "video_note.mp4"
            ) as path:
                if path:
                    sent = await dst_bot.send_video_note(
                        chat_id=dst_chat_id,
                        message_thread_id=dst_thread_id,
                        video_note=FSInputFile(path),
                        business_connection_id=business_connection_id,
                    )
                    return TransferResult(sent=sent)
            return TransferResult(skipped=True)

        if src_message.animation:
            anim = src_message.animation
            async with download_file_for_transfer(
                src_bot, anim.file_id, anim.file_size, anim.file_name or "animation.mp4"
            ) as path:
                if path:
                    sent = await dst_bot.send_animation(
                        chat_id=dst_chat_id,
                        message_thread_id=dst_thread_id,
                        animation=FSInputFile(path),
                        caption=src_message.caption,
                        business_connection_id=business_connection_id,
                    )
                    return TransferResult(sent=sent)
            return TransferResult(skipped=True)

        if src_message.sticker:
            st = src_message.sticker
            async with download_file_for_transfer(
                src_bot, st.file_id, st.file_size, "sticker.webp"
            ) as path:
                if path:
                    sent = await dst_bot.send_sticker(
                        chat_id=dst_chat_id,
                        message_thread_id=dst_thread_id,
                        sticker=FSInputFile(path),
                        business_connection_id=business_connection_id,
                    )
                    return TransferResult(sent=sent)
            return TransferResult(skipped=True)

        text = src_message.html_text or src_message.text
        if text:
            sent = await dst_bot.send_message(
                chat_id=dst_chat_id,
                message_thread_id=dst_thread_id,
                text=text,
                parse_mode=ParseMode.HTML,
                business_connection_id=business_connection_id,
            )
            return TransferResult(sent=sent)

        return TransferResult(skipped=True)

    except Exception as e:  # noqa: BLE001
        logger.warning(
            "failed to transfer message", extra={"err": f"{type(e).__name__}: {e}"}
        )
        return TransferResult(error=str(e), raw_exc=e)


def get_media_label(message: Message) -> str:
    if message.contact:
        c = message.contact
        name = " ".join(filter(None, [c.first_name, c.last_name]))
        return f"[contact] {name}: {c.phone_number}"
    if message.photo:
        return f"[photo] {message.caption or ''}"
    if message.video:
        return f"[video: {message.video.file_name or ''}] {message.caption or ''}"
    if message.document:
        return f"[document: {message.document.file_name or ''}] {message.caption or ''}"
    if message.audio:
        return f"[audio: {message.audio.title or message.audio.file_name or ''}] {message.caption or ''}"
    if message.voice:
        return "[voice]"
    if message.video_note:
        return "[video_note]"
    if message.animation:
        return f"[animation] {message.caption or ''}"
    if message.sticker:
        return f"[sticker: {message.sticker.emoji or ''}]"
    return extract_content(message) or "[empty]"
