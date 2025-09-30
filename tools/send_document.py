from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging
import os

logger = logging.getLogger(__name__)


class SendDocumentTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Send a document file to a Telegram chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            document = tool_parameters.get("document")
            caption = tool_parameters.get("caption")
            filename = tool_parameters.get("filename")
            parse_mode = tool_parameters.get("parse_mode") or None
            disable_notification = tool_parameters.get("disable_notification", False)

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not document:
                yield self.create_text_message("❌ Error: document is required")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Send document
            async def send():
                # Check if document is a URL
                if document.startswith('http://') or document.startswith('https://'):
                    message = await bot.send_document(
                        chat_id=chat_id,
                        document=document,
                        caption=caption,
                        parse_mode=parse_mode,
                        disable_notification=disable_notification,
                        filename=filename
                    )
                # Check if it's a local file
                elif os.path.isfile(document):
                    with open(document, 'rb') as doc_file:
                        message = await bot.send_document(
                            chat_id=chat_id,
                            document=doc_file,
                            caption=caption,
                            parse_mode=parse_mode,
                            disable_notification=disable_notification,
                            filename=filename or os.path.basename(document)
                        )
                else:
                    # Assume it's a file_id
                    message = await bot.send_document(
                        chat_id=chat_id,
                        document=document,
                        caption=caption,
                        parse_mode=parse_mode,
                        disable_notification=disable_notification,
                        filename=filename
                    )
                return message

            result = run_async(send())

            if result:
                # Format response
                message_data = format_message_result(result)

                # Add document-specific info
                if result.document:
                    doc = result.document
                    message_data["document"] = {
                        "file_id": doc.file_id,
                        "file_unique_id": doc.file_unique_id,
                        "file_name": doc.file_name,
                        "mime_type": doc.mime_type,
                        "file_size": doc.file_size
                    }

                yield self.create_text_message(
                    f"✅ Document sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}\n"
                    f"File: {message_data.get('document', {}).get('file_name', 'N/A')}"
                )

                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send document")

        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            yield self.create_text_message(f"❌ Error: File not found - {document}")
        except Exception as e:
            logger.error(f"Error sending document: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
