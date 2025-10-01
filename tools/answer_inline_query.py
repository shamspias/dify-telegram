from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async
import logging
import json

logger = logging.getLogger(__name__)


class AnswerInlineQueryTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Answer an inline query
        """
        try:
            # Get parameters
            inline_query_id = tool_parameters.get("inline_query_id")
            results = tool_parameters.get("results")
            cache_time = tool_parameters.get("cache_time", 300)
            is_personal = tool_parameters.get("is_personal", False)
            next_offset = tool_parameters.get("next_offset")

            # Validate inputs
            if not inline_query_id:
                yield self.create_text_message("❌ Error: inline_query_id is required")
                return

            if not results:
                yield self.create_text_message("❌ Error: results are required")
                return

            # Parse results if string
            if isinstance(results, str):
                try:
                    results_list = json.loads(results)
                except:
                    yield self.create_text_message("❌ Error: results must be valid JSON array")
                    return
            else:
                results_list = results

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Answer inline query
            async def answer():
                from telegram import InlineQueryResultArticle, InputTextMessageContent

                # Convert results to InlineQueryResult objects
                inline_results = []
                for idx, result in enumerate(results_list):
                    if result.get("type") == "article":
                        inline_results.append(
                            InlineQueryResultArticle(
                                id=result.get("id", str(idx)),
                                title=result.get("title", ""),
                                input_message_content=InputTextMessageContent(
                                    message_text=result.get("message_text", "")
                                ),
                                description=result.get("description"),
                                thumb_url=result.get("thumb_url")
                            )
                        )

                result = await bot.answer_inline_query(
                    inline_query_id=inline_query_id,
                    results=inline_results,
                    cache_time=cache_time,
                    is_personal=is_personal,
                    next_offset=next_offset
                )
                return result

            result = run_async(answer())

            if result:
                yield self.create_text_message(
                    f"✅ Inline query answered successfully!\n"
                    f"Query ID: {inline_query_id}\n"
                    f"Results: {len(results_list)}\n"
                    f"Cache Time: {cache_time}s"
                )

                yield self.create_json_message({
                    "success": True,
                    "inline_query_id": inline_query_id,
                    "results_count": len(results_list),
                    "cache_time": cache_time
                })
            else:
                yield self.create_text_message("❌ Failed to answer inline query")

        except Exception as e:
            logger.error(f"Error answering inline query: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
