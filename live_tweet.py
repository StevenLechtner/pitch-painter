import cli
import json
import pitchbypitch
import sys
import tweepy
from print_util import dprint, vprint

# Twitter bot developer credentials
api_key = "1zgs4BdzcdQ4GdASh1MN1YLrX"
api_secret = "WDrigEIEedvKmY56YVRRI5lwRQ8fgdE8xbaCyQHrlq6vTYGCyV"
bearer_token="AAAAAAAAAAAAAAAAAAAAAHxr4QEAAAAAa3f4Poyxl6tiAahYfczWUvIb2BM%3D1qjsfcexjueJJECUyoiM0caE5MoIpewkWqbeRKMagIV9AxELM0"
consumer_key="NzdCRG44ZTlOTHNlNU55MVpzRW46MTpjaQ"
consumer_secret="jpNYdzcIvpkjGQo2wz20ujesGPIgrnFtPbNEON3Ji_q1xnYNsa"
access_token = "1970860626563239936-oee1HdnDKx45FVPT9pDfbuRaGsLSA8"
access_secret = "aTre5O09neKGGQuhdXt1PKnf6JsRwULS0dmzpJfSjNmNM"

def createClient():
    # v2 authentication
    client = tweepy.Client(bearer_token=bearer_token,
                           consumer_key=api_key,
                           consumer_secret=api_secret,
                           access_token=access_token,
                           access_token_secret=access_secret)
    return client

def sendTweet(client: tweepy.Client, text: str, isTweeting=False):
    if not isTweeting:
        return "We are not tweeting right now. -t or --tweet to tweet. -h or --help for other command line options"

    # tweet text
    response = client.create_tweet(text=text)

    # tweet png
    auth = tweepy.OAuth1UserHandler(
        api_key,
        api_secret,
        access_token,
        access_secret
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
