from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class GetWebhookInfoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Get current webhook status"""
        try:
            bot = get_bot(self.runtime.credentials)

            async def get_info():
                info = await bot.get_webhook_info()
                return info

            result = run_async(get_info())

            if result:
                webhook_data = {
                    "url": result.url,
                    "has_custom_certificate": result.has_custom_certificate,
                    "pending_update_count": result.pending_update_count,
                    "ip_address": result.ip_address,
                    "last_error_date": result.last_error_date.isoformat() if result.last_error_date else None,
                    "last_error_message": result.last_error_message,
                    "max_connections": result.max_connections,
                    "allowed_updates": result.allowed_updates
                }

                status = "🟢 Active" if result.url else "⚪ Not Set"
                yield self.create_text_message(
                    f"✅ Webhook Information:\n"
                    f"Status: {status}\n"
                    f"URL: {result.url or 'Not configured'}\n"
                    f"Pending Updates: {result.pending_update_count}\n"
                    f"Last Error: {result.last_error_message or 'None'}"
                )
                yield self.create_json_message(webhook_data)
            else:
                yield self.create_text_message("❌ Failed to get webhook info")

        except Exception as e:
            logger.error(f"Error getting webhook info: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
