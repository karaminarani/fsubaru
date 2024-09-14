from typing import TYPE_CHECKING, Union

from hydrogram import filters
from hydrogram.enums import ChatType
from hydrogram.types import CallbackQuery, Message

from bot.helpers import cache
from bot.utils import config

if TYPE_CHECKING:
    from hydrogram import Client
    from hydrogram.filters import Filter


def authorized(_: "Filter", __: "Client", event: Union[CallbackQuery, Message]) -> bool:
    """
    Determines if a user or chat is authorized based on the chat type and the ID.

    Args:
        _ (Filter): Ignored argument.
        __ (Client): Ignored argument.
        event (Union[CallbackQuery, Message]): The event object containing message or callback query information.

    Returns:
        bool: True if the user is an admin; otherwise, False.
    """
    # Extract the message object from the event
    msg = event.message if isinstance(event, CallbackQuery) else event

    # Check if the message is in a private chat
    if msg.chat.type == ChatType.PRIVATE:
        # Check if the user is an admin
        if event.from_user.id in cache.admins or event.from_user.id == config.OWNER_ID:
            return True

    # For all other cases, return False
    return False


# Create the filter using the authorized function
filter_authorized = filters.create(authorized, name="filter_authorized")
