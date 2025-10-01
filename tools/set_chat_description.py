from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SetChatDescriptionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Change the description of a group, supergroup or channel"""
        try:
            chat_id = tool_parameters.get("chat_id")
            description = tool_parameters.get("description")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def set_desc():
                result = await bot.set_chat_description(
                    chat_id=chat_id,
                    description=description or ""
                )
                return result

            result = run_async(set_desc())

            if result:
                yield self.create_text_message(
                    f"✅ Chat description updated successfully!\n"
                    f"Chat ID: {chat_id}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "description": description
                })
            else:
                yield self.create_text_message("❌ Failed to set chat description")

        except Exception as e:
            logger.error(f"Error setting chat description: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
