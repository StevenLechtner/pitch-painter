import cli
import dropbox
import os
import requests
import sys
import threading
from dropbox.exceptions import ApiError
from PIL import Image, ImageDraw, ImageFont
from print_util import dprint, vprint
try:
    import passwords
except ImportError:
    raise SystemExit(
        "Error: 'passwords.py' file not found.\n"
        "Please read 'passwords_template.py', copy contents to 'passwords.py', and add your API keys."
    )

# Threads bot developer credentials
THREADS_APP_ID = passwords.THREADS_APP_ID
THREADS_APP_SECRET = passwords.THREADS_APP_SECRET
THREADS_ACCESS_TOKEN = passwords.THREADS_ACCESS_TOKEN
THREADS_USER_ID = passwords.THREADS_USER_ID
BASE_URL = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}"

# Dropbox image hosting credentials
DROPBOX_APP_KEY = passwords.DROPBOX_APP_KEY
DROPBOX_APP_SECRET = passwords.DROPBOX_APP_SECRET
DROPBOX_REFRESH_TOKEN = passwords.DROPBOX_REFRESH_TOKEN
dbx = dropbox.Dropbox(app_key=DROPBOX_APP_KEY, app_secret=DROPBOX_APP_SECRET, oauth2_refresh_token=DROPBOX_REFRESH_TOKEN)

stop_event = threading.Event()

def stop():
    dprint("thread_poster stop_event is True")
    stop_event.set()

def start():
    dprint("thread_poster stop_event is False")
    stop_event.clear()

def postThreadTextAsImage(situationText, descriptionText=None, altText=None, filepath="images/miscPk/temp.png"):
    if stop_event.is_set():
        return
    if not cli.threading:
        vprint("We are not posting a thread right now. -t or --thread to post a thread. -h or --help for other command line options")
        return

    filepath = textToPNG(situationText, filepath)
    imageUrl = uploadImageToDropbox(filepath)
    contents = {"media_type": "IMAGE", "image_url": imageUrl, "text": descriptionText, "alt_text": altText if altText else situationText, "access_token": THREADS_ACCESS_TOKEN} # thread an image
    postThread(contents)
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
    try:
        dbx.files_delete_v2(f"/{filepath}")
    except ApiError:
        pass

def uploadImageToDropbox(filepath):
    if stop_event.is_set():
        return None

    with open(filepath, "rb") as fp:
        contents = fp.read()
    uploadResp = dbx.files_upload(contents, f"/{filepath}", dropbox.files.WriteMode.overwrite, mute=True, autorename=True)
    if stop_event.is_set():
        return None

    try:
        sharedLinkMetadata = dbx.sharing_create_shared_link_with_settings(uploadResp.path_lower)
        previewUrl = sharedLinkMetadata.url
    except ApiError as apiErr:
        if apiErr.error.is_shared_link_already_exists():
            dprint(f"ApiError message: {apiErr.error.get_shared_link_already_exists()}")
            dprint(f"Preview URL: {dbx.sharing_list_shared_links().links[0].url}")
            previewUrl = dbx.sharing_list_shared_links().links[0].url
        else:
            raise apiErr
    directImageUrl = previewUrl.replace("?dl=0", "?raw=1")
    directImageUrl = directImageUrl.replace("www.dropbox", "dl.dropboxusercontent")
    dprint(f"Direct image URL: {directImageUrl}")
    return directImageUrl

def postThread(contents):
    if stop_event.is_set():
        return
    if not cli.threading:
        vprint("We are not posting a thread right now. -t or --thread to post a thread. -h or --help for other command line options")
        return

    # Try to post the thread to threads up to three times before failing
    for attempt in range(3):
        if stop_event.is_set():
            return

        creationId = createThreadToPost(contents)
        if stop_event.is_set():
            return
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
                if stop_event.wait(5):
                    return
            else:
                vprint(f"Failed to create thread to post after 3 attempts.")

def createThreadToPost(contents):
    if stop_event.is_set():
        return -1
    # Try to create thread to post up to three times before failing
    for attempt in range(3):
        if stop_event.is_set():
            return -1
        # Optional check: verify url status ok
        try:
            vprint("Checking url status...")
            urlCheck = requests.get(contents.get("image_url", None), timeout=10)
            if stop_event.is_set():
                return -1
            dprint(f"URL Check Response: \n\tStatus code: {urlCheck.status_code}\n\tContent-Type: {urlCheck.headers.get("Content-Type")}\n\tURL: {urlCheck.url}")
        except Exception as e:
            vprint(f"URL Check exception: {e}")

        # Thread creation endpoint
        vprint(f"POST endpoint /threads with image url {contents.get("image_url", None)}...")
        thread = requests.post(f"{BASE_URL}/threads", json=contents)
        if stop_event.is_set():
            return -1
        creationId = thread.json().get("id", -1)
        if creationId != -1:
            vprint(f"Thread drafted successfully! (id={creationId})")
            return creationId
        else:
            vprint(f"{BASE_URL}/threads attempt failed (attempt {attempt + 1}/3)")
            dprint(f"endpoint /threads details: \n\tStatus code: {thread.status_code}\n\tJSON: {thread.json()}\n\tRaw: {thread}")
            if attempt < 2:
                if stop_event.wait(30):
                    return -1
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
    scoreUpdateText =  ("+────────────+\n"
                        "|Score update|\n"
                        "|DET 4       |\n"
                        "|SD  3       |\n"
                        "+────────────+")
    descriptionTextFotmatted = ("Parker Meadows hits a\n"
                        "grand slam (6) to left\n"
                        "field. Justyn-Henry Malloy\n"
                        "scores. Jace Jung scores.\n"
                        "Colt Keith scores.")
    testAndScoreText = testText + "\n" + scoreUpdateText
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
    # postThread(contents)
    postThreadTextAsImage(testAndScoreText, descriptionText=descriptionTextOneLine, altText=altText)

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
