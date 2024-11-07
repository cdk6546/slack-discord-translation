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


def check_for_messages():
    while True:
        try:
            print("Checking messages for Slack to send")
            response = requests.get('http://localhost:3000/get-messages-for-slack')
            if response.status_code == 200:
                data = response.json()
                print(data)
                for msg in data.get('messages'):
                    username = msg[0]
                    content = msg[1]
                    client.chat_postMessage(channel='#bot', text=f"message from {username}: {content}")
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

        while True:
            message = ws.recv()
            logging.info(f"Raw WebSocket message: {message}")
            event = json.loads(message)
            logging.info(f"Received event: {event}")
            payload = event.get("payload")
            if payload:
                e = payload.get("event")
                t = e.get("type")
                m = str(e.get("text"))
                b = str(e.get("user"))
                u = client.users_info(user=b).get('user').get('real_name')
                logging.info(b)
                if b == bot_user_id:
                    logging.info("Ignoring own message")
                    continue
                elif t == "message":
                    data = {
                        "username": u,
                        "content": m
                    }

                    try:
                        response = requests.post('http://localhost:3000/slack-to-discord', json=data)
                        time.sleep(5)
                        print(f"Message sent with status code {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to send message: {e}")

                    client.chat_postMessage(channel='#bot', text="Hello, Slack from WebSocket!")

    except Exception as e:
        logging.error(f"Error in WebSocket connection: {e}")
    finally:
        ws.close()
