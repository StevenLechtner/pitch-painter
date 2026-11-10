import flask
import json
import os
import statsapi

GAMEPK = 745369

app = flask.Flask(__name__)

@app.route('/')
def show_index():
    content = {'name': 'Steven'}
    return flask.render_template("index.html", **content)

def main():
    app.run(host='0.0.0.0', port=8000)
    # timestamps = statsapi.get('game_timestamps', {'gamePk': GAMEPK})
    # dirPath = f"tests/snapshots/{GAMEPK}"
    # if not os.path.exists(dirPath):
    #     os.makedirs(dirPath)
    # index = 0
    # for timestamp in timestamps:
    #     try:
    #         with open(f"{dirPath}/snapshot-{f"{index:04d}"}.json", "x") as file:
    #             contents = statsapi.get('game', {'gamePk': GAMEPK, 'timestamp': timestamp})
    #             data = {'timestamp': timestamp, 'content': contents}
    #             json.dump(data, file, indent=4)
    #     except FileExistsError:
    #         pass
    #     index += 1

if __name__ == "__main__":
    main()
