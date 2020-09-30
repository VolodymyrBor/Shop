from typing import TypedDict

from django.http import HttpRequest
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404

from .cart import Cart, CartItem
from .forms import CardAddProductForm
from shop.models import Product


class CartItemDetail(CartItem):
    update_quantity_form: CardAddProductForm



@require_POST
def cart_add(request: HttpRequest, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CardAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product, quantity=cd['quantity'], override_quantity=cd['override'])
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request: HttpRequest, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request: HttpRequest):
    cart = Cart(request)

    for item in cart:
        item: CartItemDetail
        item['update_quantity_form'] = CardAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True,
        })

    context = {
        'cart': cart
    }
    return render(request, 'cart/detail.html', context)
