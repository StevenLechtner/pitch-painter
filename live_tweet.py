import cli
import requests
import statsapi
import tweepy
import os

import json
import pitchbypitch
import sys
import time

from situation import Situation
from PIL import Image, ImageDraw, ImageFont
from print_util import dprint, vprint
import textwrap

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

import dropbox

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
BASE_URL = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}"

# Image hosting credentials
# imgbb
IMGBB_API_KEY = "fbcfda7ed153930d976540d21230a2de"
# cloudinary
cloudinary.config( 
    cloud_name = "ww7oqsam", 
    api_key = "766733828814763", 
    api_secret = "JlGsY0SDOltGbcVuyQJLryo0OuQ",
    secure=True
)
# dropbox
DROPBOX_ACCESS_TOKEN = "sl.u.AGsJvt7zMb9K_jQrgg-MoVNRCmUpor6u8CIEfLU2gbFMz0PM04PIUULJKmlFGJGn6zHbS8oLxR9j_mHusQOc7qhalIhfjdtBdZmCCNYT2OXfMIm7EYxXrj2XS4jZXUXPmfgJyTOa_D3fvd3wvukUseZNYwo8-CuBC-tgqh-OM22eeB5-T4QhHFXmzcl5vOsncK0miR8sCSWeQ_AXvIwEwl2KwsBZ_AhcBnASkfml2mTGAchxAScfJjueMVJUdLuXl-kZPJUOUtk9ZK8DTg3HSMJ0wcfH1X4KWwjj9GJRAqdj8Sxgp6ksAe55wk1lj9kyKYY88XP-svDS3UooOeF5VWBZawQj3MRgULu3-95Z7m18We6R-MEH39QCdhwf8_-KpNfa8WW0xvyyV1p7tuI4XJNbqpk5aGTUJh4bbP4e11TaG8wSYEfIDzZkliKwtrHioM2CsHE052BFi2XnnfFO2OGVkXakJp7Bk3MY8mdkKe3gct8Dk5jwR1upuZGYZ9EvKj6QrBewR7wRt-ZHXv4clxleptN7EOrY38-Vwl-JjWVjlMQU3fwYo_UxacXLooh_MT97d2rRmmRZNIYwyQM5jMmh52NSNLVtRCfDVdHVwCHvLex6q0MZcIQnCOjaFqW6n-2GhL9H8z75m29ljE7O7sEF1TeYuRSzpkofFB7jeHDcdv1qV-Knp24kj1eDnsXcgnEDqgwpAcqGuBRm6hYkVNe0TLcmmcQtbs5CbSmZ8IAJopNZ0vv2982gfdJWtquBcYLKiqVA4nnK1IZeJV_WzxSmSwAzoZuXdEVFyuTdl9zcAKYM37Iqc6FeuzRjDt4SSGFPIK6vwEnxpFsFHnBGvpPblbCtF8CrE--2Ls-XvyIalqdk8Qusf8H3al8E7qp-UUHaOBuCPtZs6psP3oYr7cB1CrN_xUdmMZjYHtbMnzPkMlFOj8mVIrAbcT-vGxXNOM_K7ubgCB3B8JwHirkuhevilpGdVHRiVvhvVfAvdtUQ1XxeYg_8jchk8VNKokEIANuuoeIx-waBF4NFMjLuanb_jVXqp6fMTxwmTD9pJM6BaWwnoiR1FoTLQ6zEnC6aC6PqIdYo68JO22q6kP3RKxCfrBHyZFeIiO1NJdlJQrQ6nFBmhIt1XUVO7QBLvPAeHyCk-Ve5zrvzXoqmWKOgKE5IktKbnx12YbzYmIFBtcM1WGjx9EJfr2xbYvZQbEQxAQWCJUKPM4S7dcAZjQ83MF2s5heDWxQOGNWqh_L9ZeExT-Q1RvZTPz10lsWKw2ffwFTZldSAAJ0sOoDowwiHTQL2L9NV1Oi2WMqPZGLhLHKCcw"
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

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

