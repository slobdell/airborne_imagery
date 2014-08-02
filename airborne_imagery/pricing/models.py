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
        json_str = json_str.replace("\'", '"').replace("\xe2\x80\x9c", '"').replace("\xe2\x80\x9d", '"')
        json_dict = json.loads(json_str)
        updated = False
        for dimension, price in json_dict.items():
            updated = updated or Pricing.get_or_create_from_dimensions(dimension).update_price(price)

        valid_dimensions = set(json_dict.keys())
        all_dimensions = set(_Pricing.objects.all().values_list('dimensions', flat=True))
        invalid_dimensions = list(all_dimensions - valid_dimensions)
        if invalid_dimensions:
            updated = True
            _Pricing.objects.filter(dimensions__in=invalid_dimensions).delete()
        return updated

    @classmethod
    def to_json_str(cls):
        json_dict = {}
        for _pricing in _Pricing.objects.all():
            json_dict[_pricing.dimensions] = _pricing.price
        return json.dumps(json_dict, indent=4)

    @classmethod
    def get_all(cls):
        _pricings = _Pricing.objects.all()
        pricings = [cls._wrap(_pricing) for _pricing in _pricings]
        pricings.sort(key=lambda p: p.total_pixels)
        return pricings

    @classmethod
    def get_by_ids(cls, pricing_ids):
        _pricings = _Pricing.objects.filter(id__in=pricing_ids)
        return [cls._wrap(_pricing) for _pricing in _pricings]

    @property
    def total_pixels(self):
        dimension_str = self.dimensions
        width__height = [int(item) for item in dimension_str.split('x')]
        return width__height[0] * width__height[1]

    @property
    def dimensions(self):
        return self._pricing.dimensions

    @property
    def price(self):
        return "%.2f" % self._pricing.price

    @property
    def id(self):
        return self._pricing.id
