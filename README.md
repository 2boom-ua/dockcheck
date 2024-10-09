## Docker Monitoring & Notification Script

This Python script monitors Docker resources (containers, images, volumes, networks) and sends notifications when changes are detected. It supports various messaging services.

<div align="center">  
    <img src="https://github.com/2boom-ua/dockchek/blob/main/screen_all.jpg?raw=true" alt="" width="949" height="483">
</div>


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
        "ON": false,
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
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "SLACK": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "GOTIFY": {
        "ON": false,
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
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "PUSHBULLET": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
    "PUSHOVER": {
        "ON": false,
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
        "ON": false,
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
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "ROCKET": {
        "ON": false,
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
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "PUMBLE": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "ZULIP": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "CUSTOM": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
        "STD_BOLDS" : [
            true,
            false,
            "...."
                ]
    },
    "STARTUP_MESSAGE": true,
    "COMPACT_MESSAGE": false,
    "DEFAULT_DOT_STYLE": true,
    "SEC_REPEAT": 10
}
```

| Item   | Required   | Description   |
|------------|------------|------------|
| STD_BOLDS | true/false | "**" **standard Markdown**, "*" *non-standard Markdown*
| | | Standard Markdown use - Pumble, Mattermost, Discord, Ntfy, Gotify |
| | | Non-standard Markdown use - Telegram, Zulip, Flock, Slack, RocketChat, Flock. |
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

