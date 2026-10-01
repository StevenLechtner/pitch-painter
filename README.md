# Pitch Painter - Automated Threads Poster

## Overview

A live and accurate pitch-by-pitch scorebug of the current situation in any MLB game with Python, with the ability to
live post the generated scorebug to Meta Threads. Fully supports both finished AND live baseball games! Backed by Python with the PyQt library's GUI for application features. Additional support to retroactively report each pitch from a completed game, saving the output to a file. Scorebug includes teams, score, inning, count (balls-strikes), baserunners, outs, pitcher, and pitch count. Game descriptions such as the outcome of a pitch or an at-bat can be printed in the output console as well. Command line arguments and application settings allow for a completely user-friendly experience. Utilizing data via MLB Stats API, with no intent to distribute for profit.  

For additional examples and details, view `@pitchpainter` (my personal Threads account) on Threads!

## Setup

Developed on `Python 3.14.3`  
Download the repo and run
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
`python application.py` runs the main PyQt application GUI.  
If you want this project to also post to Threads, check the subsequent API sections to obtain and link proper API Keys.

## Flags

`cli.py` contains implementation of command line argument flags, outlined below

*   `-h, --help`  
    Shows the command line help message and exits

*   `-v, --verbose`  
    Enable verbose mode. Verbose print statements give high level insights on what the program is executing

*   `-d, --debug`  
    Enable debug logs. Debug print statements give more technical logs on what the program is executing, for developers

*   `-t, --threading`  
    Posting Threads to Meta Threads. With this on, big plays and scoring plays will be posted on the connected Threads
    account associated with this project, given the proper API Keys. With this off, no posts will be created.

Example: `python application.py -v -d -t` will print all verbose and debug statements in the console, and post big and scoring plays to Threads.

## Application GUI and Backend Algorithm

Running `application.py` gives the user a PyQt interactive GUI. The user can `select any date` in the top menu, giving a list of any and all MLB games for that date. They can then `select a game` from that date, and click the `View _` button on the bottom to see the output for that game. When a game is selected, the bottom button will change and act as a `Return` menu option to return back to the calendar and game selection screen. If the user has `--threading` enabled, then the backend will check completed plays for big plays and scoring plays, and automatically post a thread to Threads given the situation. The post will show the scoreboard situation of the game right `before` the pitch was thrown that resulted in a big play or scoring play. The post is basically a snapshot of "images taken before disaster". The post to Threads happens in a QThread parallel to the output displayed in the application console as follows: `situation details -> formatted scoreboard text -> png -> save on OS -> upload to Dropbox -> obtain URL to post to Threads -> post to Threads -> delete image on OS and Dropbox`. Alt text support on Threads posts.

## MLB StatsAPI

*   Get desired game pk from specific date  
    `https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=yyyy-mm-dd`

*   Get details about game pk  
    `https://statsapi.mlb.com/api/v1/game/<gamePK>/content`
    `https://statsapi.mlb.com/api/v1/game/<gamePK>/boxscore`

*   Get live feed from specific game  
    `https://statsapi.mlb.com/api/v1.1/game/<gamePK>/feed/live`

*   Get team info  
    `https://statsapi.mlb.com/api/v1/teams/`
    `https://statsapi.mlb.com/api/v1/teams/116`

*   Additional MLB Stats API Documentation  
    https://github.com/toddrob99/MLB-StatsAPI/wiki/Endpoints

Note: Majority of tests were with gamePK 745369  
Mac VSCode pretty print json: `Ctrl + A, Option + Shift + F`  
Windows VSCode pretty print json: `Ctrl + A, Ctrl + K + F`

## Passwords

Threads API and Dropbox API Keys/Access Tokens are user specific and should never be shared with others.  
`threads_poster.py` obtains desired keys from `passwords.py`. This file is included in the `.gitignore` as it contains the secret keys and access tokens obtained in the sections below. Copy the templated `passwords_template.py` to `passwords.py`
```
cp passwords_template.py passwords.py
```
Then edit `passwords.py` with the appropriate keys and tokens.  
Threads and Dropbox configuration are needed to correctly post to Threads.  
To configure your project for Twitter (X), add keys to `passwords.py` as well and look at the `live_tweet.py` file.  
This project no longer supports Twitter bots and has moved exclusively to Meta Threads, but `live_tweet.py` is still there for you if you want to configure it. Tweets cost $0.015 per post, while Threads is free for 250 posts every 24-hour cycle.

