#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Copyright (c) 2024 2boom.

import json
import docker
import os
import time
import requests
from schedule import every, repeat, run_pending
	

def getDockerInfo() -> dict:
	"""Get Docker node name and version."""
	try:
		docker_client = docker.from_env()
		return {
			"node_name": docker_client.info().get('Name', ""),
			"docker_version": docker_client.version().get('Version', "")
		}
	except (docker.errors.DockerException, Exception) as e:
		print(f"Error: {e}")
		return {"node_name": "", "docker_version": ""}


def getDockerResourcesCounts() -> dict:
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


def getDockerData(data_type: str) -> tuple:
	"""Retrieve detailed data for Docker resources: volumes, images, networks, and containers."""
	resource_data = []
	default_networks = ["none", "host", "bridge"]
	try:
		docker_client = docker.from_env()
		if data_type == "networks":
			networks = docker_client.networks.list()
			if networks: [resource_data.append(f"{network.name} {network.short_id}") for network in networks if network.name not in default_networks]
		elif data_type == "unetworks":
			used_networks = []
			networks = docker_client.networks.list()
			for container in docker_client.containers.list(all=True):
				[used_networks.append(network) for network in container.attrs['NetworkSettings']['Networks']]
			unused_networks = [network for network in networks if network.name not in used_networks and network.name not in default_networks]
			if unused_networks: [resource_data.append(f"{network.name} {network.short_id}") for network in unused_networks]
		elif data_type == "images":
			images = docker_client.images.list()
			if images:
				for image in images:
					image_name = image.tags[0].split(':')[0].split('/')[-1] if image.tags else image.short_id.split(':')[-1]
					resource_data.append(f"{image.short_id.split(':')[-1]} {image_name}")
		elif data_type == "containers":
			for container in docker_client.containers.list(all=True):
				container_info = docker_client.api.inspect_container(container.id)
				health_status = container_info.get("State", {}).get("Health", {}).get("Status")
				status = health_status if health_status else container_info["State"]["Status"]
				resource_data.append(f"{container.name} {container.status} {status} {container.short_id}")
		else:
			volumes = docker_client.volumes.list() if data_type == "volumes" else docker_client.volumes.list(filters={"dangling": "true"})
			if volumes: [resource_data.append(f"{volume.short_id}") for volume in volumes]
	except (docker.errors.DockerException, Exception) as e:
		print(f"Error: {e}")
	return resource_data


def SendMessage(message: str):
	"""Send notifications to various messaging services (Telegram, Discord, Gotify, Ntfy, Pushbullet, Pushover, Matrix, Zulip, Flock, Slack, RocketChat, Pumble, Mattermost, CUSTOM)."""
	"""CUSTOM - single_asterisks - Zulip, Flock, Slack, RocketChat, Flock, double_asterisks - Pumble, Mattermost """
	def SendRequest(url, json_data=None, data=None, headers=None):
		"""Send an HTTP POST request and handle exceptions."""
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")

	if telegram_on:
		for token, chat_id in zip(telegram_tokens, telegram_chat_ids):
			url = f"https://api.telegram.org/bot{token}/sendMessage"
			json_data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
			SendRequest(url, json_data)
	if slack_on:
		for url in slack_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if rocket_on:
		for url in rocket_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if zulip_on:
		for url in zulip_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if flock_on:
		for url in flock_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if custom_on:
		for url, std_bold in zip(custom_webhook_urls, custom_std_bolds):
			bold_markdown = "**" if std_bold else "*"
			json_data = {"text": message.replace("*", bold_markdown)}
			SendRequest(url, json_data)
	if matrix_on:
		for token, server_url, room_id in zip(matrix_tokens, matrix_server_urls, matrix_room_ids):
			url = f"{server_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message?access_token={token}"
			matrix_message = "<br>".join(string.replace('*', '<b>', 1).replace('*', '</b>', 1) for string in message.split("\n"))
			json_data = {"msgtype": "m.text", "body": matrix_message, "format": "org.matrix.custom.html", "formatted_body": matrix_message}
			SendRequest(url, json_data)
	if discord_on:
		for url in discord_webhook_urls:
			json_data = {"content": message.replace("*", "**")}
			SendRequest(url, json_data)
	if mattermost_on:
		for url in mattermost_webhook_urls:
			json_data = {'text': message.replace("*", "**")}
			SendRequest(url, json_data)
	if pumble_on:
		for url in pumble_webhook_urls:
			json_data = {"text": message.replace("*", "**")}
			SendRequest(url, json_data)
	if ntfy_on:
		for url in ntfy_webhook_urls:
			headers_data = {"Markdown": "yes"}
			SendRequest(url, None, message.replace("*", "**").encode(encoding = "utf-8"), headers_data)

	header, message = message.split("\n", 1)
	message = message.strip()

	if gotify_on:
		for token, server_url in zip(gotify_tokens, gotify_server_urls):
			url = f"{server_url}/message?token={token}"
			json_data = {'title': header.replace("*", ""), "message": message.replace("*", "**").replace("\n", "\n\n"), "priority": 0, "extras": {"client::display": {"contentType": "text/markdown"}}}
			SendRequest(url, json_data)
	if pushover_on:
		for token, user_key in zip(pushover_tokens, pushover_user_keys):
			url = "https://api.pushover.net/1/messages.json"
			pushover_message = "\n".join(string.replace('*', '<b>', 1).replace('*', '</b>', 1) for string in message.split("\n"))
			json_data = {"token": token, "user": user_key, "message": pushover_message, "title": header.replace("*", ""), "html": "1"}
			SendRequest(url, json_data)
	if pushbullet_on:
		for token in pushbullet_tokens:
			url = "https://api.pushbullet.com/v2/pushes"
			json_data = {'type': 'note', 'title': header.replace("*", ""), 'body': message.replace("*", "")}
			headers_data = {'Access-Token': token, 'Content-Type': 'application/json'}
			SendRequest(url, json_data, None, headers_data)


