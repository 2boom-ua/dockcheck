#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2024

import telebot
import json
import docker
import os
import time
import requests
from gotify import Gotify
import discord_notify as dn
from schedule import every, repeat, run_pending
from pushbullet import Pushbullet

def getDockerCounts():
	dockerCounts = []
	docker_client = docker.from_env()
	dockerCounts.append(len(docker_client.volumes.list()))
	dockerCounts.append(len(docker_client.images.list()))
	dockerCounts.append(len(docker_client.networks.list()))
	dockerCounts.append(len(docker_client.containers.list(all=True)))
	return dockerCounts
	
def getNetworks():
	docker_client = docker.from_env()
	networks = []
	for network in docker_client.networks.list():
		networks.append(f"{network.name}")
	return networks

def getVolumes():
	docker_client = docker.from_env()
	volumes = []
	for volume in docker_client.volumes.list():
		volumes.append(f"{volume.short_id}")
	return volumes

def getImages():
	docker_client = docker.from_env()
	images = []
	try:
		for image in docker_client.images.list():
			imagename = ''.join(image.tags).split(':')[0].split('/')[-1]
			if imagename == '': imagename = image.short_id.split(':')[-1]
			images.append(f"{image.short_id.split(':')[-1]} {imagename}")
	except Exception as e:
			print(f"error: {e}")
	return images

