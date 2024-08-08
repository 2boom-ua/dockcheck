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
	node_name = ""
	try:
		node_name = docker.from_env().info().get('Name')
	except docker.errors.DockerException as e:
		print("Error:", e)
	return node_name


def get_docker_counts():
	docker_counts = {"volumes": 0, "images": 0, "networks": 0, "containers": 0}
	try:
		docker_client = docker.from_env()
		docker_counts["volumes"] = len(docker_client.volumes.list())
		docker_counts["images"] = len(docker_client.images.list())
		docker_counts["networks"] = len(docker_client.networks.list())
		docker_counts["containers"] = len(docker_client.containers.list())
	except docker.errors.DockerException as e:
		print("Error:", e)
	except Exception as e:
		print("Error:", e)
	return docker_counts


def get_docker_data(type_of_data):
	return_data = []
	try:
		docker_client = docker.from_env()
		if type_of_data == "networks":
			networks = docker_client.networks.list()
			if networks: [return_data.append(f"{network.name}") for network in networks]
		elif type_of_data == "unetworks":
			used_networks = []
			default_networks = ["none", "host"]
			networks = docker_client.networks.list()
			containers = docker_client.containers.list(all=True)
			for container in containers:
				[used_networks.append(network) for network in container.attrs['NetworkSettings']['Networks']]
			unused_networks = [network for network in networks if network.name not in used_networks and network.name not in default_networks]
			if unused_networks: [return_data.append(f"{network.name} {network.short_id}") for network in unused_networks]
		elif type_of_data == "images":
			images = docker_client.images.list()
			if images:
				for image in images:
					imagename = ''.join(image.tags).split(':')[0].split('/')[-1]
					if imagename == '': imagename = image.short_id.split(':')[-1]
					return_data.append(f"{image.short_id.split(':')[-1]} {imagename}")
		elif type_of_data == "containers":
			for container in docker_client.containers.list(all=True):
				container_info = docker_client.api.inspect_container(container.id)
				if "State" in container_info and "Health" in container_info["State"]:
					return_data.append(f"{container.name} {container.status} {container.attrs['State']['Health']['Status']} {container.short_id}")
				else:
					return_data.append(f"{container.name} {container.status} {container.attrs['State']['Status']} {container.short_id}")
		else:
			if type_of_data == "volumes":
				volumes = docker_client.volumes.list()
			else:
				volumes = docker_client.volumes.list(filters={"dangling": "true"})
			if volumes: [return_data.append(f"{volume.short_id}") for volume in volumes]
	except docker.errors.DockerException as e:
		print("Error:", e)
	except Exception as e:
		print("Error:", e)
	return return_data


def send_message(message : str):
	if telegram_on:
		try:
			for telegram_token, telegram_chat_id in zip(telegram_tokens, telegram_chat_ids):
				response = requests.post(f"https://api.telegram.org/bot{telegram_token}/sendMessage", json = {"chat_id": telegram_chat_id, "text": message, "parse_mode": "Markdown"})
				response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending Telegram message: {e}")
	if discord_on:
		try:
			for discord_token in discord_tokens:
				response = requests.post(f"https://discord.com/api/webhooks/{discord_token}", json = {"content": message.replace("*", "**")})
				response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending Discord message: {e}")
	if slack_on:
		try:
			for slack_token in slack_tokens:
				response = requests.post(f"https://hooks.slack.com/services/{slack_token}", json = {"text": message})
				response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending Slack message: {e}")
	message = message.replace("*", "")
	header, message = message.split("\n", 1)
	message = message.strip()
	if gotify_on:
		try:
			for gotify_chat_web, gotify_token in zip(gotify_chat_webs, gotify_tokens):
				response = requests.post(f"{gotify_chat_web}/message?token={gotify_token}", json={'title': header, 'message': message, 'priority': 0})
				response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending Gotify message: {e}")
	if ntfy_on:
		try:
			for ntfy_chat_web, ntfy_token in zip(ntfy_chat_webs, ntfy_tokens):
				response = requests.post(f"{ntfy_chat_web}/{ntfy_token}", data = message.encode(encoding = 'utf-8'), headers = {"title": header})
				response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending Ntfy message: {e}")
	if pushbullet_on:
		try:
			for pushbullet_token in pushbullet_tokens:
				response = requests.post('https://api.pushbullet.com/v2/pushes',\
				json = {'type': 'note', 'title': header, 'body': message}, headers = {'Access-Token': pushbullet_token, 'Content-Type': 'application/json'})
				response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending Pushbullet message: {e}")


