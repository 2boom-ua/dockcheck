import requests
import json

def matrix_login(user_name, password, server_url):
	login_url = f"{server_url}/_matrix/client/r0/login"
	login_payload = {
		"type": "m.login.password",
		"user": user_name,
		"password": password
	}
	
	response = requests.post(login_url, json=login_payload)
	
	if response.status_code == 200:
		access_token = response.json().get("access_token")
		return access_token
	else:
		print(f"Login failed: {response.status_code} {response.reason}")
		return None

if __name__ == "__main__":
	user_name = "login_name"
	password = "your_password"
	server_url = "https://your_server"
	
	access_token = matrix_login(user_name, password, server_url)
	print(f"Token: {access_token}")
