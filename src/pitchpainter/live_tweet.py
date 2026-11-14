"""Module to automatically tweet contents to Twitter (X)."""


import sys
import tweepy
from pitchpainter import cli, passwords
from pitchpainter.print_util import dprint

# Twitter bot developer credentials
TWITTER_API_KEY = passwords.TWITTER_API_KEY
TWITTER_API_SECRET = passwords.TWITTER_API_SECRET
TWITTER_BEARER_TOKEN = passwords.TWITTER_BEARER_TOKEN
TWITTER_CONSUMER_KEY = passwords.TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET = passwords.TWITTER_CONSUMER_SECRET
TWITTER_ACCESS_TOKEN = passwords.TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_SECRET = passwords.TWITTER_ACCESS_SECRET


def create_client():
    """Create the Twitter client using tweepy."""
    # v2 authentication
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN,
                           consumer_key=TWITTER_API_KEY,
                           consumer_secret=TWITTER_API_SECRET,
                           access_token=TWITTER_ACCESS_TOKEN,
                           access_token_secret=TWITTER_ACCESS_SECRET)
    return client


def send_tweet(client: tweepy.Client, text: str, is_tweeting=False):
    """Tweet text to configured account given correct developer credentials."""
    if not is_tweeting:
        return "We are not tweeting right now. -t or --tweet to tweet. -h or --help for other command line options"

    # tweet text
    response = client.create_tweet(text=text)

    # tweet png
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET
    )
    api = tweepy.API(auth)
    media = api.media_upload("pitch.png")
    response = client.create_tweet(media_ids=[media.media_id_string])

    return response


# TODO: Remove this?
def main():
    """Test only this file's contents."""
    cli.get_options(sys.argv[1:])

    # Post a tweet
    # client = create_client()
    # response = sendTweet(client, "This is a test automatic tweet using Python woot woot", cli.threading)
    # print(response)

    print("\n\n\n")
    og_text = ("+─────────────────────────+\n"
              "|DET 0         ◆     ▲    |\n"
              "|SD  3        ◆ ◆    9    |\n"
              "|            ● ● ○  3-2   |\n"
              "|─────────────────────────|\n"
              "|Robert Suarez      P:25  |\n"
              "+─────────────────────────+\n")
    test_text = ("|─────────────|\n"
                "| DET 0               ◆          ▲            |\n"
                "| SD   3            ◆   ◆       9            |\n"
                "|                        ● ● ○    3-2         |\n"
                "|─────────────|\n"
                "| Robert Suarez             P: 25     |\n"
                "|─────────────|\n")

    dprint(test_text)
    dprint(og_text)

    # tweet the result
    # response = send_tweet(client, testText, cli.threading)
    # print(response)


if __name__ == "__main__":
    main()
