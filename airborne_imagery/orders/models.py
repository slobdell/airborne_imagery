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


class _Order(models.Model):

    class Meta:
        app_label = 'orders'
        db_table = 'orders_order__picture'

    date_created = models.DateTimeField()
    customer_email = models.CharField(max_length=100)
    completed_credit_card_payment = models.BooleanField(default=False)
    completed_photo_processing = models.BooleanField(default=False)


class Order(object):

    def __init__(self, _order):
        self._order = _order

    @classmethod
    def _wrap(cls, _order):
        return Order(_order)

    @classmethod
    def create(cls,
               customer_email,
               picture_id_to_pricing_id):
        pricing_id_to_obj = {p.id: p for p in Pricing.get_by_ids([int(i) for i in picture_id_to_pricing_id.values()])}
        _order = _Order.objects.create(date_created=datetime.datetime.utcnow(),
                                       customer_email=customer_email)
        for picture_id, pricing_id in picture_id_to_pricing_id.items():
            pricing = pricing_id_to_obj[pricing_id]
            _Order__Picture.objects.create(order_id=_order.id,
                                           picture_id=picture_id,
                                           price=pricing.price,
                                           dimensions=pricing.dimensions)
        return cls._wrap(_order)

    @classmethod
    def get_by_id(cls, order_id):
        _order = _Order.objects.get(id=order_id)
        return cls._wrap(_order)

    def get_pictures(self):
        _picture_ids = _Order__Picture.objects.filter(order_id=self.order.id).values_list('picture_id', flat=True)
        return Picture.get_by_ids(_picture_ids)

    @property
    def id(self):
        return self._order.id

    def mark_credit_card_payment_complete(self):
        self._order.completed_credit_card_payment = True
        self._order.save()

    def mark_photo_processing_complete(self):
        self._order.completed_photo_processing = True
        self._order.save()
