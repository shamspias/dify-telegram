from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendContactTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Send a phone contact to a Telegram chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            phone_number = tool_parameters.get("phone_number")
            first_name = tool_parameters.get("first_name")
            last_name = tool_parameters.get("last_name")
            vcard = tool_parameters.get("vcard")

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not phone_number:
                yield self.create_text_message("❌ Error: phone_number is required")
                return

            if not first_name:
                yield self.create_text_message("❌ Error: first_name is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Send contact
            async def send():
                kwargs = {
                    "chat_id": chat_id,
                    "phone_number": phone_number,
                    "first_name": first_name
                }

                if last_name:
                    kwargs["last_name"] = last_name
                if vcard:
                    kwargs["vcard"] = vcard

                message = await bot.send_contact(**kwargs)
                return message

            result = run_async(send())

            if result:
                # Format response
                message_data = format_message_result(result)

                # Add contact-specific info
                if result.contact:
                    contact = result.contact
                    message_data["contact"] = {
                        "phone_number": contact.phone_number,
                        "first_name": contact.first_name,
                        "last_name": contact.last_name,
                        "user_id": contact.user_id,
                        "vcard": contact.vcard
                    }

                contact_name = f"{first_name} {last_name}" if last_name else first_name
                yield self.create_text_message(
                    f"✅ Contact sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}\n"
                    f"Contact: {contact_name}\n"
                    f"Phone: {phone_number}"
                )

                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send contact")

        except Exception as e:
            logger.error(f"Error sending contact: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
