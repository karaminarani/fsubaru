from typing import Any, Dict, List, Optional

from bot.base import database
from bot.utils import config


async def add_fs_chat(chat_id: int) -> None:
    """
    Adds a chat ID to the list of subscribed chats.

    Args:
        chat_id (int): The ID of the chat to be added.
    """
    await database.add_value(int(config.BOT_ID), "FSUB_CHATS", chat_id)


async def del_fs_chat(chat_id: int) -> None:
    """
    Removes a chat ID from the list of subscribed chats.

    Args:
        chat_id (int): The ID of the chat to be removed.
    """
    await database.del_value(int(config.BOT_ID), "FSUB_CHATS", chat_id)


async def get_fs_chats() -> List[int]:
    """
    Retrieves the list of subscribed chat IDs.

    Returns:
        List[int]: A list of chat IDs that are subscribed.
    """
    doc: Optional[Dict[str, Any]] = await database.get_doc(int(config.BOT_ID))
    # Ensure the value is a list or return an empty list
    return (
        doc.get("FSUB_CHATS", [])
        if doc and isinstance(doc.get("FSUB_CHATS"), list)
        else []
    )
