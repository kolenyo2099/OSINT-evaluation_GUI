# local imports
import json
import os
import requests
import shutil

# third party imports
from bs4 import BeautifulSoup
import pandas as pd

def extract_tweets_from_url(thread_url, df):
	# extract tweets from thread url to tweets df using bs4

	# attempt to retreive metadata of thread
	access_metadata = False
	try:
		url_response = requests.get(thread_url)
		html = url_response.text

		soup = BeautifulSoup(html, 'html.parser')
		thread_info = str(soup.find('div', {'class': 'thread-info'})).split('\n')
		thread_length = [element for element in thread_info if 'tweets' in element]
		
		# in some threads, thread info is not in div element but in span element
		if not thread_length:
			thread_length = str(soup.find('span', {'class': 'thread-info'})).split('\n')
			thread_length = [element for element in thread_length if 'tweets' in element]

		thread_length = int(thread_length[0].split(' ')[0].strip())
		thread_id = thread_url[thread_url.rindex('/') + 1:thread_url.rindex('.')]
		access_metadata = True
	except:
		# error when extracting metadata
		# (in older threads, necessary metadata is inaccessible)
		access_metadata = False

	if access_metadata:
		# attempt to extract relevant elements of all tweets in thread
		try:
			for tweet_index in range(1, thread_length + 1):
				tweet_tag = soup.find('div', {'id': ('tweet_' + str(tweet_index))})
				if tweet_tag.has_attr('data-tweet'): # not present in some threads
					tweet_id = tweet_tag['data-tweet']
					tweet_author = tweet_tag['data-screenname']
					tweet_url = f'https://twitter.com/{tweet_author}/status/{tweet_id}'
					tweet_body = tweet_tag.text.strip()
					tweet_urls = list()
					tweet_images = list()

					embedded_urls = tweet_tag.find_all('a', {'class': 'entity-url'})
					for embedded_url in embedded_urls:
						tweet_urls.append(embedded_url['href'])

					embedded_images = tweet_tag.find_all('span', {'class': 'entity-image'})
					for embedded_image in embedded_images:
						url = embedded_image.find('a')
						tweet_images.append(url['href'])

					# add to df
					df = df._append({'thread_id': thread_id,
									 'id': tweet_id,
				 	 				 'url': tweet_url,
				 	 				 'author': tweet_author,
				 					 'body': tweet_body,
				 					 'tweet_urls': tweet_urls,
				 					 'tweet_images': tweet_images},
				 	 				 ignore_index = True)
		except:
			# continue (and do not add any tweets to df) if any elemant cannot be extracted
			...
	return df

def get_tweets_from_threads(user, force_scrape):
	# extract tweets from threads of user

	# if scraping is not forced and tweets of user exist in /local_data/,
	# read tweets from this file
	tweets_filename = f'./local_data/{user}/{user}_tweets.csv'
	if not force_scrape and os.path.isfile(tweets_filename):
		print(f'{user}: reading tweets from existing file {tweets_filename}')
		return True

	# open .csv file of threads
	threads_filename = f'./local_data/{user}/{user}_threads.csv'
	threads_df = pd.read_csv(threads_filename)

	# attempt to extract urls from threads_df
	thread_urls = list()
	if len(threads_df) > 0:
		for index, row in threads_df.iterrows():
			url = row['url']
			thread_urls.append(url)
	else:
		print(f'{user}: no threads found in {threads_filename}')
		return False

	# initiate tweets_df, extract tweets of each url and add to df
	tweets_df = pd.DataFrame(columns = ['thread_id', 'id', 'url', 'author', 'body', 'tweet_urls', 'tweet_images'])
	for thread_url in thread_urls:
		tweets_df = extract_tweets_from_url(thread_url, tweets_df)

	# if any tweets have been found, save to user tweets in /local_data/
	if len(tweets_df) > 0:
		print(f'{user}: saving {len(tweets_df)} tweets from {len(thread_urls)} threads to {tweets_filename}')
		tweets_df.to_csv(tweets_filename)
		return True
	else:
		return False

def scrape_threads(user, keys, force_scrape):
	# scrape thread urls based on user as search query

	query_limit = None
	threads_filename = f'./local_data/{user}/{user}_threads.csv'

	# if scraping is not forced and threads by user exist in /local_data/
	# read threads from this file
	if not force_scrape and os.path.isfile(threads_filename):
		print(f'{user}: reading threads from existing file {threads_filename}')
		query_limit = False
		return True, query_limit

	# create folder for results if not present
	if not os.path.isdir('./local_data/'):
		os.makedirs('./local_data/')
	if not os.path.isdir(f'./local_data/{user}/'):
		os.makedirs(f'./local_data/{user}')

	# add to existing .csv file of threads or create new .csv file
	try:
		df = pd.read_csv(threads_filename)
	except:
		df = pd.DataFrame(columns = ['title', 'url'])
		df.to_csv(threads_filename)

	# iterate over search results and retreive results
	index = 0
	max_results = 150
	while index < max_results:
		df, results = get_threads_by_search(keys, user, index, df, threads_filename)
		if results:
			index += 10
		else:
			if results is None:
				query_limit = True
			else:
				query_limit = False
			break

	# if any threads have been found, save to user thread files
	if len(df) > 0:
		print(f'{user}: saving {len(df)} threads to {threads_filename}')
		df.to_csv(threads_filename)
		return True, query_limit
	# delete user folder in local_data if no threads have been found
	# (to avoid empty folders and datasets)
	else:
		shutil.rmtree(f'./local_data/{user}')
		return False, query_limit

def get_threads_by_search(keys, query, index, df, filename):
	# save results of query search for threads per index

	# check neccesary keys
	if 'google_api_key' not in keys:
		print('error: no google_api_key found in keys.json')
		exit()

	if 'google_cx' not in keys:
		print('error: no google_cx key found in keys.json')
		exit()

	url = 'https://www.googleapis.com/customsearch/v1'
	params = {
		'key': keys['google_api_key'],
		'cx': keys['google_cx'],
		'q': f'thread by {query}',
		'start': index
	}

	# ensure correct response
	response = requests.get(url, params = params)
	if response.status_code != 200:
		if response.status_code == 429:
			# daily google search engine request limit hit
			print('error: daily request limit of google search engine hit')
			return df, None
		elif response.status_code == 400:
			# no more results found
			return df, False
		else:
			# other unexpected error
			print(f'error: unexpected status code in search from results: {response.status_code}')
	else:
		# read results
		data = json.loads(response.text)
		if 'items' not in data:
			# no more results found
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