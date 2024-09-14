from typing import TYPE_CHECKING

from hydrogram import Client, filters
from hydrogram.enums import ChatType
from hydrogram.errors import ListenerStopped, ListenerTimeout, RPCError
from hydrogram.helpers import ikb

from bot import (
    add_admin,
    add_fs_chat,
    button,
    cache,
    del_admin,
    del_fs_chat,
    filter_authorized,
    logger,
    update_force_text_msg,
    update_generate_status,
    update_protect_content,
    update_start_text_msg,
)

if TYPE_CHECKING:
    from hydrogram.types import CallbackQuery

    from bot import bot


@Client.on_callback_query(filter_authorized & filters.regex(r"\bcancel\b"))
async def cancel_handler_query(client: "bot", query: "CallbackQuery") -> None:
    chat_id, user_id = query.message.chat.id, query.from_user.id
    await client.stop_listening(chat_id=chat_id, user_id=user_id)


@Client.on_callback_query(filter_authorized & filters.regex(r"\bsettings\b"))
async def settings_handler_query(_: "bot", query: "CallbackQuery") -> None:
    await query.message.edit_text("<b>Bot Settings:</b>", reply_markup=ikb(button.Menu))


@Client.on_callback_query(filter_authorized & filters.regex(r"\bclose\b"))
async def close_handler_query(_: "bot", query: "CallbackQuery") -> None:
    try:
        await query.message.reply_to_message.delete()
    except RPCError:
        pass

    await query.message.delete()


@Client.on_callback_query(
    filter_authorized
    & filters.regex(r"menu_(generate|start|force|protect|admins|fsubs)")
)
async def menu_handler_query(_: "bot", query: "CallbackQuery") -> None:
    def format_list_items(item_title: str, list_items: list) -> str:
        formatted_items = (
            "".join(
                f"  {i + 1}. <code>{item}</code>\n" for i, item in enumerate(list_items)
            )
            if list_items
            else "  <code>None</code>"
        )
        return f"{item_title}:\n{formatted_items}"

    query_data = query.data.split("_")[1]
    response_texts = {
        "generate": f"Currently Generate Status is <b>{cache.generate_status}</b>",
        "start": f"<b>Start Text:</b>\n  {cache.start_text}",
        "force": f"<b>Force Text:</b>\n  {cache.force_text}",
        "protect": f"Currently Protect Content is <b>{cache.protect_content}</b>",
        "admins": format_list_items("<b>List Admins</b>", cache.admins),
        "fsubs": format_list_items("<b>List F-Subs</b>", cache.fs_chats),
    }

    if query_data in response_texts:
        await query.message.edit_text(
            response_texts[query_data],
            reply_markup=ikb(getattr(button, query_data.capitalize(), [])),
        )


@Client.on_callback_query(
    filter_authorized & filters.regex(r"change_(generate|protect)")
)
async def change_handler_query(_: "bot", query: "CallbackQuery") -> None:
    query_data = query.data.split("_")[1]

    if query_data == "generate":
        await update_generate_status()
        await cache.generate_status_init()
        logger.info("Generate Status: Changed")
        text = f"Generate Status has been changed to <b>{cache.generate_status}</b>"
        buttons = button.Generate_

    elif query_data == "protect":
        await update_protect_content()
        await cache.protect_content_init()
        logger.info("Protect Content: Changed")
        text = f"Protect Content has been changed to <b>{cache.protect_content}</b>"
        buttons = button.Protect_

    else:
        return

    await query.message.edit_text(text, reply_markup=ikb(buttons))


@Client.on_callback_query(filter_authorized & filters.regex(r"update_(start|force)"))
async def set_handler_query(client: "bot", query: "CallbackQuery") -> None:
    query_data = query.data.split("_")[1]
    await query.message.edit_text(
        f"Send a new {query_data.capitalize()} Text Message\n\n<b>Timeout:</b> 45s",
        reply_markup=ikb(button.Cancel),
    )

    buttons = ikb(button.Start_) if query_data == "start" else ikb(button.Force_)
    chat_id, user_id = query.message.chat.id, query.from_user.id

    try:
        listening = await client.listen(chat_id=chat_id, user_id=user_id, timeout=45)
        new_text = listening.text
        await listening.delete()
    except ListenerStopped:
        await query.message.edit_text(
            "<b>Process has been cancelled!</b>", reply_markup=buttons
        )
        return
    except ListenerTimeout:
        await query.message.edit_text(
            "<b>Time limit exceeded! Process has been cancelled.</b>",
            reply_markup=buttons,
        )
        return

    if not new_text:
        await query.message.edit_text(
            "<b>Invalid! Just send a text message.</b>", reply_markup=buttons
        )
    else:
        if query_data == "start":
            await update_start_text_msg(new_text)
            await cache.start_text_init()
            logger.info("Start Text: Customized")
        else:
            await update_force_text_msg(new_text)
            await cache.force_text_init()
            logger.info("Force Text: Customized")

        await query.message.edit_text(
            f"New! {query_data.capitalize()} Text Message:\n  {new_text}",
            reply_markup=buttons,
        )


