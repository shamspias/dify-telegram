from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendVenueTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Send information about a venue"""
        try:
            chat_id = tool_parameters.get("chat_id")
            latitude = tool_parameters.get("latitude")
            longitude = tool_parameters.get("longitude")
            title = tool_parameters.get("title")
            address = tool_parameters.get("address")
            foursquare_id = tool_parameters.get("foursquare_id")
            foursquare_type = tool_parameters.get("foursquare_type")
            disable_notification = tool_parameters.get("disable_notification", False)

            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return
            if latitude is None:
                yield self.create_text_message("❌ Error: latitude is required")
                return
            if longitude is None:
                yield self.create_text_message("❌ Error: longitude is required")
                return
            if not title:
                yield self.create_text_message("❌ Error: title is required")
                return
            if not address:
                yield self.create_text_message("❌ Error: address is required")
                return

            bot = get_bot(self.runtime.credentials)

            async def send():
                kwargs = {
                    "chat_id": chat_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "title": title,
                    "address": address,
                    "disable_notification": disable_notification
                }

                if foursquare_id:
                    kwargs["foursquare_id"] = foursquare_id
                if foursquare_type:
                    kwargs["foursquare_type"] = foursquare_type

                message = await bot.send_venue(**kwargs)
                return message

            result = run_async(send())

            if result:
                message_data = format_message_result(result)
                if result.venue:
                    venue = result.venue
                    message_data["venue"] = {
                        "location": {
                            "latitude": venue.location.latitude,
                            "longitude": venue.location.longitude
                        },
                        "title": venue.title,
                        "address": venue.address,
                        "foursquare_id": venue.foursquare_id,
                        "foursquare_type": venue.foursquare_type
                    }

                yield self.create_text_message(
                    f"✅ Venue sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Title: {title}\n"
                    f"Address: {address}"
                )
                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send venue")

        except Exception as e:
            logger.error(f"Error sending venue: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
