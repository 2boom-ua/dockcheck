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
	for container in containers:
		containersReturn.append(f"{container.name} {container.status}")
	return containersReturn

def get_str_from_file(filename):
	if os.path.exists(filename):
		with open(filename, "r") as data_file:
			ret = data_file.read().strip("\n")
		data_file.close()
		return ret
	return ""
	
def bold_html_txt(item):
	return f"<b>{item}</b>"
	
def telegram_message(message):
	try:
		if message != "":
			tb.send_message(CHAT_ID, message, parse_mode='html')
	except Exception as e:
		print(f"error: {e}")

if __name__ == "__main__":
	dockerClient = docker.DockerClient()		
	HOSTNAME = bold_html_txt(get_str_from_file("/proc/sys/kernel/hostname"))
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
		telegram_message(f"{HOSTNAME} (docker container)\ndocker containers monitor started: check period {SEC_REPEAT} sec.\n")
	else:
		print("config.yml not found")

@repeat(every(SEC_REPEAT).seconds)
def docker_check():
	STOPPED = False
	TMP_FILE = "/tmp/dockcheck.tmp"
	STATUS_DOT = ""
	ORANGE_DOT, GREEN_DOT, RED_DOT = "\U0001F7E0", "\U0001F7E2", "\U0001F534"
	listofcontainers = oldlistofcontainers = []
	containername = containerstatus = ""
	flistofcontainers = getContainers()
	for i in range(len(flistofcontainers)):
		listofcontainers.append(flistofcontainers[i])
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
				if STOPPED:
					containerstatus = "inactive"
				else:
					containerstatus = "".join(result[i]).split()[-1]
				containername = bold_html_txt(containername)
				if containerstatus == "running":
					STATUS_DOT = GREEN_DOT
				elif containerstatus == "inactive" or containerstatus == "removing" or containerstatus == "dead":
					STATUS_DOT = RED_DOT
				else:
					STATUS_DOT = ORANGE_DOT
				telegram_message(f"{HOSTNAME} (docker container)\n{STATUS_DOT} - {containername}: {containerstatus}\n")
				#print(f"{HOSTNAME} (docker container)\n{STATUS_DOT} - {containername}: {containerstatus}\n")
while True:
    run_pending()
    time.sleep(1)


	
	
	