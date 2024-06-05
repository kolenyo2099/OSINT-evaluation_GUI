# local imports
import json
import socket

def read_local_keys(file):
	# read keys from local file
	keys = dict()
	with open(file) as f:
		keys = json.loads(f.read())
	return keys

def check_connection(host = '8.8.8.8', port = 53, timeout = 3):
	# attempt to connect to Google 
	# to establish whether a working internet connection is present
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except socket.error as ex:
		return False