from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async
import logging
import json

logger = logging.getLogger(__name__)


class SetWebhookTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Set a webhook URL for receiving updates
        """
        try:
            # Get parameters
            url = tool_parameters.get("url")
            max_connections = tool_parameters.get("max_connections", 40)
            allowed_updates = tool_parameters.get("allowed_updates")
            drop_pending_updates = tool_parameters.get("drop_pending_updates", False)
            secret_token = tool_parameters.get("secret_token")

            # Validate URL (must be HTTPS unless empty)
            if url and not url.startswith('https://'):
                yield self.create_text_message("❌ Error: Webhook URL must use HTTPS")
                return

            # Parse allowed_updates if provided
            allowed_updates_list = None
            if allowed_updates:
                try:
                    allowed_updates_list = json.loads(allowed_updates) if isinstance(allowed_updates,
                                                                                     str) else allowed_updates
                except:
                    yield self.create_text_message("❌ Error: allowed_updates must be valid JSON array")
                    return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Set webhook
            async def set_hook():
                kwargs = {
                    "url": url,
                    "max_connections": max_connections,
                    "drop_pending_updates": drop_pending_updates
                }

                if allowed_updates_list:
                    kwargs["allowed_updates"] = allowed_updates_list

                if secret_token:
                    kwargs["secret_token"] = secret_token

                result = await bot.set_webhook(**kwargs)
                return result

            result = run_async(set_hook())

            if result:
                if url:
                    yield self.create_text_message(
                        f"✅ Webhook set successfully!\n"
                        f"URL: {url}\n"
                        f"Max Connections: {max_connections}\n"
                        f"Secret Token: {'Set' if secret_token else 'Not set'}"
                    )
                else:
                    yield self.create_text_message("✅ Webhook removed successfully!")

                yield self.create_json_message({
                    "success": True,
                    "url": url,
                    "max_connections": max_connections,
                    "allowed_updates": allowed_updates_list,
                    "drop_pending_updates": drop_pending_updates,
                    "has_secret_token": bool(secret_token)
                })
            else:
                yield self.create_text_message("❌ Failed to set webhook")

        except Exception as e:
            logger.error(f"Error setting webhook: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
