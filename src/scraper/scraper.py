# local imports
import json
import os
import requests

# third party imports
from bs4 import BeautifulSoup
import pandas as pd

def extract_tweets_from_url(thread_url, df):
	# extract tweets from thread url to tweets df

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
		# (older thread do not neccesary have metadata saved)
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
			# continue (and discard current thread) if any elemant cannot be extracted
			...
	return df

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

