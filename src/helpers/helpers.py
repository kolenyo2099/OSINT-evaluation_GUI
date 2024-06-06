# local imports
import json
import socket

def read_local_keys():
	# read keys from local file
	keys_file = './secrets/keys.json'
	keys = dict()
	with open(keys_file) as f:
		keys = json.loads(f.read())
	return keys

def read_instructions():
	# read instructions to send to GPT
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
	except socket.error as ex:
		return False