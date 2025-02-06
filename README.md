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
  - Webntfy
  - Custom

- **Customizable polling interval** through a configuration file (`config.json`).
- **Periodic checks** with Docker resource updates logged and reported.

### Requirements

- Python 3.X or higher
- Docker installed and running
- Dependencies: `docker`, `requests`, `schedule`
---

### Edit config.json:
You can use any name and any number of records for each messaging platform configuration, and you can also mix platforms as needed. The number of message platform configurations is unlimited.

[Configuration examples for Telegram, Matrix, Apprise, Pumble, Mattermost, Discord, Ntfy, Gotify, Zulip, Flock, Slack, Rocket.Chat, Pushover, Pushbullet](docs/json_message_config.md)
```
    "CUSTOM_NAME": {
        "ENABLED": false,
        "WEBHOOK_URL": [
            "first url",
            "second url",
            "...."
        ],
        "HEADER": [
            {first JSON structure},
            {second JSON structure},
            {....}
        ],
        "PYLOAD": [
            {first JSON structure},
            {second JSON structure},
            {....}
        ],
        "FORMAT_MESSAGE": [
            "markdown",
            "html",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Custom notifications |
| WEBHOOK_URL | url | The URL of your Custom webhook |
| HEADER | JSON structure | HTTP headers for each webhook request. This varies per service and may include fields like {"Content-Type": "application/json"}. |
| PAYLOAD | JSON structure | The JSON payload structure for each service, which usually includes message content and format. Like as  {"body": "message", "type": "info", "format": "markdown"}|
| FORMAT_MESSAGE | markdown,<br>html,<br>text,<br>simplified | Specifies the message format used by each service, such as markdown, html, or other text formatting.|

- **markdown** - a text-based format with lightweight syntax for basic styling (Pumble, Mattermost, Discord, Ntfy, Gotify),
- **simplified** - simplified standard Markdown (Telegram, Zulip, Flock, Slack, RocketChat).
- **html** - a web-based format using tags for advanced text styling,
- **text** - raw text without any styling or formatting.

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
---

### Clone the repository:
```
git clone https://github.com/2boom-ua/dockcheck.git
cd dockcheck
```
---
## Docker
```bash
  docker build -t dockcheck .
```
or
```bash
  docker pull ghcr.io/2boom-ua/dockcheck:latest
```
### Dowload and edit config.json
```bash
curl -L -o ./config.json  https://raw.githubusercontent.com/2boom-ua/dockcheck/main/config.json
```
### docker-cli
```bash
docker run -v ./config.json:/dockcheck/config.json -v /var/run/docker.sock:/var/run/docker.sock --name dockcheck -e TZ=UTC ghcr.io/2boom-ua/dockcheck:latest 
```
### docker-compose
```
version: "3.8"
services:
  dockcheck:
    image: ghcr.io/2boom-ua/dockcheck:latest
    container_name: dockcheck
    volumes:
      - ./config.json:/dockcheck/config.json
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - TZ=Etc/UTC
    restart: always
```

```bash
docker-compose up -d
```
---

## Running as a Linux Service
You can set this script to run as a Linux service for continuous monitoring.

### Install required Python packages:

```
pip install -r requirements.txt
```

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

### License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) for details.

### Author

- **2boom** - [GitHub](https://github.com/2boom-ua)

