from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class PromoteChatMemberTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Promote or demote a user in a supergroup or channel"""
        try:
            chat_id = tool_parameters.get("chat_id")
            user_id = tool_parameters.get("user_id")
            is_anonymous = tool_parameters.get("is_anonymous", False)
            can_manage_chat = tool_parameters.get("can_manage_chat", False)
            can_delete_messages = tool_parameters.get("can_delete_messages", False)
            can_manage_video_chats = tool_parameters.get("can_manage_video_chats", False)
            can_restrict_members = tool_parameters.get("can_restrict_members", False)
            can_promote_members = tool_parameters.get("can_promote_members", False)
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

            async def promote():
                result = await bot.promote_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    is_anonymous=is_anonymous,
                    can_manage_chat=can_manage_chat,
                    can_delete_messages=can_delete_messages,
                    can_manage_video_chats=can_manage_video_chats,
                    can_restrict_members=can_restrict_members,
                    can_promote_members=can_promote_members,
                    can_change_info=can_change_info,
                    can_invite_users=can_invite_users,
                    can_pin_messages=can_pin_messages
                )
                return result

            result = run_async(promote())

            if result:
                yield self.create_text_message(
                    f"✅ User promoted successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"User ID: {user_id}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "user_id": user_id
                })
            else:
                yield self.create_text_message("❌ Failed to promote user")

        except Exception as e:
            logger.error(f"Error promoting user: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
