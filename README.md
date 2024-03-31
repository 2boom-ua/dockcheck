# dockchek
docker containers, images, volumes status notifier for Telegram, Discord

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
