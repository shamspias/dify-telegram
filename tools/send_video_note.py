from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendVideoNoteTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Send video note (round video message)"""
        try:
            import os

            chat_id = tool_parameters.get("chat_id")
            video_note = tool_parameters.get("video_note")
            duration = tool_parameters.get("duration")
            length = tool_parameters.get("length")
            disable_notification = tool_parameters.get("disable_notification", False)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not video_note:
                yield self.create_text_message("❌ Error: video_note is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def send():
                kwargs = {
                    "chat_id": chat_id,
                    "disable_notification": disable_notification
                }

                if duration:
                    kwargs["duration"] = duration
                if length:
                    kwargs["length"] = length

                if video_note.startswith('http://') or video_note.startswith('https://'):
                    kwargs["video_note"] = video_note
                    message = await bot.send_video_note(**kwargs)
                elif os.path.isfile(video_note):
                    with open(video_note, 'rb') as vn_file:
                        kwargs["video_note"] = vn_file
                        message = await bot.send_video_note(**kwargs)
                else:
                    kwargs["video_note"] = video_note
                    message = await bot.send_video_note(**kwargs)

                return message

            result = run_async(send())

            if result:
                message_data = format_message_result(result)
                if result.video_note:
                    vn = result.video_note
                    message_data["video_note"] = {
                        "file_id": vn.file_id,
                        "file_unique_id": vn.file_unique_id,
                        "length": vn.length,
                        "duration": vn.duration,
                        "file_size": vn.file_size
                    }

                yield self.create_text_message(
                    f"✅ Video note sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Duration: {message_data.get('video_note', {}).get('duration', 'N/A')}s"
                )
                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send video note")

        except Exception as e:
            logger.error(f"Error sending video note: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
