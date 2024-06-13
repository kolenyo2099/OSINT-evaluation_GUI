# local imports
import argparse
from helpers import check_connection, read_local_keys, read_instructions
from evaluator import evaluate_single_thread, evaluate_user
from scraper import scrape_threads, get_threads_by_search, get_tweets_from_threads

# third pary imports
import pandas as pd

def evaluate(item, keys, instructions, force_scrape):
	if item.startswith('https://'):
		url = item
		evaluate_single_thread(url, keys, instructions)
	else:
		user = item
		scrape_threads(user, keys, force_scrape)
		if get_tweets_from_threads(user, force_scrape):
			evaluate_user(user, keys, instructions)

def main():
	parser = argparse.ArgumentParser(prog = 'evaluate.py',
									 description =  '',
									 epilog = '')
	parser.add_argument('input', type = str,
						help = 'help')
	parser.add_argument('--force_scrape', type = bool, default = False)
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
			evaluate(item, keys, instructions, args.force_scrape)
	else:
		evaluate(args.input, keys, instructions, args.force_scrape)

if __name__ == '__main__':
	main()