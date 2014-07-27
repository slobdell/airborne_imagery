from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class _DropboxAccessToken(models.Model):

    class Meta:
        app_label = "dropbox"
        db_table = "dropbox_dropboxaccesstoken"

    user_id = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100, null=True)
    # TODO index by user_id


class DropboxAccessToken(models.Model):
    def __init__(self, _dropbox_access_token):
        self._dropbox_access_token = _dropbox_access_token

    @classmethod
    def _wrap(cls, _dropbox_access_token):
        return DropboxAccessToken(_dropbox_access_token)

    @classmethod
    def get_or_create_from_user_id(cls, user_id):
        try:
            _dropbox_access_token = _DropboxAccessToken.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            _dropbox_access_token = _DropboxAccessToken.objects.create(user_id=user_id)
        return cls._wrap(_dropbox_access_token)

    def update_value(self, access_token_str):
        self._dropbox_access_token.access_token = access_token_str
        self._dropbox_access_token.save()
