# local imports
import json
import os
import socket

def read_local_keys():
	# read keys from local file
	keys_file = './secrets/keys.json'
	keys = dict()
	with open(keys_file) as f:
		keys = json.loads(f.read())
	return keys

def read_instructions():
	# read instructions for GPT
	instructions_file = './secrets/instructions.txt'
	instructions = None
	with open(instructions_file) as f:
		instructions = f.read()
	return instructions

def check_connection(host = '8.8.8.8', port = 53, timeout = 3):
	# attempt to connect to Google 
	# to establish whether a working internet connection is present
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except:
		return False

def check_user_blacklist(user):
	# create local data folder if not present
	if not os.path.isdir('./local_data/'):
		os.makedirs('./local_data/')

	filename = './local_data/blacklist_users.txt'
	# if blacklist users file does not exist, initiate one
	# and return False since user is not blacklisted
	if not os.path.isfile(filename):
		with open(filename, 'w') as file:
			file.write('')
		return False
	# otherwise, read blacklisted users and check if user is present
	else:
		unavailable_users = set()
		with open(filename, 'r') as file:
			users = file.read()
			unavailable_users = set(user for user in users.split('\n') if len(user) > 0)
		if user in unavailable_users:
			return True
		else:
			return False

def add_user_to_blacklist(user):
	# add user to blacklist file
	filename = './local_data/blacklist_users.txt'
	with open(filename, 'a') as file:
		file.write(user + '\n')
