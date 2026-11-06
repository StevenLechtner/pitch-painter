"""Snapshot development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = b'54+\xf6^\xcb\xc1\xafTXu@Z]\x17\x11\x9b\xcfUz\xeb\x1e\x94\xe2'
SESSION_COOKIE_NAME = 'login'

# File Upload to var/uploads/
SNAPSHOT_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = SNAPSHOT_ROOT/'var'/'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/snapshot.sqlite3
DATABASE_FILENAME = SNAPSHOT_ROOT/'var'/'snapshot.sqlite3'