def textToPNG(text, filepath="pitch.png"):
    lines = text.split("\n")
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 24)

    # Determine dimensions
    border = 40
    width = max(font.getlength(line) for line in lines) + border # width of longest line + border
    line_height = 30
    height = line_height * len(lines) + border # line height * lines + border

    image = Image.new("RGB", (int(width), height), "white")
    draw = ImageDraw.Draw(image)

    y = border / 2
    for line in lines:
        draw.text((border / 2, y), line, font=font, fill="black") # xy, text, text font, text color
        y += line_height

    dir_name = os.path.dirname(filepath)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    image.save(filepath)
    return filepath

# def textToPNG(text, filepath="pitch.png"):
#   lines = text.split("\n")
#   try:
#     font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 32)
#   except IOError:
#     font = ImageFont.load_default()

#   # Force a fixed, standard canvas size (Square 1080x1080)
#   # This guarantees it matches Meta's aspect ratio and minimum size requirements.
#   canvas_width = 1080
#   canvas_height = 1080

#   image = Image.new("RGB", (canvas_width, canvas_height), "white")
#   draw = ImageDraw.Draw(image)

#   # Starting coordinates with generous padding
#   x = 80
#   y = 80
#   line_height = 45

#   for line in lines:
#     draw.text((x, y), line, font=font, fill="black")
#     y += line_height

#   # Ensure directory exists and save
#   dir_name = os.path.dirname(filepath)
#   if dir_name and not os.path.exists(dir_name):
#     os.makedirs(dir_name)

#   image.save(filepath, "PNG")
#   return filepath

def createThreadToPost(contents):
    # Try to create thread to post up to three times before failing
    for attempt in range(3):
        response = requests.get(contents.get("image_url", None))
        print(response.status_code)
        print(response.headers.get("Content-Type"))
        print(response.url)
        print(len(response.content))
        print(contents.get("image_url"))
        thread = requests.post(f"{BASE_URL}/threads", json=contents)
        creationId = thread.json().get("id", -1)
        vprint(f"Thread creation: {thread.json()}")
        vprint(f"Thread raw: {thread}")
        vprint(f"Thread status code: {thread.status_code}")
        dprint(creationId)
        if (thread.json().get("id", -1) != -1):
            return creationId
        else:
            vprint(f"{BASE_URL}/threads attempt failed (attempt {attempt + 1}/3): {thread.json()}")
            if attempt < 2:
                time.sleep(30)
            else:
                vprint(f"Failed to create thread to post after 3 attempts.")
    return -1

# def createThreadToPost(contents):
#   # Try to create thread up to three times before failing
#   for attempt in range(3):

#     # # 1. CRITICAL: Give Cloudinary a moment to globally replicate the asset
#     # if attempt == 0:
#     #   time.sleep(
#     #       4
#     #   )  # Wait 4 seconds on the first try to let global CDN nodes sync
#     # else:
#     #   time.sleep(15)  # Wait longer on subsequent retries

#     image_url = contents.get("image_url")

#     # Optional: verify from your end
#     try:
#       response = requests.get(image_url, timeout=5)
#       print(f"URL Check Status: {response.status_code}")
#     except Exception as e:
#       print(f"URL check exception: {e}")

#     #time.sleep(5)

#     # 2. Use 'data=' instead of 'json=' for Meta Graph API compatibility
#     thread = requests.post(
#         f"{BASE_URL}/threads", data=contents
#     )  # Ensure USER_ID is included

#     creationId = thread.json().get("id", -1)

#     if creationId != -1:
#       print(f"Success! Post created: {creationId}")
#       return creationId
#     else:
#       print(
#           f"Attempt {attempt + 1}/3 failed. Meta Response:"
#           f" {thread.json()}"
#       )

#   print("Failed to create thread to post after 3 attempts.")
#   return -1

