import dropbox

from ..dropbox.constants import READ_FOLDER, PRICING_FILE
from ..dropbox.models import DropboxAccessToken
from ..pricing.models import Pricing


def propogate_new_values(new_json_str):
    for dropbox_user in DropboxAccessToken.get_all():
        client = dropbox.client.DropboxClient(dropbox_user.access_token)
        client.put_file("%s/%s" % (READ_FOLDER, PRICING_FILE), new_json_str, overwrite=True)


if __name__ == "__main__":
    for dropbox_user in DropboxAccessToken.get_all():
        client = dropbox.client.DropboxClient(dropbox_user.access_token)
        pricing_file = client.get_file("%s/%s" % (READ_FOLDER, PRICING_FILE))
        json_str = pricing_file.read()
        values_updated = Pricing.update_from_json(json_str)
        if values_updated:
            propogate_new_values(Pricing.to_json_str())
            break
