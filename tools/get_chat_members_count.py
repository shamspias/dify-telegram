from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class GetChatMembersCountTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Get the number of members in a chat"""
        try:
            chat_id = tool_parameters.get("chat_id")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def get_count():
                count = await bot.get_chat_member_count(chat_id=chat_id)
                return count

            result = run_async(get_count())

            if result is not None:
                yield self.create_text_message(
                    f"✅ Chat Members Count:\n"
                    f"Chat ID: {chat_id}\n"
                    f"Members: {result:,}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "members_count": result
                })
            else:
                yield self.create_text_message("❌ Failed to get members count")

        except Exception as e:
            logger.error(f"Error getting members count: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
