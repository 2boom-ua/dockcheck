#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# copyright: 2boom 2024

import json
import docker
import os
import time
import requests
from schedule import every, repeat, run_pending
	

def get_node_name():
	"""Get the name of the Docker node."""
	data = ""
	try:
		data = docker.from_env().info().get('Name')
	except docker.errors.DockerException as e:
		print("Error:", e)
	return data


def get_docker_counts():
	"""Get the count of Docker resources: volumes, images, networks, and containers."""
	try:
		docker_client = docker.from_env()
		return {
			"volumes": len(docker_client.volumes.list()),
			"images": len(docker_client.images.list()),
			"networks": len(docker_client.networks.list()),
			"containers": len(docker_client.containers.list())
		}
	except (docker.errors.DockerException, Exception) as e:
		print(f"Error: {e}")
		return {"volumes": 0, "images": 0, "networks": 0, "containers": 0}


def get_docker_data(data_type: str):
	"""Retrieve detailed data for Docker resources: volumes, images, networks, and containers."""
	data = []
	try:
		docker_client = docker.from_env()
		if data_type == "networks":
			networks = docker_client.networks.list()
			if networks: [data.append(f"{network.name}") for network in networks]
		elif data_type == "unetworks":
			used_networks = []
			default_networks = ["none", "host"]
			networks = docker_client.networks.list()
			containers = docker_client.containers.list(all=True)
			for container in containers:
				[used_networks.append(network) for network in container.attrs['NetworkSettings']['Networks']]
			unused_networks = [network for network in networks if network.name not in used_networks and network.name not in default_networks]
			if unused_networks: [data.append(f"{network.name} {network.short_id}") for network in unused_networks]
		elif data_type == "images":
			images = docker_client.images.list()
			if images:
				for image in images:
					imagename = ''.join(image.tags).split(':')[0].split('/')[-1]
					if imagename == '': imagename = image.short_id.split(':')[-1]
					data.append(f"{image.short_id.split(':')[-1]} {imagename}")
		elif data_type == "containers":
			for container in docker_client.containers.list(all=True):
				container_info = docker_client.api.inspect_container(container.id)
				if "State" in container_info and "Health" in container_info["State"]:
					data.append(f"{container.name} {container.status} {container.attrs['State']['Health']['Status']} {container.short_id}")
				else:
					data.append(f"{container.name} {container.status} {container.attrs['State']['Status']} {container.short_id}")
		else:
			if data_type == "volumes":
				volumes = docker_client.volumes.list()
			else:
				volumes = docker_client.volumes.list(filters={"dangling": "true"})
			if volumes: [data.append(f"{volume.short_id}") for volume in volumes]
	except (docker.errors.DockerException, Exception) as e:
		print(f"Error: {e}")
	return data


def send_message(message: str):
	"""Send notifications to various messaging services (Telegram, Discord, Slack, Gotify, Ntfy, Pushbullet, Pushover)."""
	def send_request(url, json_data=None, data=None, headers=None):
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")
	if telegram_on:
		for token, chat_id in zip(telegram_tokens, telegram_chat_ids):
			url = f"https://api.telegram.org/bot{token}/sendMessage"
			json_data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
			send_request(url, json_data)
	if discord_on:
		for token in discord_tokens:
			url = f"https://discord.com/api/webhooks/{token}"
			json_data = {"content": message.replace("*", "**")}
			send_request(url, json_data)
	if slack_on:
		for token in slack_tokens:
			url = f"https://hooks.slack.com/services/{token}"
			json_data = {"text": message}
			send_request(url, json_data)
	header, message = message.replace("*", "").split("\n", 1)
	message = message.strip()
	if gotify_on:
		for token, chat_url in zip(gotify_tokens, gotify_chat_urls):
			url = f"{chat_url}/message?token={token}"
			json_data = {'title': header, 'message': message, 'priority': 0}
			send_request(url, json_data)
	if ntfy_on:
		for token, chat_url in zip(ntfy_tokens, ntfy_chat_urls):
			url = f"{chat_url}/{token}"
			data_data = message.encode(encoding = 'utf-8')
			headers_data = {"title": header}
			send_request(url, None, data_data, headers_data)
	if pushbullet_on:
		for token in pushbullet_tokens:
			url = "https://api.pushbullet.com/v2/pushes"
			json_data = {'type': 'note', 'title': header, 'body': message}
			headers_data = {'Access-Token': token, 'Content-Type': 'application/json'}
			send_request(url, json_data, None, headers_data)
	if pushover_on:
		for token, user_key in zip(pushover_tokens, pushover_user_keys):
			url = "https://api.pushover.net/1/messages.json"
			json_data = {"token": token, "user": user_key, "message": message, "title": header}
			send_request(url, json_data)


