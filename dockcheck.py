#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2024

import json
import docker
import os
import time
import requests
from schedule import every, repeat, run_pending
from requests.exceptions import RequestException


def getHostname():
	hostname = ""
	if os.path.exists('/proc/sys/kernel/hostname'):
		with open('/proc/sys/kernel/hostname', "r") as file:
			hostname = file.read().strip('\n')
	return hostname


def getDockerCounts():
	docker_counts = {"volumes": "0", "images": "0", "networks": "0", "containers": "0"}
	try:
		docker_client = docker.from_env()
		docker_counts["volumes"] = str(len(docker_client.volumes.list()))
		docker_counts["images"] = str(len(docker_client.images.list()))
		docker_counts["networks"] = str(len(docker_client.networks.list()))
		docker_counts["containers"] = str(len(docker_client.containers.list()))
	except docker.errors.DockerException as e:
		print("error:", e)
	return docker_counts


def getDockerData(what):
	return_data = []
	try:
		docker_client = docker.from_env()
		if what == "networks":
			networks = docker_client.networks.list()
			if networks: return_data = [network.name for network in networks]
		elif what == "images":
			images = docker_client.images.list()
			if images:
				for image in images:
					imagename = ''.join(image.tags).split(':')[0].split('/')[-1]
					if imagename == '': imagename = image.short_id.split(':')[-1]
					return_data.append(f"{image.short_id.split(':')[-1]} {imagename}")
		elif what == "unused_volumes":
			volumes = docker_client.volumes.list(filters={"dangling": "true"})
			if volumes: return_data = [volume.short_id for volume in volumes]
		else:
			volumes = docker_client.volumes.list()
			if volumes: return_data = [volume.short_id for volume in volumes]
	except docker.errors.DockerException as e:
		print("error:", e)
	return return_data


def getContainers():
	containers = []
	try:
		docker_client = docker.from_env()
		if docker_client: 
			for container in docker_client.containers.list(all=True):
				container_info = docker_client.api.inspect_container(container.id)
				if "State" in container_info and "Health" in container_info["State"]:
					containers.append(f"{container.name} {container.status} {container.attrs['State']['Health']['Status']} {container.short_id}")
				else:
					containers.append(f"{container.name} {container.status} {container.attrs['State']['Status']} {container.short_id}")
	except docker.errors.DockerException as e:
		print("error:", e)
	return containers


