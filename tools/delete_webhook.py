from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class DeleteWebhookTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Remove webhook integration"""
        try:
            drop_pending_updates = tool_parameters.get("drop_pending_updates", False)

            bot = get_bot(self.runtime.credentials)

            async def delete():
                result = await bot.delete_webhook(drop_pending_updates=drop_pending_updates)
                return result

            result = run_async(delete())

            if result:
                yield self.create_text_message(
                    f"✅ Webhook deleted successfully!\n"
                    f"Pending updates dropped: {'Yes' if drop_pending_updates else 'No'}"
                )
                yield self.create_json_message({
                    "success": True,
                    "drop_pending_updates": drop_pending_updates
                })
            else:
                yield self.create_text_message("❌ Failed to delete webhook")

        except Exception as e:
            logger.error(f"Error deleting webhook: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
