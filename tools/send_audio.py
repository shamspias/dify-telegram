from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging
import os

logger = logging.getLogger(__name__)


class SendAudioTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Send an audio file to a Telegram chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            audio = tool_parameters.get("audio")
            caption = tool_parameters.get("caption")
            duration = tool_parameters.get("duration")
            performer = tool_parameters.get("performer")
            title = tool_parameters.get("title")
            parse_mode = tool_parameters.get("parse_mode") or None

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not audio:
                yield self.create_text_message("❌ Error: audio is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Send audio
            async def send():
                kwargs = {
                    "chat_id": chat_id,
                    "caption": caption,
                    "parse_mode": parse_mode
                }

                # Add optional metadata
                if duration:
                    kwargs["duration"] = duration
                if performer:
                    kwargs["performer"] = performer
                if title:
                    kwargs["title"] = title

                # Check if audio is a URL
                if audio.startswith('http://') or audio.startswith('https://'):
                    kwargs["audio"] = audio
                    message = await bot.send_audio(**kwargs)
                # Check if it's a local file
                elif os.path.isfile(audio):
                    with open(audio, 'rb') as audio_file:
                        kwargs["audio"] = audio_file
                        message = await bot.send_audio(**kwargs)
                else:
                    # Assume it's a file_id
                    kwargs["audio"] = audio
                    message = await bot.send_audio(**kwargs)

                return message

            result = run_async(send())

            if result:
                # Format response
                message_data = format_message_result(result)

                # Add audio-specific info
                if result.audio:
                    aud = result.audio
                    message_data["audio"] = {
                        "file_id": aud.file_id,
                        "file_unique_id": aud.file_unique_id,
                        "duration": aud.duration,
                        "performer": aud.performer,
                        "title": aud.title,
                        "mime_type": aud.mime_type,
                        "file_size": aud.file_size
                    }

                track_info = f"{performer} - {title}" if performer and title else "Audio"
                yield self.create_text_message(
                    f"✅ Audio sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}\n"
                    f"Track: {track_info}"
                )

                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send audio")

        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            yield self.create_text_message(f"❌ Error: Audio file not found - {audio}")
        except Exception as e:
            logger.error(f"Error sending audio: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
