# Pitch Painter

## Overview

A live and accurate pitch-by-pitch scorebug of the current situation in any MLB game with Python, with the ability to
live post the generated scorebug to Meta Threads. Backed by Python with the PyQt library's GUI for application features. Additional support to retroactively report each pitch from a completed game, saving the output to a file. Scorebug
includes teams, score, inning, count (balls-strikes), baserunners, outs, pitcher, and pitch count. Game descriptions
such as the outcome of a pitch or an at bat can be printed in the output console as well. Command line arguments and application settings allow for a completely user friendly experience. Utilizing data via MLB Stats API, with no intent
to distribute for profit.

## MLB StatsAPI

Pretty print json (works on windows vscode): Ctrl + A, Ctrl + K + F

*   Get desired game pk from specific date  
    https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2024-09-05

*   Get details about game pk  
    https://statsapi.mlb.com/api/v1/game/745369/content  
    https://statsapi.mlb.com/api/v1/game/745369/boxscore

*   Get live feed from specific game  
    https://statsapi.mlb.com/api/v1.1/game/745369/feed/live

*   Get team info  
    https://statsapi.mlb.com/api/v1/teams/  
    https://statsapi.mlb.com/api/v1/teams/116

*   Additional MLB Stats API Documentation  
    https://github.com/toddrob99/MLB-StatsAPI/wiki/Endpoints


## Threads API

First create a Facebook account and a Threads account, and link the two:  
In either app, navigate to Settings -> Accounts Center -> Profiles and personal details  
    Ensure both accounts (Facebook and Threads) are found in Profiles. If not, click Add accounts and add it.  

*   Navigate to https://developers.facebook.com/apps  
    Click Create App and follow the instructions provided.  
    Under Use Cases, choose "Access the Threads API"  

*   With the app opened, navigate to Settings -> Basic  
    There you will find your Threads app ID and Threads app secret. Do NOT share the app secret with anyone.  
    Check passwords_template.py for further instructions on how to use the app secret in this project securely.  

*   In the left panel, navigate to Use Cases -> Customize -> Settings -> User Token Generator -> Generate Access Token  

*   To convert that access token to a long term access token (1 hour -> 60 day expiration)  
    curl -i -X GET "https://graph.threads.com/access_token?grant_type=th_exchange_token&client_secret=<client_secret>&access_token=<access_token>"  

*   Get account id from API call  
    curl "https://graph.threads.net/v1.0/me?fields=id,username&access_token=<access_token>"

*   To refresh a long term access token  
    curl -i -X GET "https://graph.threads.com/refresh_access_token?grant_type=th_refresh_token&access_token=<access_token>"  

*   To view access token's expiration  
    curl -X GET "https://graph.threads.com/v1.0/debug_token?input_token=<access_token>&access_token=<access_token>"  
    date -u -r <time> to get human readable time (remove -u for local time)  
    OR  
    navigate to https://developers.facebook.com/tools/debug/accesstoken/ and paste the access token in and see  

*   See daily quota usage (x/250)  
    curl -s -X GET "https://graph.threads.com/v1.0/<id>/threads_publishing_limit?fields=quota_usage,config,reply_quota_usage,reply_config,delete_quota_usage,delete_config,location_search_quota_usage,location_search_config&access_token=<access_token>"

*   Threads API Publishing endpoint
    https://developers.facebook.com/documentation/threads/reference/publishing#post---threads-user-id--threads

*   Threads API Documentation
    https://developers.facebook.com/documentation/threads


## Dropbox

Create a Dropbox account to link with pitchpainter

*   Navigate to https://www.dropbox.com/developers/apps/  
    Click Create app and follow the instructions provided  
    I recommend to give App Folder access over Full Dropbox, but that is up to you  

*   Open the app in the developer portal to find App key and App secret. Do NOT share the app secret with anyone.  
    Check passwords_template.py for further instructions on how to use the app secret in this project securely.  
    Under OAuth 2, generate an access token  

*   To convert that access token to a refresh token, you first need an offline access token code  
    https://www.dropbox.com/oauth2/authorize?client_id=<app_key>&response_type=code&token_access_type=offline  
    Use that offline code to generate the refresh token as such  
    curl https://api.dropbox.com/oauth2/token -d code=<offline_code> -d grant_type=authorization_code -u <app_key>:<app_secret>  
    Copy the refresh token into passwords.py  

*   To manually refresh the refresh token  
    curl -X POST https://api.dropbox.com/oauth2/token -d grant_type=refresh_token -d refresh_token=<refresh_token> -u <app_key>:<app_secret>  
    Note: This is not necessary because `thread_poster.py` will automatically refresh the token if it about to expire from
    `dbx = dropbox.Dropbox(app_key=DROPBOX_APP_KEY, app_secret=DROPBOX_APP_SECRET, oauth2_refresh_token=DROPBOX_REFRESH_TOKEN)`
