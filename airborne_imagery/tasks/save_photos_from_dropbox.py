from django.conf import settings

from ..dropbox.constants import DropboxUser
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
watermark_file = "%s/%s" % (settings.STATICFILES_DIRS[0], "temp_watermark.png")
WATERMARK_SUFFIX = "-watermarked"
THUMBNAIL_SUFFIX = "-thumbnail"
# export DJANGO_SETTINGS_MODULE=airborne_imagery.settings


def upload_files_to_amazon():
    private_boto_uploader = BotoUploader(save_dir, make_public=False)
    pictures_uploaded = private_boto_uploader.start()

    public_boto_uploader = BotoUploader(watermarked_dir, make_public=True)
    watermarked_pictures_uploaded = public_boto_uploader.start()
    pictures_watermarked = [filename.replace(WATERMARK_SUFFIX, "") for filename in watermarked_pictures_uploaded]

    public_boto_uploader = BotoUploader(thumbnail_dir, make_public=True)
    thumbnail_pictures_uploaded = public_boto_uploader.start()
    pictures_thumbnailed = [filename.replace(THUMBNAIL_SUFFIX, "") for filename in thumbnail_pictures_uploaded]

    successful_filename_uploads = set.intersection(set(pictures_uploaded), set(pictures_watermarked), set(pictures_thumbnailed))
    return list(successful_filename_uploads)


def resize_and_watermark_photos():
    image_manipulator = ImageManipulator(save_dir)
    image_manipulator = (image_manipulator.
                        with_resize(400).
                        with_watermark(watermarked_dir, watermark_file, WATERMARK_SUFFIX).
                        with_thumbnail(thumbnail_dir, 150, THUMBNAIL_SUFFIX))
    image_manipulator.start()


def transfer_dropbox_pictures_to_hard_drive(user_id, access_token):
    dropbox_manager = DropBoxManager(access_token, save_dir)
    previous_event_name = ""
    for event_name, jpeg_in_mem in dropbox_manager.read_images_from_root_folder(READ_FOLDER, max_files=16):
        if event_name != previous_event_name:
            event = Event.get_or_create_from_event_name(event_name)
        date_taken = get_date_taken(jpeg_in_mem)

        picture = Picture.create_for_event(event, date_taken, user_id, BUCKET_NAME, WATERMARK_SUFFIX, THUMBNAIL_SUFFIX)
        dropbox_manager.save_file_to_hard_drive(jpeg_in_mem, picture.filename)
        picture.mark_saved_on_hard_drive()
    return dropbox_manager.transfer_finished


if __name__ == "__main__":
    for dropbox_user in DropboxUser.members():
        # TODO: map the files I transferred from dropbox and only move the files
        # where the upload was successful
        while True:
            transfer_finished = transfer_dropbox_pictures_to_hard_drive(dropbox_user.user_id, dropbox_user.access_token)
            resize_and_watermark_photos()
            successful_filename_uploads = upload_files_to_amazon()

            pictures = Picture.get_pictures_from_filenames(successful_filename_uploads)
            for picture in pictures:
                picture.mark_uploaded_to_amazon()

            if transfer_finished:
                print "All Dropbox Files synced"
                break
