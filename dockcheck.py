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
            "node_name": docker_client.info().get("Name", ""),
            "docker_version": docker_client.version().get("Version", "")
        }
    except (docker.errors.DockerException, Exception) as e:
        print(f"Error: {e}")
        return {"node_name": "", "docker_version": ""}


def getDockerResourcesCounts(stacks_enabled: bool, containers_enabled: bool, images_enabled: bool, networks_enabled: bool, volumes_enabled: bool) -> dict:
    """Retrieve the count of Docker resources (stacks, containers, images, networks, volumes)"""
    resources = {"stacks": 0, "containers": 0, "networks": 0, "volumes": 0, "images": 0}
    try:
        docker_client = docker.from_env()
        containers = docker_client.containers.list()
        compose_projects = {c.labels.get("com.docker.compose.project") for c in containers if c.labels.get("com.docker.compose.project")}
        if stacks_enabled:
            resources["stacks"] = len(compose_projects)
        if containers_enabled:
            resources["containers"] = len(containers)
        if images_enabled:
            resources["images"] = len(docker_client.images.list())
        if networks_enabled:
            resources["networks"] = len(docker_client.networks.list())
        if volumes_enabled:
            resources["volumes"] = len(docker_client.volumes.list())
    except (docker.errors.DockerException, Exception) as e:
        print(f"Error: {e}")
    return resources


def getDockerData(data_type: str) -> tuple:
    """Retrieve detailed data for Docker resources: networks, unused networks, images, containers, stacks, or volumes"""
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
                [used_networks.append(network) for network in container.attrs["NetworkSettings"]["Networks"]]
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
        elif data_type == "stacks":
            containers = docker_client.containers.list()
            for container in containers:
                labels = container.labels
                stack_name = labels.get("com.docker.compose.project")
                stack_hash = labels.get("com.docker.compose.config-hash") 
                if stack_name:
                    resource_data.append(f"{stack_name} {stack_hash}")
        else:
            volumes = docker_client.volumes.list() if data_type == "volumes" else docker_client.volumes.list(filters={"dangling": "true"})
            if volumes: [resource_data.append(f"{volume.short_id}") for volume in volumes]
    except (docker.errors.DockerException, Exception) as e:
        print(f"Error: {e}")
    return resource_data


