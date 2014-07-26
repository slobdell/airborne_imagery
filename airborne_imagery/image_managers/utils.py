import datetime
import Image
import ImageEnhance
from PIL.ExifTags import TAGS


def normalize_colorspace(pil_img):
    if pil_img.mode != 'RGBA':
        pil_img = pil_img.convert('RGBA')
    return pil_img


def resize(pil_img, target_width):
    '''
    Resizes to new target with and
    maintains the same proportions
    '''
    width_percent = (target_width / float(pil_img.size[0]))
    new_height = int((float(pil_img.size[1]) * float(width_percent)))
    return pil_img.resize((target_width, new_height), Image.ANTIALIAS)


def reduce_opacity(pil_img, opacity):
    """Returns an image with reduced opacity."""
    pil_img = normalize_colorspace(pil_img)
    alpha = pil_img.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    pil_img.putalpha(alpha)
    return pil_img


def watermark(pil_img, watermark, position="scale", opacity=1):
    if opacity < 1:
        watermark = reduce_opacity(watermark, opacity)

    layer = Image.new('RGBA', pil_img.size, (0, 0, 0, 0))
    if position == 'tile':
        for y in range(0, pil_img.size[1], watermark.size[1]):
            for x in range(0, pil_img.size[0], watermark.size[0]):
                layer.paste(watermark, (x, y))

    elif position == 'scale':
        ratio = min(
            float(pil_img.size[0]) / watermark.size[0], float(pil_img.size[1]) / watermark.size[1])
        w = int(watermark.size[0] * ratio)
        h = int(watermark.size[1] * ratio)
        watermark = watermark.resize((w, h))
        layer.paste(watermark, ((pil_img.size[0] - w) / 2, (pil_img.size[1] - h) / 2))

    else:
        layer.paste(watermark, position)
    return Image.composite(layer, pil_img, layer)


def _date_string_to_datetime(datestring):
    # 2014:02:25 16:48:10
    date__time = datestring.split(" ")
    year__month__day = [int(item) for item in date__time[0].split(":")]
    hour__minute__second = [int(item) for item in date__time[1].split(":")]
    return datetime.datetime(year=year__month__day[0],
                             month=year__month__day[1],
                             day=year__month__day[2],
                             hour=hour__minute__second[0],
                             minute=hour__minute__second[1],
                             second=hour__minute__second[2])


def get_date_taken(jpeg_in_memory):
    jpeg_in_memory.seek(0)
    pil_image = Image.open(jpeg_in_memory)
    exif_data = {}
    if hasattr(pil_image, '_getexif'):
        exifinfo = pil_image._getexif()
        if exifinfo is not None:
            for tag, value in exifinfo.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value
    for key in ('DateTimeOriginal', 'DateTimeDigitized'):
        # dont use DateTime...that's when it was last modified
        if key in exif_data:
            return _date_string_to_datetime(exif_data[key])
    return None
