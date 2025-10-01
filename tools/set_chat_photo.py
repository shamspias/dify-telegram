from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SetChatPhotoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Set a new profile photo for the chat"""
        try:
            import os

            chat_id = tool_parameters.get("chat_id")
            photo = tool_parameters.get("photo")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not photo:
                yield self.create_text_message("❌ Error: photo is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def set_photo():
                if os.path.isfile(photo):
                    with open(photo, 'rb') as photo_file:
                        result = await bot.set_chat_photo(chat_id=chat_id, photo=photo_file)
                else:
                    result = await bot.set_chat_photo(chat_id=chat_id, photo=photo)
                return result

            result = run_async(set_photo())

            if result:
                yield self.create_text_message(
                    f"✅ Chat photo updated successfully!\n"
                    f"Chat ID: {chat_id}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id
                })
            else:
                yield self.create_text_message("❌ Failed to set chat photo")

        except Exception as e:
            logger.error(f"Error setting chat photo: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