if __name__ == "__main__":
	"""Load configuration and initialize monitoring"""
	nodename = get_node_name()
	current_path = os.path.dirname(os.path.realpath(__file__))
	orange_dot, green_dot, red_dot, yellow_dot = "\U0001F7E0", "\U0001F7E2", "\U0001F534", "\U0001F7E1"
	old_list_containers = old_list_networks = old_list_volumes = old_list_images = old_list_uvolumes = old_list_unetworks = []
	monitoring_mg = ""
	docker_counts = get_docker_counts()
	header_message = f"*{nodename}* (docker.check)\ndocker monitor:\n"
	if os.path.exists(f"{current_path}/config.json"):
		with open(f"{current_path}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		sec_repeat = int(parsed_json["SEC_REPEAT"])
		telegram_on, discord_on, gotify_on, ntfy_on, pushbullet_on, pushover_on, slack_on = (parsed_json[key]["ON"] for key in ["TELEGRAM", "DISCORD", "GOTIFY", "NTFY", "PUSHBULLET", "PUSHOVER", "SLACK"])
		services = {
		"TELEGRAM": ["TOKENS", "CHAT_IDS"], "DISCORD": ["TOKENS"], "SLACK": ["TOKENS"],
		"GOTIFY": ["TOKENS", "CHAT_URLS"], "NTFY": ["TOKENS", "CHAT_URLS"], "PUSHBULLET": ["TOKENS"], "PUSHOVER": ["TOKENS", "USER_KEYS"]
		}
		for service, keys in services.items():
			if parsed_json[service]["ON"]:
				globals().update({f"{service.lower()}_{key.lower()}": parsed_json[service][key] for key in keys})
				monitoring_mg += f"- messaging: {service.capitalize()},\n"
		for resource in docker_counts:
			monitoring_mg += f"- monitoring: {docker_counts[resource]} {resource}\n"
		send_message(f"{header_message}{monitoring_mg}- polling period: {sec_repeat} seconds.")	
	else:
		print("config.json not found")

"""Periodically check for changes in Docker resources"""
@repeat(every(sec_repeat).seconds)
def docker_checker():
	"""Check for changes in Docker images"""
	global old_list_images
	status_dot = yellow_dot
	message, header_message = "", f"*{nodename}* (docker.images)\n"
	list_images = result = []
	list_images = get_docker_data("images")
	if list_images:
		if not old_list_images: old_list_images = list_images
		if len(list_images) >= len(old_list_images):
			result = list(set(list_images) - set(old_list_images))
			status_message = "pulled"
		else:
			result = list(set(old_list_images) - set(list_images))
			status_dot, status_message = red_dot, "removed"
		if result:
			for image in result:
				imageid, imagename = image.split()[0], image.split()[-1]
				if imageid == imagename:
					if imageid in ",".join(old_list_images) and status_dot != red_dot:
						status_message, status_dot = "unused", orange_dot
					message += f"{status_dot} *{imagename}*: {status_message}!\n"
					if status_dot == orange_dot: status_dot = yellow_dot
				else:
					message += f"{status_dot} *{imagename}* ({imageid}): {status_message}!\n"
				if status_dot == yellow_dot: status_message = "pulled"
			old_list_images = list_images
			message = "\n".join(sorted(message.split("\n"))).lstrip("\n")
			if all(keyword in message for keyword in [orange_dot, yellow_dot, "unused!", "pulled!"]):
				parts_ms = message.split()
				unused_id, name_im = parts_ms[1].rstrip(':').strip('*'), parts_ms[4]
				replace_name = f"{name_im} ({unused_id}):"
				message = message.replace(parts_ms[1], replace_name)
			send_message(f"{header_message}{message}")

	"""Check for changes in Docker networks and volumes"""
	check_types = ["volumes", "networks"]
	global old_list_networks
	global old_list_volumes
	for check_type in check_types:
		status_dot = yellow_dot
		message, header_message = "", f"*{nodename}* (docker.{check_type})\n"
		new_list = old_list = result = []
		if check_type == "volumes":
			old_list = old_list_volumes
			new_list = get_docker_data("volumes")
		else:
			old_list = old_list_networks
			new_list = get_docker_data("networks")
		if new_list:
			if not old_list: old_list = new_list
			if len(new_list) >= len(old_list):
				result = list(set(new_list) - set(old_list))
				status_message = "created"
			else:
				result = list(set(old_list) - set(new_list))
				status_dot, status_message = red_dot, "removed"
			if check_type == "volumes":
				old_list_volumes = new_list
			else:
				old_list_networks = new_list
			if result:
				for item in result:
					message += f"{status_dot} *{item}*: {status_message}!\n"
				message = "\n".join(sorted(message.split("\n"))).lstrip("\n")
				send_message(f"{header_message}{message}")

	"""Check for changes in Docker unused networks and volumes"""
	check_types = ["volumes", "networks"]
	global old_list_uvolumes
	global old_list_unetworks
	for check_type in check_types:
		status_dot = orange_dot
		message, header_message = "", f"*{nodename}* (docker.{check_type})\n"
		new_list = old_list = result = []
		if check_type == "volumes":
			old_list = old_list_uvolumes
			new_list = get_docker_data("unused_volumes")
		else:
			old_list = old_list_unetworks
			new_list = get_docker_data("unetworks")
		if new_list:
			if len(new_list) >= len(old_list):
				result = list(set(new_list) - set(old_list))
				status_message = "unused"
			if check_type == "volumes":
				old_list_uvolumes = new_list
			else:
				old_list_unetworks = new_list
			if result:
				for item in result:
					if check_type == "volumes":
						message += f"{status_dot} *{item}*: {status_message}!\n"
					else:
						message += f"{status_dot} *{item.split()[0]}* ({item.split()[-1]}): {status_message}!\n"
				message = "\n".join(sorted(message.split("\n"))).lstrip("\n")
				send_message(f"{header_message}{message}")

	"""Check for changes in Docker containers"""
	global old_list_containers
	status_dot = orange_dot
	message, header_message = "", f"*{nodename}* (docker.containers)\n"
	list_containers = result = []
	stopped = False
	containername, containerattr, containerstatus = "", "", "inactive"
	list_containers = get_docker_data("containers")
	if list_containers:
		if not old_list_containers: old_list_containers = list_containers
		if len(list_containers) >= len(old_list_containers):
			result = list(set(list_containers) - set(old_list_containers)) 
		else:
			result = list(set(old_list_containers) - set(list_containers))
			stopped = True
		if result:
			old_list_containers = list_containers
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
				status_dot = orange_dot
			if message:
				message = "\n".join(sorted(message.split("\n"))).lstrip("\n")  
				send_message(f"{header_message}{message}")

while True:
	run_pending()
	time.sleep(1)
