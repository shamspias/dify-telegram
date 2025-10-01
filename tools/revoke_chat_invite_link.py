from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class RevokeChatInviteLinkTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Revoke an invite link created by the bot"""
        try:
            chat_id = tool_parameters.get("chat_id")
            invite_link = tool_parameters.get("invite_link")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not invite_link:
                yield self.create_text_message("❌ Error: invite_link is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def revoke():
                link = await bot.revoke_chat_invite_link(
                    chat_id=chat_id,
                    invite_link=invite_link
                )
                return link

            result = run_async(revoke())

            if result:
                yield self.create_text_message(
                    f"✅ Invite link revoked successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"Revoked Link: {result.invite_link}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "invite_link": result.invite_link,
                    "is_revoked": result.is_revoked
                })
            else:
                yield self.create_text_message("❌ Failed to revoke invite link")

        except Exception as e:
            logger.error(f"Error revoking invite link: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
