# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2024

import telebot
import yaml
import docker
import os
import time
from schedule import every, repeat, run_pending

dockerClient = docker.DockerClient()

def getContainers():
	containersReturn = []
	containers = dockerClient.containers.list(all=True)
	for container in containers:
		containersReturn.append(f"{container} {container.image} {container.status}")
	return containersReturn

def get_str_from_file(filename):
	if os.path.exists(filename):
		with open(filename, "r") as data_file:
			ret = data_file.read().strip("\n")
		data_file.close()
		return ret
	return ""
	
def hbold(item):
	return telebot.formatting.hbold(item)
	
def telegram_message(message):
	try:
		if message != "":
			tb.send_message(CHAT_ID, message, parse_mode='html')
	except Exception as e:
		print(f"error: {e}")
		
def check_docker_status():
	try:
		client = docker.from_env()
		client.ping()
		return True
	except:
		return False
		
HOSTNAME = hbold(get_str_from_file("/proc/sys/kernel/hostname"))
CURRENT_PATH = "/root/dockcheck"
ORANGE_DOT, GREEN_DOT, RED_DOT = "\U0001F7E0", "\U0001F7E2", "\U0001F534"
SEC_REPEAT = 20
if os.path.exists(f"{CURRENT_PATH}/config.yml"):
	with open(f"{CURRENT_PATH}/config.yml", 'r') as file:
		parsed_yaml = yaml.safe_load(file)
		TOKEN = parsed_yaml["telegram"]["TOKEN"]
		CHAT_ID = parsed_yaml["telegram"]["CHAT_ID"]
		SEC_REPEAT = parsed_yaml["timeout"]["SEC_REPEAT"]
		file.close()
	tb = telebot.TeleBot(TOKEN)
	telegram_message(f"{HOSTNAME} (dockcheck)\ndocker containers monitor started: check period {SEC_REPEAT} sec.\n")
else:
	print("config.yml not found")

@repeat(every(SEC_REPEAT).seconds)
def docker_check():
	STOPPED = False
	STATUS_DOT = ""
	listofcontainers = oldlistofcontainers = []
	containername = containerstatus = ""

	flistofcontainers = getContainers()
	for i in range(len(flistofcontainers)):
		listofcontainers.append(flistofcontainers[i])
	if not os.path.exists(f"/tmp/dockcheck.tmp"):
		with open('/tmp/dockcheck.tmp', 'w') as file:
			file.write(",".join(listofcontainers))
		file.close()
	with open('/tmp/dockcheck.tmp', 'r') as file:
		oldlistofcontainers = file.read().split(",")
	file.close()
	
	if len(listofcontainers) >= len(oldlistofcontainers):
		result = list(set(listofcontainers) - set(oldlistofcontainers)) 
	else:
		result = list(set(oldlistofcontainers) - set(listofcontainers))
		STOPPED = True
	if len(result) != 0:
		with open('/tmp/dockcheck.tmp', 'w') as file:
			file.write(",".join(listofcontainers))
		file.close()
		for i in range(len(result)):
			containername = "".join(result[i]).split("'")[1].split(":")[0].split("/")[-1]
			if STOPPED:
				containerstatus = "inactive"
			else:
				containerstatus = "".join(result[i]).split()[-1]
		
			containername = hbold(containername)
			if containerstatus == "running":
				STATUS_DOT = GREEN_DOT
			elif containerstatus == "inactive":
				STATUS_DOT = RED_DOT
			else:
				STATUS_DOT = ORANGE_DOT
			telegram_message(f"{HOSTNAME} (dockcheck)\n{STATUS_DOT} - {containername} ({containerstatus})\n")
			print(f"{HOSTNAME} (dockcheck)\n{STATUS_DOT} - {containername} ({containerstatus})\n")
while True:
    run_pending()
    time.sleep(1)


	
	
	