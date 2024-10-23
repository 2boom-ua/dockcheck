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
  - Custom webhook

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

### Edit config.json:
A **config.json** file in the same directory as the script, and include your API tokens and configuration settings.

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
    "DISCORD": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "SLACK": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
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
    "NTFY": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "PUSHBULLET": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
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
    "MATTERMOST": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
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
    "FLOCK": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "PUMBLE": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "ZULIP": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "APPRISE": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ],
        "FORMATS": [
            "markdown"
        ]
    },
    "CUSTOM": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
        "CONTENT_NAMES": [
            "text",
            "body",
        "...."
        ],
        "FORMATS": [
            "asterisk",
            "markdown"
        ]
    },
    "MONITORING_RESOURCES": {
        "STACKS": true,
        "CONTAINERS": true,
        "NETWORKS": true,
        "VOLUMES": true,
        "IMAGES": true
    },
    "STARTUP_MESSAGE": true,
    "COMPACT_MESSAGE": false,
    "DEFAULT_DOT_STYLE": true,
    "SEC_REPEAT": 10
}
```
| Item | Required | Description |
|------------|------------|------------|
| **TELEGRAM** | | |
| ENABLED | true/false | Enable or disable Telegram notifications |
| TOKENS | String | The token of your Telegram bot |
| CHAT_IDS | String | The ID of the Telegram chat where notifications will be sent |
||||
| **DISCORD** | | |
| ENABLED | true/false | Enable or disable Discord notifications |
| WEBHOOK_URLS | url | The URL of your Discord webhook |
||||
| **SLACK** | | |
| ENABLED | true/false | Enable or disable Slack notifications |
| WEBHOOK_URLS | url | The URL of your Slack webhook |
||||
| **GOTIFY** | | |
| ENABLED | true/false | Enable or disable Gotify notifications |
| SERVER_URLS | url | The URL of your Gotify server |
| TOKENS | String | The token for your Gotify application |
||||
| **NTFY** | | |
| ENABLED | true/false | Enable or disable Ntfy notifications |
| WEBHOOK_URLS | url | The URL of your self-hosted Ntfy server (or use https://ntfy.sh) |
||||
| **PUSHBULLET** | | |
| ENABLED | true/false | Enable or disable Pushbullet notifications |
| TOKENS | String | The token for your Pushbullet application |
||||
| **PUSHOVER** | | |
| ENABLED | true/false | Enable or disable Pushover notifications |
| TOKENS | String | The token for your Pushover application |
| USER_KEYS | String | The user key for your Pushover application |
||||
| **MATRIX** | | |
| ENABLED | true/false | Enable or disable Matrix notifications |
| TOKENS | String | The token for your Matrix application |
| SERVER_URLS | url | The URL of your Matrix server  (or use https://matrix.org) |
||||
| **MATTERMOST** | | |
| ENABLED | true/false | Enable or disable Mattermost notifications |
| WEBHOOK_URLS | url | The URL of your Mattermost webhook |
||||
| **ROCKET** | | |
| ENABLED | true/false | Enable or disable Rocket.Chat notifications |
| SERVER_URLS | url | The URL of your Rocket.Chat server |
| TOKENS | String | The token for your Rocket.Chat application |
| CHANNEL_IDS | String | The ID of the Rocket.Chat channel where notifications will be sent |
||||
| **PUMBLE** | | |
| ENABLED | true/false | Enable or disable Pumble notifications |
| WEBHOOK_URLS | url | The URL of your Pumble webhook |
||||
| **ZULIP** | | |
| ENABLED | true/false | Enable or disable Zulip notifications |
| WEBHOOK_URLS | url | The URL of your Zulip webhook |
||||
| **FLOCK** | | |
| ENABLED | true/false | Enable or disable Flock notifications |
| WEBHOOK_URLS | url | The URL of your Flock webhook |
||||
| **APPRISE** | | |
| ENABLED | true/false | Enable or disable Apprise notifications |
| WEBHOOK_URLS | url | The URL of your Apprise webhook |
| FORMATS | markdown,<br>html,<br>text,<br>asterisk | The format(s) to be used for the notification (e.g., markdown/html/text/asterisk) |
||||
| **CUSTOM** | | |
| ENABLED | true/false | Enable or disable Custom notifications |
| WEBHOOK_URLS | url | The URL of your Custom webhook |
| FORMATS | markdown,<br>html,<br>text,<br>asterisk | The format(s) to be used for the notification (e.g., markdown/html/text/asterisk) |
| CONTENT_NAMES | text,<br>body,<br>content,<br>message | json = {"text/body/content/message": out_message} |

- **markdown** - a simple text-based format with lightweight syntax for basic styling (Pumble, Mattermost, Discord, Ntfy, Gotify),
- **html** - a web-based format using tags for advanced text styling,
- **text** - raw text without any styling or formatting.
- **asterisk** - non-standard Markdown (Telegram, Zulip, Flock, Slack, RocketChat).


| Item   | Required   | Description   |
|------------|------------|------------|
| MONITORING_RESOURCES | | |
| STACKS | true/false | monitoring docker stacks changes. | 
| CONTAINERS | true/false | monitoring docker containers changes. | 
| NETWORKS | true/false | monitoring docker nwtworks changes. | 
| VOLUMES | true/false | monitoring docker volumes changes. | 
| IMAGES | true/false | monitoring docker images changes. |
| | | |
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

