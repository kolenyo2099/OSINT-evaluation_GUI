# local imports
import argparse
from helpers import check_connection, read_local_keys
from scraper import extract_tweets_from_url

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

	# refuse invalid input
	if ':' in args.user:
		print('invalid twitter username')
		exit()

	keys = read_local_keys('keys.json')

	# scrape list of users
	if ',' in args.user:
		users = args.user.split(',')
		for user in users:
			scrape_threads(user, keys)
			get_tweets_from_threads(user)
	
	# scrape single user
	else:
		scrape_threads(args.user, keys)
		get_tweets_from_threads(args.user)

if __name__ == '__main__':
	main()