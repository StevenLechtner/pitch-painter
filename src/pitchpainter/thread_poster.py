"""Module to automatically post contents to Meta Threads."""


import os
import sys
import threading
import dropbox
import requests
from dropbox.exceptions import ApiError
from PIL import Image, ImageDraw, ImageFont
from pitchpainter import cli
try:
    from pitchpainter import passwords
except ImportError as exc:
    raise SystemExit(
        "Error: 'passwords.py' file not found.\n"
        "Please read 'passwords_template.py', copy contents to 'passwords.py', and add your API keys."
    ) from exc
from pitchpainter.print_util import dprint, vprint

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
dbx = dropbox.Dropbox(app_key=DROPBOX_APP_KEY,
                      app_secret=DROPBOX_APP_SECRET,
                      oauth2_refresh_token=DROPBOX_REFRESH_TOKEN)

stop_event = threading.Event()


def stop():
    """Stop trying to post to Threads."""
    dprint("thread_poster stop_event is True")
    stop_event.set()


def start():
    """Start trying to post to Threads."""
    dprint("thread_poster stop_event is False")
    stop_event.clear()


def post_thread_text_as_image(situation_text, description_text=None, alt_text=None, filepath="images/miscPk/temp.png"):
    """Post the given text to Threads as an image using Dropbox as a middleman.

    Convert situationText to an image,
    upload the image to dropbox to get an image url,
    and post an image to Threads using that image url.
    """
    if stop_event.is_set():
        return
    if not cli.threading:
        vprint(
            "We are not posting a thread right now. "
            "-t or --thread to post a thread. -h or --help for other command line options"
        )
        return

    filepath = text_to_png(situation_text, filepath)
    image_url = upload_image_to_dropbox(filepath)
    contents = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": description_text,
        "alt_text": alt_text if alt_text else situation_text,
        "access_token": THREADS_ACCESS_TOKEN
    }  # thread an image
    post_thread(contents)
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
    try:
        dbx.files_delete_v2(f"/{filepath}")
    except ApiError:
        pass


def upload_image_to_dropbox(filepath):
    """Upload image from filepath to Dropbox using configured Dropbox credentials. Return the direct image URL."""
    if stop_event.is_set():
        return None

    with open(filepath, "rb") as fp:
        contents = fp.read()
    upload_resp = dbx.files_upload(
        contents,
        f"/{filepath}",
        dropbox.files.WriteMode.overwrite,
        mute=True,
        autorename=True
    )
    if stop_event.is_set():
        return None

    try:
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(upload_resp.path_lower)
        preview_url = shared_link_metadata.url
    except ApiError as api_err:
        if api_err.error.is_shared_link_already_exists():
            dprint(f"ApiError message: {api_err.error.get_shared_link_already_exists()}")
            dprint(f"Preview URL: {dbx.sharing_list_shared_links().links[0].url}")
            preview_url = dbx.sharing_list_shared_links().links[0].url
        else:
            raise api_err
    direct_image_url = preview_url.replace("?dl=0", "?raw=1")
    direct_image_url = direct_image_url.replace("www.dropbox", "dl.dropboxusercontent")
    dprint(f"Direct image URL: {direct_image_url}")
    return direct_image_url


def post_thread(contents):
    """Post contents to Threads using configured Threads credentials. Attempt to post up to 3 times before failing."""
    if stop_event.is_set():
        return
    if not cli.threading:
        vprint(
            "We are not posting a thread right now. "
            "-t or --thread to post a thread. -h or --help for other command line options"
        )
        return

    # Try to post the thread to threads up to three times before failing
    for attempt in range(3):
        if stop_event.is_set():
            return

        creation_id = create_thread_to_post(contents)
        if stop_event.is_set():
            return
        # Uncomment to test thread creation without posting and adding to daily quota
        # if creationId == -1:
        #     continue
        # else:
        #     break
        publish = {"creation_id": creation_id, "access_token": THREADS_ACCESS_TOKEN}
        vprint(f"POST endpoint /threads_publish with creation id {publish.get("creation_id", -1)}...")
        thread_publish = requests.post(f"{BASE_URL}/threads_publish", json=publish, timeout=25)
        thread_publish_id = thread_publish.json().get("id", -1)
        if thread_publish_id != -1:
            vprint(f"Thread posted successfully! (id={thread_publish_id})")
            break
        vprint(f"{BASE_URL}/threads_publish attempt failed (attempt {attempt + 1}/3)")
        dprint(
            f"endpoint /threads_publish details: \n\t"
            f"Status code: {thread_publish.status_code}\n\t"
            f"JSON: {thread_publish.json()}\n\tRaw: {thread_publish}"
        )
        if attempt < 2:
            if stop_event.wait(5):
                return
        else:
            vprint("Failed to create thread to post after 3 attempts.")


