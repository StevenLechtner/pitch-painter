import cli
import json
import passwords
import pitchbypitch
import sys
import tweepy
from print_util import dprint, vprint

# Twitter bot developer credentials
TWITTER_API_KEY = passwords.TWITTER_API_KEY
TWITTER_API_SECRET = passwords.TWITTER_API_SECRET
TWITTER_BEARER_TOKEN= passwords.TWITTER_BEARER_TOKEN
TWITTER_CONSUMER_KEY= passwords.TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET= passwords.TWITTER_CONSUMER_SECRET
TWITTER_ACCESS_TOKEN = passwords.TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_SECRET = passwords.TWITTER_ACCESS_SECRET

def createClient():
    # v2 authentication
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN,
                           consumer_key=TWITTER_API_KEY,
                           consumer_secret=TWITTER_API_SECRET,
                           access_token=TWITTER_ACCESS_TOKEN,
                           access_token_secret=TWITTER_ACCESS_SECRET)
    return client

def sendTweet(client: tweepy.Client, text: str, isTweeting=False):
    if not isTweeting:
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

def main(args):
    cli.getOptions(args)
    client = createClient()

    # Post a tweet
    # response = sendTweet(client, "This is a test automatic tweet using Python woot woot", cli.threading)
    # print(response)

    with open("tests/meadows.json", "r") as f:
        game = json.load(f)
    text = pitchbypitch.printAllPitchesFromGame(game)
    print("\n\n\n")
    ogText = ("+─────────────────────────+\n"
              "|DET 0         ◆     ▲    |\n"
              "|SD  3        ◆ ◆    9    |\n"
              "|            ● ● ○  3-2   |\n"
              "|─────────────────────────|\n"
              "|Robert Suarez      P:25  |\n"
              "+─────────────────────────+\n")
    testText =  ("|─────────────|\n"
                "| DET 0               ◆          ▲            |\n"
                "| SD   3            ◆   ◆       9            |\n"
                "|                        ● ● ○    3-2         |\n"
                "|─────────────|\n"
                "| Robert Suarez             P: 25     |\n"
                "|─────────────|\n")

    dprint(testText)
    dprint(ogText)

    # tweet the result
    # response = sendTweet(client, testText, cli.threading)
    # print(response)

if __name__ == "__main__":
    main(sys.argv[1:])
