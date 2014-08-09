import random

from django.db import models


class _Coupon(models.Model):

    class Meta:
        app_label = 'coupons'
        db_table = 'coupons_coupon'

    code = models.CharField(max_length=50)
    expiration_date = models.DateTimeField(null=True)
    dollar_value = models.FloatField()
    percent_off = models.FloatField()  # value from 0..1
    reason_created = models.CharField(max_length=255)
    redeemed = models.BooleanField(default=False)


class Coupon(object):

    def __init__(self, _coupon):
        self._coupon = _coupon

    @classmethod
    def _wrap(cls, _coupon):
        return Coupon(_coupon)

    @classmethod
    def _generate_random_string(cls):
        # this string supports 10 million permutations
        random_chars = "".join([chr(random.randint(0, 25) + 65) for count in xrange(5)])
        while _Coupon.objects.filter(code=random_chars).exists():
            random_chars = "".join([chr(random.randint(0, 25) + 65) for count in xrange(5)])
        return random_chars

    @classmethod
    def create_dollar_value_with_reason(cls, dollar_value, reason_str):
        coupon_str = cls._generate_random_string()
        _coupon = _Coupon.objects.create(code=coupon_str,
                                         dollar_value=dollar_value,
                                         reason_created=reason_str,
                                         percent_off=0.0)
        return cls._wrap(_coupon)

    @classmethod
    def create_percent_off_with_reason(cls, percent_off, reason_str):
        if percent_off < 0.0 or percent_off > 1.0:
            raise ValueError("Invalid value for percent_off")
        coupon_str = cls._generate_random_string()
        _coupon = _Coupon.objects.create(code=coupon_str,
                                         dollar_value=0.0,
                                         reason_created=reason_str,
                                         percent_off=percent_off)
        return cls._wrap(_coupon)

    def is_valid(self):
        if self._coupon.dollar_value > 0:
            return True
        if self._coupon.percent_off > 0 and not self._coupon.redeemed:
            return True
        return False

    def get_amount_off(self, order_dollar_total):
        if not self.is_valid():
            return 0.0
        amount_off = self._coupon.dollar_value
        amount_off += (order_dollar_total - amount_off) * self._coupon.percent_off
        return amount_off

    def mark_redeemed(self):
        self._coupon.redeemed = True
        self._coupon.save()