if __name__ == "__main__":
	"""Load configuration and initialize monitoring"""
	docker_info = getDockerInfo()
	node_name = docker_info['node_name']
	current_path = os.path.dirname(os.path.realpath(__file__))
	docker_data_types = ["containers", "networks", "volumes", "images", "uvolumes", "unetworks"]
	old_list_containers, old_list_networks, old_list_volumes, old_list_images, old_list_uvolumes, old_list_unetworks = [getDockerData(data_type) for data_type in docker_data_types]
	unused_id_name = []
	dots = {"orange": "\U0001F7E0", "green": "\U0001F7E2", "red": "\U0001F534", "yellow": "\U0001F7E1"}
	square_dots = {"orange": "\U0001F7E7", "green": "\U0001F7E9", "red": "\U0001F7E5", "yellow": "\U0001F7E8"}
	monitoring_mg = ""
	docker_counts = getDockerResourcesCounts()
	header_message = f"*{node_name}* (docker.check)\n- docker version: {docker_info['docker_version']},\n"
	if os.path.exists(f"{current_path}/config.json"):
		with open(f"{current_path}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		sec_repeat = int(parsed_json["SEC_REPEAT"])
		if sec_repeat < 10: sec_repeat = 10
		startup_message = parsed_json["STARTUP_MESSAGE"]
		default_dot_style = parsed_json["DEFAULT_DOT_STYLE"]
		compact_format = parsed_json["COMPACT_MESSAGE"]
		if not default_dot_style:
			dots = square_dots
		orange_dot, green_dot, red_dot, yellow_dot = dots["orange"], dots["green"], dots["red"], dots["yellow"]
		messaging_platforms = ["TELEGRAM", "DISCORD", "GOTIFY", "NTFY", "PUSHBULLET", "PUSHOVER", "SLACK", "MATRIX", "MATTERMOST", "PUMBLE", "ROCKET", "ZULIP", "FLOCK", "CUSTOM"]
		telegram_on, discord_on, gotify_on, ntfy_on, pushbullet_on, pushover_on, slack_on, matrix_on, mattermost_on, pumble_on, rocket_on, zulip_on, flock_on, custom_on = (parsed_json[key]["ON"] for key in messaging_platforms)
		services = {
			"TELEGRAM": ["TOKENS", "CHAT_IDS"],
			"DISCORD": ["WEBHOOK_URLS"],
			"SLACK": ["WEBHOOK_URLS"],
			"GOTIFY": ["TOKENS", "SERVER_URLS"],
			"NTFY": ["WEBHOOK_URLS"],
			"PUSHBULLET": ["TOKENS"],
			"PUSHOVER": ["TOKENS", "USER_KEYS"],
			"MATRIX": ["TOKENS", "SERVER_URLS", "ROOM_IDS"],
			"MATTERMOST": ["WEBHOOK_URLS"],
			"PUMBLE": ["WEBHOOK_URLS"],
			"ROCKET": ["WEBHOOK_URLS"],
			"ZULIP": ["WEBHOOK_URLS"],
			"FLOCK": ["WEBHOOK_URLS"],
			"CUSTOM": ["WEBHOOK_URLS", "STD_BOLDS"]
		}
		for service, keys in services.items():
			if parsed_json[service]["ON"]:
				globals().update({f"{service.lower()}_{key.lower()}": parsed_json[service][key] for key in keys})
				monitoring_mg += f"- messaging: {service.capitalize()},\n"
		monitoring_mg += "".join(f"- monitoring: {count} {resource},\n" for resource, count in docker_counts.items())
		monitoring_mg += f"- polling period: {sec_repeat} seconds,\n- startup message: {startup_message},\n- compact message: {compact_format},\n- default dot style: {default_dot_style}."
		if startup_message:
			SendMessage(f"{header_message}{monitoring_mg}")
	else:
		print("config.json not found")


"""Periodically check for changes in Docker resources"""
@repeat(every(sec_repeat).seconds)
def DockerChecker():
	"""Check for changes in Docker images"""
	global old_list_images, unused_id_name
	status_dot, status_message = yellow_dot, "pulled"
	message, header_message = "", f"*{node_name}* (docker.images)\n"
	list_images = result = []
	list_images = getDockerData("images")
	if list_images:
		if not old_list_images: old_list_images = list_images
		if len(list_images) >= len(old_list_images):
			result = [image for image in list_images if image not in old_list_images]
		else:
			result = [image for image in old_list_images if image not in list_images]
			status_dot, status_message = red_dot, "removed"
		if result:
			old_images_str = ",".join(old_list_images)
			for image in result:
				img_parts = image.split()
				image_id, image_name = img_parts[0], img_parts[-1]
				if image_id == image_name:
					if image_id in old_images_str and status_dot != red_dot:
						status_message, status_dot = "unused", orange_dot
					if image_id in "".join(unused_id_name) and not compact_format:
						for unsed_image in unused_id_name:
							if image_id in unsed_image:
								parts_unused = unsed_image.split()
								image_unsed_name, image_unsed_id = parts_unused[0], parts_unused[-1]
								message += f"{status_dot} *{image_unsed_name}* ({image_unsed_id}): {status_message}!\n"
								unused_id_name.remove(unsed_image)
					else:
						message += f"{status_dot} *{image_name}*: {status_message}!\n"
					if status_dot == orange_dot: status_dot = yellow_dot
				else:
					message += f"{status_dot} *{image_name}*{'' if compact_format else f' ({image_id})'}: {status_message}!\n"

				if status_dot == yellow_dot: status_message = "pulled"
			old_list_images = list_images
			message = "\n".join(sorted(message.splitlines()))
			if all(keyword in message for keyword in [orange_dot, yellow_dot, "unused!", "pulled!"]) and not compact_format:
				new_message = []
				message = message.split('\n')
				half_length = len(message) // 2
				for i in range (half_length):
					tmp_message = f"{message[i]} {message[i + half_length]}"
					parts_message = tmp_message.split()
					unused_id, name_image = parts_message[1].rstrip(':').strip('*'), parts_message[4].strip('*')
					replace_name = f"*{name_image}* ({unused_id}):"
					unused_id_name.append(f"{name_image} {unused_id}")
					parts_message[1] = replace_name
					new_message.append(" ".join(parts_message))
				message = " ".join(new_message).replace('! ', '!\n')
			SendMessage(f"{header_message}{message}")

	"""Check for changes in Docker networks and volumes"""
	check_types = ["volumes", "networks"]
	global old_list_networks, old_list_volumes
	for check_type in check_types:
		status_dot, status_message = yellow_dot, "created"
		message, header_message = "", f"*{node_name}* (docker.{check_type})\n"
		new_list = old_list = result = []
		old_list = old_list_volumes if check_type == "volumes" else old_list_networks
		new_list = getDockerData(check_type)
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
				for item in result:
					message += f"{status_dot} *{item if check_type == 'volumes' else item.split()[0]}*{'' if compact_format else f' ({item.split()[-1]})'}: {status_message}!\n"
				message = "\n".join(sorted(message.splitlines()))
				SendMessage(f"{header_message}{message}")

	"""Check for changes in Docker unused networks and volumes"""
	check_types = ["volumes", "networks"]
	global old_list_uvolumes, old_list_unetworks
	for check_type in check_types:
		status_dot, status_message = orange_dot, "unused"
		message, header_message = "", f"*{node_name}* (docker.{check_type})\n"
		new_list = old_list = result = []
		old_list = old_list_uvolumes if check_type == "volumes" else old_list_unetworks
		new_list = getDockerData(f"u{check_type}")
		if new_list:
			if len(new_list) >= len(old_list):
				result = [item for item in new_list if item not in old_list]
			if check_type == "volumes":
				old_list_uvolumes = new_list
			else:
				old_list_unetworks = new_list
			if result:
				for item in result:
					message += f"{status_dot} *{item if check_type == 'volumes' else item.split()[0]}*{'' if compact_format else f' ({item.split()[-1]})'}: {status_message}!\n"
				message = "\n".join(sorted(message.splitlines()))
				SendMessage(f"{header_message}{message}")

	"""Check for changes in Docker containers"""
	global old_list_containers
	status_dot = orange_dot
	message, header_message = "", f"*{node_name}* (docker.containers)\n"
	list_containers = result = []
	stopped = False
	container_name, container_attr, container_id, container_status = "", "", "", "inactive"
	list_containers = getDockerData("containers")
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
					container_id = container_info[-1]
					if container_attr != "starting":
						if not stopped: container_status = container_info[1]
						if container_status == "running":
							status_dot = green_dot
							if container_attr != container_status:
								container_status = f"{container_attr}"
							if container_attr == "unhealthy":
								status_dot = orange_dot
						elif container_status == "created":
							status_dot = yellow_dot
						elif container_status == "inactive":
							status_dot = red_dot
						message += f"{status_dot} *{container_name}*{'' if compact_format else f' ({container_id})'}: {container_status}!\n"
				status_dot = orange_dot
			if message:
				message = "\n".join(sorted(message.splitlines()))
				SendMessage(f"{header_message}{message}")

while True:
	run_pending()
	time.sleep(1)
