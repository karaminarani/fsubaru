from typing import TYPE_CHECKING

from hydrogram import Client, filters
from hydrogram.helpers import ikb

from bot import config, filter_authorized, logger, url_safe
from plugins import list_available_commands

if TYPE_CHECKING:
    from hydrogram.types import Message

    from bot import bot


@Client.on_message(
    filter_authorized & (~filters.command(list_available_commands) & ~filters.service)
)
async def generate_handler(client: "bot", message: "Message") -> None:
    try:
        # Copy the message to the database chat
        database_chat_id = config.DATABASE_CHAT_ID
        database_message = await message.copy(database_chat_id)

        # Encode message ID
        encoded_data = url_safe.encode_data(
            f"id-{database_message.id * abs(database_chat_id)}"
        )
        encoded_data_url = f"https://t.me/{client.me.username}?start={encoded_data}"

        # Create a shareable URL
        share_encoded_data_url = f"https://t.me/share/url?url={encoded_data_url}"

        # Reply to the user with the generated URL
        await message.reply_text(
            encoded_data_url,
            quote=True,
            reply_markup=ikb([[("Share", share_encoded_data_url, "url")]]),
            disable_web_page_preview=True,
        )
    except Exception as exc:
        # Log the error and inform the user
        logger.error(f"Generator: {exc}")
        await message.reply_text("<b>An Error Occurred!</b>", quote=True)
