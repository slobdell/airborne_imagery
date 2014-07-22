from ..dropbox.constants import ACCESS_TOKEN
from ..dropbox.constants import READ_FOLDER
from ..dropbox.dropbox_manager import DropBoxManager

from ..image_managers.image_manipulator import ImageManipulator

from ..boto.boto_uploader import BotoUploader
from ..boto.constants import BUCKET_NAME

save_dir = "/tmp/dropbox_images"
watermarked_dir = "/tmp/dropbox_images_watermarked"
watermark_file = "/Users/slobdell/sites/project/temp_watermark.png"
FILENAME_SUFFIX = "-modified"

while True:
    dropbox_manager = DropBoxManager(ACCESS_TOKEN, save_dir)
    dropbox_transfer_finished = dropbox_manager.read_images_from_root_folder(READ_FOLDER, max_files=3)

    image_manipulator = ImageManipulator(save_dir, watermarked_dir, filename_suffix=FILENAME_SUFFIX)
    image_manipulator = image_manipulator.with_resize(400).with_watermark(watermark_file)
    image_manipulator.start()

    # TODO need to add django specific logic in here to actually save the data
    # event = Event.get_or_create(event_name_from_picture_folder_name)

    # for jpeg_filename in save_dir:
        # picture = Picture.get_or_create(event, file_id)
        # TODO: need to make the "-modified" thing a hard constants somewhere
        # TODO generate the URL using bucket name

    private_boto_uploader = BotoUploader(save_dir, make_public=False)
    private_boto_uploader.start()

    public_boto_uploader = BotoUploader(watermarked_dir, make_public=True)
    public_boto_uploader.start()

    if dropbox_transfer_finished:
        print "All Dropbox Files synced"
        break
