from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async
import logging

logger = logging.getLogger(__name__)


class AnswerCallbackQueryTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Answer a callback query from an inline keyboard button
        """
        try:
            # Get parameters
            callback_query_id = tool_parameters.get("callback_query_id")
            text = tool_parameters.get("text")
            show_alert = tool_parameters.get("show_alert", False)
            url = tool_parameters.get("url")
            cache_time = tool_parameters.get("cache_time", 0)

            # Validate inputs
            if not callback_query_id:
                yield self.create_text_message("❌ Error: callback_query_id is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Answer callback query
            async def answer():
                result = await bot.answer_callback_query(
                    callback_query_id=callback_query_id,
                    text=text,
                    show_alert=show_alert,
                    url=url,
                    cache_time=cache_time
                )
                return result

            result = run_async(answer())

            if result:
                yield self.create_text_message(
                    f"✅ Callback query answered successfully!\n"
                    f"Query ID: {callback_query_id}\n"
                    f"Alert Mode: {'Yes' if show_alert else 'No'}"
                )

                yield self.create_json_message({
                    "success": True,
                    "callback_query_id": callback_query_id,
                    "text": text,
                    "show_alert": show_alert,
                    "url": url
                })
            else:
                yield self.create_text_message("❌ Failed to answer callback query")

        except Exception as e:
            logger.error(f"Error answering callback query: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
