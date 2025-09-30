from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class ForwardMessageTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Forward a message from one chat to another
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            from_chat_id = tool_parameters.get("from_chat_id")
            message_id = tool_parameters.get("message_id")
            disable_notification = tool_parameters.get("disable_notification", False)
            protect_content = tool_parameters.get("protect_content", False)

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not from_chat_id:
                yield self.create_text_message("❌ Error: from_chat_id is required")
                return

            if not message_id:
                yield self.create_text_message("❌ Error: message_id is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Forward message
            async def forward():
                message = await bot.forward_message(
                    chat_id=chat_id,
                    from_chat_id=from_chat_id,
                    message_id=message_id,
                    disable_notification=disable_notification,
                    protect_content=protect_content
                )
                return message

            result = run_async(forward())

            if result:
                # Format response
                message_data = format_message_result(result)

                yield self.create_text_message(
                    f"✅ Message forwarded successfully!\n"
                    f"New Message ID: {message_data.get('message_id')}\n"
                    f"To Chat: {message_data.get('chat_id')}\n"
                    f"From Chat: {from_chat_id}\n"
                    f"Original Message ID: {message_id}"
                )

                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to forward message")

        except Exception as e:
            logger.error(f"Error forwarding message: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
