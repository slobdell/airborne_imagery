from django.db import models


class _Event(models.Model):

    class Meta:
        app_label = "events"
        db_table = "events_event"

    name = models.CharField(max_length=255)
    date_hosted = models.DateTimeField()


class Event(object):
    pass
