from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class EditMessageCaptionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Edit caption of a message"""
        try:
            chat_id = tool_parameters.get("chat_id")
            message_id = tool_parameters.get("message_id")
            caption = tool_parameters.get("caption")
            parse_mode = tool_parameters.get("parse_mode") or None

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not message_id:
                yield self.create_text_message("❌ Error: message_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def edit():
                message = await bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=caption,
                    parse_mode=parse_mode
                )
                return message

            result = run_async(edit())

            if result:
                message_data = format_message_result(result)
                yield self.create_text_message(
                    f"✅ Caption edited successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}"
                )
                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to edit caption")

        except Exception as e:
            logger.error(f"Error editing caption: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