if __name__ == "__main__":
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
		telegram_on, discord_on, gotify_on = parsed_json["TELEGRAM"]["ON"], parsed_json["DISCORD"]["ON"], parsed_json["GOTIFY"]["ON"]
		ntfy_on, pushbullet_on, slack_on = parsed_json["NTFY"]["ON"], parsed_json["PUSHBULLET"]["ON"], parsed_json["SLACK"]["ON"]
		if telegram_on:
			telegram_tokens, telegram_chat_ids = parsed_json["TELEGRAM"]["TOKENS"], parsed_json["TELEGRAM"]["CHAT_IDS"]
			monitoring_mg += "- messenging: Telegram,\n"
		if discord_on:
			discord_tokens = parsed_json["DISCORD"]["TOKENS"]
			monitoring_mg += "- messenging: Discord,\n"
		if slack_on:
			slack_tokens = parsed_json["SLACK"]["TOKENS"]
			monitoring_mg += "- messenging: Slack,\n"
		if gotify_on:
			gotify_tokens, gotify_chat_webs = parsed_json["GOTIFY"]["TOKENS"], parsed_json["GOTIFY"]["CHAT_WEB"]
			monitoring_mg += "- messenging: Gotify,\n"
		if ntfy_on:
			ntfy_tokens, ntfy_chat_webs = parsed_json["NTFY"]["TOKENS"], parsed_json["NTFY"]["CHAT_WEB"]
			monitoring_mg += "- messenging: Ntfy,\n"
		if pushbullet_on:
			pushbullet_tokens = parsed_json["PUSHBULLET"]["TOKENS"]
			monitoring_mg += "- messenging: Pushbullet,\n"
		for type_of in docker_counts:
			monitoring_mg += f"- monitoring: {docker_counts[type_of]} {type_of}\n"
		send_message(f"{header_message}{monitoring_mg}- polling period: {sec_repeat} seconds.")
	else:
		print("config.json not found")


@repeat(every(sec_repeat).seconds)
def docker_checker():
	#docker-image
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
			status_dot = red_dot
			status_message = "removed"
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


	#docker-volume.network
	check_types = ["volumes", "networks"]
	global old_list_networks
	global old_list_volumes
	for check_type in check_types:
		status_dot = yellow_dot
		message, header_message = "", f"*{nodename}* (docker.{check_type})\n"
		list_of = old_list = result = []
		if check_type == "volumes":
			old_list = old_list_volumes
			list_of = get_docker_data("volumes")
		else:
			old_list = old_list_networks
			list_of = get_docker_data("networks")
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
				old_list_volumes = list_of
			else:
				old_list_networks = list_of
			if result:
				for item in result:
					message += f"{status_dot} *{item}*: {status_message}!\n"
				message = "\n".join(sorted(message.split("\n"))).lstrip("\n")
				send_message(f"{header_message}{message}")


	#docker-unused.volumes.networks
	check_types = ["volumes", "networks"]
	global old_list_uvolumes
	global old_list_unetworks
	for check_type in check_types:
		status_dot = orange_dot
		message, header_message = "", f"*{nodename}* (docker.{check_type})\n"
		list_of = old_list = result = []
		if check_type == "volumes":
			old_list = old_list_uvolumes
			list_of = get_docker_data("unused_volumes")
		else:
			old_list = old_list_unetworks
			list_of = get_docker_data("unetworks")
		if list_of:
			if len(list_of) >= len(old_list):
				result = list(set(list_of) - set(old_list))
				status_message = "unused"
			if check_type == "volumes":
				old_list_uvolumes = list_of
			else:
				old_list_unetworks = list_of
			if result:
				for item in result:
					if check_type == "volumes":
						message += f"{status_dot} *{item}*: {status_message}!\n"
					else:
						message += f"{status_dot} *{item.split()[0]}* ({item.split()[-1]}): {status_message}!\n"
				message = "\n".join(sorted(message.split("\n"))).lstrip("\n")
				send_message(f"{header_message}{message}")


	#docker-container
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
