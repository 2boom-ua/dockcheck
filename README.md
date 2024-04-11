# dockchek
docker containers, images, volumes, networks informer for Telegram, Discord, Gotify, Ntfy, Pushbullet as linux service

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
		"WEB": "web_your_channel"
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
	"SEC_REPEAT": 10
}
```
**make as service**
```
nano /etc/systemd/system/dockcheck.service
```
```
[Unit]
Description=docker container informer
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
