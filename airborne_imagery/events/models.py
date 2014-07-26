import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


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

    @classmethod
    def _wrap(cls, _event):
        return Event(_event)

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

    @property
    def id(self):
        return self._event.id

    @property
    def name(self):
        return self._event.name
