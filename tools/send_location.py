from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendLocationTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Send a location to a Telegram chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            latitude = tool_parameters.get("latitude")
            longitude = tool_parameters.get("longitude")
            horizontal_accuracy = tool_parameters.get("horizontal_accuracy")
            live_period = tool_parameters.get("live_period")
            heading = tool_parameters.get("heading")
            proximity_alert_radius = tool_parameters.get("proximity_alert_radius")
            disable_notification = tool_parameters.get("disable_notification", False)

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if latitude is None:
                yield self.create_text_message("❌ Error: latitude is required")
                return

            if longitude is None:
                yield self.create_text_message("❌ Error: longitude is required")
                return

            # Validate ranges
            if not (-90 <= latitude <= 90):
                yield self.create_text_message("❌ Error: latitude must be between -90 and 90")
                return

            if not (-180 <= longitude <= 180):
                yield self.create_text_message("❌ Error: longitude must be between -180 and 180")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Send location
            async def send():
                kwargs = {
                    "chat_id": chat_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "disable_notification": disable_notification
                }

                # Add optional parameters
                if horizontal_accuracy:
                    kwargs["horizontal_accuracy"] = horizontal_accuracy
                if live_period:
                    kwargs["live_period"] = live_period
                if heading:
                    kwargs["heading"] = heading
                if proximity_alert_radius:
                    kwargs["proximity_alert_radius"] = proximity_alert_radius

                message = await bot.send_location(**kwargs)
                return message

            result = run_async(send())

            if result:
                # Format response
                message_data = format_message_result(result)

                # Add location-specific info
                if result.location:
                    loc = result.location
                    message_data["location"] = {
                        "latitude": loc.latitude,
                        "longitude": loc.longitude,
                        "horizontal_accuracy": loc.horizontal_accuracy,
                        "live_period": loc.live_period,
                        "heading": loc.heading,
                        "proximity_alert_radius": loc.proximity_alert_radius
                    }

                location_type = "Live" if live_period else "Static"
                yield self.create_text_message(
                    f"✅ {location_type} location sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}\n"
                    f"Coordinates: {latitude}, {longitude}"
                )

                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send location")

        except Exception as e:
            logger.error(f"Error sending location: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
