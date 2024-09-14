from typing import TYPE_CHECKING, Union

from hydrogram import filters
from hydrogram.types import CallbackQuery, Message

from bot.helpers import cache
from bot.utils import config

if TYPE_CHECKING:
    from hydrogram import Client
    from hydrogram.filters import Filter


def broadcast(_: "Filter", __: "Client", event: Union[CallbackQuery, Message]) -> bool:
    """
    Determines if a user or chat is authorized based on the chat type and the ID.

    Args:
        _ (Filter): Ignored argument.
        __ (Client): Ignored argument.
        event (Union[CallbackQuery, Message]): The event object containing message or callback query information.

    Returns:
        bool: True if the user is an admin; otherwise, False.
    """
    # Check if the user ID is in the list of admins
    if event.from_user.id in cache.admins or event.from_user.id == config.OWNER_ID:
        return True

    # Return False if none of the conditions are met
    return False


# Create the filter using the broadcast function
filter_broadcast = filters.create(broadcast, name="filter_broadcast")
