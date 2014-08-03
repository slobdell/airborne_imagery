import os
import Image

from ..boto.boto_downloader import BotoDownloader
from ..boto.boto_uploader import BotoUploader
from ..image_managers.utils import resize
from ..utils.string_encoder import encode

save_dir = "./tmp/resize_dir"
BASE_URL = "https://s3.amazonaws.com"


def _setup_save_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def _convert_dimension_str_to_tuple(dimension_str):
    return [int(item) for item in dimension_str.split("x")]


def resize_images_for_order(order):
    _setup_save_directory(save_dir)
    picture_and_dimension_list = order.get_pictures_with_dimensions()
    for picture__intended_dimensions in picture_and_dimension_list:
        picture = picture__intended_dimensions[0]
        intended_dimensions = picture__intended_dimensions[1]
        new_width, new_height = _convert_dimension_str_to_tuple(intended_dimensions)
        downloader = BotoDownloader(picture.amazon_key)
        new_filename = "%s/%s_%s.jpg" % (save_dir, picture.id, intended_dimensions)
        downloader.download(new_filename)
        print "Downloading original image from Amazon to %s" % new_filename
        pil_img = Image.open(new_filename)
        width, height = pil_img.size
        if height > width:
            print "Rotating image to landscape"
            pil_img = pil_img.rotate(90)
        print "Resizing image with new width: %s" % new_width
        pil_img = resize(pil_img, new_width)
        if height > width:
            # return to original position
            pil_img = pil_img.rotate(270)
        pil_img.save(new_filename)
        public_filename = "completed_orders/%s.jpg" % encode(new_filename)
        print "Uploading image to amazon with new filename: %s" % public_filename
        final_amazon_path = "%s/%s" % (BASE_URL, BotoUploader.upload_single_file(new_filename, public_filename))
        order.update_picture_id_with_finish_url(picture.id, final_amazon_path)
        print "Finished updating Picture %s with final URL %s" % (picture.id, final_amazon_path)
