import datetime

from django.db import models

from ..pricing.models import Pricing
from ..pictures.models import Picture


class _Order__Picture(models.Model):

    class Meta:
        app_label = 'orders'
        db_table = 'orders_order__picture'

    order_id = models.IntegerField()
    picture_id = models.IntegerField()
    price = models.FloatField()
    dimensions = models.CharField(max_length=50)
    final_picture_url = models.CharField(max_length=255)


class _Order(models.Model):

    class Meta:
        app_label = 'orders'
        db_table = 'orders_order'

    date_created = models.DateTimeField()
    customer_email = models.CharField(max_length=100)
    completed_credit_card_payment = models.BooleanField(default=False)
    completed_photo_processing = models.BooleanField(default=False)
    error_message = models.CharField(max_length=255)


class Order(object):

    def __init__(self, _order):
        self._order = _order
        self._cached_pictures = None

    @classmethod
    def _wrap(cls, _order):
        return Order(_order)

    @classmethod
    def create(cls,
               customer_email,
               picture_id_to_pricing_id):
        pricing_id_to_obj = {p.id: p for p in Pricing.get_by_ids([int(i) for i in picture_id_to_pricing_id.values()])}
        _order = _Order.objects.create(date_created=datetime.datetime.utcnow(),
                                       customer_email=customer_email,
                                       error_message="")
        for picture_id, pricing_id in picture_id_to_pricing_id.items():
            pricing = pricing_id_to_obj[pricing_id]
            _Order__Picture.objects.create(order_id=_order.id,
                                           picture_id=picture_id,
                                           price=pricing.price,
                                           dimensions=pricing.dimensions,
                                           final_picture_url="")
        return cls._wrap(_order)

    @classmethod
    def get_by_id(cls, order_id):
        _order = _Order.objects.get(id=order_id)
        return cls._wrap(_order)

    def get_pictures(self):
        if self._cached_pictures is not None:
            return self._cached_pictures

        picture_ids = _Order__Picture.objects.filter(order_id=self.id).values_list('picture_id', flat=True)
        self._cached_pictures = Picture.get_by_ids(picture_ids)
        return self._cached_pictures

    def get_pictures_with_dimensions(self):
        m2ms = _Order__Picture.objects.filter(order_id=self.id)
        picture_ids = [m2m.picture_id for m2m in m2ms]
        self._cached_pictures = Picture.get_by_ids(picture_ids)
        picture_id_to_obj = {p.id: p for p in self._cached_pictures}
        return [(picture_id_to_obj[m2m.picture_id], m2m.dimensions) for m2m in m2ms]

    @property
    def id(self):
        return self._order.id

    @property
    def total_price(self):
        all_prices = _Order__Picture.objects.filter(order_id=self.id).values_list('price', flat=True)
        total_price = sum(all_prices)
        return "%.2f" % total_price

    @property
    def num_pictures(self):
        return len(self.get_pictures())

    def mark_credit_card_payment_complete(self):
        self._order.completed_credit_card_payment = True
        self._order.save()

    def mark_photo_processing_complete(self):
        self._order.completed_photo_processing = True
        self._order.save()

    def annotate_error_message(self, error_message):
        error_message = error_message[:255]
        self._order.error_message = error_message
        self._order.save()

    def update_picture_id_with_finish_url(self, picture_id, final_url):
        # alternatively I could just update the properties as appropriate
        # instead of busting the cache
        self._cached_pictures = None
        m2m = _Order__Picture.objects.get(order_id=self.id,
                                          picture_id=picture_id)
        m2m.final_picture_url = final_url
        m2m.save()

    def get_final_image_urls(self):
        m2ms = _Order__Picture.objects.filter(order_id=self.id)
        return [m2m.final_picture_url for m2m in m2ms]
