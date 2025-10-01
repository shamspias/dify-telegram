from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendChatActionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Send chat action (typing, uploading, etc.)"""
        try:
            chat_id = tool_parameters.get("chat_id")
            action = tool_parameters.get("action")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not action:
                yield self.create_text_message("❌ Error: action is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def send():
                result = await bot.send_chat_action(chat_id=chat_id, action=action)
                return result

            result = run_async(send())

            if result:
                yield self.create_text_message(
                    f"✅ Chat action sent successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"Action: {action}"
                )
                yield self.create_json_message({
                    "success": True,
                    "chat_id": chat_id,
                    "action": action
                })
            else:
                yield self.create_text_message("❌ Failed to send chat action")

        except Exception as e:
            logger.error(f"Error sending chat action: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
