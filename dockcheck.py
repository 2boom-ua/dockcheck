#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2024

import telebot
import json
import docker
import os
import time
import requests
import discord_notify as dn
from schedule import every, repeat, run_pending

def getDockerCounts():
	docker_online = True
	try:
		docker_client = docker.from_env()
	except docker.errors.DockerException as e:
		print(f"Error connecting to Docker daemon: {e}")
		docker_online = False
	dockerCounts = {"volumes": "0", "images": "0", "networks": "0", "containers": "0"}
	if docker_online:
		dockerCounts["volumes"] = str(len(docker_client.volumes.list()))
		dockerCounts["images"] = str(len(docker_client.images.list()))
		dockerCounts["networks"] = str(len(docker_client.networks.list()))
		dockerCounts["containers"] = str(len(docker_client.containers.list()))
	return dockerCounts
	
def getNetworks():
	docker_online = True
	try:
		docker_client = docker.from_env()
	except docker.errors.DockerException as e:
		print(f"Error connecting to Docker daemon: {e}")
		docker_online = False
	networks = []
	if docker_online:
		for network in docker_client.networks.list():
			networks.append(f"{network.name}")
	return networks

def getVolumes():
	docker_online = True
	try:
		docker_client = docker.from_env()
	except docker.errors.DockerException as e:
		print(f"Error connecting to Docker daemon: {e}")
		docker_online = False
	volumes = []
	if docker_online:
		for volume in docker_client.volumes.list():
			volumes.append(f"{volume.short_id}")
	return volumes

def getImages():
	docker_online = True
	try:
		docker_client = docker.from_env()
	except docker.errors.DockerException as e:
		print(f"Error connecting to Docker daemon: {e}")
		docker_online = False
	images = []
	if docker_online:
		try:
			for image in docker_client.images.list():
				imagename = ''.join(image.tags).split(':')[0].split('/')[-1]
				if imagename == '': imagename = image.short_id.split(':')[-1]
				images.append(f"{image.short_id.split(':')[-1]} {imagename}")
		except Exception as e:
				print(f"error: {e}")
	return images

def getContainers():
	docker_online = True
	try:
		docker_client = docker.from_env()
	except docker.errors.DockerException as e:
		print(f"Error connecting to Docker daemon: {e}")
		docker_online = False
	containers = []
	if docker_online:
		for container in docker_client.containers.list(all=True):
			try:
				containers.append(f"{container.name} {container.status} {container.attrs['State']['Health']['Status']} {container.short_id}")
			except KeyError:
				containers.append(f"{container.name} {container.status} {container.attrs['State']['Status']} {container.short_id}")
	return containers
	
