from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging
import os

logger = logging.getLogger(__name__)


class SendVideoTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Send a video to a Telegram chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            video = tool_parameters.get("video")
            caption = tool_parameters.get("caption")
            duration = tool_parameters.get("duration")
            width = tool_parameters.get("width")
            height = tool_parameters.get("height")
            supports_streaming = tool_parameters.get("supports_streaming", True)
            parse_mode = tool_parameters.get("parse_mode") or None
            disable_notification = tool_parameters.get("disable_notification", False)

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not video:
                yield self.create_text_message("❌ Error: video is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Send video
            async def send():
                kwargs = {
                    "chat_id": chat_id,
                    "caption": caption,
                    "parse_mode": parse_mode,
                    "supports_streaming": supports_streaming,
                    "disable_notification": disable_notification
                }

                # Add optional parameters
                if duration:
                    kwargs["duration"] = duration
                if width:
                    kwargs["width"] = width
                if height:
                    kwargs["height"] = height

                # Check if video is a URL
                if video.startswith('http://') or video.startswith('https://'):
                    kwargs["video"] = video
                    message = await bot.send_video(**kwargs)
                # Check if it's a local file
                elif os.path.isfile(video):
                    with open(video, 'rb') as video_file:
                        kwargs["video"] = video_file
                        message = await bot.send_video(**kwargs)
                else:
                    # Assume it's a file_id
                    kwargs["video"] = video
                    message = await bot.send_video(**kwargs)

                return message

            result = run_async(send())

            if result:
                # Format response
                message_data = format_message_result(result)

                # Add video-specific info
                if result.video:
                    vid = result.video
                    message_data["video"] = {
                        "file_id": vid.file_id,
                        "file_unique_id": vid.file_unique_id,
                        "width": vid.width,
                        "height": vid.height,
                        "duration": vid.duration,
                        "mime_type": vid.mime_type,
                        "file_size": vid.file_size
                    }

                    if vid.thumbnail:
                        message_data["video"]["thumbnail"] = {
                            "file_id": vid.thumbnail.file_id,
                            "width": vid.thumbnail.width,
                            "height": vid.thumbnail.height
                        }

                yield self.create_text_message(
                    f"✅ Video sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}\n"
                    f"Duration: {message_data.get('video', {}).get('duration', 'N/A')}s\n"
                    f"Size: {message_data.get('video', {}).get('width', 'N/A')}x{message_data.get('video', {}).get('height', 'N/A')}"
                )

                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send video")

        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            yield self.create_text_message(f"❌ Error: Video file not found - {video}")
        except Exception as e:
            logger.error(f"Error sending video: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
