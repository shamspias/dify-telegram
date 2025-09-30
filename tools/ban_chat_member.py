from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async
import logging

logger = logging.getLogger(__name__)


class BanChatMemberTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Ban a user from a chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            user_id = tool_parameters.get("user_id")
            until_date = tool_parameters.get("until_date")
            revoke_messages = tool_parameters.get("revoke_messages", False)

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not user_id:
                yield self.create_text_message("❌ Error: user_id is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Ban member
            async def ban():
                result = await bot.ban_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    until_date=until_date,
                    revoke_messages=revoke_messages
                )
                return result

            result = run_async(ban())

            if result:
                ban_type = "permanently" if not until_date else f"until {until_date}"
                messages_action = " (all messages deleted)" if revoke_messages else ""

                yield self.create_text_message(
                    f"✅ User banned successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"User ID: {user_id}\n"
                    f"Ban type: {ban_type}{messages_action}"
                )

                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "until_date": until_date,
                    "revoke_messages": revoke_messages
                })
            else:
                yield self.create_text_message("❌ Failed to ban user")

        except Exception as e:
            logger.error(f"Error banning user: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
