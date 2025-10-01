from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class UnpinAllChatMessagesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Clear the list of pinned messages in a chat"""
        try:
            chat_id = tool_parameters.get("chat_id")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def unpin_all():
                result = await bot.unpin_all_chat_messages(chat_id=chat_id)
                return result

            result = run_async(unpin_all())

            if result:
                yield self.create_text_message(
                    f"✅ All messages unpinned successfully!\n"
                    f"Chat ID: {chat_id}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id
                })
            else:
                yield self.create_text_message("❌ Failed to unpin all messages")

        except Exception as e:
            logger.error(f"Error unpinning all messages: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
