from ..dropbox.constants import ACCESS_TOKEN
from ..dropbox.constants import USER_ID
from ..dropbox.constants import READ_FOLDER
from ..dropbox.dropbox_manager import DropBoxManager

from ..pictures.models import Picture
from ..events.models import Event

from ..image_managers.image_manipulator import ImageManipulator
from ..image_managers.utils import get_date_taken

from ..boto.boto_uploader import BotoUploader
from ..boto.constants import BUCKET_NAME

save_dir = "/tmp/dropbox_images"
watermarked_dir = "/tmp/dropbox_images_watermarked"
thumbnail_dir = "/tmp/dropbox_images_thumbnail"
watermark_file = "/Users/slobdell/sites/project/temp_watermark.png"
# TODO: Above statement should be using the settings file
WATERMARK_SUFFIX = "-watermarked"
THUMBNAIL_SUFFIX = "-thumbnail"

while True:
    # TODO loop through all photographers and their respective dropbox token
    dropbox_manager = DropBoxManager(ACCESS_TOKEN, save_dir)
    previous_event_name = ""
    for event_name, jpeg_in_mem in dropbox_manager.read_images_from_root_folder(READ_FOLDER, max_files=16):
        if event_name != previous_event_name:
            event = Event.get_or_create_from_event_name(event_name)
        date_taken = get_date_taken(jpeg_in_mem)
        picture = Picture.create_for_event(event, date_taken, USER_ID, BUCKET_NAME, WATERMARK_SUFFIX, THUMBNAIL_SUFFIX)
        dropbox_manager.save_file_to_hard_drive(jpeg_in_mem, picture.filename)
        picture.mark_saved_on_hard_drive()

    image_manipulator = ImageManipulator(save_dir)
    image_manipulator = (image_manipulator.
                        with_resize(400).
                        with_watermark(watermarked_dir, watermark_file, WATERMARK_SUFFIX).
                        with_thumbnail(thumbnail_dir, 150, THUMBNAIL_SUFFIX))
    image_manipulator.start()

    # TODO need to add django specific logic in here to actually save the data
    # event = Event.get_or_create(event_name_from_picture_folder_name)

    private_boto_uploader = BotoUploader(save_dir, make_public=False)
    pictures_uploaded = private_boto_uploader.start()

    public_boto_uploader = BotoUploader(watermarked_dir, make_public=True)
    watermarked_pictures_uploaded = public_boto_uploader.start()
    pictures_watermarked = [filename.replace(WATERMARK_SUFFIX, "") for filename in watermarked_pictures_uploaded]

    public_boto_uploader = BotoUploader(thumbnail_dir, make_public=True)
    thumbnail_pictures_uploaded = public_boto_uploader.start()
    pictures_thumbnailed = [filename.replace(THUMBNAIL_SUFFIX, "") for filename in thumbnail_pictures_uploaded]

    successful_filename_uploads = set.intersection(set(pictures_uploaded), set(pictures_watermarked), set(pictures_thumbnailed))
    pictures = Picture.get_pictures_from_filenames(successful_filename_uploads)
    for picture in pictures:
        picture.mark_uploaded_to_amazon()

    if dropbox_manager.transfer_finished:
        print "All Dropbox Files synced"
        break
