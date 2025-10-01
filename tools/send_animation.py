from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendAnimationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Send animation (GIF or H.264/MPEG-4 AVC video without sound)"""
        try:
            import os

            chat_id = tool_parameters.get("chat_id")
            animation = tool_parameters.get("animation")
            caption = tool_parameters.get("caption")
            duration = tool_parameters.get("duration")
            width = tool_parameters.get("width")
            height = tool_parameters.get("height")
            parse_mode = tool_parameters.get("parse_mode") or None
            disable_notification = tool_parameters.get("disable_notification", False)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if not animation:
                yield self.create_text_message("❌ Error: animation is required")
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
                if width:
                    kwargs["width"] = width
                if height:
                    kwargs["height"] = height

                if animation.startswith('http://') or animation.startswith('https://'):
                    kwargs["animation"] = animation
                    message = await bot.send_animation(**kwargs)
                elif os.path.isfile(animation):
                    with open(animation, 'rb') as anim_file:
                        kwargs["animation"] = anim_file
                        message = await bot.send_animation(**kwargs)
                else:
                    kwargs["animation"] = animation
                    message = await bot.send_animation(**kwargs)

                return message

            result = run_async(send())

            if result:
                message_data = format_message_result(result)
                if result.animation:
                    anim = result.animation
                    message_data["animation"] = {
                        "file_id": anim.file_id,
                        "file_unique_id": anim.file_unique_id,
                        "width": anim.width,
                        "height": anim.height,
                        "duration": anim.duration,
                        "file_size": anim.file_size
                    }

                yield self.create_text_message(
                    f"✅ Animation sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}"
                )
                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send animation")

        except Exception as e:
            logger.error(f"Error sending animation: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
