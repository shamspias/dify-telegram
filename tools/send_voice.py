from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendVoiceTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Send voice message"""
        try:
            import os

            chat_id = tool_parameters.get("chat_id")
            voice = tool_parameters.get("voice")
            caption = tool_parameters.get("caption")
            duration = tool_parameters.get("duration")
            parse_mode = tool_parameters.get("parse_mode") or None
            disable_notification = tool_parameters.get("disable_notification", False)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not voice:
                yield self.create_text_message("❌ Error: voice is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def send():
                kwargs = {
                    "chat_id": chat_id,
                    "caption": caption,
                    "parse_mode": parse_mode,
                    "disable_notification": disable_notification
                }

                if duration:
                    kwargs["duration"] = duration

                if voice.startswith('http://') or voice.startswith('https://'):
                    kwargs["voice"] = voice
                    message = await bot.send_voice(**kwargs)
                elif os.path.isfile(voice):
                    with open(voice, 'rb') as voice_file:
                        kwargs["voice"] = voice_file
                        message = await bot.send_voice(**kwargs)
                else:
                    kwargs["voice"] = voice
                    message = await bot.send_voice(**kwargs)

                return message

            result = run_async(send())

            if result:
                message_data = format_message_result(result)
                if result.voice:
                    v = result.voice
                    message_data["voice"] = {
                        "file_id": v.file_id,
                        "file_unique_id": v.file_unique_id,
                        "duration": v.duration,
                        "mime_type": v.mime_type,
                        "file_size": v.file_size
                    }

                yield self.create_text_message(
                    f"✅ Voice message sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Duration: {message_data.get('voice', {}).get('duration', 'N/A')}s"
                )
                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send voice message")

        except Exception as e:
            logger.error(f"Error sending voice: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
