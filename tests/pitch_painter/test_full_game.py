from pitchpainter import game_processor

outputs = []

def drawPitchOutput(text):
    """Only append situation output from printAllPitchesFromGame()."""
    if '+─────────────────────────+\n|DET' in text:
        outputs.append(text)

def outputAll(text):
    """Append all output from printAllPitchesFromGame()."""
    outputs.append(text)

def test_full_game():
    """Check every pitch from the September 5th, 2024 game between the Detroit Tigers and San Diego Padres"""
    game_pk = 745369
    test_thread = game_processor.GameProcessorWorker(game_pk)
    test_thread.output.connect(drawPitchOutput)
    processor = game_processor.GameProcessor(stop_event=test_thread.stop_event,
                                             output=test_thread.output,
                                             game_pk=game_pk,
                                             filepath="tests/pitch_painter/data/meadows.json")
    processor.print_all_pitches_from_game()
    file_outputs = []
    with open("tests/pitch_painter/data/meadows_correct_pitches.txt", "r") as f:
        file_outputs = f.readlines()
    index = 0
    correct_outputs = []
    situation = ""
    for line in file_outputs:
        # read 7 lines as one object - a situation is 7 lines long
        if index < 7:
            situation += line
            index += 1
        else:
            index = 1
            correct_outputs.append(situation.rstrip())  # strip off the last new line in the situation text
            situation = line
    correct_outputs.append(situation.rstrip())  # append the last situation that the loop doesn't account for
    index = 0
    assert len(outputs) == len(correct_outputs)
    # ensure every single pitch matches the verified meadows_correct_pitches file output
    while index < len(outputs):
        assert outputs[index] == correct_outputs[index]
        index += 1