def SendMessage(message : str):
	message = message.replace("\t", "")
	if telegram_on:
		try:
			response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if discord_on:
		try:
			response = requests.post(discord_web, json={"content": message.replace("*", "**")})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if slack_on:
		try:
			response = requests.post(slack_web, json = {"text": message})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	message = message.replace("*", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if gotify_on:
		try:
			response = requests.post(f"{gotify_web}/message?token={gotify_token}",\
			json={'title': header, 'message': message, 'priority': 0})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if ntfy_on:
		try:
			response = requests.post(f"{ntfy_web}/{ntfy_sub}", data=message.encode(encoding='utf-8'), headers={"Title": header})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if pushbullet_on:
		try:
			response = requests.post('https://api.pushbullet.com/v2/pushes',\
			json={'type': 'note', 'title': header, 'body': message},\
			headers={'Access-Token': pushbullet_api, 'Content-Type': 'application/json'})
		except requests.exceptions.RequestException as e:
			print("error:", e)


if __name__ == "__main__":
	hostname = getHostname()
	current_path = os.path.dirname(os.path.realpath(__file__))
	sec_repeat = 20
	old_list_container = old_list_network = old_list_volume = old_list_image = old_list_uvolume = []
	telegram_on = discord_on = gotify_on = ntfy_on = slack_on = pushbullet_on = False
	token = chat_id = discord_web = gotify_web = gotify_token = ntfy_web = ntfy_sub = pushbullet_api = slack_web = messaging_service = ""
	docker_counts = getDockerCounts()
	if os.path.exists(f"{current_path}/config.json"):
		with open(f"{current_path}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		sec_repeat = int(parsed_json["SEC_REPEAT"])
		telegram_on = parsed_json["TELEGRAM"]["ON"]
		discord_on = parsed_json["DISCORD"]["ON"]
		gotify_on = parsed_json["GOTIFY"]["ON"]
		ntfy_on = parsed_json["NTFY"]["ON"]
		pushbullet_on = parsed_json["PUSHBULLET"]["ON"]
		slack_on = parsed_json["SLACK"]["ON"]
		if telegram_on:
			token = parsed_json["TELEGRAM"]["TOKEN"]
			chat_id = parsed_json["TELEGRAM"]["CHAT_ID"]
			messaging_service += "- messenging: Telegram,\n"
		if discord_on:
			discord_web = parsed_json["DISCORD"]["WEB"]
			messaging_service += "- messenging: Discord,\n"
		if gotify_on:
			gotify_web = parsed_json["GOTIFY"]["WEB"]
			gotify_token = parsed_json["GOTIFY"]["TOKEN"]
			messaging_service += "- messenging: Gotify,\n"
		if ntfy_on:
			ntfy_web = parsed_json["NTFY"]["WEB"]
			ntfy_sub = parsed_json["NTFY"]["SUB"]
			messaging_service += "- messenging: Ntfy,\n"
		if pushbullet_on:
			pushbullet_api = parsed_json["PUSHBULLET"]["API"]
			messaging_service += "- messenging: Pushbullet,\n"
		if slack_on:
			slack_web = parsed_json["SLACK"]["WEB"]
			messaging_service += "- messenging: Slack,\n"
		SendMessage(f"*{hostname}* (docker.check)\ndocker monitor:\n{messaging_service}\
		- monitoring: {docker_counts['containers']} containers,\n\
		- monitoring: {docker_counts['images']} images,\n\
		- monitoring: {docker_counts['networks']} networks,\n\
		- monitoring: {docker_counts['volumes']} volumes,\n\
		- polling period: {sec_repeat} seconds.")
	else:
		print("config.json not found")


@repeat(every(sec_repeat).seconds)
def docker_checker():
	orange_dot, green_dot, red_dot, yellow_dot = "\U0001F7E0", "\U0001F7E2", "\U0001F534", "\U0001F7E1"
	#docker-image
	global old_list_image
	status_dot = yellow_dot
	message, status_message, header_message = "", "", f"*{hostname}* (docker.images)\n"
	list_image = result = []
	imagename = imageid = ""
	list_image = getDockerData("images")
	if list_image:
		if not old_list_image: old_list_image = list_image
		if len(list_image) >= len(old_list_image):
			result = list(set(list_image) - set(old_list_image))
			status_message = "pulled"
		else:
			result = list(set(old_list_image) - set(list_image))
			status_dot = red_dot
			status_message = "removed"
		if result:
			for image in result:
				imageid = image.split()[0]
				imagename = image.split()[-1]
				if imageid == imagename:
					if imageid in ",".join(old_list_image) and status_dot != red_dot:
						status_message = "unused"
						status_dot = orange_dot
					message += f"{status_dot} *{imagename}*: {status_message}!\n"
					if status_dot == orange_dot: status_dot = yellow_dot
				else:
					message += f"{status_dot} *{imagename}* ({imageid}): {status_message}!\n"
				if status_dot == yellow_dot: status_message = "pulled"
			old_list_image = list_image
			message = "\n".join(sorted(message.split("\n"))).lstrip("\n")
			SendMessage(f"{header_message}{message}")


	#docker-unused.volumes
	global old_list_uvolume
	status_dot = orange_dot
	message, status_message, header_message = "", "", f"*{hostname}* (docker.volumes)\n"
	list_of = old_list = result = []
	old_list = old_list_uvolume
	list_of = getDockerData("unused_volumes")
	if list_of:
		if len(list_of) >= len(old_list):
			result = list(set(list_of) - set(old_list))
			status_message = "unused"
		old_list_uvolume = list_of
		if result:
			for item in result:
				message += f"{status_dot} *{item}*: {status_message}!\n"
			message = "\n".join(sorted(message.split("\n"))).lstrip("\n")
			SendMessage(f"{header_message}{message}")


	#docker-volume-network
	check_types = ["volumes", "networks"]
	global old_list_network
	global old_list_volume
	for check_type in check_types:
		status_dot = yellow_dot
		message, status_message, header_message = "", "", f"*{hostname}* (docker.{check_type})\n"
		list_of = old_list = result = []
		if check_type == "volumes":
			old_list = old_list_volume
			list_of = getDockerData("volumes")
		else:
			old_list = old_list_network
			list_of = getDockerData("networks")
		if list_of:
			if not old_list: old_list = list_of
			if len(list_of) >= len(old_list):
				result = list(set(list_of) - set(old_list))
				status_message = "created"
			else:
				result = list(set(old_list) - set(list_of))
				status_dot = red_dot
				status_message = "removed"
			if check_type == "volumes":
				old_list_volume = list_of
			else:
				old_list_network = list_of
			if result:
				for item in result:
					message += f"{status_dot} *{item}*: {status_message}!\n"
				message = "\n".join(sorted(message.split("\n"))).lstrip("\n")
				SendMessage(f"{header_message}{message}")


	#docker-container
	global old_list_container
	status_dot = orange_dot
	message, header_message = "", f"*{hostname}* (docker.containers)\n"
	list_container = result = []
	stopped = False
	containername, containerattr, containerstatus = "", "", "inactive"
	list_container = getContainers()
	if list_container:
		if not old_list_container: old_list_container = list_container
		if len(list_container) >= len(old_list_container):
			result = list(set(list_container) - set(old_list_container)) 
		else:
			result = list(set(old_list_container) - set(list_container))
			stopped = True
		if result:
			old_list_container = list_container
			for container in result:
				containername = "".join(container).split()[0]
				if containername != "":
					containerattr = "".join(container).split()[2]
					if containerattr != "starting":
						if not stopped: containerstatus = "".join(container).split()[1]
						if containerstatus == "running":
							status_dot = green_dot
							if containerattr != containerstatus: containerstatus = f"{containerstatus} ({containerattr})"
							if containerattr == "unhealthy": status_dot = orange_dot
						elif containerstatus == "created": status_dot = yellow_dot
						elif containerstatus == "inactive": status_dot = red_dot
						message += f"{status_dot} *{containername}*: {containerstatus}!\n"
			if message:
				message = "\n".join(sorted(message.split("\n"))).lstrip("\n")  
				SendMessage(f"{header_message}{message}")


while True:
	run_pending()
	time.sleep(1)
