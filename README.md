# dockchek
docker containers, images, volumes, networks informer for Telegram, Discord, Gotify as linux service

*** [Gotify - a simple server for sending and receiving messages (in real time per WebSocket). ](https://github.com/gotify/server)



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
	"SEC_REPEAT": 10,
	"GROUP_MESSAGE": true
}
```
**make as service**
```
nano /etc/systemd/system/dockcheck.service
```
```
[Unit]
Description=docker container status notifier
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
