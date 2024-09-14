import asyncio
from typing import TYPE_CHECKING

from hydrogram import Client, filters
from hydrogram.errors import FloodWait, RPCError
from hydrogram.helpers import ikb

from bot import (
    add_broadcast_data_id,
    button,
    cache,
    del_broadcast_data_id,
    del_user,
    filter_broadcast,
    get_users,
    logger,
)

if TYPE_CHECKING:
    from hydrogram.types import CallbackQuery, Message

    from bot import bot


class BroadcastManager:
    def __init__(self):
        self.is_running = False
        self.sent = 0
        self.failed = 0
        self.total = 0

    async def start_broadcast(
        self, client: "bot", message: "Message", broadcast_msg: "Message"
    ) -> None:
        if self.is_running:
            await message.reply_text(
                "<b>Currently, a broadcast is running. Check the status for details.</b>",
                quote=True,
            )
            return

        progress_msg = await message.reply_text(
            "<b>Broadcasting...</b>",
            quote=True,
            reply_markup=ikb(button.Broadcast),
        )

        users, admins = await get_users(), cache.admins
        user_ids = [user for user in users if user not in admins]

        self.is_running, self.total = True, len(user_ids)
        logger.info("Broadcast: Starting...")

        chat_id, message_id = message.chat.id, progress_msg.id
        await add_broadcast_data_id(chat_id, message_id)

        for user_id in user_ids:
            if not self.is_running:
                break

            try:
                await broadcast_msg.copy(user_id, protect_content=cache.protect_content)
                self.sent += 1
            except FloodWait as fw:
                logger.warning(f"FloodWait: Sleep {fw.value}")
                await asyncio.sleep(fw.value)
            except RPCError:
                await del_user(user_id)
                self.failed += 1
            except Exception:
                continue

            if (self.sent + self.failed) % 250 == 0:
                await self.update_progress(progress_msg)

        await self.finalize_broadcast(message, progress_msg)

    async def update_progress(self, message: "Message") -> None:
        await message.edit_text(
            "<b>Broadcast Status</b>\n"
            f"  - <code>Sent  :</code> {self.sent} - {self.total}\n"
            f"  - <code>Failed:</code> {self.failed}",
            reply_markup=ikb(button.Broadcast),
        )

    async def finalize_broadcast(
        self, message: "Message", progress_msg: "Message"
    ) -> None:
        status_msg = (
            "Broadcast Finished"
            if self.sent + self.failed == self.total
            else "Broadcast Stopped"
        )

        await message.reply_text(
            f"<b>{status_msg}</b>\n"
            f"  - <code>Sent  :</code> {self.sent} - {self.total}\n"
            f"  - <code>Failed:</code> {self.failed}",
            quote=True,
            reply_markup=ikb(button.Close),
        )

        logger.info(status_msg)
        await del_broadcast_data_id()
        await progress_msg.delete()

        self.is_running, self.sent, self.failed, self.total = False, 0, 0, 0


broadcast_manager = BroadcastManager()


@Client.on_message(filter_broadcast & filters.command(["broadcast", "bc"]))
async def broadcast_handler(client: "bot", message: "Message") -> None:
    broadcast_msg = message.reply_to_message

    if not broadcast_msg:
        if not broadcast_manager.is_running:
            await message.reply_text(
                "<b>Please reply to the message you want to broadcast!</b>",
                quote=True,
            )
        else:
            await message.reply_text(
                "<b>Broadcast Status</b>\n"
                f"  - <code>Sent  :</code> {broadcast_manager.sent} - {broadcast_manager.total}\n"
                f"  - <code>Failed:</code> {broadcast_manager.failed}",
                quote=True,
                reply_markup=ikb(button.Broadcast),
            )
        return

    await broadcast_manager.start_broadcast(client, message, broadcast_msg)


@Client.on_message(filter_broadcast & filters.command("stop"))
async def stop_broadcast_handler(_: "bot", message: "Message") -> None:
    if not broadcast_manager.is_running:
        await message.reply_text(
            "<b>No broadcast is currently running!</b>", quote=True
        )
        return

    broadcast_manager.is_running = False
    await message.reply_text("<b>Broadcast has been stopped!</b>", quote=True)


@Client.on_callback_query(filter_broadcast & filters.regex(r"\bbroadcast\b"))
async def broadcast_handler_query(_: "bot", query: "CallbackQuery") -> None:
    await query.message.edit_text("<b>Refreshing...</b>")
    await broadcast_manager.update_progress(query.message)
