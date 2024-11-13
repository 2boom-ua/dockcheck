## Docker Monitoring & Notification Script

This Python script monitors Docker resources (containers, images, volumes, networks) and sends notifications when changes are detected. It supports various messaging services.

<div align="center">  
    <img src="https://github.com/2boom-ua/dockchek/blob/main/screen_all.jpg?raw=true" alt="" width="949" height="483">
</div>


*The idea for this software was inspired by* [petersem/monocker](https://github.com/petersem/monocker)

### Features

- **Monitors Docker resources:**
  - Containers (running, stopped, created, unhealthy, etc.)
  - Images (pulled, removed, unused)
  - Volumes and Networks (created, removed, unused)
- **Real-time notifications with support for multiple accounts** via:
  - Telegram
  - Discord
  - Slack
  - Gotify
  - Ntfy
  - Pushbullet
  - Pushover
  - Rocket.chat
  - Matrix
  - Mattermost
  - Zulip
  - Pumble
  - Flock
  - Apprise
  - Custom

- **Customizable polling interval** through a configuration file (`config.json`).
- **Periodic checks** with Docker resource updates logged and reported.

### Requirements

- Python 3.x
- Docker installed and running
- Dependencies: `docker`, `requests`, `schedule`

### Clone the repository:
```
git clone https://github.com/2boom-ua/dockcheck.git
cd dockcheck
```
### Install required Python packages:

```
pip install -r requirements.txt
```

## Edit config.json:
A **config.json** file in the same directory as the script, and include your API tokens and configuration settings.

#### TELEGRAM
```
{
    "TELEGRAM": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "CHAT_IDS": [
            "first chat_id",
            "second chat_id",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Telegram notifications |
| TOKENS | String | The token of your Telegram bot |
| CHAT_IDS | String | The ID of the Telegram chat where notifications will be sent |


#### DISCORD
```
    "DISCORD": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Discord notifications |
| WEBHOOK_URLS | url | The URL of your Discord webhook |


#### SLACK
```
    "SLACK": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Slack notifications |
| WEBHOOK_URLS | url | The URL of your Slack webhook |


#### GOTIFY
```
    "GOTIFY": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "CHAT_URLS": [
            "first server_url",
            "second server_url",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Gotify notifications |
| SERVER_URLS | url | The URL of your Gotify server |
| TOKENS | String | The token for your Gotify application |


#### NTFY
```
    "NTFY": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Ntfy notifications |
| WEBHOOK_URLS | url | The URL of your self-hosted Ntfy server (or use https://ntfy.sh) |


#### PUSHBULLET
```
    "PUSHBULLET": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Pushbullet notifications |
| TOKENS | String | The token for your Pushbullet application |


#### PUSHOVER
```
    "PUSHOVER": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "USER_KEYS": [
            "first user_key",
            "second user_key",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Pushover notifications |
| TOKENS | String | The token for your Pushover application |
| USER_KEYS | String | The user key for your Pushover application |


#### MATRIX
```
    "MATRIX": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "SERVER_URLS": [
            "first server_url",
            "second server_url",
            "...."
        ],
        "ROOM_IDS": [
            "!first room_id",
            "!second room_id",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Matrix notifications |
| TOKENS | String | The token for your Matrix application |
| SERVER_URLS | url | The URL of your Matrix server |


#### MATTERMOST
```
    "MATTERMOST": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Mattermost notifications |
| WEBHOOK_URLS | url | The URL of your Mattermost webhook |


#### ROCKET
```
    "ROCKET": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
		"USER_IDS": [
            "first user_id",
            "second user_id",
            "...."
        ],
        "SERVER_URLS": [
           "first server_url",
            "second server_url",
            "...."
        ],
		"CHANNEL_IDS": [
            "#first channel",
            "#second channel",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Rocket.Chat notifications |
| SERVER_URLS | url | The URL of your Rocket.Chat server |
| TOKENS | String | The token for your Rocket.Chat application |
| CHANNEL_IDS | String | The ID of the Rocket.Chat channel where notifications will be sent |


#### FLOCK
```
    "FLOCK": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Flock notifications |
| WEBHOOK_URLS | url | The URL of your Flock webhook |


#### PUMBLE
```
    "PUMBLE": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Pumble notifications |
| WEBHOOK_URLS | url | The URL of your Pumble webhook |


#### ZULIP
```
    "ZULIP": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Zulip notifications |
| WEBHOOK_URLS | url | The URL of your Zulip webhook |


#### APPRISE
```
    "APPRISE": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ],
        "FORMAT_MESSAGES": [
            "markdown",
            "html",
            ...
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Apprise notifications |
| WEBHOOK_URLS | url | The URL of your Apprise webhook |
| FORMATS | markdown,<br>html,<br>text,<br>asterisk | The format(s) to be used for the notification (e.g., markdown/html/text/asterisk) |


#### CUSTOM
```
    "CUSTOM": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ],
        "HEADERS": [
            {first JSON structure},
            {second JSON structure},
            ...
        ],
        "PYLOADS": [
            {first JSON structure},
            {second JSON structure},
            ...
        ],
        "FORMAT_MESSAGES": [
            "markdown",
            "html",
            ...
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| **CUSTOM** | | |
| ENABLED | true/false | Enable or disable Custom notifications |
| WEBHOOK_URLS | url | The URL of your Custom webhook |
| HEADERS | JSON structure | HTTP headers for each webhook request. This varies per service and may include fields like {"Content-Type": "application/json"}. |
| PAYLOAD | JSON structure | The JSON payload structure for each service, which usually includes message content and format. Like as  {"body": "message", "type": "info", "format": "markdown"}|
| FORMAT_MESSAGE | markdown,<br>html,<br>text,<br>asterisk | Specifies the message format used by each service, such as markdown, html, or other text formatting.|

- **markdown** - a simple text-based format with lightweight syntax for basic styling (Pumble, Mattermost, Discord, Ntfy, Gotify),
- **html** - a web-based format using tags for advanced text styling,
- **text** - raw text without any styling or formatting.
- **asterisk** - non-standard Markdown (Telegram, Zulip, Flock, Slack, RocketChat).

##### Examples for Telegram, Matrix, Apprise, Ntfy, Zulip, Gotify, Pushover, Pushbullet
you can use any name except predefined TELEGRAM, DISCORD, GOTIFY, NTFY, PUSHBULLET, PUSHOVER, SLACK, MATRIX, MATTERMOST, PUMBLE, ROCKET, ZULIP, FLOCK, APPRISE, also use any number of CUSTOM blocks
```
    "CUSTOM": {
        "ENABLED": true,
        "WEBHOOK_URLS": [
            "https://api.telegram.org/bot{token}/sendMessage",
            "{server_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message?access_token={token}",
            "{server_url}/notify/{config_id}",
            "{server_url}/{subsribe}",
            "{organizattion}.zulipchat.com/api/v1/external/slack_incoming?api_key={api_key}",
            "{server_url}/message?token={token}",
            "https://api.pushover.net/1/messages.json",
            "https://api.pushbullet.com/v2/pushes"
        ],
        "HEADERS": [
            {},
            {"Content-Type": "application/json"},
            {"Content-Type": "application/json"},
            {"Content-Type": "text/markdown"},
            {},
            {},
            {"Content-type": "application/json"},
            {"Content-Type": "application/json", "Access-Token": "{token}"}
        ],
        "PYLOADS": [
            {"chat_id": "{chat_id}", "text": "message", "parse_mode": "Markdown"},
            {"msgtype": "m.text", "body": "message", "format": "org.matrix.custom.html", "formatted_body": "message"},
            {"body": "message", "type": "info", "format": "markdown"},
            {"data": "message"},
            {"text": "message"},
            {"title": "title", "message": "message", "priority": 0, "extras": {"client::display": {"contentType": "text/markdown"}}},
            {"token": "{token}", "user": "{user_key}", "title": "header", "message": "message", "html": "1"},
            {"type": "note", "title": "header", "body": "message"}
        ],
        "FORMAT_MESSAGES": [
            "asterisk",
            "html",
            "markdown",
            "markdown",
            "asterisk",
            "markdown",
            "markdown",
            "text"
        ]
    }
```

```
"MONITORING_RESOURCES": {
        "STACKS": true,
        "CONTAINERS": true,
        "NETWORKS": true,
        "VOLUMES": true,
        "IMAGES": true
    },
```

| Item   | Required   | Description   |
|------------|------------|------------|
| **MONITORING_RESOURCES** | | |
| STACKS | true/false | monitoring docker stacks changes. | 
| CONTAINERS | true/false | monitoring docker containers changes. | 
| NETWORKS | true/false | monitoring docker nwtworks changes. | 
| VOLUMES | true/false | monitoring docker volumes changes. | 
| IMAGES | true/false | monitoring docker images changes. |

```
    "STARTUP_MESSAGE": true,
    "COMPACT_MESSAGE": false,
    "DEFAULT_DOT_STYLE": true,
    "SEC_REPEAT": 10
```
| Item   | Required   | Description   |
|------------|------------|------------|
| STARTUP_MESSAGE | true/false | On/Off startup message. | 
| COMPACT_MESSAGE | true/false | On/Off compact format message. | 
| DEFAULT_DOT_STYLE | true/false | Round/Square dots. |
| SEC_REPEAT | 10 | Set the poll period in seconds. Minimum is 10 seconds. | 

## Running as a Linux Service
You can set this script to run as a Linux service for continuous monitoring.

Create a systemd service file:
```
nano /etc/systemd/system/dockcheck.service
```
Add the following content:

```
[Unit]
Description=docker state change monitor
After=multi-user.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /opt/dockcheck/dockcheck.py

[Install]
WantedBy=multi-user.target
```
Start and enable the service:

```
systemctl daemon-reload
```
```
systemctl enable dockcheck.service
```
```
systemctl start dockcheck.service
```

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) for details.

## Author

- **2boom** - [GitHub](https://github.com/2boom-ua)

