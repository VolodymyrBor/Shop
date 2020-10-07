from typing import Iterable, List, Iterator, Union

import redis
from django.conf import settings

from .models import Product
from orders.models import OrderItem


r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD)


class Recommender:

    def products_bought(self, products: Iterable[Union[Product, OrderItem]]):
        products_ids = list(self._extract_product_id(products))
        for product_id in products_ids:
            for with_id in products_ids:
                if product_id != with_id:
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, products: Iterable[Union[Product, OrderItem]], max_result: int = 6) -> List[Product]:
        product_ids = list(self._extract_product_id(products))
        if len(product_ids) == 1:
            suggestions = r.zrange(self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_result]
        else:
            flat_ids = ''.join(map(str, product_ids))
            tmp_key = f'tmp_{flat_ids}'
            keys = [self.get_product_key(pid) for pid in product_ids]
            r.zunionstore(tmp_key, keys)
            r.zrem(tmp_key, *product_ids)
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_result]
            r.delete(tmp_key)
        suggestions_product_ids = list(map(int, suggestions))
        suggested_products = list(Product.objects.filter(pk__in=suggestions_product_ids))
        suggested_products.sort(key=lambda p: suggestions_product_ids.index(p.pk))
        return suggested_products

    def clear_purchases(self):
        for pid in Product.objects.values_list('pk', flat=True):
            r.delete(self.get_product_key(pid))

    @staticmethod
    def get_product_key(product_id):
        return f'product:{product_id}:purchased_with'

    @staticmethod
    def _extract_product_id(items: Iterable[Union[Product, OrderItem]]) -> Iterator[int]:
        for item in items:
            if isinstance(item, OrderItem):
                yield item.product.pk
            else:
                yield item.pk
