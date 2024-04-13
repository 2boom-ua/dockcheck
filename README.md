# dockchek
A Docker State Change Monitor and Notifier (Telegram, Discord, Gotify, Ntfy, Pushbullet, Slack) as linux service

![alt text](https://github.com/2boom-ua/dockchek/blob/main/screen.jpg?raw=true)

```
pip install -r requirements.txt
```

**config.json**
```
{
	"TELEGRAM": {
		"ON": true,
		"TOKEN": "your_token",
		"CHAT_ID": "your_chat_id"
	},
	"DISCORD": {
		"ON": true,
		"WEB": "web_hook_url"
	},
	"GOTIFY": {
		"ON": true,
		"TOKEN": "your_token",
		"WEB": "server_url"
	},
	"NTFY": {
		"ON": true,
		"SUB": "your_subscribe",
		"WEB": "server_url"
	},
	"PUSHBULLET": {
		"ON": false,
		"API": "your_api_key"
	},
	"SLACK": {
		"ON": true,
		"WEB": "web_hook_url"
	},
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
