from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async
import logging

logger = logging.getLogger(__name__)


class PinChatMessageTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Pin a message in a chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            message_id = tool_parameters.get("message_id")
            disable_notification = tool_parameters.get("disable_notification", False)

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not message_id:
                yield self.create_text_message("❌ Error: message_id is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Pin message
            async def pin():
                result = await bot.pin_chat_message(
                    chat_id=chat_id,
                    message_id=message_id,
                    disable_notification=disable_notification
                )
                return result

            result = run_async(pin())

            if result:
                notification_status = "silently" if disable_notification else "with notification"

                yield self.create_text_message(
                    f"✅ Message pinned {notification_status}!\n"
                    f"Chat ID: {chat_id}\n"
                    f"Message ID: {message_id}"
                )

                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "silent": disable_notification
                })
            else:
                yield self.create_text_message("❌ Failed to pin message")

        except Exception as e:
            logger.error(f"Error pinning message: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