@Client.on_callback_query(filter_authorized & filters.regex(r"add_(admin|f-sub)"))
async def add_handler_query(client: "bot", query: "CallbackQuery") -> None:
    query_data = query.data.split("_")[1]
    entity_data = "User ID" if query_data == "admin" else "Chat ID"
    await query.message.edit_text(
        f"Send a {entity_data} to add {query_data.title()}\n\n<b>Timeout:</b> 45s",
        reply_markup=ikb(button.Cancel),
    )

    buttons = ikb(button.Admins_) if query_data == "admin" else ikb(button.Fsubs_)
    chat_id, user_id = query.message.chat.id, query.from_user.id

    try:
        listening = await client.listen(chat_id=chat_id, user_id=user_id, timeout=45)
        await listening.delete()
        new_id = int(listening.text)
    except ListenerStopped:
        await query.message.edit_text(
            "<b>Process has been cancelled!</b>", reply_markup=buttons
        )
        return
    except ListenerTimeout:
        await query.message.edit_text(
            "<b>Time limit exceeded! Process has been cancelled.</b>",
            reply_markup=buttons,
        )
        return
    except ValueError:
        await query.message.edit_text(
            f"<b>Invalid! Just send a {entity_data}.</b>", reply_markup=buttons
        )
        return

    list_ids = cache.admins if query_data == "admin" else cache.fs_chats
    if new_id in list_ids:
        await query.message.edit_text(
            f"<b>That's {entity_data} already added!</b>", reply_markup=buttons
        )
        return

    try:
        chat = await client.get_chat(new_id)
        if (query_data == "admin" and chat.type != ChatType.PRIVATE) or (
            query_data == "fsub"
            and chat.type not in [ChatType.SUPERGROUP, ChatType.CHANNEL]
        ):
            raise Exception
    except Exception:
        await query.message.edit_text(
            f"<b>That's {entity_data} isn't valid!</b>", reply_markup=buttons
        )
        return

    if query_data == "admin":
        await add_admin(new_id)
        logger.info("Bot Admins: Updating...")
        await cache.admins_init()
    else:
        await add_fs_chat(new_id)
        logger.info("Sub. Chats: Updating...")
        await cache.fs_chats_init()

    await query.message.edit_text(
        f"Added new {query_data.title()}: <code>{new_id}</code>",
        reply_markup=buttons,
    )


@Client.on_callback_query(filter_authorized & filters.regex(r"del_(admin|f-sub)"))
async def del_handler_query(client: "bot", query: "CallbackQuery") -> None:
    query_data = query.data.split("_")[1]
    entity_data = "User ID" if query_data == "admin" else "Chat ID"
    await query.message.edit_text(
        f"Send a {entity_data} to delete {query_data.title()}\n\n<b>Timeout:</b> 45s",
        reply_markup=ikb(button.Cancel),
    )

    buttons = ikb(button.Admins_) if query_data == "admin" else ikb(button.Fsubs_)
    chat_id, user_id = query.message.chat.id, query.from_user.id

    try:
        listening = await client.listen(chat_id=chat_id, user_id=user_id, timeout=45)
        await listening.delete()
        get_id = int(listening.text)
    except ListenerStopped:
        await query.message.edit_text(
            "<b>Process has been cancelled!</b>", reply_markup=buttons
        )
        return
    except ListenerTimeout:
        await query.message.edit_text(
            "<b>Time limit exceeded! Process has been cancelled.</b>",
            reply_markup=buttons,
        )
        return
    except ValueError:
        await query.message.edit_text(
            f"<b>Invalid! Just send a {entity_data}.</b>", reply_markup=buttons
        )
        return

    list_ids = cache.admins if query_data == "admin" else cache.fs_chats
    if get_id not in list_ids:
        await query.message.edit_text(
            f"<b>That's {entity_data} not found!</b>", reply_markup=buttons
        )
        return

    if query_data == "admin":
        if get_id == query.from_user.id:
            await query.message.edit_text(
                "<b>No rights! That's Yours.</b>", reply_markup=buttons
            )
            return

        await del_admin(get_id)
        logger.info("Bot Admins: Updating...")
        await cache.admins_init()
    else:
        await del_fs_chat(get_id)
        logger.info("Sub. Chats: Updating...")
        await cache.fs_chats_init()

    await query.message.edit_text(
        f"The {query_data.title()} has been deleted: <code>{get_id}</code>",
        reply_markup=buttons,
    )
