from django.db import models


class _Event(models.Model):

    class Meta:
        app_label = "events"
        db_table = "events_event"

    name = models.CharField(max_length=255)
    date_hosted = models.DateTimeField()


class Event(object):

    @classmethod
    def get_or_create_from_event_name(cls, event_name):
        raise NotImplementedError
