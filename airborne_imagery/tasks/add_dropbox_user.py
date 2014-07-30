import sys
import dropbox

from ..dropbox.constants import APP_KEY, APP_SECRET, READ_FOLDER
from ..dropbox.models import DropboxAccessToken


if __name__ == "__main__":
    authorization_code = sys.argv[1]
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
    access_token, user_id = flow.finish(authorization_code)
    dropbox_access_token = DropboxAccessToken.get_or_create_from_user_id(user_id)
    dropbox_access_token.update_value(access_token)
    client = dropbox.client.DropboxClient(access_token)
    try:
        client.file_create_folder(READ_FOLDER)
    except dropbox.rest.ErrorResponse:
        pass  # folder already exists
