from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_user_result
import logging

logger = logging.getLogger(__name__)


class GetChatMemberTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Get information about a member of a chat"""
        try:
            chat_id = tool_parameters.get("chat_id")
            user_id = tool_parameters.get("user_id")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not user_id:
                yield self.create_text_message("❌ Error: user_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def get_member():
                member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
                return member

            result = run_async(get_member())

            if result:
                user_data = format_user_result(result.user)
                member_data = {
                    "user": user_data,
                    "status": result.status,
                    "until_date": result.until_date.isoformat() if result.until_date else None
                }

                if result.status == 'administrator':
                    member_data["permissions"] = {
                        "can_manage_chat": getattr(result, 'can_manage_chat', False),
                        "can_delete_messages": getattr(result, 'can_delete_messages', False),
                        "can_manage_video_chats": getattr(result, 'can_manage_video_chats', False),
                        "can_restrict_members": getattr(result, 'can_restrict_members', False),
                        "can_promote_members": getattr(result, 'can_promote_members', False),
                        "can_change_info": getattr(result, 'can_change_info', False),
                        "can_invite_users": getattr(result, 'can_invite_users', False),
                        "can_pin_messages": getattr(result, 'can_pin_messages', False)
                    }

                status_emoji = {
                    'creator': '👑',
                    'administrator': '⭐',
                    'member': '👤',
                    'restricted': '🚫',
                    'left': '👋',
                    'kicked': '⛔'
                }.get(result.status, '👤')

                yield self.create_text_message(
                    f"✅ Member Information:\n"
                    f"{status_emoji} Status: {result.status}\n"
                    f"User: {user_data.get('first_name', '')} {user_data.get('last_name', '')}\n"
                    f"Username: @{user_data.get('username', 'N/A')}\n"
                    f"User ID: {user_id}"
                )
                yield self.create_json_message(member_data)
            else:
                yield self.create_text_message("❌ Failed to get member info")

        except Exception as e:
            logger.error(f"Error getting chat member: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
