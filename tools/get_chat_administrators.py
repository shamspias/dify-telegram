from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_user_result
import logging

logger = logging.getLogger(__name__)


class GetChatAdministratorsTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get a list of administrators in a chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Get administrators
            async def get_admins():
                admins = await bot.get_chat_administrators(chat_id=chat_id)
                return admins

            result = run_async(get_admins())

            if result:
                # Format response
                admin_list = []
                for admin in result:
                    admin_data = format_user_result(admin.user)
                    admin_data['status'] = admin.status

                    # Add additional info based on status
                    if hasattr(admin, 'custom_title') and admin.custom_title:
                        admin_data['custom_title'] = admin.custom_title

                    if hasattr(admin, 'is_anonymous'):
                        admin_data['is_anonymous'] = admin.is_anonymous

                    # Add permissions for administrators
                    if admin.status == 'administrator':
                        admin_data['permissions'] = {
                            'can_manage_chat': getattr(admin, 'can_manage_chat', False),
                            'can_delete_messages': getattr(admin, 'can_delete_messages', False),
                            'can_manage_video_chats': getattr(admin, 'can_manage_video_chats', False),
                            'can_restrict_members': getattr(admin, 'can_restrict_members', False),
                            'can_promote_members': getattr(admin, 'can_promote_members', False),
                            'can_change_info': getattr(admin, 'can_change_info', False),
                            'can_invite_users': getattr(admin, 'can_invite_users', False),
                            'can_pin_messages': getattr(admin, 'can_pin_messages', False),
                            'can_post_messages': getattr(admin, 'can_post_messages', False),
                            'can_edit_messages': getattr(admin, 'can_edit_messages', False)
                        }

                    admin_list.append(admin_data)

                # Create readable output
                output = [
                    f"✅ Chat Administrators ({len(admin_list)}):",
                    ""
                ]

                for i, admin in enumerate(admin_list, 1):
                    status_emoji = {
                        'creator': '👑',
                        'administrator': '⭐',
                        'member': '👤'
                    }.get(admin['status'], '👤')

                    name = admin.get('first_name', '')
                    if admin.get('last_name'):
                        name += f" {admin['last_name']}"
                    username = f"@{admin['username']}" if admin.get('username') else ''
                    custom_title = admin.get('custom_title', '')

                    line = f"{i}. {status_emoji} {name} {username}"
                    if custom_title:
                        line += f" ({custom_title})"
                    output.append(line)

                yield self.create_text_message("\n".join(output))
                yield self.create_json_message({
                    "total_administrators": len(admin_list),
                    "administrators": admin_list
                })
            else:
                yield self.create_text_message("❌ Failed to get administrators")

        except Exception as e:
            logger.error(f"Error getting administrators: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
