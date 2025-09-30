from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging
import os

logger = logging.getLogger(__name__)


class SendStickerTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Send a sticker to a Telegram chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            sticker = tool_parameters.get("sticker")
            emoji = tool_parameters.get("emoji")

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not sticker:
                yield self.create_text_message("❌ Error: sticker is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Send sticker
            async def send():
                kwargs = {
                    "chat_id": chat_id
                }

                if emoji:
                    kwargs["emoji"] = emoji

                # Check if sticker is a URL
                if sticker.startswith('http://') or sticker.startswith('https://'):
                    kwargs["sticker"] = sticker
                    message = await bot.send_sticker(**kwargs)
                # Check if it's a local file
                elif os.path.isfile(sticker):
                    with open(sticker, 'rb') as sticker_file:
                        kwargs["sticker"] = sticker_file
                        message = await bot.send_sticker(**kwargs)
                else:
                    # Assume it's a file_id
                    kwargs["sticker"] = sticker
                    message = await bot.send_sticker(**kwargs)

                return message

            result = run_async(send())

            if result:
                # Format response
                message_data = format_message_result(result)

                # Add sticker-specific info
                if result.sticker:
                    stick = result.sticker
                    message_data["sticker"] = {
                        "file_id": stick.file_id,
                        "file_unique_id": stick.file_unique_id,
                        "type": stick.type,
                        "width": stick.width,
                        "height": stick.height,
                        "is_animated": stick.is_animated,
                        "is_video": stick.is_video,
                        "emoji": stick.emoji,
                        "file_size": stick.file_size
                    }

                sticker_type = "Animated" if result.sticker.is_animated else (
                    "Video" if result.sticker.is_video else "Static")
                yield self.create_text_message(
                    f"✅ {sticker_type} sticker sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}\n"
                    f"Emoji: {result.sticker.emoji if result.sticker.emoji else 'N/A'}"
                )

                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send sticker")

        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            yield self.create_text_message(f"❌ Error: Sticker file not found - {sticker}")
        except Exception as e:
            logger.error(f"Error sending sticker: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
