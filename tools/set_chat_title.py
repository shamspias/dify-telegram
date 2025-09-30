from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async
import logging

logger = logging.getLogger(__name__)


class SetChatTitleTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Set the title of a chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            title = tool_parameters.get("title")

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not title:
                yield self.create_text_message("❌ Error: title is required")
                return

            if len(title) < 1 or len(title) > 255:
                yield self.create_text_message("❌ Error: title must be 1-255 characters")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Set title
            async def set_title():
                result = await bot.set_chat_title(
                    chat_id=chat_id,
                    title=title
                )
                return result

            result = run_async(set_title())

            if result:
                yield self.create_text_message(
                    f"✅ Chat title updated successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"New Title: {title}"
                )

                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "title": title
                })
            else:
                yield self.create_text_message("❌ Failed to set chat title")

        except Exception as e:
            logger.error(f"Error setting chat title: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
