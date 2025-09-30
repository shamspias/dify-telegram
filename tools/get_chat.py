from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_chat_result
import logging

logger = logging.getLogger(__name__)


class GetChatTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get information about a Telegram chat
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

            # Get chat info
            async def get_info():
                chat = await bot.get_chat(chat_id=chat_id)
                # Also get member count if it's a group/channel
                members_count = None
                if chat.type in ['group', 'supergroup', 'channel']:
                    try:
                        members_count = await bot.get_chat_member_count(chat_id=chat_id)
                    except:
                        pass
                return chat, members_count

            chat, members_count = run_async(get_info())

            if chat:
                # Format response
                chat_data = format_chat_result(chat)
                if members_count:
                    chat_data['members_count'] = members_count

                # Create readable output
                chat_type_names = {
                    'private': 'Private Chat',
                    'group': 'Group',
                    'supergroup': 'Supergroup',
                    'channel': 'Channel'
                }

                output = [
                    "✅ Chat Information:",
                    f"ID: {chat_data.get('id')}",
                    f"Type: {chat_type_names.get(chat_data.get('type'), chat_data.get('type'))}",
                ]

                if chat_data.get('title'):
                    output.append(f"Title: {chat_data.get('title')}")
                if chat_data.get('username'):
                    output.append(f"Username: @{chat_data.get('username')}")
                if chat_data.get('first_name'):
                    output.append(f"First Name: {chat_data.get('first_name')}")
                if chat_data.get('last_name'):
                    output.append(f"Last Name: {chat_data.get('last_name')}")
                if chat_data.get('description'):
                    output.append(f"Description: {chat_data.get('description')}")
                if chat_data.get('members_count'):
                    output.append(f"Members: {chat_data.get('members_count')}")
                if chat_data.get('invite_link'):
                    output.append(f"Invite Link: {chat_data.get('invite_link')}")

                yield self.create_text_message("\n".join(output))
                yield self.create_json_message(chat_data)
            else:
                yield self.create_text_message("❌ Failed to get chat information")

        except Exception as e:
            logger.error(f"Error getting chat info: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
