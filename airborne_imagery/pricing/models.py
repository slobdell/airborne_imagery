import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class _Pricing(models.Model):

    class Meta:
        app_label = "pricing"
        db_table = "pricing_pricing"

    dimensions = models.CharField(max_length=50)
    price = models.FloatField(default=100.0)
    event_id = models.IntegerField(null=True)


class Pricing(object):

    def __init__(self, _pricing):
        self._pricing = _pricing

    @classmethod
    def _wrap(cls, _pricing):
        return Pricing(_pricing)

    @classmethod
    def get_or_create_from_dimensions_and_event_id(cls, dimension_string, event_id):
        try:
            _pricing = _Pricing.objects.get(dimensions=dimension_string, event_id=event_id)
        except ObjectDoesNotExist:
            _pricing = _Pricing.objects.create(dimensions=dimension_string, event_id=event_id)
        return cls._wrap(_pricing)

    def update_price(self, price):
        if price != self._pricing.price:
            self._pricing.price = price
            self._pricing.save()
            return True
        return False

    @classmethod
    def update_from_json(cls, json_str, event):
        '''
        An event of None denotes the default price
        '''
        json_str = json_str.replace("\'", '"').replace("\xe2\x80\x9c", '"').replace("\xe2\x80\x9d", '"')
        json_dict = json.loads(json_str)
        updated = False
        event_id = event.id if event is not None else None
        for dimension, price in json_dict.items():
            updated_single_price = Pricing.get_or_create_from_dimensions_and_event_id(dimension, event_id).update_price(price)
            updated = updated or updated_single_price

        valid_dimensions = set(json_dict.keys())
        all_dimensions = set(_Pricing.objects.filter(event_id=event_id).values_list('dimensions', flat=True))
        invalid_dimensions = list(all_dimensions - valid_dimensions)
        if invalid_dimensions:
            updated = True
            _Pricing.objects.filter(event_id=event_id, dimensions__in=invalid_dimensions).delete()
        return updated

    @classmethod
    def to_json_str_for_event_id(cls, event_id):
        json_dict = {}
        for _pricing in _Pricing.objects.filter(event_id=event_id):
            json_dict[_pricing.dimensions] = _pricing.price
        return json.dumps(json_dict, indent=4)

    @classmethod
    def get_for_event_id(cls, event_id):
        _pricings = _Pricing.objects.filter(event_id=event_id)
        if not _pricings:
            _pricings = _Pricing.objects.filter(event_id=None)
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
