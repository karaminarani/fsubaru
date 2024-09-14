from typing import Any, Dict, List, Optional

from bot.base import database
from bot.utils import config


async def add_user(user_id: int) -> None:
    """
    Adds a user ID to the list of bot users in the database.

    Args:
        user_id (int): The ID of the user to add.
    """
    await database.add_value(int(config.BOT_ID), "BOT_USERS", user_id)


async def del_user(user_id: int) -> None:
    """
    Removes a user ID from the list of bot users in the database.

    Args:
        user_id (int): The ID of the user to remove.
    """
    await database.del_value(int(config.BOT_ID), "BOT_USERS", user_id)


async def get_users() -> List[int]:
    """
    Retrieves the list of bot users from the database.

    Returns:
        List[int]: A list of user IDs that are associated with the bot.
                   Returns an empty list if no users are found or if the document does not exist.
    """
    doc: Optional[Dict[str, Any]] = await database.get_doc(int(config.BOT_ID))
    return (
        doc.get("BOT_USERS", [])
        if doc and isinstance(doc.get("BOT_USERS"), list)
        else []
    )
