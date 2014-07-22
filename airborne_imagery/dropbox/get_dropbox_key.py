import dropbox
from sys import stdin


APP_KEY = "2i6dyvmy8mzy9is"
APP_SECRET = "31l1c6drlblyiiu"
# TODO you can add a web hook so that my website gets notified whenever a
# change gets made
flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
authorize_url = flow.start()
print '1. Go to: ' + authorize_url
print '2. Click "Allow" (you might have to log in first)'
print '3. Copy the authorization code and input it here.'
# AUTHORIZATION_CODE = "4qv5gtGv_mkAAAAAAAAO-niqKSpjwUFsOz5Lt7dxfes"
authorization_code = stdin.readline()
access_token, user_id = flow.finish(authorization_code)
with open("access_token.txt", "w+") as f:
    f.write(access_token)
print access_token