def send_message(message : str):
	message = message.replace("\t", "")
	if TELEGRAM_ON:
		try:
			tb.send_message(CHAT_ID, message, parse_mode="markdown")
		except Exception as e:
			print(f"error: {e}")
	if DISCORD_ON:
		try:
			notifier.send(message.replace("*", "**"), print_message=False)
		except Exception as e:
			print(f"error: {e}")
	if SLACK_ON:
		try:
			requests.post(SLACK_WEB, json = {"text": message})
		except Exception as e:
			print(f"error: {e}")
	message = message.replace("*", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if GOTIFY_ON:
		try:
			requests.post(f"{GOTIFY_WEB}/message?token={GOTIFY_TOKEN}",\
			json={'title': header, 'message': message, 'priority': 0})
		except Exception as e:
			print(f"error: {e}")
	if NTFY_ON:
		try:
			requests.post(f"{NTFY_WEB}/{NTFY_SUB}", data=message.encode(encoding='utf-8'), headers={"Title": header})
		except Exception as e:
			print(f"error: {e}")
	if PUSHBULLET_ON:
		try:
			requests.post('https://api.pushbullet.com/v2/pushes',\
			json={'type': 'note', 'title': header, 'body': message},\
			headers={'Access-Token': PUSHBULLET_API, 'Content-Type': 'application/json'})
		except Exception as e:
			print(f"error: {e}")

if __name__ == "__main__":
	HOSTNAME = open("/proc/sys/kernel/hostname", "r").read().strip("\n")
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
			tb = telebot.TeleBot(TOKEN)
		if DISCORD_ON:
			DISCORD_WEB = parsed_json["DISCORD"]["WEB"]
			notifier = dn.Notifier(DISCORD_WEB)
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
	ORANGE_DOT, GREEN_DOT, RED_DOT, WHITE_DOT = "\U0001F7E0", "\U0001F7E2", "\U0001F534", "\U000026AA"
	#docker-image-network-volume
	tmpfiles = ["/tmp/dockimage.tmp", "/tmp/docknetworks.tmp", "/tmp/dockvolume.tmp"]
	messageheader = ["image", "network", "volume"]
	for j in range(len(tmpfiles)):
		TMP_FILE = tmpfiles[j]
		STATUS_DOT = GREEN_DOT
		STATUS_MESSAGE, MESSAGE, HEADER_MESSAGE = "", "", f"*{HOSTNAME}* (docker-{messageheader[j]})\n"
		LISTofitem = oldLISTofitem = result = []
		if messageheader[j] == "network":
			LISTofitem = getNetworks()
		elif messageheader[j] == "volume":
			LISTofitem = getVolumes()
		else:
			imagename = imageid = ""
			LISTofitem = getImages()
		if len(LISTofitem) != 0:
			if not os.path.exists(TMP_FILE):
				with open(TMP_FILE, "w") as file:
					file.write(",".join(LISTofitem))
				file.close()
			with open(TMP_FILE, "r") as file:
				oldLISTofitem = file.read().split(",")
			file.close()
			if len(LISTofitem) >= len(oldLISTofitem):
				result = list(set(LISTofitem) - set(oldLISTofitem))
				STATUS_DOT = WHITE_DOT
				STATUS_MESSAGE = "created"
			else:
				result = list(set(oldLISTofitem) - set(LISTofitem))
				STATUS_DOT = RED_DOT
				STATUS_MESSAGE = "removed"
			if len(result) != 0:
				with open(TMP_FILE, "w") as file:
					file.write(",".join(LISTofitem))
				file.close()
				for i in range(len(result)):
					if messageheader[j] == "image":
						imagename = result[i].split()[-1]
						imageid = result[i].split()[0]
						if imageid == imagename:
							MESSAGE += f"{STATUS_DOT} *{imagename}*: {STATUS_MESSAGE}!\n"
						else:
							MESSAGE += f"{STATUS_DOT} *{imagename}* ({imageid}): {STATUS_MESSAGE}!\n"
					else:
						MESSAGE += f"{STATUS_DOT} *{result[i]}*: {STATUS_MESSAGE}!\n"
				MESSAGE = "\n".join(sorted(MESSAGE.split("\n"))).lstrip("\n")
				send_message(f"{HEADER_MESSAGE}{MESSAGE}")
		
	#docker-container
	TMP_FILE = "/tmp/dockcontainer.tmp"
	STOPPED = False
	STATUS_DOT = ORANGE_DOT
	MESSAGE, HEADER_MESSAGE = "", f"*{HOSTNAME}* (docker-container)\n"
	LISTofitem = oldLISTofitem = result = []
	containername, containerattr, containerstatus = "", "", "inactive"
	LISTofitem = getContainers()
	if len(LISTofitem) != 0:
		if not os.path.exists(TMP_FILE):
			with open(TMP_FILE, "w") as file:
				file.write(",".join(LISTofitem))
			file.close()
		with open(TMP_FILE, "r") as file:
			oldLISTofitem = file.read().split(",")
		file.close()
		if len(LISTofitem) >= len(oldLISTofitem):
			result = list(set(LISTofitem) - set(oldLISTofitem)) 
		else:
			result = list(set(oldLISTofitem) - set(LISTofitem))
			STOPPED = True
		if len(result) != 0:
			with open(TMP_FILE, "w") as file:
				file.write(",".join(LISTofitem))
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
