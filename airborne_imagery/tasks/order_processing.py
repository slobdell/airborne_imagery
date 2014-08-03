import os
import Image

from ..boto.boto_downloader import BotoDownloader
from ..boto.boto_uploader import BotoUploader
from ..image_managers.utils import resize
from ..utils.string_encoder import encode

save_dir = "./tmp/resize_dir"


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
        pil_img = Image.open(new_filename)
        width, height = pil_img.size
        if height > width:
            pil_img = pil_img.rotate(90)
        pil_img = resize(pil_img, new_width)
        pil_img.save(new_filename)
        # upload the image to boto with new filename
        # make it public
        final_url = ""
        order.update_picture_id_with_finish_url(picture.id, final_url)
