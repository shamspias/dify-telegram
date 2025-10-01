from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class UnbanChatMemberTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Unban a previously banned user in a supergroup or channel"""
        try:
            chat_id = tool_parameters.get("chat_id")
            user_id = tool_parameters.get("user_id")
            only_if_banned = tool_parameters.get("only_if_banned", True)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not user_id:
                yield self.create_text_message("❌ Error: user_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def unban():
                result = await bot.unban_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    only_if_banned=only_if_banned
                )
                return result

            result = run_async(unban())

            if result:
                yield self.create_text_message(
                    f"✅ User unbanned successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"User ID: {user_id}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "user_id": user_id
                })
            else:
                yield self.create_text_message("❌ Failed to unban user")

        except Exception as e:
            logger.error(f"Error unbanning user: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
