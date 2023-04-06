import pandas as pd
import requests
import os


def get_tweets(usernames: str, start: str, end: str = None, token: str = None) -> pd.DataFrame:
    """
    The twitter function makes a GET request to the Twitter API for the tweets endpoint to get the public metrics.

    SAMPLE CODE

    google_tweets = get_tweets(usernames='google', start='2023-01-01')
    # or you can pass multiple usernames
    google_amazon_tweets = get_tweets(usernames='google,amazon', start='2023-01-01')

    :param usernames: str Twitter usernames separated by a comma with not space: 'name1,name2,name3'
    :param start: str a date string that indicates the start date for posts
    :param end: str default value is None but you can enter an end date if you want
    :param token: str Twitter API bearer token if None look for the environment variable TWITTERTOKEN
    :return: Tuple[Any, List[pd.DataFrame]] Will return two frames - the first is the followers frame and the
             second is the media frame
    """

    start = start + 'T00:00:00.000Z'

    if not token:
        token = os.environ.get('TWITTERTOKEN')

    # set the Authorization header for authentication
    headers = {"Authorization": f"Bearer {token}"}
    # We some user data because we need the account id
    user_info_url = (f"https://api.twitter.com/2/users/by?"
                     f"usernames={usernames}"
                     f"&user.fields=created_at,name,public_metrics")
    # make the GET request
    data = requests.get(user_info_url, headers=headers).json()['data']
    # dict comprehension in case there are multiple usernames provided
    account_data = {d['username']: {'id': d['id'],
                                    'followers_count': d['public_metrics']['followers_count'],
                                    'tweet_count': d['public_metrics']['tweet_count']}
                    for d in data}

    # create an empty list to append DataFrames durning iteration
    all_tweets = []
    for username, val in account_data.items():
        if not end:  # URL if no end date supplied
            posts_url = (f"https://api.twitter.com/2/users/{val['id']}/tweets?"
                         "max_results=100"
                         f"&start_time={start}"
                         "&tweet.fields=created_at,public_metrics")
        else:  # URL if end date supplied
            end = end + 'T00:00:00.000Z'
            posts_url = (f"https://api.twitter.com/2/users/{val['id']}/tweets?"
                         "max_results=100"
                         f"&start_time={start}"
                         f"&end_time={end}"
                         "&tweet.fields=created_at,public_metrics")

        try:
            posts = requests.get(posts_url, headers=headers).json()
            post_data = pd.json_normalize(posts['data'])
            post_data['account'] = username
            all_tweets.append(post_data)
            # this while loop handles the pagination as the Twitter API will return a max of 100 results
            while True:
                try:
                    posts = requests.get(posts_url + f"&pagination_token={posts['meta']['next_token']}",
                                         headers=headers).json()['data']
                    next_df = pd.json_normalize(posts)
                    next_df['account'] = username
                    all_tweets.append(next_df)
                except TypeError:  # if no next_token is found break
                    break
        # if there are no twitter posts `posts['data']` it will raise a KeyError
        except KeyError:
            pass
    # concat all the frames together
    tweets_df = pd.concat(all_tweets)
    tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at']).dt.date
    tweets_df = tweets_df.sort_values('created_at')

    return tweets_df

