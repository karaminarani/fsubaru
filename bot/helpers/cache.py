from typing import TYPE_CHECKING, Dict, List, Optional

from hydrogram.enums import ChatType
from hydrogram.errors import RPCError

from bot.base import bot
from bot.db_funcs import (
    del_fs_chat,
    get_admins,
    get_force_text_msg,
    get_fs_chats,
    get_generate_status,
    get_protect_content,
    get_start_text_msg,
)
from bot.utils import logger

if TYPE_CHECKING:
    from hydrogram import Client


class Cache:
    def __init__(self, client: "Client") -> None:
        """
        Initializes the Caches with the given bot client.

        Args:
            client (bot): The bot client instance.
        """
        self.client = client
        self.start_text: str = "Initializing..."
        self.force_text: str = "Initializing..."
        self.admins: List[int] = []
        self.fs_chats: Dict[int, Dict[str, str]] = {}
        self.protect_content: bool = False
        self.generate_status: bool = False

    async def start_text_init(self) -> str:
        """
        Initializes the start text from the database.

        Returns:
            str: The start text.
        """
        self.start_text = await get_start_text_msg()
        return self.start_text

    async def force_text_init(self) -> str:
        """
        Initializes the force text from the database.

        Returns:
            str: The force text.
        """
        self.force_text = await get_force_text_msg()
        return self.force_text

    async def admins_init(self) -> List[int]:
        """
        Initializes the list of admin user IDs from the database and adds the owner ID.

        Returns:
            List[int]: A list of admin user IDs.
        """
        self.admins = await get_admins()
        for i, user_id in enumerate(self.admins):
            logger.info(f"Bot Admin {i + 1}: {user_id}")

        return self.admins

    async def fs_chats_init(self) -> Dict[int, Dict[str, str]]:
        """
        Initializes the list of free subscription chats from the database and verifies their details.

        Returns:
            Dict[int, Dict[str, Union[str, str]]]: A dictionary of chat details.
        """
        self.fs_chats.clear()  # Restore to default

        fs_chats = await get_fs_chats()
        for i, chat_id in enumerate(fs_chats):
            try:
                chat = await self.client.get_chat(chat_id=chat_id)
                chat_type = (
                    "Group"
                    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]
                    else "Channel"
                )
                invite_link = chat.invite_link
                if not invite_link:
                    raise RPCError

                self.fs_chats[chat_id] = {
                    "chat_type": chat_type,
                    "invite_link": invite_link,
                }
                logger.info(f"Sub. Chat {i + 1}: {chat_id}")
            except RPCError as rpc:
                logger.warning(f"Sub. Chat {i + 1}: {rpc.MESSAGE}")
                await del_fs_chat(chat_id)

        return self.fs_chats

    async def protect_content_init(self) -> bool:
        """
        Initializes the content protection status from the database.

        Returns:
            bool: The content protection status.
        """
        self.protect_content = await get_protect_content()
        return self.protect_content

    async def generate_status_init(self) -> bool:
        """
        Initializes the generate status from the database.

        Returns:
            bool: The generate status.
        """
        self.generate_status = await get_generate_status()
        return self.generate_status

    async def user_is_not_join(self, user_id: int) -> Optional[List[int]]:
        """
        Checks which subscription chats the user has not joined yet.

        Args:
            user_id (int): The ID of the user to check.

        Returns:
            Optional[List[int]]: A list of chat IDs that the user has not joined, or None if the user is an admin.
        """
        chat_ids = list(self.fs_chats.keys())
        if not chat_ids or user_id in self.admins:
            return None

        already_joined = set()
        for chat_id in chat_ids:
            try:
                await self.client.get_chat_member(chat_id, user_id)
                already_joined.add(chat_id)
            except RPCError:
                continue

        return [chat_id for chat_id in chat_ids if chat_id not in already_joined]


cache: Cache = Cache(bot)
