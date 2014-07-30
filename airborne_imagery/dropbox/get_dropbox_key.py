import dropbox
from .constants import APP_KEY, APP_SECRET

from sys import stdin


# TODO you can add a web hook so that my website gets notified whenever a
# change gets made
flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
authorize_url = flow.start()
print '1. Go to: ' + authorize_url
print '2. Click "Allow" (you might have to log in first)'
print '3. Copy the authorization code and input it here.'
'''
# AUTHORIZATION_CODE = "4qv5gtGv_mkAAAAAAAAO-niqKSpjwUFsOz5Lt7dxfes"
authorization_code = stdin.readline().strip()
print "attemping to use: %s" % authorization_code
access_token, user_id = flow.finish(authorization_code)
with open("access_token.txt", "w+") as f:
    f.write(user_id)
    f.write(access_token)
print user_id
print access_token
'''
