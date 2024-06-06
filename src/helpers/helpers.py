# local imports
import json
import socket

def read_local_keys():
	# read keys from local file
	keys_file = '../secrets/keys.json'
	keys = dict()
	with open(keys_file) as f:
		keys = json.loads(f.read())
	return keys

def read_instructions():
	# read instructions to send to GPT
	instructions_file = '../secrets/instructions.txt'
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

def evaluate_user(user, keys):
	# evaluate all threads of specified user

	# open .csv file of tweets by user
	tweets_filename = f'./data/{user}/{user}_tweets.csv'
	tweets_df = None
	try:
		tweets_df = pd.read_csv(tweets_filename)
	except:
		print(f'no file for tweets found at: {tweets_filename}')
		print(f'(first run scrape_user_threads [user] to scrape tweets)')
		exit()

	# extract all tweets, grouped per thread
	evaluations = list()
	threads = tweets_df.groupby('thread_id')
	for thread_id, group in threads:
		thread_tweets = []
		for index, row in group.iterrows():
			tweet = {
			'body': row['body'],
			'tweet_urls': row['tweet_urls'],
			'tweet_images': row['tweet_images']}
			thread_tweets.append(tweet)

		# post for evaluation, add results to evaluations
		usage, result = get_evaluation(thread_tweets, keys)
		if result is not None:
			result = json.loads(result)
			result['thread_id'] = thread_id
			evaluations.append(result)
		else:
			print(f'error encountered when evaluting, excluding thread {thread_id}')

	# export evaluations to json file
	results_file = f'./data/{user}/{user}_evaluations.json'
	with open(results_file, 'w') as file:
		json.dump(evaluations, file, indent = 4)
	print(f'saved evaluations of {len(threads)} threads to to {results_file}')  

def evaluate_single_thread(thread_url, keys):
	# extract tweets, thread_id from thread url
	tweets_df = pd.DataFrame(columns = ['thread_id', 'id', 'url', 'author', 'body', 'tweet_urls', 'tweet_images'])
	tweets_df = extract_tweets_from_url(thread_url, tweets_df)
	thread_id = thread_url[thread_url.rindex('/') + 1:]
	if '.' in thread_id:
		thread_id = thread_id[:thread_id.rindex('.')]

	# create folder for individual results of not present
	if not os.path.isdir('./data/individual threads/'):
		os.makedirs('./data/individual threads/')

	# save tweets of individual thread
	tweets_filename = f'./data/individual threads/{thread_id}_tweets.csv'
	tweets_df.to_csv(tweets_filename)
	print(f'saved {len(tweets_df)} tweets of thread to {tweets_filename}')

	# extract content of tweets
	thread_tweets = list()
	for index, row in tweets_df.iterrows():
		tweet = {
		'body': row['body'],
		'tweet_urls': row['tweet_urls'],
		'tweet_images': row['tweet_images']}
		thread_tweets.append(tweet)

	# post for evaluation
	usage, result = get_evaluation(thread_tweets, keys)
	if result is not None:
		result = json.loads(result)
		result['thread_id'] = thread_id

		# export evaluation to json file
		results_filename = f'./data/individual threads/{thread_id}_evaluation.json'
		with open(results_filename, 'w') as file:
			json.dump(result, file, indent = 4)
		print(f'saved evaluation of thread to {results_filename}')
	else:
		print(f'error encountered when evaulting thread {thread_id}')