## Threads API

Threads API is used to physically post a thread to Threads, given the proper API Keys.  
First create a Facebook account and a Threads account, and link the two:  
In either app, navigate to Settings -> Accounts Center -> Profiles and personal details  
    Ensure both accounts (Facebook and Threads) are found in Profiles. If not, click Add accounts and add it.  

*   Navigate to https://developers.facebook.com/apps  
    Click Create App and follow the instructions provided.  
    Under Use Cases, choose "Access the Threads API"  

*   With the app opened, navigate to `Settings -> Basic`  
    There you will find your Threads app ID and Threads app secret. Do **NOT** share the app secret with anyone.  
    Check `passwords_template.py` for further instructions on how to use the app secret in this project securely.  

*   In the left panel, navigate to `Use Cases -> Customize -> Settings -> User Token Generator -> Generate Access Token`  

*   To convert that access token to a long term access token (1 hour -> 60 day expiration)  
    `curl -i -X GET "https://graph.threads.com/access_token?grant_type=th_exchange_token&client_secret=<client_secret>&access_token=<access_token>"`  

*   Get account id from API call  
    `curl "https://graph.threads.net/v1.0/me?fields=id,username&access_token=<access_token>"`

*   To refresh a long term access token  
    `curl -i -X GET "https://graph.threads.com/refresh_access_token?grant_type=th_refresh_token&access_token=<access_token>"`  

*   To view access token's expiration  
    `curl -X GET "https://graph.threads.com/v1.0/debug_token?input_token=<access_token>&access_token=<access_token>"`  
    `date -u -r <time>` to get human-readable time (remove -u for local time)  
    OR  
    navigate to https://developers.facebook.com/tools/debug/accesstoken/ and paste the access token in and see  

*   See daily quota usage (x/250)  
    `curl -s -X GET "https://graph.threads.com/v1.0/<id>/threads_publishing_limit?fields=quota_usage,config,reply_quota_usage,reply_config,delete_quota_usage,delete_config,location_search_quota_usage,location_search_config&access_token=<access_token>"`

*   Threads API Publishing endpoint
    https://developers.facebook.com/documentation/threads/reference/publishing#post---threads-user-id--threads

*   Threads API Documentation
    https://developers.facebook.com/documentation/threads


## Dropbox API

Dropbox API is used to obtain an image URL that Threads can use to post a Thread.  
The program converts text to png, uploads the png to Dropbox, and uses the resulting URL to post to Threads.  
This is done because Threads' monospace font fights with the scoreboard format, and converting the text to png ensures
that the post will have the desired formatting. Threads requires an image URL to post an image, so Dropbox is used as
a middleman to host an image for a short period of time. The image is saved on the OS and uploaded to Dropbox, used to post a Thread, and then deleted from the OS and Dropbox seamlessly.  
`text -> png -> save on OS -> upload to Dropbox -> obtain URL to post to Threads -> post to Threads -> delete image on OS and Dropbox`  

First, create a Dropbox account to link with pitchpainter. Then:

*   Navigate to https://www.dropbox.com/developers/apps/  
    Click Create app and follow the instructions provided  
    I recommend to give App Folder access over Full Dropbox, but that is up to you  

*   Open the app in the developer portal to find App key and App secret. Do **NOT** share the app secret with anyone.  
    Check `passwords_template.py` for further instructions on how to use the app secret in this project securely.  
    Under OAuth 2, generate an access token  

*   To convert that access token to a refresh token, you first need an offline access token code  
    https://www.dropbox.com/oauth2/authorize?client_id=<app_key>&response_type=code&token_access_type=offline  
    Use that offline code to generate the refresh token as such  
    `curl https://api.dropbox.com/oauth2/token -d code=<offline_code> -d grant_type=authorization_code -u <app_key>:<app_secret>`  
    Copy the refresh token into passwords.py  

*   To manually refresh the refresh token  
    `curl -X POST https://api.dropbox.com/oauth2/token -d grant_type=refresh_token -d refresh_token=<refresh_token> -u <app_key>:<app_secret>`  
    Note: This is not necessary because `thread_poster.py` will automatically refresh the token if it is about to expire from
    `dbx = dropbox.Dropbox(app_key=DROPBOX_APP_KEY, app_secret=DROPBOX_APP_SECRET, oauth2_refresh_token=DROPBOX_REFRESH_TOKEN)`
