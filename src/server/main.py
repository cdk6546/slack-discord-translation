import datetime

from flask import Flask, request, jsonify

app = Flask(__name__)
slack_to_discord_stack = []
discord_to_slack_stack = []


@app.route('/discord-to-slack', methods=['POST'])
def discord_to_slack():
    data = request.get_json()
    username = data['username']
    content = data['content']
    timestamp = datetime.datetime.now().isoformat()  # Generate timestamp
    print(f"Received message from Discord: {username}: {content}: {timestamp}")

    data_tuple = (username, content)
    discord_to_slack_stack.append(data_tuple)

    # call slack message method

    return {'status': 'success'}


@app.route('/slack-to-discord', methods=['POST'])
def slack_to_discord():
    data = request.get_json()
    username = data['username']
    content = data['content']
    print(f"Received message from Slack: {username}: {content}")

    data_tuple = (username, content)
    slack_to_discord_stack.append(data_tuple)

    # call discord message method

    return {'status': 'success'}


@app.route('/get-messages-for-discord', methods=['GET'])
def get_messages_for_discord():
    messages = slack_to_discord_stack.copy()
    print(messages)
    slack_to_discord_stack.clear()
    return jsonify({'messages': messages}), 200


if __name__ == '__main__':
    app.run(port=3000, debug=True)
