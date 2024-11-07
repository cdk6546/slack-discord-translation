import datetime

from flask import Flask, request, jsonify

app = Flask(__name__)

# The stack data structure that holds messages
# to be mirrored from Slack to Discord
slack_to_discord_stack = []

# The stack data structure that holds messages
# to be mirrored from Discord to Slack
discord_to_slack_stack = []


# The processing for a POST request to add messages to the
# discord_to_slack stack
@app.route('/discord-to-slack', methods=['POST'])
def discord_to_slack():
    data = request.get_json()
    username = data['username']
    content = data['content']
    timestamp = datetime.datetime.now().isoformat()  # Generate timestamp
    print(f"Received message from Discord: {username}: {content}: {timestamp}")

    data_tuple = (username, content)
    discord_to_slack_stack.append(data_tuple)

    return {'status': 'success'}

# The processing for a POST request to add messages to the
# slack_to_discord stack
@app.route('/slack-to-discord', methods=['POST'])
def slack_to_discord():
    data = request.get_json()
    username = data['username']
    content = data['content']
    timestamp = datetime.datetime.now().isoformat()  # Generate timestamp

    print(f"Received message from Slack: {username}: {content}: {timestamp}")

    data_tuple = (username, content)
    slack_to_discord_stack.append(data_tuple)

    return {'status': 'success'}

# The processing for a GET request to get messages from the
# slack_to_discord stack
@app.route('/get-messages-for-discord', methods=['GET'])
def get_messages_for_discord():
    messages = slack_to_discord_stack.copy()
    print(messages)
    slack_to_discord_stack.clear()
    return jsonify({'messages': messages}), 200

# The processing for a GET request to get messages from the
# discord_to_slack stack
@app.route('/get-messages-for-slack', methods=['GET'])
def get_messages_for_slack():
    messages = discord_to_slack_stack.copy()
    print(messages)
    discord_to_slack_stack.clear()
    return jsonify({'messages': messages}), 200


if __name__ == '__main__':
    app.run(port=3000, debug=True)
