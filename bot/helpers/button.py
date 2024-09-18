from typing import TYPE_CHECKING, List, Optional, Tuple

from hydrogram.helpers import ikb

from bot.utils import config

from .cache import cache

if TYPE_CHECKING:
    from hydrogram import Client
    from hydrogram.types import Message


class Button:
    """
    Defines various inline button layouts for the bot.
    """

    Contact: List[List[Tuple[str, str, str]]] = [
        [("Contact", f"https://t.me/{config.OWNER_USERNAME.strip('@')}", "url")]
    ]
    Close: List[List[Tuple[str, str]]] = [[("Close", "close")]]
    Broadcast: List[List[Tuple[str, str]]] = [[("Refresh", "broadcast")]]
    Ping: List[List[Tuple[str, str]]] = [[("Refresh", "ping")]]
    Uptime: List[List[Tuple[str, str]]] = [[("Refresh", "uptime")]]
    Menu: List[List[Tuple[str, str]]] = [
        [("Generate Status", "menu_generate")],
        [("Start", "menu_start"), ("Force", "menu_force")],
        [("Protect Content", "menu_protect")],
        [("Admins", "menu_admins"), ("F-Subs", "menu_fsubs")],
        [("Report and Feedback", "https://t.me/6281991816908", "url")],
    ]
    Cancel: List[List[Tuple[str, str]]] = [[("Cancel", "cancel")]]
    Generate: List[List[Tuple[str, str]]] = [
        [("« Back", "settings"), ("Change", "change_generate")]
    ]
    Generate_: List[List[Tuple[str, str]]] = [[("« Back", "menu_generate")]]
    Start: List[List[Tuple[str, str]]] = [
        [("« Back", "settings"), ("Set", "update_start")]
    ]
    Start_: List[List[Tuple[str, str]]] = [[("« Back", "menu_start")]]
    Force: List[List[Tuple[str, str]]] = [
        [("« Back", "settings"), ("Set", "update_force")]
    ]
    Force_: List[List[Tuple[str, str]]] = [[("« Back", "menu_force")]]
    Protect: List[List[Tuple[str, str]]] = [
        [("« Back", "settings"), ("Change", "change_protect")]
    ]
    Protect_: List[List[Tuple[str, str]]] = [[("« Back", "menu_protect")]]
    Admins: List[List[Tuple[str, str]]] = [
        [("Add", "add_admin"), ("Del.", "del_admin")],
        [("« Back", "settings")],
    ]
    Admins_: List[List[Tuple[str, str]]] = [[("« Back", "menu_admins")]]
    Fsubs: List[List[Tuple[str, str]]] = [
        [("Add", "add_f-sub"), ("Del.", "del_f-sub")],
        [("« Back", "settings")],
    ]
    Fsubs_: List[List[Tuple[str, str]]] = [[("« Back", "menu_fsubs")]]


button: Button = Button()


def admin_buttons() -> ikb:
    """
    Creates an inline keyboard with buttons for admin-related actions.

    Returns:
        ikb: An inline keyboard with buttons for managing chats and additional settings.
    """
    buttons: List[Tuple[str, str, str]] = []
    fs_data = cache.fs_chats
    if fs_data:
        for chat_id, chat_info in fs_data.items():
            chat_type = chat_info.get("chat_type", "Unknown")
            invite_link = chat_info.get("invite_link", "#")
            buttons.append((chat_type, invite_link, "url"))

    button_layouts: List[List[Tuple[str, str, str]]] = [
        buttons[i : i + 3] for i in range(0, len(buttons), 3)
    ]
    button_layouts.append([("Bot Settings", "settings")])

    return ikb(button_layouts)


async def join_buttons(
    client: "Client", message: "Message", user_id: int
) -> Optional[ikb]:
    """
    Creates an inline keyboard with buttons for joining chats the user hasn't joined yet.

    Args:
        client (Client): The hydrogram client instance.
        message (Message): The message that triggered this action.
        user_id (int): The ID of the user for whom the join buttons are being created.

    Returns:
        Optional[ikb]: An inline keyboard with join buttons, or None if the user is already joined.
    """
    no_join_ids = await cache.user_is_not_join(user_id)
    if not no_join_ids:
        return None

    buttons: List[Tuple[str, str, str]] = []
    fs_data = cache.fs_chats
    for chat_id in no_join_ids:
        chat_info = fs_data.get(chat_id, {})
        chat_type = chat_info.get("chat_type", "Unknown")
        invite_link = chat_info.get("invite_link", "#")
        buttons.append((f"Join {chat_type}", invite_link, "url"))

    button_layouts: List[List[Tuple[str, str, str]]] = [
        buttons[i : i + 2] for i in range(0, len(buttons), 2)
    ]

    if len(message.command) > 1:
        start_url = f"https://t.me/{client.me.username}?start={message.command[1]}"
        button_layouts.append([("Try Again", start_url, "url")])

    return ikb(button_layouts)
