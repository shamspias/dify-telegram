from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class StopPollTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Stop a poll which was sent by the bot"""
        try:
            chat_id = tool_parameters.get("chat_id")
            message_id = tool_parameters.get("message_id")

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not message_id:
                yield self.create_text_message("❌ Error: message_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def stop():
                poll = await bot.stop_poll(chat_id=chat_id, message_id=message_id)
                return poll

            result = run_async(stop())

            if result:
                poll_data = {
                    "id": result.id,
                    "question": result.question,
                    "options": [{"text": opt.text, "voter_count": opt.voter_count} for opt in result.options],
                    "total_voter_count": result.total_voter_count,
                    "is_closed": result.is_closed
                }

                yield self.create_text_message(
                    f"✅ Poll stopped successfully!\n"
                    f"Chat ID: {chat_id}\n"
                    f"Message ID: {message_id}\n"
                    f"Total Votes: {result.total_voter_count}"
                )
                yield self.create_json_message(poll_data)
            else:
                yield self.create_text_message("❌ Failed to stop poll")

        except Exception as e:
            logger.error(f"Error stopping poll: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
