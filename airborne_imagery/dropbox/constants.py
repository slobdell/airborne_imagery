READ_FOLDER = "test_folder"
FINISH_FOLDER = "Airborne_Imagery_Finished"


class _DropboxUser(object):
    def __init__(self, user_name, user_id, access_token):
        self.user_name = user_name
        self.user_id = user_id
        self.access_token = access_token


class DropboxUser(object):
    SCOTT_LOBDELL = _DropboxUser("Scott Lobdell", "46399067", "4qv5gtGv_mkAAAAAAAAPMsyYEOvj0jZ1sAV9bhqI5uAUj4mSohgeDvOKsUC_PPIq")

    @classmethod
    def members(cls):
        return [getattr(cls, attr) for attr in dir(cls) if attr.isupper()]
