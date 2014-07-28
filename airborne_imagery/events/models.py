import datetime
import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models

from ..pictures.models import Picture


class _Event(models.Model):

    class Meta:
        app_label = "events"
        db_table = "events_event"

    name = models.CharField(max_length=255)
    date_hosted = models.DateTimeField()
    # TODO make sure that I index on name, should be unique...


class Event(object):

    def __init__(self, _event):
        self._event = _event
        self._cached_pictures = None
        self._cached_cover_picture = None

    @classmethod
    def _wrap(cls, _event):
        return Event(_event)

    @classmethod
    def get_by_id(cls, event_id):
        _event = _Event.objects.get(id=event_id)
        return cls._wrap(_event)

    @classmethod
    def get_or_create_from_event_name(cls, event_name):
        cleaned_event_name = " ".join(event_name.split())
        cleaned_event_name = cleaned_event_name.title()
        try:
            _event = _Event.objects.get(name=cleaned_event_name)
        except ObjectDoesNotExist:
            _event = _Event.objects.create(name=cleaned_event_name,
                                           date_hosted=datetime.datetime.utcnow())
        return cls._wrap(_event)

    @classmethod
    def get_events_by_most_recent(cls, max_count=None):
        # this assumes that a relatively small number of events will take place
        # total...no paging built in or anything
        _events = _Event.objects.all().order_by("-date_hosted")
        if max_count is not None:
            _events = _events[:max_count]
        return [cls._wrap(_event) for _event in _events]

    def get_pictures(self):
        if self._cached_pictures is not None:
            return self._cached_pictures
        self._cached_pictures = Picture.get_pictures_from_event(self)
        return self._cached_pictures

    @property
    def _cover_picture(self):
        if self._cached_cover_picture is not None:
            return self._cached_cover_picture
        try:
            self._cached_cover_picture = random.choice(self.get_pictures())
        except IndexError:
            self._cached_cover_picture = None
        return self._cached_cover_picture

    @property
    def cover_picture_thumbnail(self):
        if self._cover_picture:
            return self._cover_picture.thumbnail_url
        return None

    @property
    def cover_picture_watermarl(self):
        if self._cover_picture:
            return self._cover_picture.watermark_url
        return None

    @property
    def id(self):
        return self._event.id

    @property
    def name(self):
        return self._event.name

    @property
    def formatted_date(self):
        datetime_obj = self._event.date_hosted
        return datetime_obj.strftime("%B %d, %Y")

    @property
    def url(self):
        return reverse('event', args=[self.id])
