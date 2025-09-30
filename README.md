# 🤖 Telegram Plugin for Dify

<div align="center">

![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Telegram Bot API](https://img.shields.io/badge/telegram--bot-22.5-blue.svg)

**Complete Telegram Bot API integration for Dify**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Tool Development](#-tool-development-guide) • [API Reference](#-api-reference)

</div>

---

## 📖 Overview

This comprehensive Dify plugin provides full integration with the Telegram Bot API, enabling you to:
- Send and receive messages
- Manage chats and users
- Send media (photos, videos, documents)
- Handle callback queries and inline keyboards
- Manage webhooks
- And much more!

**Multi-language Support**: English, Russian, Bangla, Chinese (Simplified), Japanese

---

## ✨ Features

### 📬 Message Operations
- ✅ Send Message
- ✅ Forward Message
- Copy Message
- Edit Message Text
- Edit Message Caption
- Delete Message
- Pin/Unpin Messages
- Send Chat Action (typing indicators)

### 🖼️ Media Operations
- ✅ Send Photo
- Send Video
- Send Audio
- Send Document
- Send Animation (GIF)
- Send Voice Message
- Send Video Note
- Send Sticker
- Send Location/Venue
- Send Contact
- Send Poll
- Send Dice
- Send Media Group

### 💬 Chat Operations
- ✅ Get Chat Info
- Get Chat Administrators
- Get Chat Member
- Get Chat Members Count
- Leave Chat
- Set Chat Description/Title/Photo
- Restrict/Promote/Ban Members
- Manage Invite Links
- Set Chat Permissions

### 🎯 Callback & Inline
- ✅ Answer Callback Query
- Answer Inline Query
- Edit Inline Messages
- Stop Poll

### 📁 File Operations
- Get File
- Upload File

### 🔗 Webhook Operations
- Set Webhook
- Delete Webhook
- Get Webhook Info

---

## 🚀 Installation

### Prerequisites
- Dify Platform (version 0.6.0+)
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### Steps

1. **Get Your Bot Token**
   ```
   1. Open Telegram and search for @BotFather
   2. Send /newbot and follow instructions
   3. Copy the bot token provided
   ```

2. **Install Plugin in Dify**
   - Navigate to **Plugins** → **Add Plugin**
   - Upload this plugin or install from marketplace
   - Enter your Bot Token in credentials

3. **Start Using**
   - Add Telegram tools to your workflows
   - Configure each tool with required parameters

---

## 📚 Usage Examples

### Example 1: Send a Simple Message

```json
{
  "tool": "send_message",
  "parameters": {
    "chat_id": "123456789",
    "text": "Hello from Dify!",
    "parse_mode": "Markdown"
  }
}
```

### Example 2: Send a Photo with Caption

```json
{
  "tool": "send_photo",
  "parameters": {
    "chat_id": "123456789",
    "photo": "https://example.com/photo.jpg",
    "caption": "Check out this photo!",
    "parse_mode": "HTML"
  }
}
```

### Example 3: Get Chat Information

```json
{
  "tool": "get_chat",
  "parameters": {
    "chat_id": "@channelname"
  }
}
```

### Example 4: Answer Callback Query

```json
{
  "tool": "answer_callback_query",
  "parameters": {
    "callback_query_id": "abc123",
    "text": "Button clicked!",
    "show_alert": true
  }
}
```

---

## 🛠️ Tool Development Guide

### Plugin Structure

```
telegram_bot/
├── main.py                          # Entry point
├── manifest.yaml                    # Plugin configuration
├── requirements.txt                 # Dependencies
├── PRIVACY.md                      # Privacy policy
├── README.md                       # This file
├── provider/
│   ├── telegram.py                 # Provider implementation
│   └── telegram.yaml               # Provider configuration
└── tools/
    ├── _helpers.py                 # Shared helper functions
    ├── send_message.yaml           # ✅ Implemented
    ├── send_message.py             # ✅ Implemented
    ├── send_photo.yaml             # ✅ Implemented
    ├── send_photo.py               # ✅ Implemented
    ├── get_chat.yaml               # ✅ Implemented
    ├── get_chat.py                 # ✅ Implemented
    ├── answer_callback_query.yaml  # ✅ Implemented
    ├── answer_callback_query.py    # ✅ Implemented
    └── ... (other tools to implement)
```

### How to Add a New Tool

Follow this pattern to create any of the remaining tools:

#### Step 1: Create YAML Configuration

Create `tools/your_tool_name.yaml`:

```yaml
identity:
  name: your_tool_name
  author: your_username
  label:
    en_US: Tool Name
    ru_RU: Название инструмента
    bn_BD: টুলের নাম
    zh_Hans: 工具名称
    ja_JP: ツール名
description:
  human:
    en_US: Description of what this tool does
    ru_RU: Описание того, что делает этот инструмент
    bn_BD: এই টুলটি কী করে তার বর্ণনা
    zh_Hans: 此工具的功能描述
    ja_JP: このツールの機能説明
  llm: Brief description for AI understanding

parameters:
  - name: parameter_name
    type: string  # or: number, boolean, select, etc.
    required: true
    label:
      en_US: Parameter Label
      ru_RU: Метка параметра
      bn_BD: প্যারামিটার লেবেল
      zh_Hans: 参数标签
      ja_JP: パラメータラベル
    human_description:
      en_US: Human-readable description
      # ... other languages
    llm_description: AI-readable description
    form: llm  # or: form

extra:
  python:
    source: tools/your_tool_name.py
```

#### Step 2: Create Python Implementation

Create `tools/your_tool_name.py`:

```python
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools._helpers import get_bot, run_async
import logging

logger = logging.getLogger(__name__)


class YourToolNameTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Brief description of what this tool does
        """
        try:
            # 1. Extract parameters
            param1 = tool_parameters.get("param1")
            param2 = tool_parameters.get("param2", "default_value")

            # 2. Validate inputs
            if not param1:
                yield self.create_text_message("❌ Error: param1 is required")
                return

            # 3. Get bot instance
            bot = get_bot(self.runtime.credentials)

            # 4. Execute Telegram API call
            async def execute():
                result = await bot.some_method(
                    param1=param1,
                    param2=param2
                )
                return result

            result = run_async(execute())

            # 5. Format and yield results
            if result:
                yield self.create_text_message("✅ Operation successful!")
                yield self.create_json_message({
                    "success": True,
                    "data": result
                })
            else:
                yield self.create_text_message("❌ Operation failed")

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            yield self.create_text_message(f"❌ Error: {str(e)}")
```

#### Step 3: Add to Provider Configuration

Update `provider/telegram.yaml`:

```yaml
tools:
  # ... existing tools
  - tools/your_tool_name.yaml
```

---

## 📋 Remaining Tools to Implement

### Message Operations (7 tools)
- [ ] `forward_message.yaml` + `.py`
- [ ] `copy_message.yaml` + `.py`
- [ ] `edit_message_text.yaml` + `.py`
- [ ] `edit_message_caption.yaml` + `.py`
- [ ] `delete_message.yaml` + `.py`
- [ ] `pin_chat_message.yaml` + `.py`
- [ ] `unpin_chat_message.yaml` + `.py`
- [ ] `unpin_all_chat_messages.yaml` + `.py`
- [ ] `send_chat_action.yaml` + `.py`

### Media Operations (12 tools)
- [ ] `send_video.yaml` + `.py`
- [ ] `send_audio.yaml` + `.py`
- [ ] `send_document.yaml` + `.py`
- [ ] `send_animation.yaml` + `.py`
- [ ] `send_voice.yaml` + `.py`
- [ ] `send_video_note.yaml` + `.py`
- [ ] `send_sticker.yaml` + `.py`
- [ ] `send_location.yaml` + `.py`
- [ ] `send_venue.yaml` + `.py`
- [ ] `send_contact.yaml` + `.py`
- [ ] `send_poll.yaml` + `.py`
- [ ] `send_dice.yaml` + `.py`
- [ ] `send_media_group.yaml` + `.py`

### Chat Operations (15 tools)
- [ ] `get_chat_administrators.yaml` + `.py`
- [ ] `get_chat_member.yaml` + `.py`
- [ ] `get_chat_members_count.yaml` + `.py`
- [ ] `leave_chat.yaml` + `.py`
- [ ] `set_chat_description.yaml` + `.py`
- [ ] `set_chat_title.yaml` + `.py`
- [ ] `set_chat_photo.yaml` + `.py`
- [ ] `delete_chat_photo.yaml` + `.py`
- [ ] `restrict_chat_member.yaml` + `.py`
- [ ] `promote_chat_member.yaml` + `.py`
- [ ] `ban_chat_member.yaml` + `.py`
- [ ] `unban_chat_member.yaml` + `.py`
- [ ] `export_chat_invite_link.yaml` + `.py`
- [ ] `create_chat_invite_link.yaml` + `.py`
- [ ] `revoke_chat_invite_link.yaml` + `.py`
- [ ] `set_chat_permissions.yaml` + `.py`

### Callback & Inline (2 tools)
- [ ] `answer_inline_query.yaml` + `.py`
- [ ] `stop_poll.yaml` + `.py`

### File Operations (1 tool)
- [ ] `get_file.yaml` + `.py`

### Webhook Operations (3 tools)
- [ ] `set_webhook.yaml` + `.py`
- [ ] `delete_webhook.yaml` + `.py`
- [ ] `get_webhook_info.yaml` + `.py`

---

## 📖 API Reference

### Common Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `chat_id` | string | Chat ID or @username |
| `text` | string | Message text |
| `parse_mode` | select | Markdown, HTML, or none |
| `disable_notification` | boolean | Send silently |
| `reply_to_message_id` | number | Reply to specific message |

### Helper Functions

Available in `tools/_helpers.py`:

```python
# Get bot instance
bot = get_bot(credentials)

# Run async function
result = run_async(async_function())

# Format results
message_data = format_message_result(message)
chat_data = format_chat_result(chat)
user_data = format_user_result(user)
```

---

## 🔒 Security

- Bot tokens are encrypted by Dify
- All API calls use HTTPS
- No data is logged or stored
- See [PRIVACY.md](PRIVACY.md) for details

---

## 🤝 Contributing

Contributions are welcome! To add a new tool:

1. Fork the repository
2. Create your tool following the guide above
3. Test thoroughly
4. Submit a pull request

---

## 📄 License

MIT License - see LICENSE file

---

## 💬 Support

- **Telegram Bot API Docs**: https://core.telegram.org/bots/api
- **python-telegram-bot Docs**: https://docs.python-telegram-bot.org/
- **Issues**: Open a GitHub issue: https://github.com/shamspias/dify-telegram
- **Email**: info@shamspias.com

---

## 🙏 Credits

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 22.5
- For [Dify](https://dify.ai) platform
- Created by Shamsuddin Ahmed