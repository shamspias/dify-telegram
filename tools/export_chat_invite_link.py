from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class ExportChatInviteLinkTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Generate a new primary invite link for a chat"""
        try:
            chat_id = tool_parameters.get("chat_id")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def export():
                link = await bot.export_chat_invite_link(chat_id=chat_id)
                return link

            result = run_async(export())

            if result:
                yield self.create_text_message(
                    f"✅ Invite link generated successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"Link: {result}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "invite_link": result
                })
            else:
                yield self.create_text_message("❌ Failed to generate invite link")

        except Exception as e:
            logger.error(f"Error exporting invite link: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
