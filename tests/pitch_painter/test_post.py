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
from pitchpainter.game import Game
from pitchpainter.win_probability import WinProbability


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
    image_path = thread_poster.text_to_png(situation, filepath=str(test_filepath))

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
    url = thread_poster.upload_image_to_dropbox(str(test_image))

    # Verify Dropbox methods were called correctly
    mock_dbx.files_upload.assert_called_once()
    mock_dbx.sharing_create_shared_link_with_settings.assert_called_once_with("/images/test_image_upload.png")

    # Verify valid URL transformation (?dl=0 -> ?raw=1 and domain replacement)
    assert url == "https://dl.dropboxusercontent.com/s/abcdef/test_image_upload.png?raw=1"


@patch("pitchpainter.thread_poster.requests.post")
@patch("pitchpainter.thread_poster.create_thread_to_post")
@patch("pitchpainter.thread_poster.upload_image_to_dropbox")
@patch("pitchpainter.thread_poster.text_to_png")
@patch("pitchpainter.thread_poster.cli")
def test_post_thread_text_as_image(mock_cli, mock_text_to_png, mock_upload, mock_create_thread, mock_requests_post):
    """Test the end-to-end flow of posting a thread.
    
    Does not physically upload to Dropbox or post to Threads.
    Confirms that the workflow is correct and a post would upload with the following:
        <br>1) Network Connection.
        <br>2) Valid DROPBOX_REFRESH_TOKEN.
        <br>3) Valid THREADS_ACCESS_TOKEN.
    <br>From src/pitchpainter/passwords.py. Check README.md or src/pitchpainter/passwords_template.py for more details.
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
    thread_poster.post_thread_text_as_image(situation_text=situation, description_text=description)
    mock_text_to_png.assert_not_called()
    mock_upload.assert_not_called()
    mock_create_thread.assert_not_called()
    mock_requests_post.assert_not_called()

    # Mock enable threading in CLI - should post
    mock_cli.threading = True
    thread_poster.post_thread_text_as_image(situation_text=situation, description_text=description)
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
        json=expected_publish_payload,
        timeout=25
    )


def test_scoring_play_envokes_post(monkeypatch):
    # choose a scoring play that is not above the threshold - check for both and then confirm its still worthy
    game = Game()
    winProbPath = "tests/pitch_painter/data/rangers_30_win_prob.json"
    game.get_game_by_file_path("tests/pitch_painter/data/rangers_30_orioles_3.json")
    winProb = WinProbability(_filepath=winProbPath)
    monkeypatch.setattr(WinProbability, "NORM_PROBS_ADDED", 25)
    monkeypatch.setattr(WinProbability, "NORM_LEV_IDX", 2.5)
    monkeypatch.setattr(WinProbability, "NORM_DRAMA_IDX", 150)
    monkeypatch.setattr(WinProbability, "PROBS_ADDED_WEIGHT", 0.7)
    monkeypatch.setattr(WinProbability, "LEV_IDX_WEIGHT", 0.15)
    monkeypatch.setattr(WinProbability, "DRAMA_IDX_WEIGHT", 0.15)
    monkeypatch.setattr(WinProbability, "THRESHOLD", 0.375)

    # If it's a big play but not above the threshold, it has to be a scoring play
    # This play was a 3 run homer (27-3 -> 30-3), a major blowout. The play was not impactful, but it was a scoring play
    assert winProb.is_a_big_play(96, winProbPath) == True
    assert winProb.is_above_threshold(96, winProbPath) == False


def test_big_play_envokes_post(monkeypatch):
    # choose a non scoring play that is above the threshold - check for both and then confirm its still worthy
    # atBatIndex = 29. ground out.
    game = Game()
    winProbPath = "tests/pitch_painter/data/ws_game_7_win_prob.json"
    game.get_game_by_file_path("tests/pitch_painter/data/ws_game_7_game.json")
    winProb = WinProbability(_filepath=winProbPath)
    monkeypatch.setattr(WinProbability, "NORM_PROBS_ADDED", 25)
    monkeypatch.setattr(WinProbability, "NORM_LEV_IDX", 2.5)
    monkeypatch.setattr(WinProbability, "NORM_DRAMA_IDX", 150)
    monkeypatch.setattr(WinProbability, "PROBS_ADDED_WEIGHT", 0.7)
    monkeypatch.setattr(WinProbability, "LEV_IDX_WEIGHT", 0.15)
    monkeypatch.setattr(WinProbability, "DRAMA_IDX_WEIGHT", 0.15)
    monkeypatch.setattr(WinProbability, "THRESHOLD", 0.375)

    # This play was a ground out with second and third in a one run game of the world series
    # It was not a scoring play, but it was above the threshold so it was a big play
    assert winProb.is_a_big_play(29, winProbPath) == True
    assert winProb.is_above_threshold(29, winProbPath) == True


def test_all_scoring_and_big_plays_from_game_envokes_post(monkeypatch):
    # check all plays from a game and compare that all of the post plays are expected given threshold weights
    win_prob_path = "tests/pitch_painter/data/meadows_win_prob.json"
    win_prob = WinProbability(_filepath=win_prob_path)
    monkeypatch.setattr(WinProbability, "NORM_PROBS_ADDED", 25)
    monkeypatch.setattr(WinProbability, "NORM_LEV_IDX", 2.5)
    monkeypatch.setattr(WinProbability, "NORM_DRAMA_IDX", 150)
    monkeypatch.setattr(WinProbability, "PROBS_ADDED_WEIGHT", 0.7)
    monkeypatch.setattr(WinProbability, "LEV_IDX_WEIGHT", 0.15)
    monkeypatch.setattr(WinProbability, "DRAMA_IDX_WEIGHT", 0.15)
    monkeypatch.setattr(WinProbability, "THRESHOLD", 0.375)

    assert len(win_prob.win_probabilities) == 71
    found_threshold_0_375_big_plays = []
    correct_threshold_0_375_big_plays = [6, True, 7, True, 13, True, 49, True, 61, True, 62, True, 63, True, 64, True, 65, True, 67, True, 68, True, 70, True]
    for i in range(72):
        if win_prob.is_a_big_play(i, win_prob_path):
            found_threshold_0_375_big_plays += (i, win_prob.is_above_threshold(i, win_prob_path))
    assert found_threshold_0_375_big_plays == correct_threshold_0_375_big_plays

    monkeypatch.setattr(WinProbability, "THRESHOLD", 0.5)
    assert len(win_prob.win_probabilities) == 71
    found_threshold_0_5_big_plays = []
    correct_threshold_0_5_big_plays = [7, False, 13, False, 64, True, 65, True, 67, True, 70, True]
    for i in range(72):
        if win_prob.is_a_big_play(i, win_prob_path):
            found_threshold_0_5_big_plays += (i, win_prob.is_above_threshold(i, win_prob_path))
    assert found_threshold_0_5_big_plays == correct_threshold_0_5_big_plays
