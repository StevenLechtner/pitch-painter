'''
cp passwords_template.py passwords.py
Update values to connect your Threads application and Dropbox (for image uploads to Threads)
Check notes.txt to learn how to create/connect your Threads app to this project, get ids,
and generate long term access tokens from short term ones (valid for 60 days, can be refreshed)
Also check notes.txt for Dropbox keys. Note that Dropbox's refresh token will automatically refresh when used!
'''

# Threads bot developer credentials
THREADS_APP_ID = "your_threads_app_id_here"
THREADS_APP_SECRET = "your_threads_app_secret_here"
THREADS_ACCESS_TOKEN = "your_threads_(long_term)_access_token_here"
THREADS_USER_ID = "your_threads_user_id_here"

# Dropbox image hosting credentials
DROPBOX_APP_KEY = "your_dropbox_app_key_here"
DROPBOX_APP_SECRET = "your_dropbox_app_secret_here"
DROPBOX_REFRESH_TOKEN = "your_dropbox_refresh_token_here"

# Twitter bot developer credentials (if I need)
TWITTER_API_KEY = "your_twitter_api_key_here"
TWITTER_API_SECRET = "your_twitter_api_secret_here"
TWITTER_BEARER_TOKEN = "your_twitter_bearer_token_here"
TWITTER_CONSUMER_KEY = "your_twitter_consumer_key_here"
TWITTER_CONSUMER_SECRET = "your_twitter_consumer_secret_here"
TWITTER_ACCESS_TOKEN = "your_twitter_access_token_here"
TWITTER_ACCESS_SECRET = "your_twitter_access_secret_here"
TWITTER_ANOTHER_ACCESS_TOKEN = "your_twitter_another_access_token_here"
TWITTER_ANOTHER_ACCESS_REFRESH_TOKEN = "your_twitter_another_access_refresh_token_here"
