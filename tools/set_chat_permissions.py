from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SetChatPermissionsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Set default chat permissions for all members"""
        try:
            from telegram import ChatPermissions

            chat_id = tool_parameters.get("chat_id")
            can_send_messages = tool_parameters.get("can_send_messages", True)
            can_send_media_messages = tool_parameters.get("can_send_media_messages", True)
            can_send_polls = tool_parameters.get("can_send_polls", True)
            can_send_other_messages = tool_parameters.get("can_send_other_messages", True)
            can_add_web_page_previews = tool_parameters.get("can_add_web_page_previews", True)
            can_change_info = tool_parameters.get("can_change_info", False)
            can_invite_users = tool_parameters.get("can_invite_users", True)
            can_pin_messages = tool_parameters.get("can_pin_messages", False)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def set_perms():
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
                result = await bot.set_chat_permissions(
                    chat_id=chat_id,
                    permissions=permissions
                )
                return result

            result = run_async(set_perms())

            if result:
                yield self.create_text_message(
                    f"✅ Chat permissions updated successfully!\n"
                    f"Chat ID: {chat_id}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "permissions": {
                        "can_send_messages": can_send_messages,
                        "can_send_media_messages": can_send_media_messages,
                        "can_send_polls": can_send_polls,
                        "can_invite_users": can_invite_users
                    }
                })
            else:
                yield self.create_text_message("❌ Failed to set permissions")

        except Exception as e:
            logger.error(f"Error setting permissions: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
