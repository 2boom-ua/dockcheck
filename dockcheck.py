#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2024

import telebot
import yaml
import docker
import os
import time
from schedule import every, repeat, run_pending

def getContainers():
	docker_client = docker.from_env()
	containers = []
	[containers.append(f"{container.name} {container.status} {container.short_id}") for container in docker_client.containers.list(all=True)]
	return containers
	
def telegram_message(message : str):
	try:
		tb.send_message(CHAT_ID, message, parse_mode='markdown')
	except Exception as e:
		print(f"error: {e}")

if __name__ == "__main__":
	HOSTNAME = open('/proc/sys/kernel/hostname', 'r').read().strip('\n')
	CURRENT_PATH = "/root/dockcheck"
	SEC_REPEAT = 20
	if os.path.exists(f"{CURRENT_PATH}/config.yml"):
		with open(f"{CURRENT_PATH}/config.yml", 'r') as file:
			parsed_yaml = yaml.safe_load(file)
			TOKEN = parsed_yaml["telegram"]["TOKEN"]
			CHAT_ID = parsed_yaml["telegram"]["CHAT_ID"]
			SEC_REPEAT = parsed_yaml["timeout"]["SEC_REPEAT"]
		file.close()
		tb = telebot.TeleBot(TOKEN)
		telegram_message(f"*{HOSTNAME}* (docker)\ncontainers monitor started: check period {SEC_REPEAT} sec.\n")
	else:
		print("config.yml not found")

@repeat(every(SEC_REPEAT).seconds)
def docker_check():
	STOPPED = False
	TMP_FILE = "/tmp/dockcheck.tmp"
	ORANGE_DOT, GREEN_DOT, RED_DOT = "\U0001F7E0", "\U0001F7E2", "\U0001F534"
	STATUS_DOT = ORANGE_DOT
	listofcontainers = oldlistofcontainers = []
	stroldlistofcontainers, containername, containerid, containerstatus = "", "", "", "inactive"
	listofcontainers = getContainers()
	if not os.path.exists(TMP_FILE):
		with open(TMP_FILE, 'w') as file:
			file.write(",".join(listofcontainers))
		file.close()
	else:
		with open(TMP_FILE, 'r') as file:
			stroldlistofcontainers = file.read()
			oldlistofcontainers = stroldlistofcontainers.split(",")
		file.close()
	if len(listofcontainers) >= len(oldlistofcontainers):
		result = list(set(listofcontainers) - set(oldlistofcontainers)) 
	else:
		result = list(set(oldlistofcontainers) - set(listofcontainers))
		STOPPED = True
	if len(result) != 0:
		with open(TMP_FILE, 'w') as file:
			file.write(",".join(listofcontainers))
		file.close()
		for i in range(len(result)):
			containername = "".join(result[i]).split()[0]
			containerid  = "".join(result[i]).split()[-1]
			if containername != "":
				if not STOPPED: containerstatus = "".join(result[i]).split()[1]
				if containerstatus == "running":
					STATUS_DOT = GREEN_DOT
					if (containerid not in stroldlistofcontainers and containername in stroldlistofcontainers) and not STOPPED:
						containerstatus += " (changed)"
					elif (containerid not in stroldlistofcontainers and containername not in stroldlistofcontainers) and not STOPPED:
						containerstatus += " (started)"
				elif containerstatus == "inactive":
					STATUS_DOT = RED_DOT
			# ORANGE_DOT - created, paused, restarting, removing, exited
				telegram_message(f"*{HOSTNAME}* (docker)\n{STATUS_DOT} - *{containername}* ({containerid}) is _{containerstatus}_!\n")
while True:
    run_pending()
    time.sleep(1)


	
	
	