def getContainers():
	docker_client = docker.from_env()
	containers = []
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
	message = message.replace("*", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if GOTIFY_ON:
		gotify = Gotify(base_url=GOTIFY_WEB, app_token=GOTIFY_TOKEN)
		try:
			gotify.create_message(message, title = header)
		except Exception as e:
			print(f"error: {e}")
	if NTFY_ON:
		try:
			requests.post(f"{NTFY_WEB}/{NTFY_SUB}", data=message.encode(encoding='utf-8'), headers={"Title": header})
		except Exception as e:
			print(f"error: {e}")
	if PUSHBULLET_ON:
		try:
			push = pb.push_note(header, message)
		except Exception as e:
			print(f"error: {e}")

def messaging_service():
	messaging = ""
	if TELEGRAM_ON:
		messaging += "- messenging: Telegram,\n"
	if DISCORD_ON:
		messaging += "- messenging: Discord,\n"
	if GOTIFY_ON:
		messaging += "- messenging: Gotify,\n"
	if NTFY_ON:
		messaging += "- messenging: Ntfy,\n"
	if PUSHBULLET_ON:
		messaging += "- messenging: Pushbullet,\n"
	return messaging

if __name__ == "__main__":
	HOSTNAME = open("/proc/sys/kernel/hostname", "r").read().strip("\n")
	CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
	SEC_REPEAT = 20
	MESSAGE_TYPE = "single"
	TELEGRAM_ON = DISCORD_ON = GOTIFY_ON = NTFY_ON = False
	TOKEN = CHAT_ID = DISCORD_WEB = GOTIFY_WEB = GOTIFY_TOKEN = NTFY_WEB = NTFY_SUB = PUSHBULLET_ON = ""
	dockerCounts = getDockerCounts()
	if os.path.exists(f"{CURRENT_PATH}/config.json"):
		with open(f"{CURRENT_PATH}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		file.close()
		SEC_REPEAT = int(parsed_json["SEC_REPEAT"])
		GROUP_MESSAGE = parsed_json["GROUP_MESSAGE"]
		TELEGRAM_ON = parsed_json["TELEGRAM"]["ON"]
		DISCORD_ON = parsed_json["DISCORD"]["ON"]
		GOTIFY_ON = parsed_json["GOTIFY"]["ON"]
		NTFY_ON = parsed_json["NTFY"]["ON"]
		PUSHBULLET_ON = parsed_json["PUSHBULLET"]["ON"]
		if TELEGRAM_ON:
			TOKEN = parsed_json["TELEGRAM"]["TOKEN"]
			CHAT_ID = parsed_json["TELEGRAM"]["CHAT_ID"]
			tb = telebot.TeleBot(TOKEN)
		if DISCORD_ON:
			DISCORD_WEB = parsed_json["DISCORD"]["WEB"]
			notifier = dn.Notifier(DISCORD_WEB)
		if GOTIFY_ON:
			GOTIFY_WEB = parsed_json["GOTIFY"]["WEB"]
			GOTIFY_TOKEN = parsed_json["GOTIFY"]["TOKEN"]
		if NTFY_ON:
			NTFY_WEB = parsed_json["NTFY"]["WEB"]
			NTFY_SUB = parsed_json["NTFY"]["SUB"]
		if PUSHBULLET_ON:
			PUSHBULLET_API = parsed_json["PUSHBULLET"]["API"]
			pb = Pushbullet(PUSHBULLET_API)
		if GROUP_MESSAGE: MESSAGE_TYPE = "group"
		send_message(f"*{HOSTNAME}* (docker-check)\ndocker monitor:\n{messaging_service()}\
		- message type: {MESSAGE_TYPE},\n\
		- monitoring: {dockerCounts[3]} containers,\n\
		- monitoring: {dockerCounts[1]} images,\n\
		- monitoring: {dockerCounts[2]} networks,\n\
		- monitoring: {dockerCounts[0]} volumes,\n\
		- polling period: {SEC_REPEAT} seconds.")
	else:
		print("config.json not found")
		
@repeat(every(SEC_REPEAT).seconds)
def docker_checker():
	ORANGE_DOT, GREEN_DOT, RED_DOT = "\U0001F7E0", "\U0001F7E2", "\U0001F534"		
	#docker-image 
	TMP_FILE = "/tmp/dockimage.tmp"
	STATUS_DOT = GREEN_DOT
	NEWIMAGE = False
	STATUS_MESSAGE, MESSAGE, HEADER_MESSAGE = "", "", f"*{HOSTNAME}* (docker-image)\n"
	LISTofimages = oldLISTofimages = sort_message = result = []
	LISTofimages = getImages()
	imagename = imageid = ""
	if not os.path.exists(TMP_FILE):
		with open(TMP_FILE, "w") as file:
			file.write(",".join(LISTofimages))
		file.close()
	with open(TMP_FILE, "r") as file:
		oldLISTofimages = file.read().split(",")
	file.close()
	if len(LISTofimages) >= len(oldLISTofimages):
		result = list(set(LISTofimages) - set(oldLISTofimages))
		NEWIMAGE = True
	else:
		result = list(set(oldLISTofimages) - set(LISTofimages))
		STATUS_DOT = RED_DOT
		STATUS_MESSAGE = "removed"
	if len(result) != 0:
		with open(TMP_FILE, "w") as file:
			file.write(",".join(LISTofimages))
		file.close()
		for i in range(len(result)):
			imagename = result[i].split()[-1]
			imageid = result[i].split()[0]
			if imageid == imagename and NEWIMAGE:
				STATUS_DOT = ORANGE_DOT
				STATUS_MESSAGE = "stored"
			if imageid != imagename and NEWIMAGE:
				STATUS_DOT = GREEN_DOT
				STATUS_MESSAGE = "created"
			if GROUP_MESSAGE:
				if imageid == imagename:
					MESSAGE += f"{STATUS_DOT} *{imagename}*: {STATUS_MESSAGE}!\n"
				else:
					MESSAGE += f"{STATUS_DOT} *{imagename}* ({imageid}): {STATUS_MESSAGE}!\n"
			else:
				MESSAGE = f"{STATUS_DOT} *{imagename}* ({imageid}): {STATUS_MESSAGE}!\n"
				if imageid == imagename:
					MESSAGE = f"{STATUS_DOT} *{imagename}*: {STATUS_MESSAGE}!\n"
				send_message(f"{HEADER_MESSAGE}{MESSAGE}")
		if GROUP_MESSAGE:
			sort_message = MESSAGE.split("\n")
			sort_message.sort()
			MESSAGE = "\n".join(sort_message).lstrip("\n")
			send_message(f"{HEADER_MESSAGE}{MESSAGE}")
	
	#docker-network
	TMP_FILE = "/tmp/docknetworks.tmp"
	STATUS_DOT = GREEN_DOT
	NEWNET = False
	STATUS_MESSAGE, MESSAGE, HEADER_MESSAGE = "", "", f"*{HOSTNAME}* (docker-network)\n"
	LISTofnetworks = oldLISTofnetworks = result = []
	LISTofnetworks = getNetworks()
	networkname = ""
	if not os.path.exists(TMP_FILE):
		with open(TMP_FILE, "w") as file:
			file.write(",".join(LISTofnetworks))
		file.close()
	with open(TMP_FILE, "r") as file:
		oldLISTofnetworks = file.read().split(",")
	file.close()
	if len(LISTofnetworks) >= len(oldLISTofnetworks):
		result = list(set(LISTofnetworks) - set(oldLISTofnetworks))
		NEWNET = True
	else:
		result = list(set(oldLISTofnetworks) - set(LISTofnetworks))
		STATUS_DOT = RED_DOT
		STATUS_MESSAGE = "removed"
	if len(result) != 0:
		with open(TMP_FILE, "w") as file:
			file.write(",".join(LISTofnetworks))
		file.close()
		for i in range(len(result)):
			networkname = result[i]
			if NEWNET:
				STATUS_DOT = GREEN_DOT
				STATUS_MESSAGE = "created"
			if GROUP_MESSAGE:
				MESSAGE += f"{STATUS_DOT} *{networkname}*: {STATUS_MESSAGE}!\n"
			else:
				MESSAGE = f"{STATUS_DOT} *{networkname}*: {STATUS_MESSAGE}!\n"
				send_message(f"{HEADER_MESSAGE}{MESSAGE}")
		if GROUP_MESSAGE: send_message(f"{HEADER_MESSAGE}{MESSAGE}")

	#docker-volume
	TMP_FILE = "/tmp/dockvolume.tmp"
	STATUS_DOT = GREEN_DOT
	NEWVOLUME = False
	STATUS_MESSAGE, MESSAGE, HEADER_MESSAGE = "", "", f"*{HOSTNAME}* (docker-volume)\n"
	LISTofvolumes = oldLISTofvolumes = result = []
	LISTofvolumes = getVolumes()
	volumename = ""
	if not os.path.exists(TMP_FILE):
		with open(TMP_FILE, "w") as file:
			file.write(",".join(LISTofvolumes))
		file.close()
	with open(TMP_FILE, "r") as file:
		oldLISTofvolumes = file.read().split(",")
	file.close()
	if len(LISTofvolumes) >= len(oldLISTofvolumes):
		result = list(set(LISTofvolumes) - set(oldLISTofvolumes))
		NEWVOLUME = True
	else:
		result = list(set(oldLISTofvolumes) - set(LISTofvolumes))
		STATUS_DOT = RED_DOT
		STATUS_MESSAGE = "removed"
	if len(result) != 0:
		with open(TMP_FILE, "w") as file:
			file.write(",".join(LISTofvolumes))
		file.close()
		for i in range(len(result)):
			volumename = result[i]
			if NEWVOLUME:
				STATUS_DOT = GREEN_DOT
				STATUS_MESSAGE = "created"
			if GROUP_MESSAGE:
				MESSAGE += f"{STATUS_DOT} *{volumename}*: {STATUS_MESSAGE}!\n"
			else:
				MESSAGE = f"{STATUS_DOT} *{volumename}*: {STATUS_MESSAGE}!\n"
				send_message(f"{HEADER_MESSAGE}{MESSAGE}")
		if GROUP_MESSAGE: send_message(f"{HEADER_MESSAGE}{MESSAGE}")
		
	#docker-container
	TMP_FILE = "/tmp/dockcontainer.tmp"
	STOPPED = False
	STATUS_DOT = ORANGE_DOT
	MESSAGE, HEADER_MESSAGE = "", f"*{HOSTNAME}* (docker-container)\n"
	LISTofcontainers = oldLISTofcontainers = sort_message = result = []
	containername, containerattr, containerstatus = "", "", "inactive"
	LISTofcontainers = getContainers()
	if not os.path.exists(TMP_FILE):
		with open(TMP_FILE, "w") as file:
			file.write(",".join(LISTofcontainers))
		file.close()
	with open(TMP_FILE, "r") as file:
		oldLISTofcontainers = file.read().split(",")
	file.close()
	if len(LISTofcontainers) >= len(oldLISTofcontainers):
		result = list(set(LISTofcontainers) - set(oldLISTofcontainers)) 
	else:
		result = list(set(oldLISTofcontainers) - set(LISTofcontainers))
		STOPPED = True
	if len(result) != 0:
		with open(TMP_FILE, "w") as file:
			file.write(",".join(LISTofcontainers))
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
				elif containerstatus == "inactive":
					STATUS_DOT = RED_DOT
				if GROUP_MESSAGE:
					MESSAGE += f"{STATUS_DOT} *{containername}*: {containerstatus}!\n"
				else:
					send_message(f"{HEADER_MESSAGE}{STATUS_DOT} *{containername}*: {containerstatus}!\n")	
		if GROUP_MESSAGE:
			sort_message = MESSAGE.split("\n")
			sort_message.sort()
			MESSAGE = "\n".join(sort_message).lstrip("\n")
			send_message(f"{HEADER_MESSAGE}{MESSAGE}")

while True:
    run_pending()
    time.sleep(1)
