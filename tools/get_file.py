from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class GetFileTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Get basic info about a file and prepare it for downloading"""
        try:
            file_id = tool_parameters.get("file_id")

            if not file_id:
                yield self.create_text_message("❌ Error: file_id is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def get():
                file = await bot.get_file(file_id=file_id)
                return file

            result = run_async(get())

            if result:
                file_data = {
                    "file_id": result.file_id,
                    "file_unique_id": result.file_unique_id,
                    "file_size": result.file_size,
                    "file_path": result.file_path
                }

                yield self.create_text_message(
                    f"✅ File info retrieved successfully!\n"
                    f"File ID: {result.file_id}\n"
                    f"Size: {result.file_size:,} bytes\n"
                    f"Path: {result.file_path}"
                )
                yield self.create_json_message(file_data)
            else:
                yield self.create_text_message("❌ Failed to get file info")

        except Exception as e:
            logger.error(f"Error getting file: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
