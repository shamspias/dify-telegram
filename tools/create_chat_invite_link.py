from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class CreateChatInviteLinkTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Create an additional invite link for a chat"""
        try:
            chat_id = tool_parameters.get("chat_id")
            name = tool_parameters.get("name")
            expire_date = tool_parameters.get("expire_date")
            member_limit = tool_parameters.get("member_limit")
            creates_join_request = tool_parameters.get("creates_join_request", False)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def create():
                kwargs = {"chat_id": chat_id}
                if name:
                    kwargs["name"] = name
                if expire_date:
                    kwargs["expire_date"] = expire_date
                if member_limit:
                    kwargs["member_limit"] = member_limit
                if creates_join_request:
                    kwargs["creates_join_request"] = creates_join_request

                link = await bot.create_chat_invite_link(**kwargs)
                return link

            result = run_async(create())

            if result:
                yield self.create_text_message(
                    f"✅ Invite link created successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"Link: {result.invite_link}\n"
                    f"Name: {result.name or 'N/A'}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "invite_link": result.invite_link,
                    "name": result.name,
                    "expire_date": result.expire_date.isoformat() if result.expire_date else None,
                    "member_limit": result.member_limit
                })
            else:
                yield self.create_text_message("❌ Failed to create invite link")

        except Exception as e:
            logger.error(f"Error creating invite link: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
