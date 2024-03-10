#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2024
# pip install telebot docker schedule

import telebot
import json
import docker
import os
import time
from schedule import every, repeat, run_pending

def getContainers():
	docker_client = docker.from_env()
	containers = []
	for container in docker_client.containers.list(all=True):
		try:
			containers.append(f"{container.name} {container.status} {container.attrs['State']['Health']['Status']} {container.short_id}")
		except KeyError:
			containers.append(f"{container.name} {container.status} {container.attrs['State']['Status']} {container.short_id}")
	return containers

def getContainersCount():
	docker_client = docker.from_env()
	count = len(docker_client.containers.list(all=True))
	return count

def telegram_message(message : str):
	try:
		tb.send_message(CHAT_ID, message, parse_mode="markdown")
	except Exception as e:
		print(f"error: {e}")

if __name__ == "__main__":
	HOSTNAME = open("/proc/sys/kernel/hostname", "r").read().strip("\n")
	CURRENT_PATH =  os.path.dirname(os.path.realpath(__file__))
	SEC_REPEAT = 20
	if os.path.exists(f"{CURRENT_PATH}/config.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/config.json", "r").read())
		SHORT_MESSAGE = parsed_json["SHORT_MESSAGE"]
		SEC_REPEAT = int(parsed_json["SEC_REPEAT"])
		TOKEN = parsed_json["TELEGRAM"]["TOKEN"]
		CHAT_ID = parsed_json["TELEGRAM"]["CHAT_ID"]
		tb = telebot.TeleBot(TOKEN)
		telegram_message(f"*{HOSTNAME}* (dockcheck)\n- polling period {SEC_REPEAT} seconds,\n- compact message {str(SHORT_MESSAGE).lower()},\n- currently monitoring {getContainersCount()} containers.")
	else:
		print("config.json not found")

@repeat(every(SEC_REPEAT).seconds)
def docker_check():
	STOPPED = False
	TMP_FILE = "/tmp/dockcheck.tmp"
	ORANGE_DOT, GREEN_DOT, RED_DOT = "\U0001F7E0", "\U0001F7E2", "\U0001F534"
	STATUS_DOT = ORANGE_DOT
	listofcontainers = oldlistofcontainers = []
	containername, containerid, containerattr, containerstatus =  "", "", "", "inactive"
	listofcontainers = getContainers()
	if not os.path.exists(TMP_FILE):
		with open(TMP_FILE, "w") as file:
			file.write(",".join(listofcontainers))
		file.close()
	with open(TMP_FILE, "r") as file:
		oldlistofcontainers = file.read().split(",")
	file.close()
	if len(listofcontainers) >= len(oldlistofcontainers):
		result = list(set(listofcontainers) - set(oldlistofcontainers)) 
	else:
		result = list(set(oldlistofcontainers) - set(listofcontainers))
		STOPPED = True
	if len(result) != 0:
		with open(TMP_FILE, "w") as file:
			file.write(",".join(listofcontainers))
		file.close()
		for i in range(len(result)):
			containername = "".join(result[i]).split()[0]
			if containername != "":
				containerattr = "".join(result[i]).split()[2]
				containerid  = "".join(result[i]).split()[-1]
				if not STOPPED: containerstatus = "".join(result[i]).split()[1]
				if containerstatus == "running":
					STATUS_DOT = GREEN_DOT
					containerstatus = containerattr
				elif containerstatus == "inactive":
					STATUS_DOT = RED_DOT
			# ORANGE_DOT - created, paused, restarting, removing, exited
				if SHORT_MESSAGE:
					telegram_message(f"*{HOSTNAME}* (dockcheck)\n*{containername}*: {containerstatus}\n")
				else:
					telegram_message(f"*{HOSTNAME}* (dockcheck)\n{STATUS_DOT} *{containername}:* ({containerid}), {containerstatus}!\n")
while True:
    run_pending()
    time.sleep(1)


	
	
	