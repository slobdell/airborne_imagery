import os
import Image

from .utils import resize
from .utils import watermark
from .utils import normalize_colorspace
from .utils import orient_photo_using_exif


class ImageManipulator(object):

    def __init__(self, read_directory):
        self.read_directory = read_directory

        self.resize = False
        self.watermark = False

    def with_resize(self, target_width):
        self.resize = True
        self.target_width = target_width
        return self

    def with_watermark(self, write_directory, watermark_filepath, filename_suffix):
        self.watermark = True
        self.watermark_file = Image.open(watermark_filepath)
        self.watermark_write_directory = write_directory
        self.watermark_suffix = filename_suffix
        self._setup_save_directory(self.watermark_write_directory)
        return self

    def with_thumbnail(self, write_directory, thumbnail_width, filename_suffix):
        self.thumbnail = True
        self.thumbnail_width = thumbnail_width
        self.thumbnail_write_directory = write_directory
        self.thumbnail_suffix = filename_suffix
        self._setup_save_directory(self.thumbnail_write_directory)
        return self

    def _setup_save_directory(self, output_directory):
        print output_directory
        print output_directory
        print output_directory
        print output_directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    def _create_new_filename_with_suffix(self, old_filename, suffix):
        split_filename = old_filename.split('.')
        split_filename[-2] = split_filename[-2] + suffix
        new_filename = ".".join(split_filename)
        return new_filename

    def start(self):
        for root, dirs, filenames in os.walk(self.read_directory):
            for filename in filenames:
                filename_with_path = "%s/%s" % (root, filename)
                filename_with_path = filename_with_path.replace(self.read_directory, "", 1)
                full_path = "%s%s" % (self.read_directory, filename_with_path)
                pil_img = Image.open(full_path)
                pil_img = orient_photo_using_exif(pil_img)
                pil_img = normalize_colorspace(pil_img)

                if self.resize:
                    pil_img = resize(pil_img, self.target_width)

                if self.thumbnail:
                    thumbnail_img = resize(pil_img, self.thumbnail_width)
                    thumbnail_filename = self._create_new_filename_with_suffix(filename_with_path, self.thumbnail_suffix)
                    new_path = "%s/%s" % (self.thumbnail_write_directory, thumbnail_filename)
                    if not os.path.exists(os.path.dirname(new_path)):
                        os.makedirs(os.path.dirname(new_path))
                    thumbnail_img.save(new_path)

                if self.watermark:
                    watermarked_img = watermark(pil_img, self.watermark_file)
                    watermark_filename = self._create_new_filename_with_suffix(filename_with_path, self.watermark_suffix)
                    new_path = "%s/%s" % (self.watermark_write_directory, watermark_filename)
                    if not os.path.exists(os.path.dirname(new_path)):
                        os.makedirs(os.path.dirname(new_path))
                    watermarked_img.save(new_path)

                print "Finished applying transformations from %s" % full_path
