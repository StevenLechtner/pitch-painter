# # what we want to test:
#     # creating a "correct" image
#     # posting to threads (post and then delete)
#     # correct alt text
#     # post all scoring plays (don't actually post, but test that all scoring plays would be a post)
#     # post all big plays (again, don't actually post, but test that all big plays would be a post)

# from pitchpainter.pitch_posting_processor import enqueueAtBatForProcessing, enqueuePitchForProcessing
# from pitchpainter.situation import Situation

# def test_scoring_post_to_threads():
#     """Post a situation to threads, verify contents, and then delete the post from Threads and image from Dropbox."""
#     situation = (
#         "+─────────────────────────+\n"
#         "|DET 0         ◆     ▲    |\n"
#         "|SD  3        ◆ ◆    9    |\n"
#         "|            ● ● ○  3-2   |\n"
#         "|─────────────────────────|\n"
#         "|Robert Suarez      P:25  |\n"
#         "+─────────────────────────+"
#     )
#     description = (
#         "Parker Meadows hits a grand slam (6) to left field. "
#         "Justyn-Henry Malloy scores. Jace Jung scores. Colt Keith scores."
#     )
#     lastPitch = Situation()
#     enqueuePitchForProcessing(745369, situation, description, True, 4, 3)

# def test_big_play_no_score_post_to_threads():
#     pass










import os
from unittest.mock import patch, MagicMock
from PIL import Image
from pitchpainter import thread_poster


def test_text_to_png(tmp_path):
    """Test that textToPNG successfully generates a png from text."""
    test_filepath = tmp_path / "images" / "test_output.png"
    situation = (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    )
    image_path = thread_poster.textToPNG(situation, filepath=str(test_filepath))

    # Verify that the image exists
    assert image_path == str(test_filepath)
    assert os.path.exists(test_filepath)

    # Verify that the image is a valid png
    with Image.open(test_filepath) as img:
        assert img.format == "PNG"
        assert img.width > 0
        assert img.height > 0


@patch("pitchpainter.thread_poster.dbx")
def test_upload_image_to_dropbox_success(mock_dbx, tmp_path):
    """Test uploading an image to Dropbox and generating a direct link url."""
    # Create a temporary local file to upload
    test_image = tmp_path / "test_image_upload.png"
    test_image.write_bytes(b"fake image bytes")
    
    # Mock Dropbox responses
    mock_upload_resp = MagicMock()
    mock_upload_resp.path_lower = "/images/test_image_upload.png"
    mock_dbx.files_upload.return_value = mock_upload_resp
    
    mock_link_meta = MagicMock()
    mock_link_meta.url = "https://www.dropbox.com/s/abcdef/test_image_upload.png?dl=0"
    mock_dbx.sharing_create_shared_link_with_settings.return_value = mock_link_meta

    # Run upload function
    url = thread_poster.uploadImageToDropbox(str(test_image))

    # Verify Dropbox methods were called correctly
    mock_dbx.files_upload.assert_called_once()
    mock_dbx.sharing_create_shared_link_with_settings.assert_called_once_with("/images/test_image_upload.png")

    # Verify valid URL transformation (?dl=0 -> ?raw=1 and domain replacement)
    assert url == "https://dl.dropboxusercontent.com/s/abcdef/test_image_upload.png?raw=1"


@patch("pitchpainter.thread_poster.requests.post")
@patch("pitchpainter.thread_poster.createThreadToPost")
@patch("pitchpainter.thread_poster.uploadImageToDropbox")
@patch("pitchpainter.thread_poster.textToPNG")
@patch("pitchpainter.thread_poster.cli")
def test_post_thread_text_as_image(mock_cli, mock_text_to_png, mock_upload, mock_create_thread, mock_requests_post):
    """Test the end-to-end flow of posting a thread.
    
    Does not physically upload to Dropbox or post to Threads.
    Confirms that the workflow is correct and a post would upload with the following:
        1) Network Connection.
        2) Valid DROPBOX_REFRESH_TOKEN.
        3) Valid THREADS_ACCESS_TOKEN.
    From src/pitchpainter/passwords.py. Check README.md or src/pitchpainter/passwords_template.py for more details.
    """
    # Mock return values for intermediates
    mock_text_to_png.return_value = "images/test_image_upload.png"
    mock_upload.return_value = "https://dl.dropboxusercontent.com/test_image_upload.png?raw=1"
    mock_create_thread.return_value = 123456
    
    # Mock Threads publish response
    mock_pub_response = MagicMock()
    mock_pub_response.status_code = 200
    mock_pub_response.json.return_value = {"id": 123456}
    mock_requests_post.return_value = mock_pub_response

    # Call post in thread_poster.py
    situation = (
        "+─────────────────────────+\n"
        "|DET 0         ◆     ▲    |\n"
        "|SD  3        ◆ ◆    9    |\n"
        "|            ● ● ○  3-2   |\n"
        "|─────────────────────────|\n"
        "|Robert Suarez      P:25  |\n"
        "+─────────────────────────+"
    )
    description = (
        "Parker Meadows hits a grand slam (6) to left field. "
        "Justyn-Henry Malloy scores. Jace Jung scores. Colt Keith scores."
    )

    # Mock disable threading in CLI - should not try to post
    mock_cli.threading = False
    thread_poster.postThreadTextAsImage(situationText=situation, descriptionText=description)
    mock_text_to_png.assert_not_called()
    mock_upload.assert_not_called()
    mock_create_thread.assert_not_called()
    mock_requests_post.assert_not_called()

    # Mock enable threading in CLI - should post
    mock_cli.threading = True
    thread_poster.postThreadTextAsImage(situationText=situation, descriptionText=description)
    mock_text_to_png.assert_called_once_with(situation, "images/miscPk/temp.png")
    mock_upload.assert_called_once_with("images/test_image_upload.png")
    # Verify createThreadToPost was invoked, but since it's mocked, we just verify it received the expected arguments
    mock_create_thread.assert_called_once()
    # Verify requests.post was called with the correct Meta Threads API payload structure
    expected_publish_payload = {
        "creation_id": 123456,
        "access_token": thread_poster.THREADS_ACCESS_TOKEN
    }
    mock_requests_post.assert_called_once_with(
        f"{thread_poster.BASE_URL}/threads_publish", 
        json=expected_publish_payload
    )