def sendThread(contents):
    if not cli.threading:
        vprint("We are not posting a thread right now. -t or --thread to tweet. -h or --help for other command line options")
        return

    # create the thread to post
    # thread = requests.post(f"{baseUrl}/threads", json=contents)
    # creationId = thread.json().get("id", -1)
    # vprint(f"Thread creation: {thread.json()}")
    # vprint(f"Thread raw: {thread}")
    # vprint(f"Thread status code: {thread.status_code}")
    # dprint(creationId)

    # Try to create thread to post up to three times before failing
    creationId = createThreadToPost(contents)

    # post the thread to threads
    for attempt in range(3):
        publish = {"creation_id": creationId, "access_token": THREADS_ACCESS_TOKEN}
        threadPublish = requests.post(f"{BASE_URL}/threads_publish", json=publish)
        vprint(f"Thread publish: {threadPublish.json()}")
        dprint(f"Thread publish raw: {threadPublish}")
        dprint(f"Thread publish raw status code: {threadPublish.status_code}")

        if (threadPublish.json().get("id", -1) != -1):
            break
        else:
            vprint(f"{BASE_URL}/threads_publish attempt failed (attempt {attempt + 1}/3): {threadPublish.json()}")
            if attempt < 2:
                time.sleep(5)
                creationId = createThreadToPost(contents)
            else:
                vprint(f"Failed to create thread to post after 3 attempts.")

def sendThreadImageFromText(text, filepath="images/miscPk/temp.jpg"):
    if not cli.threading:
        vprint("We are not posting a thread right now. -t or --thread to tweet. -h or --help for other command line options")
        return

    filepath = textToPNG(text, filepath)
    # imageUrl = uploadImageToImgbb(filepath)
    #imageUrl = uploadImageToCloudinary(filepath)
    imageUrl = uploadImageToDropbox(filepath)
    print(imageUrl)
    contents = {"media_type": "IMAGE", "image_url": imageUrl, "access_token": THREADS_ACCESS_TOKEN} # thread an image
    sendThread(contents)
    os.remove(filepath)
    dbx.files_delete_v2(f"/{filepath}")

def uploadImageToDropbox(filepath):
    with open(filepath, "rb") as fp:
        contents = fp.read()

    dbx.files_upload(contents, f"/{filepath}", dropbox.files.WriteMode.add, mute=True)
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(f"/{filepath}")
    preview_url = shared_link_metadata.url
    direct_image_url = preview_url.replace("?dl=0", "?raw=1")
    direct_image_url = direct_image_url.replace("www.dropbox", "dl.dropboxusercontent")
    return direct_image_url

def uploadImageToCloudinary(filepath):
    """Uploads a local PNG file to Cloudinary and returns a 100% reliable URL."""
    print(f"Uploading {filepath} to Cloudinary...")
    try:
        response = cloudinary.uploader.upload(filepath, resource_type="image", format="jpg", transformation=[{"fetch_format": "jpg"}, {"color_space": "srgb"}],)
        secure_url = response.get("secure_url")
        print(f"Upload successful. Secure URL: {secure_url}")
        return secure_url
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        return None

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

    # tweet the result
    # response = sendTweet(client, testText, cli.threading)
    # print(response)

    # thread the result
    # filepath = textToPNG(ogText)
    # imageUrl = uploadImageToImgbb(filepath)
    # print(f"Image URL: {imageUrl}")
    # # contents = {"media_type": "TEXT", "text": "Hello, World!", "access_token": THREADS_ACCESS_TOKEN} # thread a text box
    # contents = {"media_type": "IMAGE", "image_url": imageUrl, "access_token": THREADS_ACCESS_TOKEN} # thread an image
    # # contents = {"media_type": "TEXT", "text": testText, "access_token": THREADS_ACCESS_TOKEN}
    # # deleteImageFromImgbb("https://ibb.co/LDnVKRJB/0e1797976c3c19c9c509aa712854d7f3")
    # sendThread(contents)
    sendThreadImageFromText(ogText)

    # # debug testing
    # awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"] # LAA
    # homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"] # HOU
    # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"] # José Quijada
    # situation = Situation()
    # situation.startNewGame(homeAbbr, awayAbbr, currentPitcher)
    # dprint(pitchbypitch.drawPitchForTweeting(situation))
    # dprint(textToPNG(pitchbypitch.drawPitch(situation)))

if __name__ == "__main__":
    main(sys.argv[1:])
