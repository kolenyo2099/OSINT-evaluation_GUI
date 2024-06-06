# local imports
import argparse
from helpers import check_connection, read_local_keys, read_instructions, evaluate_single_thread
from scraper import evaluate_single_thread

def evaluate(item, keys):
	if item.startswith('https://'):
		evaluate_single_thread(item, keys)
	else
		search for threads of user
		get threads
		get tweets from threads
		evaluate threads


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

	try:
		keys = read_local_keys()
	except:
		print('error reading keys from /secrets/keys.json')
		exit()

	try:
		instructions = read_instructions()
	except:
		print('error reading instructions from /secrets/instructions.txt')
		exit()

	if ',' in args.input:
		for item in args.input.split(','):
			evaluate(item, keys)
	else:
		evaluate(item, keys)

if __name__ == '__main__':
	main()