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

def getVolumes():
	docker_client = docker.from_env()
	volumes = []
	for volume in docker_client.volumes.list():
		volumes.append(f"{volume.short_id}")
	return volumes

def getVolumesCount():
	docker_client = docker.from_env()
	count = len(docker_client.volumes.list())
	return count

def getImages():
	docker_client = docker.from_env()
	images = []
	for image in docker_client.images.list():
		imagename = ''.join(image.tags).split(':')[0].split('/')[-1]
		if imagename == "": imagename = image.short_id.split(':')[-1]
		images.append(f"{image.short_id.split(':')[-1]} {imagename}")
	return images

def getImagesCount():
	docker_client = docker.from_env()
	count = len(docker_client.images.list())
	return count

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
	CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
	SEC_REPEAT = 20
	MESSAGE_TYPE = "single"
	if os.path.exists(f"{CURRENT_PATH}/config.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/config.json", "r").read())
		SEC_REPEAT = int(parsed_json["SEC_REPEAT"])
		GROUP_MESSAGE = parsed_json["GROUP_MESSAGE"]
		TOKEN = parsed_json["TELEGRAM"]["TOKEN"]
		CHAT_ID = parsed_json["TELEGRAM"]["CHAT_ID"]
		if GROUP_MESSAGE: MESSAGE_TYPE = "group"
		tb = telebot.TeleBot(TOKEN)
		telegram_message(f"*{HOSTNAME}* (dockcheck)\n\
		- polling period: {SEC_REPEAT} seconds,\n\
		- message type: {MESSAGE_TYPE},\n\
		- currently monitoring: {getContainersCount()} containers,\n\
		- currently monitoring: {getImagesCount()} images,\n\
		- currently monitoring: {getVolumesCount()} volumes.")
	else:
		print("config.json not found")
		
@repeat(every(SEC_REPEAT).seconds)
def docker_volume():
	TMP_FILE = "/tmp/dockvolume.tmp"
	ORANGE_DOT, GREEN_DOT, RED_DOT = "\U0001F7E0", "\U0001F7E2", "\U0001F534"
	STATUS_DOT = GREEN_DOT
	NEWVOLUME = False
	STATUS_MESSAGE, MESSAGE, HEADER_MESSAGE = "", "", f"*{HOSTNAME}* (dockvolume)\n"
	LISTofvolumes = oldLISTofvolumes = []
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
				telegram_message(f"{HEADER_MESSAGE}{MESSAGE}")
		if GROUP_MESSAGE: telegram_message(f"{HEADER_MESSAGE}{MESSAGE}")
		
@repeat(every(SEC_REPEAT).seconds)
def docker_image():
	TMP_FILE = "/tmp/dockimage.tmp"
	ORANGE_DOT, GREEN_DOT, RED_DOT = "\U0001F7E0", "\U0001F7E2", "\U0001F534"
	STATUS_DOT = GREEN_DOT
	NEWIMAGE = False
	STATUS_MESSAGE, MESSAGE, HEADER_MESSAGE = "", "", f"*{HOSTNAME}* (dockimage)\n"
	LISTofimages = oldLISTofimages = []
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
				telegram_message(f"{HEADER_MESSAGE}{MESSAGE}")
		if GROUP_MESSAGE: telegram_message(f"{HEADER_MESSAGE}{MESSAGE}")

@repeat(every(SEC_REPEAT).seconds)
def docker_container():
	STOPPED = False
	TMP_FILE = "/tmp/dockcontainer.tmp"
	ORANGE_DOT, GREEN_DOT, RED_DOT = "\U0001F7E0", "\U0001F7E2", "\U0001F534"
	STATUS_DOT = ORANGE_DOT
	MESSAGE, HEADER_MESSAGE = "", f"*{HOSTNAME}* (dockcontainer)\n"
	LISTofcontainers = oldLISTofcontainers = []
	oldSTRofcontainer, containername, containerid, containerattr, containerstatus = "", "", "", "", "inactive"
	LISTofcontainers = getContainers()
	if not os.path.exists(TMP_FILE):
		with open(TMP_FILE, "w") as file:
			file.write(",".join(LISTofcontainers))
		file.close()
	with open(TMP_FILE, "r") as file:
		oldSTRofcontainer = file.read()
		oldLISTofcontainers = oldSTRofcontainer.split(",")
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
				containerid = "".join(result[i]).split()[-1]
				if not STOPPED: containerstatus = "".join(result[i]).split()[1]
				if containerstatus == "running":
					STATUS_DOT = GREEN_DOT
					if containerattr != containerstatus:
						containerstatus = f"{containerstatus} ({containerattr})"
					if containerid not in oldSTRofcontainer and containername in oldSTRofcontainer:
						containerstatus = f"{containerstatus.split()[0]} (id changed)"
				elif containerstatus == "inactive":
					STATUS_DOT = RED_DOT
				# ORANGE_DOT - created, paused, restarting, removing, exited
				if GROUP_MESSAGE:
					MESSAGE += f"{STATUS_DOT} *{containername}*: {containerstatus}!\n"
				else:
					telegram_message(f"{HEADER_MESSAGE}{STATUS_DOT} *{containername}*: {containerstatus}!\n")	
		if GROUP_MESSAGE: telegram_message(f"{HEADER_MESSAGE}{MESSAGE}")

while True:
    run_pending()
    time.sleep(1)
