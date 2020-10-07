from operator import itemgetter

from django.http import HttpRequest
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404

from .cart import Cart, CartItem
from .forms import CardAddProductForm
from shop.models import Product
from shop.recommender import Recommender
from coupons.forms import CouponApplyForm


class CartItemDetail(CartItem):
    update_quantity_form: CardAddProductForm


@require_POST
def cart_add(request: HttpRequest, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    form = CardAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product, quantity=cd['quantity'], override_quantity=cd['override'])
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request: HttpRequest, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
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

    coupon_apply_form = CouponApplyForm()
    r = Recommender()
    recommended_products = r.suggest_products_for(item['product'] for item in cart)

    context = {
        'cart': cart,
        'coupon_apply_form': coupon_apply_form,
        'recommended_products': recommended_products,
    }
    return render(request, 'cart/detail.html', context)
