from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from telegram import Bot
from telegram.error import TelegramError
import asyncio


class TelegramProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate Telegram Bot Token by making a test API call
        """
        try:
            bot_token = credentials.get("bot_token")

            if not bot_token:
                raise ToolProviderCredentialValidationError("Bot token is required")

            # Test the token by getting bot info
            async def test_token():
                bot = Bot(token=bot_token)
                try:
                    await bot.get_me()
                    return True
                except TelegramError as e:
                    raise ToolProviderCredentialValidationError(f"Invalid bot token: {str(e)}")
                finally:
                    # Clean up
                    if hasattr(bot, 'shutdown'):
                        await bot.shutdown()

            # Run async validation
            try:
                asyncio.run(test_token())
            except RuntimeError:
                # If event loop is already running, create new loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(test_token())
                finally:
                    loop.close()

        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Validation failed: {str(e)}")
