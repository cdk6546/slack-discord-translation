# slack-discord-translation
an application to mirror messages from a slack channel to a discord channel and vice versa
## requirements
dependencies can be installed via the ```requirements.txt```, however, here's a list:
<blockquote><details>
  <summary>open me!</summary>
<ul>
<li>requests</li>
<li>websocket</li>
<li>websocket-client</li>
<li>python-dotenv</li>
<li>flask</li>
</ul>
</details></blockquote>

the following variables also need to exist in a ```.env``` file:
<blockquote><details>
  <summary>open me!</summary>
<ul>
<li>DISCORD_BOT_TOKEN</li>
<li>SLACK_CLIENT_ID</li>
<li>SLACK_CLIENT_SECRET</li>
<li>SLACK_BOT_TOKEN</li>
<li>SLACK_APP_TOKEN</li>
<li>DISCORD_CHANNEL_ID</li>
<li>SLACK_CHANNEL_NAME</li>
</ul>
</details></blockquote>

## how to run
<ul>
<li>first off, have all of the information needed in the <code>.env</code> file, aka all of the discord + slack api tokens</li>
<li>run <code>python main.py</code> inside all of the folders (./discord_b/, ./server/, ./slack/), starting all of the instances</li>
<li>send a message in either the specified discord channel or slack channel!</li>
</ul>