def SendMessage(message: str):
    """Internal function to send HTTP POST requests with error handling"""
    def SendRequest(url, json_data=None, data=None, headers=None):
        try:
            response = requests.post(url, json=json_data, data=data, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
    
    """"Converts Markdown-like syntax to HTML format."""
    def toHTMLFormat(message: str) -> str:
        message = ''.join(f"<b>{part}</b>" if i % 2 else part for i, part in enumerate(message.split('*')))
        return message.replace("\n", "<br>")

    """Converts the message to the specified format (HTML, Markdown, or plain text)"""
    def toMarkdownFormat(message: str, m_format: str) -> str:
        if m_format == "html":
            return toHTMLFormat(message)
        elif m_format == "markdown":
            return message.replace("*", "**")
        elif m_format == "text":
            return message.replace("*", "")
        return message

    """Iterate through multiple platform configurations"""
    for url, header, pyload, format_message in zip(platform_webhook_url, platform_header, platform_pyload, platform_format_message):
        data, ntfy = None, False
        formated_message = toMarkdownFormat(message, format_message)
        header_json = header if header else None
        for key in list(pyload.keys()):
            if key == "title":
                delimiter = "<br>" if format_message == "html" else "\n"
                header, formated_message = formated_message.split(delimiter, 1)
                pyload[key] = header.replace("*", "")
            elif key == "extras":
                formated_message = formated_message.replace("\n", "\n\n")
                pyload["message"] = formated_message
            elif key == "data":
                ntfy = True
            pyload[key] = formated_message if key in ["text", "content", "message", "body", "formatted_body", "data"] else pyload[key]
        pyload_json = None if ntfy else pyload
        data = formated_message.encode("utf-8") if ntfy else None
        """Send the request with the appropriate payload and headers"""
        SendRequest(url, pyload_json, data, header_json)


if __name__ == "__main__":
    """Load configuration and initialize monitoring"""
    docker_info = getDockerInfo()
    node_name = docker_info["node_name"]
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
    old_list_images = unused_image_name = []
    old_list_stacks = old_list_containers = []
    old_list_networks = old_list_unetworks = []
    old_list_volumes = old_list_uvolumes = []
    dots = {"orange": "\U0001F7E0", "green": "\U0001F7E2", "red": "\U0001F534", "yellow": "\U0001F7E1"}
    square_dots = {"orange": "\U0001F7E7", "green": "\U0001F7E9", "red": "\U0001F7E5", "yellow": "\U0001F7E8"}
    header_message = f"*{node_name}* (.dockcheck)\n"
    monitoring_message = f"- docker version: {docker_info['docker_version']},\n"
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config_json = json.loads(file.read())
        try:
            startup_message = config_json.get("STARTUP_MESSAGE", True)
            compact_format = config_json.get("COMPACT_MESSAGE", False)
            default_dot_style = config_json.get("DEFAULT_DOT_STYLE", True)
            sec_repeat = max(int(config_json.get("SEC_REPEAT", 10)), 10)
            monitoring_resources = config_json.get("MONITORING_RESOURCES", {})
            stacks_enabled = monitoring_resources.get("STACKS", True)
            containers_enabled = monitoring_resources.get("CONTAINERS", True)
            networks_enabled = monitoring_resources.get("NETWORKS", True)
            volumes_enabled = monitoring_resources.get("VOLUMES", True)
            images_enabled = monitoring_resources.get("IMAGES", True)
        except (json.JSONDecodeError, ValueError, TypeError, KeyError):
            startup_message, compact_format, default_dot_style = True, False, True
            sec_repeat = 10
            stacks_enabled = containers_enabled = networks_enabled = volumes_enabled = images_enabled = True
        if not default_dot_style:
            dots = square_dots
        orange_dot, green_dot, red_dot, yellow_dot = dots["orange"], dots["green"], dots["red"], dots["yellow"]
        no_messaging_keys = ["MONITORING_RESOURCES", "STARTUP_MESSAGE", "COMPACT_MESSAGE", "DEFAULT_DOT_STYLE", "SEC_REPEAT"]
        messaging_platforms = list(set(config_json) - set(no_messaging_keys))
        for platform in messaging_platforms:
            if config_json[platform].get("ENABLED", False):
                for key, value in config_json[platform].items():
                    platform_key = f"platform_{key.lower()}"
                    if platform_key in globals():
                        globals()[platform_key] = (globals()[platform_key] if isinstance(globals()[platform_key], list) else [globals()[platform_key]])
                        globals()[platform_key].extend(value if isinstance(value, list) else [value])
                    else:
                        globals()[platform_key] = value if isinstance(value, list) else [value]
                monitoring_message += f"- messaging: {platform.lower().capitalize()},\n"
        monitoring_message = "\n".join([*sorted(monitoring_message.splitlines()), ""])
        data_sources = {
            "stacks": stacks_enabled,
            "containers": containers_enabled,
            "images": images_enabled,
            "networks": networks_enabled,
            "volumes": volumes_enabled,
            "uvolumes": volumes_enabled,
            "unetworks": networks_enabled
        }
        for resource, condition in data_sources.items():
            if condition:
                globals()[f"old_list_{resource}"] = getDockerData(resource)
        docker_counts = getDockerResourcesCounts(stacks_enabled, containers_enabled, images_enabled, networks_enabled, volumes_enabled)
        monitoring_message += "".join(f"- monitoring: {count} {resource},\n" for resource, count in docker_counts.items() if count != 0)
        monitoring_message += (
            f"- startup message: {startup_message},\n"
            f"- compact message: {compact_format},\n"
            f"- default dot style: {default_dot_style},\n"
            f"- polling period: {sec_repeat} seconds."
        )
        if all(value in globals() for value in ["platform_webhook_url", "platform_header", "platform_pyload", "platform_format_message"]):
            if startup_message:
                SendMessage(f"{header_message}{monitoring_message}")
        else:
            print("config.json is wrong")
            sys.exit(1)
    else:
        print("config.json not found")
        sys.exit(1)


"""Periodically check for changes in Docker monitoring resources"""
@repeat(every(sec_repeat).seconds)
def DockerChecker():
    """Check for changes in Docker images"""
    if images_enabled:
        global old_list_images, unused_image_name
        status_dot, status_message = yellow_dot, "pulled"
        message, header_message = "", f"*{node_name}* (.images)\n"
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
                        if image_id in "".join(unused_image_name) and not compact_format:
                            for unsed_image in unused_image_name:
                                if image_id in unsed_image:
                                    parts_unused = unsed_image.split()
                                    image_unsed_name, image_unsed_id = parts_unused[0], parts_unused[-1]
                                    message += f"{status_dot} *{image_unsed_name}* ({image_unsed_id}): {status_message}!\n"
                                    unused_image_name.remove(unsed_image)
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
                        unused_image_name.append(f"{name_image} {unused_id}")
                        parts_message[1] = replace_name
                        new_message.append(" ".join(parts_message))
                    message = " ".join(new_message).replace("! ", "!\n")
                SendMessage(f"{header_message}{message}")

    """Check for changes in Docker networks and volumes"""
    if networks_enabled or volumes_enabled:
        check_types = ["networks" if networks_enabled else None, "volumes" if volumes_enabled else None]
        check_types = [check for check in check_types if check]
        global old_list_networks, old_list_volumes
        for check_type in check_types:
            status_dot, status_message = yellow_dot, "created"
            message, header_message = "", f"*{node_name}* (.{check_type})\n"
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
                        item_name = item.split()[0]
                        item_detail = f" ({item.split()[-1]})" if check_type != "volumes" and not compact_format else ""
                        message += f"{status_dot} *{item_name}*{item_detail}: {status_message}!\n"
                    message = "\n".join(sorted(message.splitlines()))
                    SendMessage(f"{header_message}{message}")
    
        """Check for changes in Docker unused networks and volumes"""
        global old_list_uvolumes, old_list_unetworks
        for check_type in check_types:
            status_dot, status_message = orange_dot, "unused"
            message, header_message = "", f"*{node_name}* (.{check_type})\n"
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
                        item_name = item.split()[0]
                        item_detail = f" ({item.split()[-1]})" if check_type != "volumes" and not compact_format else ""
                        message += f"{status_dot} *{item_name}*{item_detail}: {status_message}!\n"
                    message = "\n".join(sorted(message.splitlines()))
                    SendMessage(f"{header_message}{message}")
                
    """Check for changes in Docker stacks"""
    if stacks_enabled:
        global old_list_stacks
        status_dot, status_message = orange_dot, "changed"
        message, header_message = "", f"*{node_name}* (.stacks)\n"
        list_stacks = result = []
        list_stacks = getDockerData("stacks")
        if list_stacks:
            if not old_list_stacks:
                old_list_stacks = list_stacks
            if len(list_stacks) == len(old_list_stacks):
                result = [item for item in list_stacks if item not in old_list_stacks]
            if result:
                old_list_stacks = list_stacks
                for stack in result:
                    stack_name, stack_hash = stack.split()
                    message += f"{status_dot} *{stack_name}*{'' if compact_format else f' ({stack_hash[:12]})'}: {status_message}!\n"
                message = "\n".join(sorted(message.splitlines()))
                SendMessage(f"{header_message}{message}")

    """Check for changes in Docker containers"""
    if containers_enabled:
        global old_list_containers
        status_dot = orange_dot
        message, header_message = "", f"*{node_name}* (.containers)\n"
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
                                container_status = container_attr if container_attr != container_status else container_status
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
