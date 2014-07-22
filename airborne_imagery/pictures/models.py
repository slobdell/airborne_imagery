from django.db import models


class _Picture(models.Model):

    class Meta:
        app_label = 'pictures'
        db_table = 'pictures_picture'

    event_id = models.IntegerField()
    photographer = models.CharField(max_length=100, null=True)
    date_taken = models.DateTimeField()
    photo_url = models.CharField(max_length=255)
    sample_photo_url = models.CharField(max_length=255)
    successful_upload = models.BooleanField(default=False)
    # TODO: add an index for event_id, id

    # python manage.py sqlall pictures
    # https://s3.amazonaws.com/airborne-imagery/1-modified.jpg


class Picture(object):
    BASE_URL = "https://s3.amazonaws.com"
    pass
