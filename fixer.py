import yaml
from pathlib import Path

# Common parameter descriptions
COMMON_DESCRIPTIONS = {
    'parse_mode': 'Format for text parsing',
    'disable_notification': 'Send message silently',
    'disable_web_page_preview': 'Disable link previews',
    'reply_to_message_id': 'Reply to specific message',
    'protect_content': 'Protect content from forwarding',
    'caption': 'Caption text',
    'duration': 'Duration in seconds',
    'width': 'Width in pixels',
    'height': 'Height in pixels',
    'quality': 'Quality setting',
    'chat_id': 'Target chat identifier',
    'user_id': 'Target user identifier',
    'message_id': 'Message identifier',
    'text': 'Message text',
    'photo': 'Photo to send',
    'video': 'Video to send',
    'audio': 'Audio to send',
    'document': 'Document to send',
    'sticker': 'Sticker to send',
    'animation': 'Animation to send',
    'voice': 'Voice message to send',
    'video_note': 'Video note to send',
    'location': 'Location coordinates',
    'venue': 'Venue information',
    'contact': 'Contact information',
    'poll': 'Poll data',
    'until_date': 'Date until action applies',
}


def fix_file(file_path):
    print(f"Processing: {file_path}")

    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    if 'parameters' not in data:
        print(f"  ⚠️ No parameters found")
        return

    fixed_count = 0
    for param in data['parameters']:
        param_name = param.get('name', '')

        # Add human_description if missing
        if 'human_description' not in param:
            desc = COMMON_DESCRIPTIONS.get(param_name, f"Parameter {param_name}")
            param['human_description'] = {'en_US': desc}
            fixed_count += 1
            print(f"  + Added human_description for: {param_name}")

        # Ensure it's a dict with en_US
        elif not isinstance(param['human_description'], dict):
            param['human_description'] = {'en_US': str(param['human_description'])}
            fixed_count += 1
        elif 'en_US' not in param['human_description']:
            desc = COMMON_DESCRIPTIONS.get(param_name, f"Parameter {param_name}")
            param['human_description']['en_US'] = desc
            fixed_count += 1

        # Add llm_description if missing
        if 'llm_description' not in param:
            param['llm_description'] = param_name.replace('_', ' ')

    if fixed_count > 0:
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
        print(f"  ✅ Fixed {fixed_count} parameters")
    else:
        print(f"  ✅ Already valid")


def main():
    print("=" * 60)
    print("🔧 Fixing human_description Fields")
    print("=" * 60)
    print()

    tools_dir = Path('tools')
    yaml_files = sorted(tools_dir.glob('*.yaml'))

    for yaml_file in yaml_files:
        fix_file(yaml_file)
        print()

    print("=" * 60)
    print("✅ All files processed!")
    print("Now run: dify plugin package .")
    print("=" * 60)


if __name__ == '__main__':
    main()