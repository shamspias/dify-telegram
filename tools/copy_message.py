from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async
import logging

logger = logging.getLogger(__name__)


class CopyMessageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Copy a message without link to original"""
        try:
            chat_id = tool_parameters.get("chat_id")
            from_chat_id = tool_parameters.get("from_chat_id")
            message_id = tool_parameters.get("message_id")
            caption = tool_parameters.get("caption")
            parse_mode = tool_parameters.get("parse_mode") or None
            disable_notification = tool_parameters.get("disable_notification", False)
            protect_content = tool_parameters.get("protect_content", False)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not from_chat_id:
                yield self.create_text_message("❌ Error: from_chat_id is required")
                return
            if not message_id:
                yield self.create_text_message("❌ Error: message_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def copy():
                message_id_result = await bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=from_chat_id,
                    message_id=message_id,
                    caption=caption,
                    parse_mode=parse_mode,
                    disable_notification=disable_notification,
                    protect_content=protect_content
                )
                return message_id_result

            result = run_async(copy())

            if result:
                yield self.create_text_message(
                    f"✅ Message copied successfully!\n"
                    f"New Message ID: {result}\n"
                    f"To Chat: {chat_id}\n"
                    f"From Chat: {from_chat_id}"
                )
                yield self.create_json_message({
                    "success": True,
                    "message_id": result,
                    "chat_id": chat_id
                })
            else:
                yield self.create_text_message("❌ Failed to copy message")

        except Exception as e:
            logger.error(f"Error copying message: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
