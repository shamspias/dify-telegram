from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async
import logging

logger = logging.getLogger(__name__)


class DeleteMessageTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Delete a message from a chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            message_id = tool_parameters.get("message_id")

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not message_id:
                yield self.create_text_message("❌ Error: message_id is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Delete message
            async def delete():
                result = await bot.delete_message(
                    chat_id=chat_id,
                    message_id=message_id
                )
                return result

            result = run_async(delete())

            if result:
                yield self.create_text_message(
                    f"✅ Message deleted successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"Message ID: {message_id}"
                )

                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "message_id": message_id
                })
            else:
                yield self.create_text_message("❌ Failed to delete message")

        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
