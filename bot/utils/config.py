import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv("config.env")  # take environment variables from config.env


class Config:
    """
    Configuration class that reads environment variables to set various settings.
    """

    def __init__(self):
        self.OWNER_ID = self._get_int_env("OWNER_ID")
        self.API_ID = self._get_int_env("API_ID")
        self.API_HASH: str = os.environ.get("API_HASH", None)
        self.BOT_TOKEN: str = os.environ.get("BOT_TOKEN", None)
        self.MONGODB_URL: str = os.environ.get("MONGODB_URL", None)
        self.DATABASE_CHAT_ID = self._get_int_env("DATABASE_CHAT_ID")
        self.OWNER_USERNAME: str = os.environ.get("OWNER_USERNAME", "@BotFather")

        # Perform validation
        self._validate_required_vars()
        self.BOT_ID = self._parse_bot_id(self.BOT_TOKEN)

    def _get_int_env(self, key: str) -> Optional[int]:
        """
        Helper method to get an environment variable as an integer.
        """
        value = os.environ.get(key, None)
        if value is not None:
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"{key}: Invalid")
        return None

    def _parse_bot_id(self, bot_token: str) -> Optional[str]:
        """
        Helper method to parse the bot ID from the BOT_TOKEN.
        """
        if bot_token and ":" in bot_token:
            return bot_token.split(":", 1)[0]
        return None

    def _validate_required_vars(self):
        """
        Validate that all required environment variables are present.
        """
        required_vars = {
            "BOT_TOKEN": self.BOT_TOKEN,
            "MONGODB_URL": self.MONGODB_URL,
            "API_HASH": self.API_HASH,
            "OWNER_ID": self.OWNER_ID,
            "API_ID": self.API_ID,
            "DATABASE_CHAT_ID": self.DATABASE_CHAT_ID,
        }
        for var_name, value in required_vars.items():
            if value is None:
                raise ValueError(f"{var_name}: Missed")


config: Config = Config()
