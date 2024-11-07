import time
from threading import Thread

import discord
import os
import requests

from flask.cli import load_dotenv


# A class that represents the Discord bot instance
# Processes messages in a specific Discord channel to be mirrored
# in Slack.
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    # Upon a message received in the Discord channel, create and send
    # a POST request to the server for it to be mirrored
    async def on_message(self, message):
        # Logs a message that was sent in the server, for debugging purposes
        print(f'Message from {message.author}: {message.content}')

        # Does not allow a bot's previous mirror to be resent
        if message.author.id == self.user.id:
            return

        data = {
            "username": str(message.author.display_name),
            "content": message.content
        }

        try:
            # POST with the data from the message
            response = requests.post('http://localhost:3000/discord-to-slack', json=data)

            # Hopefully it's 200 OK
            print(f"Message sent with status code {response.status_code}")

        # If the post fails, throw an exception
        except requests.exceptions.RequestException as e:
            print(f"Failed to send message: {e}")

    # Sending message in a specific channel, called inside the check_for_messages
    # function when a Slack message needs mirrored to Discord
    async def send_message(self, message, username, channel_id):
        channel = self.get_channel(channel_id)
        await channel.send(f'message from {username}: {message}')


def check_for_messages(c):
    while True:
        try:
            print("Checking messages for Discord to send")

            # Sends a GET request to the server to get the messages to mirror from Slack
            # to Discord
            response = requests.get('http://localhost:3000/get-messages-for-discord')

            # If the GET request is successful, meaning, there is data to process...
            if response.status_code == 200:
                data = response.json()
                print(data)
                for msg in data.get('messages'):
                    username = msg[0]
                    content = msg[1]
                    channel_id = 804411959743086646
                    # Queue a task in the client to send this message
                    c.loop.create_task(client.send_message(content, username, channel_id))
            time.sleep(5)  # Check for new messages every 5 seconds
        except Exception as e:
            print(f"Error while checking messages: {e}")


# Initialize the client
def initialize_client():
    intents = discord.Intents.default()
    intents.message_content = True
    c = MyClient(intents=intents)
    return c


# Start up the client
def run_client(c):
    # Load the .ENV file variables
    load_dotenv()
    discord_token = os.getenv("DISCORD_BOT_TOKEN")

    # Run the client using the bot token
    c.run(discord_token)


if __name__ == '__main__':
    client = initialize_client()

    # Create a thread that runs alongside the client that
    # checks for messages to be mirrored from Slack to Discord
    thread = Thread(target=check_for_messages, args=(client,))
    thread.start()

    run_client(client)