def create_thread_to_post(contents):
    """Use contents to create a post for Threads. Return the post's creationId, -1 if failed to create 3 times."""
    if stop_event.is_set():
        return -1
    # Try to create thread to post up to three times before failing
    for attempt in range(3):
        if stop_event.is_set():
            return -1
        # Optional check: verify url status ok
        try:
            vprint("Checking url status...")
            url_check = requests.get(contents.get("image_url", None), timeout=10)
            if stop_event.is_set():
                return -1
            dprint(
                f"URL Check Response: \n\tStatus code: {url_check.status_code}\n\t"
                f"Content-Type: {url_check.headers.get("Content-Type")}\n\tURL: {url_check.url}"
            )
        except requests.exceptions.RequestException as e:
            vprint(f"URL Check exception: {e}")

        # Thread creation endpoint
        vprint(f"POST endpoint /threads with image url {contents.get("image_url", None)}...")
        thread = requests.post(f"{BASE_URL}/threads", json=contents, timeout=25)
        if stop_event.is_set():
            return -1
        creation_id = thread.json().get("id", -1)
        if creation_id != -1:
            vprint(f"Thread drafted successfully! (id={creation_id})")
            return creation_id
        vprint(f"{BASE_URL}/threads attempt failed (attempt {attempt + 1}/3)")
        dprint(
            f"endpoint /threads details: \n\tStatus code: {thread.status_code}\n\t"
            f"JSON: {thread.json()}\n\tRaw: {thread}"
        )
        if attempt < 2:
            if stop_event.wait(30):
                return -1
        else:
            vprint("Failed to create thread to post after 3 attempts.")
    return -1


def text_to_png(text, filepath="images/miscPk/temp.png"):
    """Convert text to a PNG file and save to filepath."""
    lines = text.split("\n")
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 24)

    # Determine dimensions
    border = 40
    width = max(font.getlength(line) for line in lines) + border  # width of longest line + border
    line_height = 30
    height = line_height * len(lines) + border  # line height * lines + border

    image = Image.new("RGB", (int(width), height), "white")
    draw = ImageDraw.Draw(image)

    y = border / 2
    for line in lines:
        draw.text((border / 2, y), line, font=font, fill="black")  # xy, text, text font, text color
        y += line_height

    dir_name = os.path.dirname(filepath)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    image.save(filepath)
    return filepath


# TODO: move these tests to actual pytest test functions in tests/pitch_painter/test_*.py
def main():
    """Test this file (Deprecated)."""
    cli.get_options(sys.argv[1:])

    test_text = (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    )
    score_update_text = (
        "+────────────+\n"
        "|Score update|\n"
        "|DET 4       |\n"
        "|SD  3       |\n"
        "+────────────+"
    )
    # description_text_fotmatted = (
    #     "Parker Meadows hits a\n"
    #     "grand slam (6) to left\n"
    #     "field. Justyn-Henry Malloy\n"
    #     "scores. Jace Jung scores.\n"
    #     "Colt Keith scores."
    # )
    # combined = test_text + "\n" + description_text_fotmatted
    test_and_score_text = test_text + "\n" + score_update_text
    description_text_one_line = (
        "Parker Meadows hits a grand slam (6) to left field. "
        "Justyn-Henry Malloy scores. Jace Jung scores. Colt Keith scores."
    )
    alt_text = (
        "|─────────────|\n"
        "| DET 0               ◆          ▲            |\n"
        "| SD   3            ◆   ◆       9            |\n"
        "|                        ● ● ○    3-2         |\n"
        "|─────────────|\n"
        "| Robert Suarez             P: 25     |\n"
        "|─────────────|\n"
    )

    # TODO: Move everything below to unit_tests.py; main() is not needed at all here.

    # thread the result
    # filepath = textToPNG(descriptionText)
    # imageUrl = uploadImageToDropbox(filepath)
    # print(f"Image URL: {imageUrl}")
    # # contents = {"media_type": "TEXT", "text": "Hello, World!", "access_token": THREADS_ACCESS_TOKEN}  # thread a txt
    # contents = {"media_type": "IMAGE", "image_url": imageUrl, "access_token": THREADS_ACCESS_TOKEN}  # thread an image
    # postThread(contents)
    post_thread_text_as_image(test_and_score_text, description_text=description_text_one_line, alt_text=alt_text)

    # # debug testing
    # awayAbbr = game["gameData"]["teams"]["away"]["abbreviation"]  # LAA
    # homeAbbr = game["gameData"]["teams"]["home"]["abbreviation"]  # HOU
    # currentPitcher = game["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["fullName"]  # José Quijada
    # situation = Situation()
    # situation.startNewGame(homeAbbr, awayAbbr, currentPitcher)
    # dprint(pitchbypitch.drawPitchForTweeting(situation))
    # dprint(textToPNG(pitchbypitch.drawPitch(situation)))


if __name__ == "__main__":
    main()
