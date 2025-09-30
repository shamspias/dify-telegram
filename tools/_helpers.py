"""
Helper functions for Telegram tools
"""
from telegram import Bot
from telegram.error import TelegramError
import asyncio
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def get_bot(credentials: dict) -> Bot:
    """Create and return a Telegram Bot instance"""
    bot_token = credentials.get("bot_token")
    return Bot(token=bot_token)


async def execute_telegram_action(bot: Bot, action_func, *args, **kwargs) -> Dict[str, Any]:
    """
    Execute a Telegram bot action with proper error handling
    """
    try:
        result = await action_func(*args, **kwargs)
        return {
            "success": True,
            "result": result,
            "error": None
        }
    except TelegramError as e:
        logger.error(f"Telegram API error: {str(e)}")
        return {
            "success": False,
            "result": None,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "success": False,
            "result": None,
            "error": str(e)
        }


def run_async(coro):
    """Run async function in sync context"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create new loop if one is already running
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except RuntimeError:
        # If event loop issues, create fresh loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)


def format_message_result(message) -> Dict[str, Any]:
    """Format Telegram message object to dict"""
    if not message:
        return {}

    return {
        "message_id": message.message_id,
        "chat_id": message.chat.id,
        "chat_type": message.chat.type,
        "date": message.date.isoformat() if message.date else None,
        "text": message.text,
        "caption": message.caption,
        "from_user": {
            "id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name
        } if message.from_user else None
    }


def format_chat_result(chat) -> Dict[str, Any]:
    """Format Telegram chat object to dict"""
    if not chat:
        return {}

    return {
        "id": chat.id,
        "type": chat.type,
        "title": chat.title,
        "username": chat.username,
        "first_name": chat.first_name,
        "last_name": chat.last_name,
        "description": chat.description,
        "invite_link": chat.invite_link,
        "members_count": getattr(chat, 'members_count', None)
    }


def format_user_result(user) -> Dict[str, Any]:
    """Format Telegram user object to dict"""
    if not user:
        return {}

    return {
        "id": user.id,
        "is_bot": user.is_bot,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "language_code": user.language_code
    }


def parse_keyboard_markup(keyboard_data: str) -> Any:
    """
    Parse keyboard markup from string format
    Expected formats:
    - "button1,button2|button3,button4" for reply keyboard (| = new row)
    - JSON string for inline keyboards
    """
    if not keyboard_data:
        return None

    try:
        import json
        # Try to parse as JSON first (for inline keyboards)
        return json.loads(keyboard_data)
    except:
        # Simple text format for reply keyboards
        from telegram import ReplyKeyboardMarkup, KeyboardButton
        rows = keyboard_data.split('|')
        keyboard = [[KeyboardButton(btn.strip()) for btn in row.split(',')] for row in rows]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
