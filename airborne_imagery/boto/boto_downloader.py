import boto

from boto.exception import S3ResponseError

from .constants import ACCESS_KEY
from .constants import BUCKET_NAME
from .constants import SECRET_KEY


# TODO: refactor common stuff into base class
class BotoDownloader(object):

    def __init__(self, target_filename):
        self.target_filename = target_filename

    def _get_connection(self):
        conn = boto.connect_s3(aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)
        return conn

    def _get_or_create_bucket(self, connection, name):
        """Retrieves a bucket if it exists, otherwise creates it."""
        try:
            return connection.get_bucket(name)
        except S3ResponseError:
            return connection.create_bucket(name)

    def download(self, download_filename):
        connection = self._get_connection()
        bucket = self._get_or_create_bucket(connection, BUCKET_NAME)
        try:
            key = bucket.get_key(self.target_filename)
        except AttributeError:
            return False
        key.get_contents_to_filename(download_filename)
        return True
