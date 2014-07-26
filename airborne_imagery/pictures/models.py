from django.db import models


class _Picture(models.Model):

    class Meta:
        app_label = 'pictures'
        db_table = 'pictures_picture'

    event_id = models.IntegerField()
    photographer_name = models.CharField(max_length=100, null=True)
    date_taken = models.DateTimeField(null=True)
    saved_to_hard_drive = models.BooleanField(default=False)
    uploaded_to_amazon = models.BooleanField(default=False)
    amazon_bucket = models.CharField(max_length=255)
    watermark_suffix = models.CharField(max_length=100)
    thumbnail_suffix = models.CharField(max_length=100)
    event_name_at_save_time = models.CharField(max_length=255)
    # index on event_id, id
    # index on id


class Picture(object):

    BASE_URL = "https://s3.amazonaws.com"

    def __init__(self, _picture):
        self._picture = _picture

    @classmethod
    def _wrap(cls, _picture):
        return Picture(_picture)

    @classmethod
    def create_for_event(cls,
                         event_obj,
                         date_taken,
                         photographer_name,
                         amazon_bucket,
                         watermark_suffix,
                         thumbnail_suffix):

        _picture = _Picture.objects.create(event_id=event_obj.id,
                                           photographer_name=photographer_name,
                                           date_taken=date_taken,
                                           amazon_bucket=amazon_bucket,
                                           watermark_suffix=watermark_suffix,
                                           thumbnail_suffix=thumbnail_suffix,
                                           event_name_at_save_time=event_obj.name)
        return Picture._wrap(_picture)

    def mark_saved_on_hard_drive(self):
        self._picture.saved_to_hard_drive = True
        self._picture.save()

    def mark_uploaded_to_amazon(self):
        self._picture.uploaded_to_amazon = True
        self._picture.save()

    @classmethod
    def get_pictures_from_filenames(cls, file_paths):
        filenames = [file_path.split("/")[-1] for file_path in file_paths]
        ids = [int(filename.split(".")[0]) for filename in filenames]
        _pictures = _Picture.objects.filter(id__in=ids)
        return [Picture._wrap(_picture) for _picture in _pictures]

    @property
    def thumbnail_url(self):
        return "%s/%s/%s/%s%s.jpg" % (self.BASE_URL,
                                      self._picture.amazon_bucket,
                                      self._picture.event_name_at_save_time,
                                      self.id,
                                      self._picture.thumbnail_suffix)

    @property
    def watermark_url(self):
        return "%s/%s/%s/%s%s.jpg" % (self.BASE_URL,
                                      self._picture.amazon_bucket,
                                      self._picture.event_name_at_save_time,
                                      self.id,
                                      self._picture.watermark_suffix)

    @property
    def filename(self):
        return "%s/%s.jpg" % (self._picture.event_name_at_save_time, self._picture.id)

    @property
    def id(self):
        return self._picture.id
