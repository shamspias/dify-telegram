from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendDiceTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Send a dice, darts, basketball, football, bowling, or slot machine"""
        try:
            chat_id = tool_parameters.get("chat_id")
            emoji = tool_parameters.get("emoji", "🎲")
            disable_notification = tool_parameters.get("disable_notification", False)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def send():
                message = await bot.send_dice(
                    chat_id=chat_id,
                    emoji=emoji,
                    disable_notification=disable_notification
                )
                return message

            result = run_async(send())

            if result:
                message_data = format_message_result(result)
                if result.dice:
                    message_data["dice"] = {
                        "emoji": result.dice.emoji,
                        "value": result.dice.value
                    }

                yield self.create_text_message(
                    f"✅ Dice sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Emoji: {emoji}\n"
                    f"Value: {result.dice.value if result.dice else 'N/A'}"
                )
                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send dice")

        except Exception as e:
            logger.error(f"Error sending dice: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
