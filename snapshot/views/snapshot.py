"""
Snapshot JSON text view.

URLs include:
/
/snapshots/<snapshot_id>/
"""

import json
import os
import flask
import snapshot


@snapshot.app.route('/snapshots/<snapshot_id>/')
def show_snapshot(snapshot_id):
    """Display / route."""
    input_context = {}
    input_context["snapshot_id"] = snapshot_id

    metadata_path = f"tests/snapshots/metadata.json"
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found at: {metadata_path}. Run ./bin/snapshotdb <gamePk> create")
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    filepath = metadata.get(snapshot_id)
    if not filepath:
        print(f"Could not lookup filepath from {snapshot_id} in {metadata_path}")
        return None
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} not found. Run ./bin/snapshotdb <gamePk> create")
    with open(filepath, "r", encoding="utf-8") as f:
        snapshot_data = json.load(f)
    input_context["content"] = snapshot_data

    context = {"context": input_context}
    return flask.render_template("snapshot.html", **context)
