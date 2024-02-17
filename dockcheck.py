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
	containersReturn = []
	containers = dockerClient.containers.list(all=True)
	[containersReturn.append(f"{container.name} {container.status}") for container in containers]
	return containersReturn
	
def telegram_message(message : str):
	try:
		tb.send_message(CHAT_ID, message, parse_mode='markdown')
	except Exception as e:
		print(f"error: {e}")

if __name__ == "__main__":
	dockerClient = docker.DockerClient()
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
	containername, containerstatus = "", "inactive"
	flistofcontainers = getContainers()
	[listofcontainers.append(flistofcontainers[i]) for i in range(len(flistofcontainers))]
	if not os.path.exists(TMP_FILE):
		with open(TMP_FILE, 'w') as file:
			file.write(",".join(listofcontainers))
		file.close()
	with open(TMP_FILE, 'r') as file:
		oldlistofcontainers = file.read().split(",")
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
			if containername != "":
				if not STOPPED:
					containerstatus = "".join(result[i]).split()[-1]
				if containerstatus == "running":
					STATUS_DOT = GREEN_DOT
				elif containerstatus == "inactive":
					STATUS_DOT = RED_DOT
				# restarting, paused, exited
				telegram_message(f"*{HOSTNAME}* (docker)\n{STATUS_DOT} - *{containername}* is {containerstatus}!\n")
while True:
    run_pending()
    time.sleep(1)


	
	
	