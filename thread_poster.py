import cli
import dropbox
import os
import requests
import sys
import time
from PIL import Image, ImageDraw, ImageFont
from print_util import dprint, vprint

# Threads bot developer credentials
THREADS_APP_ID = "939353101979475"
THREADS_APP_SECRET = "685c1596e92d7783929587707bb6ab6e"
THREADS_ACCESS_TOKEN = "THAANWViZC2T1NBYmJwQi1pTEg5NXE3ZA3ZAHOFhNMm5oekNONTRZAVm9OVEJoSlhDcjN5MmN5b2NodXRsdndCU25GNjBpZADFlLWQ4UC1rTk01ZAlFaQ1JhS2NkaWRNNUVTcmxYbWJuZAkRjY0Q2a3hPWEFzT0tZAMTZAWZA2JybEFSZAUVmSkdRUQZDZD"
THREADS_USER_ID = "28665889336435626"
BASE_URL = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}"

# Dropbox image hosting credentials
DROPBOX_APP_KEY = "c240comt7wz8sqo"
DROPBOX_APP_SECRET = "uumup20acpe76wy"
DROPBOX_REFRESH_TOKEN = "LIZk_Wjvb7MAAAAAAAAAAYO9nqhCcmdldXOmazBt-EEZzVt5biCE64wSj1KDLhM2"
dbx = dropbox.Dropbox(app_key=DROPBOX_APP_KEY, app_secret=DROPBOX_APP_SECRET, oauth2_refresh_token=DROPBOX_REFRESH_TOKEN)

def postThreadTextAsImage(situationText, descriptionText=None, altText=None, filepath="images/miscPk/temp.png"):
    if not cli.threading:
        vprint("We are not posting a thread right now. -t or --thread to post a thread. -h or --help for other command line options")
        return

    filepath = textToPNG(situationText, filepath)
    imageUrl = uploadImageToDropbox(filepath)
    contents = {"media_type": "IMAGE", "image_url": imageUrl, "text": descriptionText, "alt_text": altText if altText else situationText, "access_token": THREADS_ACCESS_TOKEN} # thread an image
    postThread(contents)
    os.remove(filepath)
    dbx.files_delete_v2(f"/{filepath}")

def uploadImageToDropbox(filepath):
    with open(filepath, "rb") as fp:
        contents = fp.read()

    dbx.files_upload(contents, f"/{filepath}", dropbox.files.WriteMode.add, mute=True)
    sharedLinkMetadata = dbx.sharing_create_shared_link_with_settings(f"/{filepath}")
    previewUrl = sharedLinkMetadata.url
    directImageUrl = previewUrl.replace("?dl=0", "?raw=1")
    directImageUrl = directImageUrl.replace("www.dropbox", "dl.dropboxusercontent")
    dprint(f"Direct image URL: {directImageUrl}")
    return directImageUrl

def postThread(contents):
    if not cli.threading:
        vprint("We are not posting a thread right now. -t or --thread to post a thread. -h or --help for other command line options")
        return

    # Try to post the thread to threads up to three times before failing
    for attempt in range(3):
        creationId = createThreadToPost(contents)
        # Uncomment to test thread creation without posting and adding to daily quota
        # if creationId == -1:
        #     continue
        # else:
        #     break
        publish = {"creation_id": creationId, "access_token": THREADS_ACCESS_TOKEN}
        vprint(f"POST endpoint /threads_publish with creation id {publish.get("creation_id", -1)}...")
        threadPublish = requests.post(f"{BASE_URL}/threads_publish", json=publish)
        threadPublishId = threadPublish.json().get("id", -1)
        if threadPublishId != -1:
            vprint(f"Thread posted successfully! (id={threadPublishId})")
            break
        else:
            vprint(f"{BASE_URL}/threads_publish attempt failed (attempt {attempt + 1}/3)")
            dprint(f"endpoint /threads_publish details: \n\tStatus code: {threadPublish.status_code}\n\tJSON: {threadPublish.json()}\n\tRaw: {threadPublish}")
            if attempt < 2:
                time.sleep(5)
            else:
                vprint(f"Failed to create thread to post after 3 attempts.")

def createThreadToPost(contents):
    # Try to create thread to post up to three times before failing
    for attempt in range(3):
        # Optional check: verify url status ok
        try:
            vprint("Checking url status...")
            urlCheck = requests.get(contents.get("image_url", None), timeout=10)
            dprint(f"URL Check Response: \n\tStatus code: {urlCheck.status_code}\n\tContent-Type: {urlCheck.headers.get("Content-Type")}\n\tURL: {urlCheck.url}")
        except Exception as e:
            vprint(f"URL Check exception: {e}")

        # Thread creation endpoint
        vprint(f"POST endpoint /threads with image url {contents.get("image_url", None)}...")
        thread = requests.post(f"{BASE_URL}/threads", json=contents)
        creationId = thread.json().get("id", -1)
        if creationId != -1:
            vprint(f"Thread drafted successfully! (id={creationId})")
            return creationId
        else:
            vprint(f"{BASE_URL}/threads attempt failed (attempt {attempt + 1}/3)")
            dprint(f"endpoint /threads details: \n\tStatus code: {thread.status_code}\n\tJSON: {thread.json()}\n\tRaw: {thread}")
            if attempt < 2:
                time.sleep(30)
            else:
                vprint(f"Failed to create thread to post after 3 attempts.")
    return -1

def textToPNG(text, filepath="images/miscPk/temp.png"):
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

def main(args):
    cli.getOptions(args)

    testText = ("+─────────────────────────+\n"
                "|DET 0         ◆     ▲    |\n"
                "|SD  3        ◆ ◆    9    |\n"
                "|            ● ● ○  3-2   |\n"
                "|─────────────────────────|\n"
                "|Robert Suarez      P:25  |\n"
                "+─────────────────────────+")
    descriptionTextFotmatted = ("Parker Meadows hits a\n"
                        "grand slam (6) to left\n"
                        "field. Justyn-Henry Malloy\n"
                        "scores. Jace Jung scores.\n"
                        "Colt Keith scores.")
    descriptionTextOneLine = ("Parker Meadows hits a grand slam (6) to left field. Justyn-Henry Malloy scores. Jace Jung scores. Colt Keith scores.")
    combined = testText + "\n" + descriptionTextFotmatted
    altText =  ("|─────────────|\n"
                "| DET 0               ◆          ▲            |\n"
                "| SD   3            ◆   ◆       9            |\n"
                "|                        ● ● ○    3-2         |\n"
                "|─────────────|\n"
                "| Robert Suarez             P: 25     |\n"
                "|─────────────|\n")

    # TODO: Move everything below to unit_tests.py; main() is not needed at all here.

    # thread the result
    # filepath = textToPNG(descriptionText)
    # imageUrl = uploadImageToDropbox(filepath)
    # print(f"Image URL: {imageUrl}")
    # # contents = {"media_type": "TEXT", "text": "Hello, World!", "access_token": THREADS_ACCESS_TOKEN} # thread a text box
    # contents = {"media_type": "IMAGE", "image_url": imageUrl, "access_token": THREADS_ACCESS_TOKEN} # thread an image
    # # deleteImageFromImgbb("https://ibb.co/LDnVKRJB/0e1797976c3c19c9c509aa712854d7f3")
    # postThread(contents)
    postThreadTextAsImage(testText, descriptionText=descriptionTextOneLine, altText=altText)

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
