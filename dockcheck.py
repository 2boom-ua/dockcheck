#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# copyright: 2boom 2024

import json
import docker
import os
import time
import requests
from schedule import every, repeat, run_pending
	

def get_node_name() -> str:
	"""Get the name of the Docker node."""
	try:
		return docker.from_env().info().get('Name')
	except docker.errors.DockerException as e:
		print("Error:", e)
	return ""


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
			for container in docker_client.containers.list(all=True):
				[used_networks.append(network) for network in container.attrs['NetworkSettings']['Networks']]
			unused_networks = [network for network in networks if network.name not in used_networks and network.name not in default_networks]
			if unused_networks: [data.append(f"{network.name} {network.short_id}") for network in unused_networks]
		elif data_type == "images":
			images = docker_client.images.list()
			if images:
				for image in images:
					imagename = image.tags[0].split(':')[0].split('/')[-1] if image.tags else image.short_id.split(':')[-1]
					data.append(f"{image.short_id.split(':')[-1]} {imagename}")
		elif data_type == "containers":
			for container in docker_client.containers.list(all=True):
				container_info = docker_client.api.inspect_container(container.id)
				health_status = container_info.get("State", {}).get("Health", {}).get("Status")
				status = health_status if health_status else container_info["State"]["Status"]
				data.append(f"{container.name} {container.status} {status} {container.short_id}")

		else:
			volumes = docker_client.volumes.list() if data_type == "volumes" else docker_client.volumes.list(filters={"dangling": "true"})
			if volumes: [data.append(f"{volume.short_id}") for volume in volumes]
	except (docker.errors.DockerException, Exception) as e:
		print(f"Error: {e}")
	return data


