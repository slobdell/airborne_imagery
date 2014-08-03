import datetime

from django.core.urlresolvers import reverse
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
    # TODO need to index by date, ID, and event_id


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

    @classmethod
    def get_pictures_in_month_day_year(cls, month, day, year):
        start = datetime.datetime(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
        end = start + datetime.timedelta(days=1)
        _pictures = (_Picture.objects.
                     filter(date_taken__gte=start).
                     filter(date_taken__lt=end).
                     filter(uploaded_to_amazon=True))
        return [Picture._wrap(_picture) for _picture in _pictures]

    @classmethod
    def get_pictures_in_month_and_year(cls, month, year):
        ''' 1 is January, 12 is December '''
        start = datetime.datetime(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start + datetime.timedelta(days=31)).replace(day=1)
        _pictures = (_Picture.objects.
                     filter(date_taken__gte=start).
                     filter(date_taken__lt=end).
                     filter(uploaded_to_amazon=True))
        return [Picture._wrap(_picture) for _picture in _pictures]

    @classmethod
    def get_by_id(cls, picture_id):
        _picture = _Picture.objects.get(id=picture_id)
        return Picture._wrap(_picture)

    @classmethod
    def get_by_ids(cls, picture_ids):
        _pictures = _Picture.objects.filter(id__in=picture_ids)
        return [Picture._wrap(_picture) for _picture in _pictures]

    @classmethod
    def get_pictures_from_event(cls, event_obj):
        _pictures = _Picture.objects.filter(event_id=event_obj.id).filter(uploaded_to_amazon=True)
        return [Picture._wrap(_picture) for _picture in _pictures]

    @classmethod
    def get_pictures_by_most_recent(cls, max_count=None):
        _pictures = (_Picture.objects.
                     exclude(date_taken__isnull=True).
                     filter(uploaded_to_amazon=True).
                     order_by("-date_taken"))
        if max_count:
            _pictures = _pictures[:max_count]
        return [Picture._wrap(_picture) for _picture in _pictures]

    @classmethod
    def get_most_recent_datetime(cls):
        return _Picture.objects.all().latest('date_taken').date_taken

    @property
    def amazon_key(self):
        return "%s/%s.jpg" % (self._picture.event_name_at_save_time,
                              self.id)

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

    @property
    def event_name(self):
        return self._picture.event_name_at_save_time

    @property
    def event_id(self):
        return self._picture.event_id

    @property
    def url(self):
        return reverse('picture', args=[self.id])

    @property
    def date_taken(self):
        return self._picture.date_taken
