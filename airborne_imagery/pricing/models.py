import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class _Pricing(models.Model):

    class Meta:
        app_label = "pricing"
        db_table = "pricing_pricing"

    dimensions = models.CharField(max_length=50)
    price = models.FloatField(default=100.0)


class Pricing(object):

    def __init__(self, _pricing):
        self._pricing = _pricing

    @classmethod
    def _wrap(cls, _pricing):
        return Pricing(_pricing)

    @classmethod
    def get_or_create_from_dimensions(cls, dimension_string):
        try:
            _pricing = _Pricing.objects.get(dimensions=dimension_string)
        except ObjectDoesNotExist:
            _pricing = _Pricing.objects.create(dimensions=dimension_string)
        return cls._wrap(_pricing)

    def update_price(self, price):
        if price != self._pricing.price:
            self._pricing.price = price
            self._pricing.save()
            return True
        return False

    @classmethod
    def update_from_json(cls, json_str):
        json_dict = json.loads(json_str)
        updated = False
        for dimension, price in json_dict.items():
            updated = updated or Pricing.get_or_create_from_dimensions(dimension).update_price(price)
        return updated

    @classmethod
    def to_json_str(cls):
        json_dict = {}
        for _pricing in _Pricing.objects.all():
            json_dict[_pricing.dimensions] = _pricing.price
        return json.dumps(json_dict, indent=4)
