from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendMediaGroupTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Send a group of photos or videos as an album"""
        try:
            import json
            from telegram import InputMediaPhoto, InputMediaVideo

            chat_id = tool_parameters.get("chat_id")
            media = tool_parameters.get("media")
            disable_notification = tool_parameters.get("disable_notification", False)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not media:
                yield self.create_text_message("❌ Error: media is required")
                return

            # Parse media if string
            if isinstance(media, str):
                try:
                    media_list = json.loads(media)
                except:
                    yield self.create_text_message("❌ Error: media must be valid JSON array")
                    return
            else:
                media_list = media

            if len(media_list) < 2 or len(media_list) > 10:
                yield self.create_text_message("❌ Error: media group must have 2-10 items")
                return

            bot = get_bot(self.runtime.credentials)

            async def send():
                # Convert to InputMedia objects
                input_media = []
                for item in media_list:
                    media_type = item.get("type", "photo")
                    media_url = item.get("media")
                    caption = item.get("caption")

                    if media_type == "photo":
                        input_media.append(InputMediaPhoto(media=media_url, caption=caption))
                    elif media_type == "video":
                        input_media.append(InputMediaVideo(media=media_url, caption=caption))

                messages = await bot.send_media_group(
                    chat_id=chat_id,
                    media=input_media,
                    disable_notification=disable_notification
                )
                return messages

            result = run_async(send())

            if result:
                message_ids = [msg.message_id for msg in result]

                yield self.create_text_message(
                    f"✅ Media group sent successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"Items: {len(result)}\n"
                    f"Message IDs: {', '.join(map(str, message_ids))}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "message_ids": message_ids,
                    "count": len(result)
                })
            else:
                yield self.create_text_message("❌ Failed to send media group")

        except Exception as e:
            logger.error(f"Error sending media group: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
