# dockchek
docker container status notifier

**config.json**
```
{
	"TELEGRAM": {
		"TOKEN": "your_token",
		"CHAT_ID": "your_chat_id"
	},
	"MIN_REPEAT": 1
}
```
**make as service**
```
nano /etc/systemd/system/dockcheck.service
```
```
[Unit]
Description=check active docker's containers
After=multi-user.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /root/dockcheck/dockcheck.py

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
