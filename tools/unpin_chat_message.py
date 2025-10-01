from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class UnpinChatMessageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Remove a message from the list of pinned messages"""
        try:
            chat_id = tool_parameters.get("chat_id")
            message_id = tool_parameters.get("message_id")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def unpin():
                result = await bot.unpin_chat_message(
                    chat_id=chat_id,
                    message_id=message_id
                )
                return result

            result = run_async(unpin())

            if result:
                yield self.create_text_message(
                    f"✅ Message unpinned successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"Message ID: {message_id or 'most recent'}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "message_id": message_id
                })
            else:
                yield self.create_text_message("❌ Failed to unpin message")

        except Exception as e:
            logger.error(f"Error unpinning message: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
