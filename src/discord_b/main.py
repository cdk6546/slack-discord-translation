import time
from threading import Thread

import discord
import os
import requests

from flask.cli import load_dotenv


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author.id == self.user.id:
            return

        data = {
            "username": str(message.author),
            "content": message.content
        }

        try:
            response = requests.post('http://localhost:3000/discord-to-slack', json=data)
            print(f"Message sent with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send message: {e}")

        if message.content.startswith('!hello'):
            await message.reply('Hello!', mention_author=True)

    async def send_message(self, message, username, channel_id):
        channel = self.get_channel(channel_id)
        await channel.send(f'message from {username}: {message}')


def check_for_messages(c):
    while True:
        try:
            response = requests.get('http://localhost:3000/get-messages-for-discord')
            if response.status_code == 200:
                data = response.json()
                print(data)
                for msg in data.get('messages'):
                    username = msg[0]
                    content = msg[1]
                    channel_id = 804411959743086646
                    c.loop.create_task(client.send_message(content, username, channel_id))
            time.sleep(5)  # Check every 5 seconds
            print("check")
        except Exception as e:
            print(f"Error while checking messages: {e}")


def initialize_client():
    intents = discord.Intents.default()
    intents.message_content = True
    c = MyClient(intents=intents)
    return c


def run_client(c):
    load_dotenv()
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    c.run(discord_token)


if __name__ == '__main__':
    client = initialize_client()

    thread = Thread(target=check_for_messages, args=(client,))
    thread.start()

    run_client(client)

