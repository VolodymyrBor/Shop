from decimal import Decimal
from typing import TypedDict, Dict, Iterator, NamedTuple

from django.conf import settings
from django.http import HttpRequest

from shop.models import Product


class ProductDict(TypedDict):
    quantity: int
    price: str


class CartItem(TypedDict):
    quantity: int
    price: Decimal
    product: Product
    total_price: Decimal


class Cart:

    def __init__(self, request: HttpRequest):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart: Dict[str, ProductDict] = cart

    def add(self, product: Product, quantity: int = 1, override_quantity=False):
        """
        Add new product to cart.
        :param product: product
        :param quantity:
        :param override_quantity: if true change exist quantity of the product
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = ProductDict(quantity=0, price=str(product.price))

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        """
        Save cart
        """
        self.session.modified = True

    def remove(self, product: Product):
        """
        Remove product from cart
        :param product:
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_price(self):
        """
        Computing total price of cart
        :return: total price
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Remove cart from session
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def __iter__(self) -> Iterator[CartItem]:
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart: dict = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        cart: Dict[str, CartItem]

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
