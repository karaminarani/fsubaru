import base64
from typing import List, Optional, Union

import aiofiles

from .config import config


class URLSafe:
    @staticmethod
    def add_padding(data_string: str) -> str:
        """
        Adds padding to the data string to make its length a multiple of 4.

        Args:
            data_string (str): The data string to which padding will be added.

        Returns:
            str: The padded data string.
        """
        return data_string + "=" * (-len(data_string) % 4)

    @staticmethod
    def del_padding(data_string: str) -> str:
        """
        Removes padding from the data string.

        Args:
            data_string (str): The data string from which padding will be removed.

        Returns:
            str: The data string without padding.
        """
        return data_string.rstrip("=")

    def encode_data(self, data: str) -> str:
        """
        Encodes a string into a URL-safe base64 string.

        Args:
            data (str): The string to encode.

        Returns:
            str: The URL-safe base64 encoded string.
        """
        data_bytes = data.encode("utf-8")
        encoded_data = base64.urlsafe_b64encode(data_bytes)
        return self.del_padding(encoded_data.decode("utf-8"))

    def decode_data(self, data_string: str) -> Optional[str]:
        """
        Decodes a URL-safe base64 string back into the original string.

        Args:
            data_string (str): The URL-safe base64 string to decode.

        Returns:
            Optional[str]: The decoded string, or None if decoding fails.
        """
        try:
            data_padding = self.add_padding(data_string)
            encoded_data = base64.urlsafe_b64decode(data_padding)
            return encoded_data.decode("utf-8")
        except (base64.binascii.Error, UnicodeDecodeError):
            return None


url_safe: URLSafe = URLSafe()


async def aiofiles_read(path: str) -> str:
    """
    Reads the content of a file asynchronously.

    Args:
        path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    async with aiofiles.open(path, mode="r") as doc:
        content = await doc.read()

    return content


def decode_data(encoded_data: str) -> Union[List[int], range]:
    """
    Decodes the given encoded data into a list of IDs or a range of IDs.

    Args:
        encoded_data (str): The encoded data to decode.

    Returns:
        Union[List[int], range]: A list of IDs or a range of IDs.
    """
    database_chat_id = config.DATABASE_CHAT_ID
    decoded_data = url_safe.decode_data(encoded_data).split("-")
    if len(decoded_data) == 2:
        return [int(int(decoded_data[1]) / abs(database_chat_id))]

    elif len(decoded_data) == 3:
        start_id = int(int(decoded_data[1]) / abs(database_chat_id))
        end_id = int(int(decoded_data[2]) / abs(database_chat_id))
        if start_id < end_id:
            return range(start_id, end_id + 1)
        else:
            return range(start_id, end_id - 1, -1)
