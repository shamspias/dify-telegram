from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendMessageTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Send a text message to a Telegram chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            text = tool_parameters.get("text")
            parse_mode = tool_parameters.get("parse_mode") or None
            disable_web_page_preview = tool_parameters.get("disable_web_page_preview", False)
            disable_notification = tool_parameters.get("disable_notification", False)
            reply_to_message_id = tool_parameters.get("reply_to_message_id")

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not text:
                yield self.create_text_message("❌ Error: text is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Send message
            async def send():
                message = await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview,
                    disable_notification=disable_notification,
                    reply_to_message_id=reply_to_message_id
                )
                return message

            result = run_async(send())

            if result:
                # Format response
                message_data = format_message_result(result)

                yield self.create_text_message(
                    f"✅ Message sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}"
                )

                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send message")

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
