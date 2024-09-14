import asyncio
import sys
from typing import TYPE_CHECKING

import aiofiles
from hydrogram import Client, filters
from hydrogram.helpers import ikb

import bot
from bot import aiofiles_read, button, config, get_gist_raw, logger

if TYPE_CHECKING:
    from hydrogram.types import Message

    from bot import bot


@Client.on_message(filters.filter_authorized & filters.command("set"))
async def settings_handler(_: "bot", message: "Message") -> None:
    await message.reply_text(
        "<b>Bot Settings:</b>", quote=True, reply_markup=ikb(button.Menu)
    )


@Client.on_message(filters.user(config.OWNER_ID) & filters.command(["logs", "log"]))
async def logs_handler(_: "bot", message: "Message") -> None:
    logs_msg = await message.reply_text("<b>Retrieving...</b>", quote=True)
    logs_doc = await aiofiles_read("logs.txt")
    logs_url = await get_gist_raw(content=str(logs_doc))

    logs_button = ikb([[("View", logs_url, "url")]])
    await logs_msg.edit_text("<b>Bot Logs</b>", reply_markup=logs_button)


@Client.on_message(filters.user(config.OWNER_ID) & filters.command(["restart", "r"]))
async def restart_handler(_: "bot", message: "Message") -> None:
    async def async_restart_func() -> None:
        process = await asyncio.create_subprocess_exec(sys.executable, *sys.argv)
        await process.wait()

    self_msg = await message.reply_text("<b>Restarting...</b>", quote=True)
    chat_id, self_id, message_id = message.chat.id, self_msg.id, message.id

    async with aiofiles.open(".restart", mode="w") as doc:
        await doc.write(f"{chat_id} - {self_id} - {message_id}")

    logger.info("Bot: Restarting...")
    await async_restart_func()