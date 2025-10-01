from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class RestrictChatMemberTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Restrict a user in a supergroup"""
        try:
            from telegram import ChatPermissions

            chat_id = tool_parameters.get("chat_id")
            user_id = tool_parameters.get("user_id")
            until_date = tool_parameters.get("until_date")
            can_send_messages = tool_parameters.get("can_send_messages", False)
            can_send_media_messages = tool_parameters.get("can_send_media_messages", False)
            can_send_polls = tool_parameters.get("can_send_polls", False)
            can_send_other_messages = tool_parameters.get("can_send_other_messages", False)
            can_add_web_page_previews = tool_parameters.get("can_add_web_page_previews", False)
            can_change_info = tool_parameters.get("can_change_info", False)
            can_invite_users = tool_parameters.get("can_invite_users", False)
            can_pin_messages = tool_parameters.get("can_pin_messages", False)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not user_id:
                yield self.create_text_message("❌ Error: user_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def restrict():
                permissions = ChatPermissions(
                    can_send_messages=can_send_messages,
                    can_send_media_messages=can_send_media_messages,
                    can_send_polls=can_send_polls,
                    can_send_other_messages=can_send_other_messages,
                    can_add_web_page_previews=can_add_web_page_previews,
                    can_change_info=can_change_info,
                    can_invite_users=can_invite_users,
                    can_pin_messages=can_pin_messages
                )
                result = await bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    permissions=permissions,
                    until_date=until_date
                )
                return result

            result = run_async(restrict())

            if result:
                yield self.create_text_message(
                    f"✅ User restricted successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"User ID: {user_id}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "permissions": {
                        "can_send_messages": can_send_messages,
                        "can_send_media_messages": can_send_media_messages,
                        "can_send_polls": can_send_polls
                    }
                })
            else:
                yield self.create_text_message("❌ Failed to restrict user")

        except Exception as e:
            logger.error(f"Error restricting user: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
