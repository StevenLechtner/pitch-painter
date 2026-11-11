from pitchpainter.live_game import printAllPitchesFromGame, LiveGameWorker

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
    gamePk = 745369
    testThread = LiveGameWorker(gamePk)
    testThread.output.connect(drawPitchOutput)
    printAllPitchesFromGame(gamePk,
                            testThread.output,
                            testThread.stop_event,
                            filepath="tests/pitch_painter/data/meadows.json")
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
