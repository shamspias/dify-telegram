from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendPhotoTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Send a photo to a Telegram chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            photo = tool_parameters.get("photo")
            caption = tool_parameters.get("caption")
            parse_mode = tool_parameters.get("parse_mode") or None
            disable_notification = tool_parameters.get("disable_notification", False)

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not photo:
                yield self.create_text_message("❌ Error: photo is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Send photo
            async def send():
                # Check if photo is a URL or file_id
                if photo.startswith('http://') or photo.startswith('https://'):
                    # Send from URL
                    message = await bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=caption,
                        parse_mode=parse_mode,
                        disable_notification=disable_notification
                    )
                else:
                    # Assume it's a file_id or local file path
                    try:
                        with open(photo, 'rb') as photo_file:
                            message = await bot.send_photo(
                                chat_id=chat_id,
                                photo=photo_file,
                                caption=caption,
                                parse_mode=parse_mode,
                                disable_notification=disable_notification
                            )
                    except FileNotFoundError:
                        # Treat as file_id
                        message = await bot.send_photo(
                            chat_id=chat_id,
                            photo=photo,
                            caption=caption,
                            parse_mode=parse_mode,
                            disable_notification=disable_notification
                        )
                return message

            result = run_async(send())

            if result:
                # Format response
                message_data = format_message_result(result)

                # Add photo-specific info
                if result.photo:
                    photo_sizes = [
                        {
                            "file_id": p.file_id,
                            "width": p.width,
                            "height": p.height,
                            "file_size": p.file_size
                        }
                        for p in result.photo
                    ]
                    message_data["photo_sizes"] = photo_sizes

                yield self.create_text_message(
                    f"✅ Photo sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}"
                )

                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send photo")

        except Exception as e:
            logger.error(f"Error sending photo: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
