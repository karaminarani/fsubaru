from hydrogram import Client
from hydrogram.enums import ParseMode
from hydrogram.errors import RPCError
from hydrogram.types import BotCommand, BotCommandScopeAllPrivateChats

from bot.utils import config, logger

from .exception import BotError
from .mongo import database


class Bot(Client):
    """
    A class representing the Telegram bot.

    Methods:
        start() -> None:
            Starts the bot and connects to MongoDB.

        stop() -> None:
            Stops the bot and closes the MongoDB connection.

        bot_commands_setup() -> None:
            Sets up bot commands for users.
    """

    def __init__(self) -> None:
        """
        Initializes the Bot instance with required configurations.
        """
        super().__init__(
            name=str(config.BOT_ID),
            api_id=int(config.API_ID),
            api_hash=str(config.API_HASH),
            bot_token=str(config.BOT_TOKEN),
            workdir="sessions",
            plugins={"root": "plugins"},
        )

    async def start(self) -> None:
        """
        Starts the bot, connecting to MongoDB and setting up commands.
        """
        logger.info("MongoDB: Connecting...")
        await database.connect()

        logger.info("Bot: Starting...")
        try:
            await super().start()
            logger.info("Bot: Started")
        except RPCError as rpc:
            raise BotError(str(rpc.MESSAGE))

        await self.bot_commands_setup()
        self.set_parse_mode(ParseMode.HTML)

    async def stop(self) -> None:
        """
        Stops the bot and closes the MongoDB connection.
        """
        logger.info("Bot: Stopping...")
        try:
            await super().stop()
        except Exception as exc:
            logger.error(str(exc))
        else:
            logger.info("Bot: Stopped")

        logger.info("MongoDB: Closing...")
        await database.close()

    async def bot_commands_setup(self) -> None:
        """
        Sets up the bot commands for user interaction.
        """
        await self.delete_bot_commands()
        try:
            await self.set_bot_commands(
                commands=[
                    BotCommand("start", "Start Bot"),
                    BotCommand("ping", "Server Latency"),
                    BotCommand("uptime", "Bot Uptime"),
                    BotCommand("privacy", "Privacy Policy"),
                    BotCommand("restart", "Restart Bot (Admin)"),
                ],
                scope=BotCommandScopeAllPrivateChats(),
            )
        except RPCError:
            pass


# Instantiate the bot
bot: Bot = Bot()
