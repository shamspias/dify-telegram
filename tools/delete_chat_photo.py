from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class DeleteChatPhotoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Delete a chat photo"""
        try:
            chat_id = tool_parameters.get("chat_id")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def delete():
                result = await bot.delete_chat_photo(chat_id=chat_id)
                return result

            result = run_async(delete())

            if result:
                yield self.create_text_message(
                    f"✅ Chat photo deleted successfully!\n"
                    f"Chat ID: {chat_id}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id
                })
            else:
                yield self.create_text_message("❌ Failed to delete chat photo")

        except Exception as e:
            logger.error(f"Error deleting chat photo: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
