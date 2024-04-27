#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2024

import json
import docker
import os
import time
import requests
from schedule import every, repeat, run_pending

def getHostname():
	hostname = ""
	if os.path.exists('/proc/sys/kernel/hostname'):
		with open('/proc/sys/kernel/hostname', "r") as file:
			hostname = file.read().strip('\n')
		file.close()
	return hostname

def getDockerEnv():
	docker_client = []
	try:
		docker_client = docker.from_env()
	except docker.errors.DockerException as e:
		print(f"Error connecting to Docker daemon: {e}")
	return docker_client

def getDockerCounts():
	dockerCounts = {"volumes": "0", "images": "0", "networks": "0", "containers": "0"}
	docker_client = getDockerEnv()
	if docker_client:
		dockerCounts["volumes"] = str(len(docker_client.volumes.list()))
		dockerCounts["images"] = str(len(docker_client.images.list()))
		dockerCounts["networks"] = str(len(docker_client.networks.list()))
		dockerCounts["containers"] = str(len(docker_client.containers.list()))
	return dockerCounts

def getDockerData(what):
	returndata = []
	docker_client = getDockerEnv()
	if docker_client:
		if what == "network":
			for network in docker_client.networks.list():
				returndata.append(f"{network.name}")
		elif what == "image":
			for image in docker_client.images.list():
				imagename = ''.join(image.tags).split(':')[0].split('/')[-1]
				if imagename == '': imagename = image.short_id.split(':')[-1]
				returndata.append(f"{image.short_id.split(':')[-1]} {imagename}")
		else:
			for volume in docker_client.volumes.list():
				returndata.append(f"{volume.short_id}")
	return returndata

def getContainers():
	containers = []
	docker_client = getDockerEnv()
	if docker_client: 
		for container in docker_client.containers.list(all=True):
			container_info = docker_client.api.inspect_container(container.id)
			if "State" in container_info and "Health" in container_info["State"]:
				containers.append(f"{container.name} {container.status} {container.attrs['State']['Health']['Status']} {container.short_id}")
			else:
				containers.append(f"{container.name} {container.status} {container.attrs['State']['Status']} {container.short_id}")
	return containers
	
