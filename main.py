import asyncio

# Attempt to use uvloop for the event loop if available
try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

from typing import Union

import aiofiles.os
from hydrogram import errors
from hydrogram.enums import ParseMode
from hydrogram.helpers import ikb

from bot import (
    BotError,
    aiofiles_read,
    bot,
    button,
    cache,
    config,
    del_broadcast_data_id,
    get_broadcast_data_ids,
    initial_database,
    logger,
)


async def send_msg_to_admins(
    msg_text: str,
    parse_mode: Union[ParseMode.HTML, ParseMode.MARKDOWN] = ParseMode.HTML,
) -> None:
    """
    Sends a message to the bot administrators.

    Args:
        msg_text (str): The message text to send.
    """
    contact_button = ikb(button.Contact)
    for admin in cache.admins:
        try:
            await bot.send_message(
                chat_id=admin,
                text=msg_text,
                reply_markup=contact_button,
                parse_mode=parse_mode,
            )
        except errors.RPCError:
            continue


async def send_restart_msg(chat_id: int, message_id: int, text: str) -> None:
    """
    Sends a restart message to a specific chat.

    Args:
        chat_id (int): The ID of the chat to send the message to.
        message_id (int): The ID of the message to reply to.
        text (str): The message text to send.
    """
    await bot.send_message(chat_id, text, reply_to_message_id=message_id)


async def cache_db_init() -> None:
    """
    Initializes various cache-related handlers.
    """
    await asyncio.gather(
        cache.force_text_init(),
        cache.start_text_init(),
        cache.generate_status_init(),
        cache.protect_content_init(),
        cache.admins_init(),
        cache.fs_chats_init(),
    )


async def restart_data_init() -> None:
    """
    Handles the initialization process when the bot restarts, including sending messages and handling broadcast data.
    """
    try:
        # Check if the restart flag file exists
        if await aiofiles.os.path.isfile(".restart"):
            # Read the restart data from the file
            content = await aiofiles_read(".restart")
            chat_id, self_id, message_id = map(int, content.split(" - "))

            await send_restart_msg(chat_id, message_id, "<b>Bot Restarted!</b>")
            await bot.delete_messages(chat_id, self_id)

            await aiofiles.os.remove(".restart")

        else:
            chat_id, message_id = await get_broadcast_data_ids()
            if chat_id and message_id:
                logger.info(f"BroadcastID: {chat_id}, {message_id}")

                await send_restart_msg(chat_id, message_id, "<b>Bot Started!</b>")
                await del_broadcast_data_id()

    except Exception as exc:
        logger.error(str(exc))


async def main() -> None:
    """
    Main function to initialize and run the bot, including database setup, cache initialization,
    restart handling, and setting up the scheduler.
    """
    # Start bot and connect MongoDB
    await bot.start()

    # Initializing MongoDB
    await initial_database()

    # Fetching MongoDB
    await cache_db_init()

    # Initializing BroadcastID
    await restart_data_init()

    logger.info(f"@{bot.me.username} {config.BOT_ID}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
        logger.info("Bot Activated!")
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: Terminating...")
    except BotError as e:
        logger.error(str(e))
    finally:
        loop.run_until_complete(bot.stop())
        loop.close()