def send_message(message: str):
	"""Send notifications to various messaging services (Telegram, Discord, Slack, Gotify, Ntfy, Pushbullet, Pushover)."""
	def send_request(url, json_data = None, data = None, headers = None):
		try:
			response = requests.post(url, json = json_data, data = data, headers = headers)
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
	node_name = get_node_name()
	current_path = os.path.dirname(os.path.realpath(__file__))
	old_list_containers = old_list_networks = old_list_volumes = old_list_images = old_list_uvolumes = old_list_unetworks = []
	dots = {"orange": "\U0001F7E0", "green": "\U0001F7E2", "red": "\U0001F534", "yellow": "\U0001F7E1"}
	square_dots = {"orange": "\U0001F7E7", "green": "\U0001F7E9", "red": "\U0001F7E5", "yellow": "\U0001F7E8"}
	monitoring_mg = ""
	docker_counts = get_docker_counts()
	header_message = f"*{node_name}* (docker.check)\ndocker monitor:\n"
	if os.path.exists(f"{current_path}/config.json"):
		with open(f"{current_path}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		sec_repeat = int(parsed_json["SEC_REPEAT"])
		default_dot_style = parsed_json["DEFAULT_DOT_STYLE"]
		if not default_dot_style:
			dots = square_dots
		orange_dot, green_dot, red_dot, yellow_dot = dots["orange"], dots["green"], dots["red"], dots["yellow"]
		telegram_on, discord_on, gotify_on, ntfy_on, pushbullet_on, pushover_on, slack_on = (parsed_json[key]["ON"] for key in ["TELEGRAM", "DISCORD", "GOTIFY", "NTFY", "PUSHBULLET", "PUSHOVER", "SLACK"])
		services = {"TELEGRAM": ["TOKENS", "CHAT_IDS"], "DISCORD": ["TOKENS"], "SLACK": ["TOKENS"],"GOTIFY": ["TOKENS", "CHAT_URLS"],
			"NTFY": ["TOKENS", "CHAT_URLS"], "PUSHBULLET": ["TOKENS"], "PUSHOVER": ["TOKENS", "USER_KEYS"]}
		for service, keys in services.items():
			if parsed_json[service]["ON"]:
				globals().update({f"{service.lower()}_{key.lower()}": parsed_json[service][key] for key in keys})
				monitoring_mg += f"- messaging: {service.capitalize()},\n"
		monitoring_mg += "".join(f"- monitoring: {count} {resource}\n" for resource, count in docker_counts.items())
		send_message(f"{header_message}{monitoring_mg}- polling period: {sec_repeat} seconds.")	
	else:
		print("config.json not found")


"""Periodically check for changes in Docker resources"""
@repeat(every(sec_repeat).seconds)
def docker_checker():
	"""Check for changes in Docker images"""
	global old_list_images
	status_dot, status_message = yellow_dot, "pulled"
	message, header_message = "", f"*{node_name}* (docker.images)\n"
	list_images = result = []
	list_images = get_docker_data("images")
	if list_images:
		if not old_list_images: old_list_images = list_images
		if len(list_images) >= len(old_list_images):
			result = [image for image in list_images if image not in old_list_images]
		else:
			result = [image for image in old_list_images if image not in list_images]
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
			message = "\n".join(sorted(message.splitlines()))
			if all(keyword in message for keyword in [orange_dot, yellow_dot, "unused!", "pulled!"]):
				parts_message = message.split()
				unused_id, name_image = parts_message[1].rstrip(':').strip('*'), parts_message[4]
				replace_name = f"{name_image} ({unused_id}):"
				message = message.replace(parts_message[1], replace_name)
			send_message(f"{header_message}{message}")

	"""Check for changes in Docker networks and volumes"""
	check_types = ["volumes", "networks"]
	global old_list_networks
	global old_list_volumes
	for check_type in check_types:
		status_dot, status_message = yellow_dot, "created"
		message, header_message = "", f"*{node_name}* (docker.{check_type})\n"
		new_list = old_list = result = []
		old_list = old_list_volumes if check_type == "volumes" else old_list_networks
		new_list = get_docker_data(check_type)
		if new_list:
			if not old_list: old_list = new_list
			if len(new_list) >= len(old_list):
				result = [item for item in new_list if item not in old_list]
			else:
				result = [item for item in old_list if item not in new_list]
				status_dot, status_message = red_dot, "removed"
			if check_type == "volumes":
				old_list_volumes = new_list
			else:
				old_list_networks = new_list
			if result:
				message = "\n".join(sorted(f"{status_dot} *{item}*: {status_message}!" for item in result))
				send_message(f"{header_message}{message}")

	"""Check for changes in Docker unused networks and volumes"""
	check_types = ["volumes", "networks"]
	global old_list_uvolumes
	global old_list_unetworks
	for check_type in check_types:
		status_dot, status_message = orange_dot, "unused"
		message, header_message = "", f"*{node_name}* (docker.{check_type})\n"
		new_list = old_list = result = []
		old_list = old_list_uvolumes if check_type == "volumes" else old_list_unetworks
		new_list = get_docker_data(f"u{check_type}")
		if new_list:
			if len(new_list) >= len(old_list):
				result = [item for item in new_list if item not in old_list]
			if check_type == "volumes":
				old_list_uvolumes = new_list
			else:
				old_list_unetworks = new_list
			if result:
				for item in result:
					message += f"{status_dot} *{item}*: {status_message}!\n" if check_type == "volumes" else f"{status_dot} *{item.split()[0]}* ({item.split()[-1]}): {status_message}!\n"
				message = "\n".join(sorted(message.splitlines()))
				send_message(f"{header_message}{message}")

	"""Check for changes in Docker containers"""
	global old_list_containers
	status_dot = orange_dot
	message, header_message = "", f"*{node_name}* (docker.containers)\n"
	list_containers = result = []
	stopped = False
	container_name, container_attr, container_status = "", "", "inactive"
	list_containers = get_docker_data("containers")
	if list_containers:
		if not old_list_containers:
			old_list_containers = list_containers
		if len(list_containers) >= len(old_list_containers):
			result = [item for item in list_containers if item not in old_list_containers]
		else:
			result = [item for item in old_list_containers if item not in list_containers]
			stopped = True
		if result:
			old_list_containers = list_containers
			for container in result:
				container_info = "".join(container).split()
				container_name = container_info[0]
				if container_name:
					container_attr = container_info[2]
					if container_attr != "starting":
						if not stopped: container_status = container_info[1]
						if container_status == "running":
							status_dot = green_dot
							if container_attr != container_status:
								container_status = f"{container_status} ({container_attr})"
							if container_attr == "unhealthy":
								status_dot = orange_dot
						elif container_status == "created":
							status_dot = yellow_dot
						elif container_status == "inactive":
							status_dot = red_dot
						message += f"{status_dot} *{container_name}*: {container_status}!\n"
				status_dot = orange_dot
			if message:
				message = "\n".join(sorted(message.splitlines()))
				send_message(f"{header_message}{message}")

while True:
	run_pending()
	time.sleep(1)
