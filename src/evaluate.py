import argparse
import traceback
from helpers import check_connection, read_local_keys, read_instructions, check_user_blacklist, add_user_to_blacklist
from evaluator import evaluate_single_thread, evaluate_user
from scraper import scrape_threads, get_tweets_from_threads

def evaluate(item, keys, instructions, force_scrape=False, skip_scrape=False, skip_evaluation=False):
    result = {}
    print(f"Evaluating item: {item}")

    try:
        if item.startswith('https://'):
            url = item
            result = evaluate_single_thread(url, keys, instructions, skip_scrape, skip_evaluation)
            print(f"Result from evaluate_single_thread: {result}")
            if not result or 'error' in result:
                print(f"Evaluation error: {result.get('error', 'No result returned')}")
        else:
            user = item
            if check_user_blacklist(user):
                result = {"error": f'{user}: present in /local_data/blacklist_users.txt (due to previous search having no results)'}
                print(result)
            else:
                if not skip_scrape:
                    results, query_limit = scrape_threads(user, keys, force_scrape)
                    print(f"Scraping threads for user {user} completed. Results: {results}")

                    if results:
                        if get_tweets_from_threads(user, force_scrape):
                            if not skip_evaluation:
                                result = evaluate_user(user, keys, instructions)
                                print(f"Result from evaluate_user: {result}")
                                if not result or 'error' in result:
                                    print(f"Evaluation error: {result.get('error', 'No result returned')}")
                        else:
                            result = {"error": f'{user}: no tweets could be scraped for evaluation'}
                            print(result)
                    else:
                        if query_limit == False:
                            result = {"error": f'{user}: no threads have been found in search, add user to blacklist'}
                            add_user_to_blacklist(user)
                            print(result)
                else:
                    if not skip_evaluation:
                        result = evaluate_user(user, keys, instructions)
                        print(f"Result from evaluate_user: {result}")
                        if not result or 'error' in result:
                            print(f"Evaluation error: {result.get('error', 'No result returned')}")
    except Exception as e:
        print(f"Error during evaluation: {e}")
        print(traceback.format_exc())
        result = {"error": str(e)}

    if not result:
        result = {"error": "No evaluation result returned"}
    
    return result

def main():
    parser = argparse.ArgumentParser(prog='evaluate.py',
                                     description='Tool to evaluate threads of X/Twitter users based on custom instructions using GPT',
                                     epilog='Cees van Spaendonck - University of Amsterdam - 12425001 - New Media & Digital Culture MA Thesis - June 2024')
    parser.add_argument('input', type=str, help='help')
    parser.add_argument('--force_scrape', type=bool, default=False)
    parser.add_argument('--skip_scrape', type=bool, default=False)
    parser.add_argument('--skip_evaluation', type=bool, default=False)
    args = parser.parse_args()

    if check_connection() is False:
        print('No internet connection')
        exit()

    try:
        keys = read_local_keys()
        print("Keys successfully read.")
    except Exception as e:
        print(f"Error reading keys: {e}")
        exit()

    try:
        instructions = read_instructions()
        print("Instructions successfully read.")
    except Exception as e:
        print(f"Error reading instructions: {e}")
        exit()

    if ',' in args.input:
        for item in args.input.split(','):
            print(evaluate(item, keys, instructions, args.force_scrape,
                           args.skip_scrape,
                           args.skip_evaluation))
    else:
        print(evaluate(args.input, keys, instructions, args.force_scrape,
                       args.skip_scrape,
                       args.skip_evaluation))

if __name__ == '__main__':
    main()