def send_message(message : str):
	message = message.replace("\t", "")
	if TELEGRAM_ON:
		try:
			response = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if DISCORD_ON:
		try:
			response = requests.post(DISCORD_WEB, json={"content": message.replace("*", "**")})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if SLACK_ON:
		try:
			response = requests.post(SLACK_WEB, json = {"text": message})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	message = message.replace("*", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if GOTIFY_ON:
		try:
			response = requests.post(f"{GOTIFY_WEB}/message?token={GOTIFY_TOKEN}",\
			json={'title': header, 'message': message, 'priority': 0})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if NTFY_ON:
		try:
			response = requests.post(f"{NTFY_WEB}/{NTFY_SUB}", data=message.encode(encoding='utf-8'), headers={"Title": header})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if PUSHBULLET_ON:
		try:
			response = requests.post('https://api.pushbullet.com/v2/pushes',\
			json={'type': 'note', 'title': header, 'body': message},\
			headers={'Access-Token': PUSHBULLET_API, 'Content-Type': 'application/json'})
		except requests.exceptions.RequestException as e:
			print("error:", e)

if __name__ == "__main__":
	HOSTNAME = getHostname()
	CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
	SEC_REPEAT = 20
	TELEGRAM_ON = DISCORD_ON = GOTIFY_ON = NTFY_ON = SLACK_ON = PUSHBULLET_ON = False
	TOKEN = CHAT_ID = DISCORD_WEB = GOTIFY_WEB = GOTIFY_TOKEN = NTFY_WEB = NTFY_SUB = PUSHBULLET_API = SLACK_WEB = MESSAGING_SERVICE = ""
	dockerCounts = getDockerCounts()
	if os.path.exists(f"{CURRENT_PATH}/config.json"):
		with open(f"{CURRENT_PATH}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		file.close()
		SEC_REPEAT = int(parsed_json["SEC_REPEAT"])
		TELEGRAM_ON = parsed_json["TELEGRAM"]["ON"]
		DISCORD_ON = parsed_json["DISCORD"]["ON"]
		GOTIFY_ON = parsed_json["GOTIFY"]["ON"]
		NTFY_ON = parsed_json["NTFY"]["ON"]
		PUSHBULLET_ON = parsed_json["PUSHBULLET"]["ON"]
		SLACK_ON = parsed_json["SLACK"]["ON"]
		if TELEGRAM_ON:
			TOKEN = parsed_json["TELEGRAM"]["TOKEN"]
			CHAT_ID = parsed_json["TELEGRAM"]["CHAT_ID"]
			MESSAGING_SERVICE += "- messenging: Telegram,\n"
		if DISCORD_ON:
			DISCORD_WEB = parsed_json["DISCORD"]["WEB"]
			MESSAGING_SERVICE += "- messenging: Discord,\n"
		if GOTIFY_ON:
			GOTIFY_WEB = parsed_json["GOTIFY"]["WEB"]
			GOTIFY_TOKEN = parsed_json["GOTIFY"]["TOKEN"]
			MESSAGING_SERVICE += "- messenging: Gotify,\n"
		if NTFY_ON:
			NTFY_WEB = parsed_json["NTFY"]["WEB"]
			NTFY_SUB = parsed_json["NTFY"]["SUB"]
			MESSAGING_SERVICE += "- messenging: Ntfy,\n"
		if PUSHBULLET_ON:
			PUSHBULLET_API = parsed_json["PUSHBULLET"]["API"]
			MESSAGING_SERVICE += "- messenging: Pushbullet,\n"
		if SLACK_ON:
			SLACK_WEB = parsed_json["SLACK"]["WEB"]
			MESSAGING_SERVICE += "- messenging: Slack,\n"
		send_message(f"*{HOSTNAME}* (docker-check)\ndocker monitor:\n{MESSAGING_SERVICE}\
		- monitoring: {dockerCounts['containers']} containers,\n\
		- monitoring: {dockerCounts['images']} images,\n\
		- monitoring: {dockerCounts['networks']} networks,\n\
		- monitoring: {dockerCounts['volumes']} volumes,\n\
		- polling period: {SEC_REPEAT} seconds.")
	else:
		print("config.json not found")
		
@repeat(every(SEC_REPEAT).seconds)
def docker_checker():
	ORANGE_DOT, GREEN_DOT, RED_DOT, YELLOW_DOT = "\U0001F7E0", "\U0001F7E2", "\U0001F534", "\U0001F7E1"
	#docker-image-network-volume
	tmpfiles = ["/tmp/dockimage.tmp", "/tmp/docknetworks.tmp", "/tmp/dockvolume.tmp"]
	typeofcheck = ["image", "network", "volume"]
	for j in range(len(tmpfiles)):
		TMP_FILE = tmpfiles[j]
		STATUS_DOT = GREEN_DOT
		STATUS_MESSAGE, MESSAGE, HEADER_MESSAGE = "", "", f"*{HOSTNAME}* (docker-{typeofcheck[j]})\n"
		ListOfItem = oldListOfItem = result = []
		imagename = imageid = ""
		ListOfItem = getDockerData(typeofcheck[j])
		if ListOfItem:
			if not os.path.exists(TMP_FILE):
				with open(TMP_FILE, "w") as file:
					file.write(",".join(ListOfItem))
				file.close()
			with open(TMP_FILE, "r") as file:
				oldListOfItem = file.read().split(",")
			file.close()
			if len(ListOfItem) >= len(oldListOfItem):
				result = list(set(ListOfItem) - set(oldListOfItem))
				STATUS_DOT = YELLOW_DOT
				STATUS_MESSAGE = "created"
			else:
				result = list(set(oldListOfItem) - set(ListOfItem))
				STATUS_DOT = RED_DOT
				STATUS_MESSAGE = "removed"
			if result:
				with open(TMP_FILE, "w") as file:
					file.write(",".join(ListOfItem))
				file.close()
				for i in range(len(result)):
					if typeofcheck[j] == "image":
						imagename = result[i].split()[-1]
						imageid = result[i].split()[0]
						if imageid == imagename:
							if imageid in ",".join(oldListOfItem) and STATUS_DOT != RED_DOT: STATUS_MESSAGE = "stored"
							MESSAGE += f"{STATUS_DOT} *{imagename}*: {STATUS_MESSAGE}!\n"
						else:
							MESSAGE += f"{STATUS_DOT} *{imagename}* ({imageid}): {STATUS_MESSAGE}!\n"
					else:
						MESSAGE += f"{STATUS_DOT} *{result[i]}*: {STATUS_MESSAGE}!\n"
					if STATUS_DOT == YELLOW_DOT: STATUS_MESSAGE = "created"
				MESSAGE = "\n".join(sorted(MESSAGE.split("\n"))).lstrip("\n")
				send_message(f"{HEADER_MESSAGE}{MESSAGE}")
		
	#docker-container
	TMP_FILE = "/tmp/dockcontainer.tmp"
	STOPPED = False
	STATUS_DOT = ORANGE_DOT
	MESSAGE, HEADER_MESSAGE = "", f"*{HOSTNAME}* (docker-container)\n"
	ListOfItem = oldListOfItem = result = []
	containername, containerattr, containerstatus = "", "", "inactive"
	ListOfItem = getContainers()
	if ListOfItem:
		if not os.path.exists(TMP_FILE):
			with open(TMP_FILE, "w") as file:
				file.write(",".join(ListOfItem))
			file.close()
		with open(TMP_FILE, "r") as file:
			oldListOfItem = file.read().split(",")
		file.close()
		if len(ListOfItem) >= len(oldListOfItem):
			result = list(set(ListOfItem) - set(oldListOfItem)) 
		else:
			result = list(set(oldListOfItem) - set(ListOfItem))
			STOPPED = True
		if result:
			with open(TMP_FILE, "w") as file:
				file.write(",".join(ListOfItem))
			file.close()
			for i in range(len(result)):
				containername = "".join(result[i]).split()[0]
				if containername != "":
					containerattr = "".join(result[i]).split()[2]
					if not STOPPED: containerstatus = "".join(result[i]).split()[1]
					if containerstatus == "running":
						STATUS_DOT = GREEN_DOT
						if containerattr != containerstatus: containerstatus = f"{containerstatus} ({containerattr})"
						if containerattr == "unhealthy": STATUS_DOT = ORANGE_DOT
					elif containerstatus == "inactive": STATUS_DOT = RED_DOT
					MESSAGE += f"{STATUS_DOT} *{containername}*: {containerstatus}!\n"
			MESSAGE = "\n".join(sorted(MESSAGE.split("\n"))).lstrip("\n")
			send_message(f"{HEADER_MESSAGE}{MESSAGE}")

while True:
    run_pending()
    time.sleep(1)
