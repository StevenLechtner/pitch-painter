import cli
import requests
import statsapi
import tweepy

import json
import pitchbypitch
import sys
import time

from situation import Situation
from PIL import Image, ImageDraw, ImageFont
from print_util import dprint, vprint
import textwrap

# Twitter bot developer credentials
api_key = "1zgs4BdzcdQ4GdASh1MN1YLrX"
api_secret = "WDrigEIEedvKmY56YVRRI5lwRQ8fgdE8xbaCyQHrlq6vTYGCyV"
bearer_token="AAAAAAAAAAAAAAAAAAAAAHxr4QEAAAAAa3f4Poyxl6tiAahYfczWUvIb2BM%3D1qjsfcexjueJJECUyoiM0caE5MoIpewkWqbeRKMagIV9AxELM0"
consumer_key="NzdCRG44ZTlOTHNlNU55MVpzRW46MTpjaQ"
consumer_secret="jpNYdzcIvpkjGQo2wz20ujesGPIgrnFtPbNEON3Ji_q1xnYNsa"
access_token = "1970860626563239936-oee1HdnDKx45FVPT9pDfbuRaGsLSA8"
access_secret = "aTre5O09neKGGQuhdXt1PKnf6JsRwULS0dmzpJfSjNmNM"

# Threads bot developer credentials
THREADS_APP_ID = "939353101979475"
THREADS_APP_SECRET = "685c1596e92d7783929587707bb6ab6e"
THREADS_ACCESS_TOKEN = "THAANWViZC2T1NBYmJwQi1pTEg5NXE3ZA3ZAHOFhNMm5oekNONTRZAVm9OVEJoSlhDcjN5MmN5b2NodXRsdndCU25GNjBpZADFlLWQ4UC1rTk01ZAlFaQ1JhS2NkaWRNNUVTcmxYbWJuZAkRjY0Q2a3hPWEFzT0tZAMTZAWZA2JybEFSZAUVmSkdRUQZDZD"
THREADS_USER_ID = "28665889336435626"

# Image hosting credentials (imgbb)
IMGBB_API_KEY = "fbcfda7ed153930d976540d21230a2de"

# # Determines if tweet gets sent out or not
# isTweeting = False

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
    # response = client.create_tweet(text=text)

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

def formatScoreboard():
    return "yah"

def textToPNG(text, filename="pitch.png"):
    font = ImageFont.truetype(
        "/System/Library/Fonts/Menlo.ttc",
        24
    )

    lines = text.split("\n")

    # Determine dimensions
    bbox = font.getbbox("M")
    char_width = bbox[2] - bbox[0]
    line_height = 30

    width = max(
        font.getlength(line)
        for line in lines
    ) + 40

    height = line_height * len(lines) + 40

    image = Image.new("RGB", (int(width), height), "white")
    draw = ImageDraw.Draw(image)

    y = 20

    for line in lines:
        draw.text(
            (20, y),
            line,
            font=font,
            fill="black"
        )
        y += line_height

    image.save(filename)

    return filename

def sendThread(contents):
    baseUrl = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}"

    # create the thread to post
    thread = requests.post(f"{baseUrl}/threads", json=contents)
    creationId = thread.json().get("id", -1)
    vprint(f"Thread creation: {thread.json()}")
    dprint(creationId)

    # post the thread to threads
    publish = {"creation_id": creationId, "access_token": THREADS_ACCESS_TOKEN}
    threadPublish = requests.post(f"{baseUrl}/threads_publish", json=publish)
    vprint(f"Thread publish: {threadPublish.json()}")

def uploadImageToImgbb(filepath):
    with open(filepath, "rb") as image:
        imageResp = requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}", files={"image": image})
    vprint(f"Image upload: {imageResp.json()}")
    return imageResp.json().get("data", {}).get("url", None)

def deleteImageFromImgbb(imageUrl):
    imageResp = requests.post(imageUrl)
    vprint(f"Delete image: {imageResp.status_code}")

def main(args):
    cli.getOptions(args)
    client = createClient()

    # Post a tweet
    # response = sendTweet(client, "This is a test automatic tweet using Python woot woot")
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
    dprint(formatScoreboard())
    
    # response = sendTweet(client, testText, cli.tweet)
    # print(response)

    filepath = textToPNG(ogText)
    imageUrl = uploadImageToImgbb(filepath)
    print(f"Image URL: {imageUrl}")
    # contents = {"media_type": "TEXT", "text": "Hello, World!", "access_token": THREADS_ACCESS_TOKEN} # thread a text box
    contents = {"media_type": "IMAGE", "image_url": imageUrl, "access_token": THREADS_ACCESS_TOKEN} # thread an image
    # contents = {"media_type": "TEXT", "text": testText, "access_token": THREADS_ACCESS_TOKEN}
    # deleteImageFromImgbb("https://ibb.co/LDnVKRJB/0e1797976c3c19c9c509aa712854d7f3")
    sendThread(contents)

    awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
    homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
    currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
    situation = Situation()
    situation.startNewGame(homeAbbr, awayAbbr, currentPitcher)
    dprint(pitchbypitch.drawPitchForTweeting(situation))
    dprint(textToPNG(pitchbypitch.drawPitch(situation)))

if __name__ == "__main__":
    main(sys.argv[1:])
