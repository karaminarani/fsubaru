import time
from typing import TYPE_CHECKING

from hydrogram import Client, filters
from hydrogram.helpers import ikb
from hydrogram.raw.functions import Ping

from bot import button, logger

if TYPE_CHECKING:
    from hydrogram.types import CallbackQuery, Message

    from bot import bot


@Client.on_message(filters.private & filters.command("ping"))
async def ping_handler(client: "bot", message: "Message") -> None:
    try:
        latency = await ping_function(client)
        await message.reply_text(
            f"<b>Latency:</b> {latency}",
            quote=True,
            reply_markup=ikb(button.Ping),
        )
    except Exception as exc:
        logger.error(f"Latency: {exc}")
        await message.reply_text("<b>An Error Occurred!</b>", quote=True)


@Client.on_callback_query(filters.regex(r"\bping\b"))
async def ping_handler_query(client: "bot", query: "CallbackQuery") -> None:
    await query.message.edit_text("<b>Refreshing...</b>")

    try:
        latency = await ping_function(client)
        await query.message.edit_text(
            f"<b>Latency:</b> {latency}", reply_markup=ikb(button.Ping)
        )
    except Exception as exc:
        logger.error(f"Latency: {exc}")
        await query.message.edit_text(
            "<b>An Error Occurred!</b>", reply_markup=ikb(button.Ping)
        )


async def ping_function(client: "bot") -> str:
    try:
        start_time = time.time()
        await client.invoke(Ping(ping_id=0))
        end_time = time.time()

        # Calculate latency in milliseconds
        latency_ms = (end_time - start_time) * 1000
        return f"{latency_ms:.2f} ms"
    except Exception as exc:
        logger.error(f"Latency: {exc}")
        return "<b>An Error Occurred!</b>"
