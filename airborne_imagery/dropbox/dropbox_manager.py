import dropbox
import os
import StringIO

from .constants import FINISH_FOLDER


class DropBoxManager(object):
    '''
    USAGE:

    dropbox_manager = DropBoxManager(ACCESS_TOKEN, "/tmp/dropbox_images")
    dropbox_manager.read_images_from_root_folder(READ_FOLDER)
    '''

    def __init__(self, access_token, save_directory):
        self.client = dropbox.client.DropboxClient(access_token)
        self.save_directory = save_directory
        self._setup_save_directory()
        self.transfer_finished = False

    def _setup_save_directory(self):
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def upload_file(self, filename):
        destination = "/%s/%s" % (FINISH_FOLDER, filename)
        print "Uploading %s to %s..." % (filename, destination)
        f = open(filename, 'rb')
        response = self.client.put_file(destination, f)
        print "uploaded:", response

    def get_jpeg_paths_in_folder(self, dropbox_path):
        root_data = self.client.metadata(dropbox_path)
        children_data = root_data["contents"]
        for child_data in children_data:
            if FINISH_FOLDER in child_data["path"]:
                continue
            if child_data["is_dir"]:
                for jpeg in self.get_jpeg_paths_in_folder(child_data["path"]):
                    yield jpeg
            elif child_data["mime_type"] == "image/jpeg":
                yield child_data["path"]

    def download_file(self, file_path):
        print "Downloading %s..." % file_path
        f, metadata = self.client.get_file_and_metadata(file_path)
        output = StringIO.StringIO()
        output.write(f.read())
        return output

    def move_file(self, old_file_path):
        split_file_path = old_file_path.split("/")
        filename = split_file_path[-1]
        root_folder = "/".join(split_file_path[0:-1])
        finish_folder = "%s/%s/%s" % (root_folder, FINISH_FOLDER, filename)
        print "Moving %s to %s" % (old_file_path, finish_folder)
        self.client.file_move(old_file_path, finish_folder)

    def save_file_to_hard_drive(self, jpeg_in_memory, filename):
        new_filename = "%s/%s" % (self.save_directory, filename)
        print "Saving %s" % new_filename
        with open(new_filename, "w+") as file:
            file.write(jpeg_in_memory.getvalue())
        jpeg_in_memory.close()

    def get_parent_folder_from_file_path(self, file_path):
        return file_path.split("/")[-2]

    def read_images_from_root_folder(self, root_folder_name, max_files=None):
        files_moved = 0
        for jpeg_path in self.get_jpeg_paths_in_folder("/%s" % root_folder_name):
            jpeg_in_memory = self.download_file(jpeg_path)
            event_name = self.get_parent_folder_from_file_path(jpeg_path)
            yield event_name, jpeg_in_memory
            self.move_file(jpeg_path)
            files_moved += 1
            if max_files and files_moved >= max_files:
                return
        self.transfer_finished = True
