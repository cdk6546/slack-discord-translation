import json
import logging
import os
import time
from threading import Thread

import requests
from slack_sdk import WebClient
from dotenv import load_dotenv
import websocket as w

logging.basicConfig(level=logging.DEBUG)
load_dotenv()
app_token = os.environ["SLACK_APP_TOKEN"]
bot_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=bot_token)

bot_info = client.auth_test()
bot_user_id = bot_info["user_id"]
slack_channel_name = os.environ["DISCORD_CHANNEL_ID"]


# Check for messages from Discord to be mirrored to Slack every 5 seconds
def check_for_messages():
    while True:
        try:
            print("Checking messages for Slack to send")

            # Send a GET request to retrieve the messages to mirror from Discord to Slack
            response = requests.get('http://localhost:3000/get-messages-for-slack')

            # If the request is successful, we know there is data to process
            if response.status_code == 200:
                data = response.json()
                print(data)
                for msg in data.get('messages'):
                    username = msg[0]
                    content = msg[1]
                    client.chat_postMessage(channel=slack_channel_name, text=f"message from {username}: {content}")
            time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            print(f"Error while checking messages: {e}")


if __name__ == "__main__":
    thread = Thread(target=check_for_messages)
    thread.start()

    try:
        response = client.apps_connections_open(app_token=app_token)
        websocket_url = response.get("url")
        logging.info(response)
        logging.info(websocket_url)

        try:
            ws = w.create_connection(websocket_url)
            logging.info("Connected to WebSocket")
        except w.WebSocketConnectionClosedException as e:
            logging.warning("WebSocket connection closed unexpectedly: reconnecting")
            ws = w.create_connection(websocket_url)

        # Slack client is non-blocking, so we need to put it in a loop
        while True:
            # Receive the current event from the Slack websocket
            message = ws.recv()

            # Convert the event data to JSON format
            event = json.loads(message)
            logging.info(f"Received event: {event}")

            # Get the payload field from the JSON data
            payload = event.get("payload")

            # If there is a payload, meaning that it is a valid event
            if payload:
                # Get the event field to get the data from
                e = payload.get("event")

                # Event type
                t = e.get("type")

                # Content/text
                m = str(e.get("text"))

                # User ID
                b = str(e.get("user"))

                # Get name from User ID
                u = client.users_info(user=b).get('user').get('real_name')

                # If it's a message from a bot, aka a previously mirrored message,
                # it's invalid
                if b == bot_user_id:
                    continue

                # If the event type is a message, we want to process it.
                elif t == "message":

                    # Put the data into a JSON format
                    data = {
                        "username": u,
                        "content": m
                    }

                    try:
                        # Make a POST request so this message can be mirrored from Slack to Discord
                        response = requests.post('http://localhost:3000/slack-to-discord', json=data)
                        time.sleep(5)  # Delay 5 seconds between message events
                        print(f"Message sent with status code {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to send message: {e}")

    except Exception as e:
        logging.error(f"Error in WebSocket connection: {e}")
    finally:
        ws.close()
