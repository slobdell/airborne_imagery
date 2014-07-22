import os
import Image
from .utils import resize
from .utils import watermark
from .utils import normalize_colorspace


class ImageManipulator(object):

    def __init__(self, read_directory, write_directory, filename_suffix):
        self.read_directory = read_directory
        self.write_directory = write_directory

        self.resize = False
        self.watermark = False
        self.filename_suffix = filename_suffix
        self._setup_save_directory()

    def with_resize(self, target_width):
        self.resize = True
        self.target_width = target_width
        return self

    def with_watermark(self, watermark_filepath):
        self.watermark = True
        self.watermark_file = Image.open(watermark_filepath)
        return self

    def _setup_save_directory(self):
        if not os.path.exists(self.write_directory):
            os.makedirs(self.write_directory)

    def apply_transformations(self, pil_img):
        pil_img = normalize_colorspace(pil_img)
        if self.resize:
            pil_img = resize(pil_img, self.target_width)

        if self.watermark:
            pil_img = watermark(pil_img, self.watermark_file)

        return pil_img

    def start(self):
        for filename in os.listdir(self.read_directory):
            full_path = "%s/%s" % (self.read_directory, filename)
            pil_image = Image.open(full_path)
            updated_image = self.apply_transformations(pil_image)

            split_filename = filename.split('.')
            split_filename[-2] = split_filename[-2] + self.filename_suffix
            new_filename = ".".join(split_filename)
            new_path = "%s/%s" % (self.write_directory, new_filename)
            print "Apply transofmrations from %s to %s" % (full_path, new_path)
            updated_image.save(new_path)
