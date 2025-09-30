from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async, format_message_result
import logging

logger = logging.getLogger(__name__)


class SendPollTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Send a poll or quiz to a Telegram chat
        """
        try:
            # Get parameters
            chat_id = tool_parameters.get("chat_id")
            question = tool_parameters.get("question")
            options = tool_parameters.get("options")
            is_anonymous = tool_parameters.get("is_anonymous", True)
            poll_type = tool_parameters.get("type", "regular")
            allows_multiple_answers = tool_parameters.get("allows_multiple_answers", False)
            correct_option_id = tool_parameters.get("correct_option_id")
            explanation = tool_parameters.get("explanation")
            open_period = tool_parameters.get("open_period")
            disable_notification = tool_parameters.get("disable_notification", False)

            # Validate inputs
            if not chat_id:
                yield self.create_text_message("❌ Error: chat_id is required")
                return

            if not question:
                yield self.create_text_message("❌ Error: question is required")
                return

            if not options:
                yield self.create_text_message("❌ Error: options are required")
                return

            # Parse options
            if isinstance(options, str):
                options_list = [opt.strip() for opt in options.split(',')]
            else:
                options_list = options

            # Validate options
            if len(options_list) < 2 or len(options_list) > 10:
                yield self.create_text_message("❌ Error: Poll must have 2-10 options")
                return

            # Validate quiz requirements
            if poll_type == "quiz" and correct_option_id is None:
                yield self.create_text_message("❌ Error: correct_option_id is required for quiz type")
                return

            # Get bot instance
            bot = get_bot(self.runtime.credentials)

            # Send poll
            async def send():
                kwargs = {
                    "chat_id": chat_id,
                    "question": question,
                    "options": options_list,
                    "is_anonymous": is_anonymous,
                    "type": poll_type,
                    "allows_multiple_answers": allows_multiple_answers,
                    "disable_notification": disable_notification
                }

                # Add quiz-specific parameters
                if poll_type == "quiz":
                    kwargs["correct_option_id"] = correct_option_id
                    if explanation:
                        kwargs["explanation"] = explanation

                # Add optional parameters
                if open_period:
                    kwargs["open_period"] = open_period

                message = await bot.send_poll(**kwargs)
                return message

            result = run_async(send())

            if result:
                # Format response
                message_data = format_message_result(result)

                # Add poll-specific info
                if result.poll:
                    poll = result.poll
                    poll_data = {
                        "id": poll.id,
                        "question": poll.question,
                        "options": [
                            {
                                "text": opt.text,
                                "voter_count": opt.voter_count
                            }
                            for opt in poll.options
                        ],
                        "total_voter_count": poll.total_voter_count,
                        "is_closed": poll.is_closed,
                        "is_anonymous": poll.is_anonymous,
                        "type": poll.type,
                        "allows_multiple_answers": poll.allows_multiple_answers
                    }

                    if poll.type == "quiz":
                        poll_data["correct_option_id"] = poll.correct_option_id
                        poll_data["explanation"] = poll.explanation

                    message_data["poll"] = poll_data

                poll_type_display = "Quiz" if poll_type == "quiz" else "Poll"
                yield self.create_text_message(
                    f"✅ {poll_type_display} sent successfully!\n"
                    f"Message ID: {message_data.get('message_id')}\n"
                    f"Chat ID: {message_data.get('chat_id')}\n"
                    f"Question: {question}\n"
                    f"Options: {len(options_list)}"
                )

                yield self.create_json_message(message_data)
            else:
                yield self.create_text_message("❌ Failed to send poll")

        except Exception as e:
            logger.error(f"Error sending poll: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
