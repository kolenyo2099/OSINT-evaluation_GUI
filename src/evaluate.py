# local imports
import argparse
from helpers import check_connection, read_local_keys, read_instructions

def main():
	parser = argparse.ArgumentParser(prog = 'evaluate.py',
									 description =  '',
									 epilog = '')
	parser.add_argument('input', type = str,
						help = 'help')
	args = parser.parse_args()

	# make sure an internet connection is active
	if check_connection() is False:
		print('no internet connection')
		exit()

	keys = read_local_keys()

	# if ',' in args.input:
	# 	for i in args.input.split(','):
	# 		# if i is url
	# 			# get tweets from thread url
	# 			# evaluate thread
	# 		# else
	# 			# search for threads of user
	# 			# get threads
	# 			# get tweets from threads
	# 			# evaluate threads
	# else:
	# 	# if args.input is url
	# 		# get tweets from thread url
	# 		# evaluate thread
	# 	# else
	# 		# search for threads of user
	# 		# get threads
	# 		# get tweets from threads
	# 		# evaluate threads

if __name__ == '__main__':
	main()