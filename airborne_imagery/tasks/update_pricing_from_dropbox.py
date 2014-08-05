import dropbox

from ..dropbox.constants import READ_FOLDER, PRICING_FILE
from ..dropbox.dropbox_manager import DropBoxManager
from ..dropbox.models import DropboxAccessToken
from ..events.models import Event
from ..pricing.models import Pricing


def propogate_new_values(event_name, new_json_str):
    for dropbox_user in DropboxAccessToken.get_all():
        client = dropbox.client.DropboxClient(dropbox_user.access_token)
        if event_name:
            client.put_file("%s/%s/%s" % (READ_FOLDER, event_name, PRICING_FILE), new_json_str, overwrite=True)
        else:
            client.put_file("%s/%s" % (READ_FOLDER, PRICING_FILE), new_json_str, overwrite=True)


if __name__ == "__main__":
    for dropbox_user in DropboxAccessToken.get_all():
        dropbox_manager = DropBoxManager(dropbox_user.access_token, None)
        for event_name, json_str in dropbox_manager.read_pricing_files_from_root_folder(READ_FOLDER):
            if READ_FOLDER in event_name:
                event = None
            else:
                event = Event.get_or_create_from_event_name(event_name)
            values_updated = Pricing.update_from_json(json_str, event)
            if values_updated:
                if event:
                    event_id = event.id
                    event_name = event.name
                else:
                    event_id = None
                    event_name = None
                propogate_new_values(event_name, Pricing.to_json_str_for_event_id(event_id))
                break
