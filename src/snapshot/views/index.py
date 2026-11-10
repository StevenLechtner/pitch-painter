"""
Snapshot index (main) view.

URLs include:
/
/uploads/<path:filename>
"""
# import arrow
import os
import flask
import snapshot as snapshot


@snapshot.app.route('/')
def show_index():
    """Display / route."""
    input_context = {}
    input_context["name"] = "Steven"
    input_context["gamePks"] = [d for d in os.listdir("tests/snapshots/") if os.path.isdir(os.path.join("tests/snapshots/", d))]
    context = {"context": input_context}
    return flask.render_template("index.html", **context)


@snapshot.app.route('/uploads/<path:filename>')
def download_file(filename):
    """Display /uploads/<path:filename> route."""
    if 'username' not in flask.session:
        return flask.abort(403)

    if snapshot.app.config['UPLOAD_FOLDER']/filename is None:
        return flask.abort(404)

    return flask.send_from_directory(snapshot.app.config['UPLOAD_FOLDER'],
                                     filename, as_attachment=True)


def find_likes_count(connection, postid):
    """Find number of likes for the post."""
    cur = connection.execute(
        "SELECT COUNT(postid) AS likes "
        "FROM likes "
        "WHERE postid == ? ",
        [postid]
    )
    return cur.fetchall()


def find_comments(connection, postid):
    """Find comments for the post."""
    cur = connection.execute(
        "SELECT * "
        "FROM comments "
        "WHERE comments.postid == ? ",
        [postid]
    )
    return cur.fetchall()
