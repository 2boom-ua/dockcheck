# dockcheck

Python script monitors Docker resources (containers, images, networks, and volumes) on a node and sends notifications when changes occur. 

Resource Counting: Counts Docker volumes, images, networks, and containers.
Detailed Data Retrieval: Gathers detailed information on Docker resources, including unused networks and volumes.
Messaging Integration: Sends notifications via multiple platforms (Telegram, Discord, Slack, Gotify, Ntfy, Pushbullet, and Pushover) whenever there are changes, like new images being pulled, containers stopping, or networks being created or removed.
Periodic Monitoring: The script runs continuously, checking for updates at regular intervals specified in a configuration file (config.json).

The script is designed to keep Docker administrators informed about the state of their Docker environment, alerting them to changes that could indicate potential issues or necessary actions. 

![alt text](https://github.com/2boom-ua/dockchek/blob/main/screen_all.jpg?raw=true)


```
pip install -r requirements.txt
```

**config.json**
```
{
    "TELEGRAM": {
        "ON": true,
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
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
    "SLACK": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
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
        "ON": true,
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
    "PUSHBULLET": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
    "PUSHOVER": {
        "ON": true,
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
    "DEFAULT_DOT_STYLE": true,
    "SEC_REPEAT": 10
}
```
**make as service**
```
nano /etc/systemd/system/dockcheck.service
```
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
```
systemctl daemon-reload
```
```
systemctl enable dockcheck.service
```
```
systemctl start dockcheck.service
```
