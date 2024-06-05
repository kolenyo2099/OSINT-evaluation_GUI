# local imports
import json
import os
import requests

# third party imports
from bs4 import BeautifulSoup
import pandas as pd

def get_tweets_from_threads(user):
	# extract tweets from threads of user

	# attempt to open .csv file of threads
	threads_filename = f'../local_data/{user}/{user}_threads.csv'
	threads_df = None
	try:
		threads_df = pd.read_csv(threads_filename)
	except:
		print(f'no file for threads found at: {threads_filename}')
		exit()

	# attempt to extract urls from threads_df
	thread_urls = list()
	if len(threads_df) > 0:
		for index, row in threads_df.iterrows():
			url = row['url']
			thread_urls.append(url)
	else:
		print(f'no threads found in {threads_filename}')
		exit()

	# initiate tweets_df
	tweets_df = pd.DataFrame(columns = ['thread_id', 'id', 'url', 'author', 'body', 'tweet_urls', 'tweet_images'])
	for thread_url in thread_urls:
		tweets_df = extract_tweets_from_url(thread_url, tweets_df)

	if len(tweets_df) > 0:
		tweets_filename = f'../local_data/{user}/{user}_tweets.csv'
		print(f'saving {len(tweets_df)} tweets from {len(thread_urls)} threads to {tweets_filename}')
		tweets_df.to_csv(tweets_filename)
	else:
		print('no tweets could be scraped')

def scrape_threads(user, keys):
	# scrape thread urls based on user as search query

	# create folder for results if not present
	if not os.path.isdir('../local_data/'):
		os.makedirs('../local_data/')
	if not os.path.isdir(f'../local_data/{user}/'):
		os.makedirs(f'../local_data/{user}')

	# add to existing .csv file or create new .csv file
	filename = f'../local_data/{user}/{user}_threads.csv'
	try:
		df = pd.read_csv(filename)
	except:
		df = pd.DataFrame(columns = ['title', 'url'])
		df.to_csv(filename)

	# iterate over search results
	index = 0
	max_results = 150
	while index < max_results:
		df, results = get_threads_by_search(keys, user, index, df, filename)
		if results:
			index += 10
		else:
			break

	if len(df) > 0:
		print(f'saving {len(df)} threads to {filename}')
		df.to_csv(filename)
	else:
		print('no threads found')

def get_threads_by_search(keys, query, index, df, filename):
	# save results of query search for threads per index

	# check neccesary keys
	if 'google_api_key' not in keys:
		print('error: no google_api_key found in keys.json')
		exit()

	if 'google_cx' not in keys:
		print('error: no google_cx key found in keys.json')
		exit()

	url = f'https://www.googleapis.com/customsearch/v1'
	params = {
		'key': keys['google_api_key'],
		'cx': keys['google_cx'],
		'q': f'thread by {query}',
		'start': index
	}

	# ensure response
	response = requests.get(url, params=params)
	if response.status_code != 200:
		if response.status_code == 429:
			print('error: daily request limit hit')
			return df, False
		elif response.status_code == 400: # no more results found
			return df, False
		else:
			print(f'error from results {start}-{start + 10}: {response.status_code}')
	# response ok
	else:
		data = json.loads(response.text)
		if 'items' not in data: # no more results found
			return df, False
		else:
			# save results if author matches query and if not present yet
			for item in data['items']:
				title = item['title']
				if title.lower().startswith(f'thread by @{query}'):
					url = item['link']
					if url.endswith('.html') is False:
						url += '.html'
					if 'scrolly' in url:
						url = url.replace('scrolly', 'thread')
					scraped_urls = set(df['url'])
					if url not in scraped_urls:
						df = df._append({'title': title, 'url': url}, ignore_index = True)
	return df, True

