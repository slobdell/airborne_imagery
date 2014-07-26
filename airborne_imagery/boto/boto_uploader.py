import boto
import gevent
import gevent.pool
import os

from boto.exception import S3ResponseError
from gevent import monkey

from .constants import ACCESS_KEY
from .constants import BUCKET_NAME
from .constants import SECRET_KEY

POOL_SIZE = 16
ASYNC = True

PROGRESS_INTERVAL = 5
IGNORED_FILES = {
    ".DS_Store"
}
ACCEPTABLE_FILENAMES = {
    "jpg",
    "JPG",
    "jpeg",
    "JPEG"
}

# TODO: need to make a group policy right here
S3_ACL = "bucket-owner-full-control"


class BotoUploader(object):

    def __init__(self, read_directory, make_public=False):
        self.read_directory = read_directory
        self.make_public = make_public
        self.files_uploaded = []

    def progress_reporter(self, bytes_transfered, bytes_sent, filename):
        percent_finished = 0
        if bytes_sent:
            percent_finished = (100 * bytes_transfered) / bytes_sent
        print "%s: %s%%" % (filename, percent_finished)

    def _get_or_create_bucket(self, connection, name):
        """Retrieves a bucket if it exists, otherwise creates it."""
        try:
            return connection.get_bucket(name)
        except S3ResponseError:
            return connection.create_bucket(name)  # , policy=S3_ACL)

    def _get_connection(self):
        conn = boto.connect_s3(aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)
        return conn

    def _standard_transfer(self, bucket, filename):
        print "Uploading %s to %s" % (filename, bucket)
        key_name = filename.replace(self.read_directory, "", 1)
        key = bucket.get_key(key_name)
        if key is None:
            key = bucket.new_key(key_name)
        else:
            print "File: %s already exists on Amazon." % filename
            return

        def dynamic_progress_reporter(bytes_transfered, bytes_sent):
            f = filename
            self.progress_reporter(bytes_transfered, bytes_sent, f)

        key.set_contents_from_filename(filename, replace=True,
                                    cb=dynamic_progress_reporter,
                                    num_cb=PROGRESS_INTERVAL,
                                    reduced_redundancy=False)
        if self.make_public:
            key.make_public()
        self.files_uploaded.append(key_name)
        print "Finished transferring %s" % filename

    def _remove_file(self, filename):
        print "Removing %s" % filename
        os.remove(filename)

    def upload(self, filename):
        connection = self._get_connection()
        bucket = self._get_or_create_bucket(connection, BUCKET_NAME)
        self._standard_transfer(bucket, filename)
        self._remove_file(filename)

    def find_new_pictures(self, picture_directory):
        for (dirpath, dirnames, filenames) in os.walk(picture_directory):
            for filename in filenames:
                if filename in IGNORED_FILES:
                    continue
                if not ("." in filename and filename.split(".")[-1] in ACCEPTABLE_FILENAMES):
                    continue
                full_path = "%s/%s" % (dirpath, filename)
                yield full_path

    def start(self):
        if ASYNC:
            monkey.patch_all(socket=True, dns=True, time=True, select=True,thread=False, os=True, ssl=True, httplib=False, aggressive=True)
            pool = gevent.pool.Pool(POOL_SIZE)
            greenlets = []
            for file_path in self.find_new_pictures(self.read_directory):
                greenlets.append(pool.spawn(self.upload, file_path))
            gevent.joinall(greenlets)
        else:
            for file_path in self.find_new_pictures(self.read_directory):
                self.upload(file_path)
        return self.files_uploaded
