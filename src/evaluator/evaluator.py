import logging
import traceback
import json
import os
import pandas as pd
from openai import OpenAI
from scraper import extract_tweets_from_url

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='evaluate.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def evaluate_user(user, keys, instructions):
    # Evaluate all threads in local data of specified user
    tweets_filename = f'./local_data/{user}/{user}_tweets.csv'
    tweets_df = None
    try:
        tweets_df = pd.read_csv(tweets_filename)
    except FileNotFoundError:
        logging.error(f'{user}: no file for tweets found at: {tweets_filename} - evaluation skipped')
        return {"error": f"No file for tweets found at: {tweets_filename}"}

    user_evaluations = []
    threads = tweets_df.groupby('thread_id')
    for thread_id, group in threads:
        thread_tweets = []
        for index, row in group.iterrows():
            tweet = {
                'body': row['body'],
                'tweet_urls': row['tweet_urls'],
                'tweet_images': row['tweet_images']
            }
            thread_tweets.append(tweet)

        usage, result = get_evaluation(thread_tweets, keys, instructions)
        if result is not None:
            try:
                result = json.loads(result)
                user_evaluations.append(result)
            except json.JSONDecodeError:
                logging.error(f'{user}: evaluation of {thread_id} is not saved as the response is not structured in JSON format. Please check /secrets/instructions.txt')
        else:
            logging.error(f'{user}: error encountered when evaluating thread {thread_id}')

    if user_evaluations:
        results_file = f'./local_data/{user}/{user}_evaluations.json'
        with open(results_file, 'w') as file:
            json.dump(user_evaluations, file, indent=4)
        logging.info(f'{user}: saved evaluations of {len(threads)} threads to {results_file}')
    else:
        logging.info(f'{user}: no evaluations saved')

def evaluate_single_thread(thread_url, keys, instructions, skip_scrape=False, skip_evaluation=False):
    thread_id = thread_url[thread_url.rindex('/') + 1:]
    if '.' in thread_id:
        thread_id = thread_id[:thread_id.rindex('.')]
    tweets_filename = f'./local_data/individual threads/{thread_id}_tweets.csv'

    if skip_scrape:
        try:
            tweets_df = pd.read_csv(tweets_filename)
        except FileNotFoundError:
            logging.error(f'{thread_id}: error reading tweets from {tweets_filename}')
            return {"error": f"Error reading tweets from {tweets_filename}"}
    else:
        tweets_df = pd.DataFrame(columns=['thread_id', 'id', 'url', 'author', 'body', 'tweet_urls', 'tweet_images'])
        tweets_df = extract_tweets_from_url(thread_url, tweets_df)

        if not os.path.isdir('./local_data/individual threads/'):
            os.makedirs('./local_data/individual threads/')

        tweets_df.to_csv(tweets_filename)
        logging.info(f'{thread_id}: saved {len(tweets_df)} tweets of thread to {tweets_filename}')

    if len(tweets_df) < 1:
        logging.error(f'{thread_url}: error in extracting tweets')
        return {"error": f"Error in extracting tweets from {thread_url}"}

    if not skip_evaluation:
        thread_tweets = []
        for index, row in tweets_df.iterrows():
            tweet = {
                'body': row['body'],
                'tweet_urls': row['tweet_urls'],
                'tweet_images': row['tweet_images']
            }
            thread_tweets.append(tweet)

        usage, result = get_evaluation(thread_tweets, keys, instructions)
        if result is not None:
            try:
                result = json.loads(result)
                results_filename = f'./local_data/individual threads/{thread_id}_evaluation.json'
                with open(results_filename, 'w') as file:
                    json.dump(result, file, indent=4)
                logging.info(f'{thread_id}: saved evaluation of thread to {results_filename}')
                return result
            except json.JSONDecodeError:
                logging.error(f'{thread_id}: evaluation is not saved as the response is not structured in JSON format. Please check /secrets/instructions.txt')
                return {"error": "Evaluation response is not structured in JSON format"}
        else:
            logging.error(f'{thread_id}: error encountered when evaluating thread')
            return {"error": f"Error encountered when evaluating thread {thread_id}"}
    else:
        return {"message": "Evaluation skipped"}

def get_evaluation(thread, keys, instructions):
    if 'open_ai_key' not in keys:
        logging.error('error: no open_ai_key present in keys.json')
        return (None, {"error": "No open_ai_key present in keys.json"})

    client = OpenAI(api_key=keys['open_ai_key'])
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            temperature=0.2,
            response_format={
                'type': 'json_object'
            },
            messages=[
                {
                    "role": "system",
                    "content": instructions
                },
                {
                    "role": "user",
                    "content": f"First, closely look at your custom instructions. Then, stick to them precisely to evaluate the following thread: {thread}"
                }
            ]
        )
        return (response.usage, response.choices[0].message.content)
    except Exception as e:
        logging.error(f'error: evaluation response from GPT: {e}')
        return (None, {"error": f"Evaluation response from GPT: {e}"})
