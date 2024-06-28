import requests
from config import TG_API_TOKEN  as bot_token

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
api_url = f'https://api.telegram.org/bot{bot_token}'

def send_reminder(text):
    # Replace 'YOUR_GROUP_CHAT_ID' with your actual group chat ID
    group_chat_id = -1002059824895  # Replace with your actual group chat ID
    group = -1001354680838# https://t.me/c/1354680838/15650
    topic = 15650
    # # Sending a message to the group
    # group_url = f'{api_url}/sendMessage'
    # group_params = {'chat_id': group_chat_id, 'text': text}
    # requests.post(group_url, params=group_params)

    # Sending a message to a specific topic within the group
    topic_command = 30  # Replace with the actual command supported by your bot
    topic_message = text
    topic_url = f'{api_url}/sendMessage'
    topic_params = {'chat_id': group, 'text':  topic_message, 'reply_to_message_id':topic}
    requests.post(topic_url, params=topic_params)
