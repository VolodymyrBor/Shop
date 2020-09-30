from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404

from .models import Category, Product
from cart.forms import CardAddProductForm


def product_list(request: HttpRequest, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
    }
    return render(request, 'shop/product/list.html', context)


def product_detail(request: HttpRequest, pid, slug):
    product = get_object_or_404(Product, id=pid, slug=slug, available=True)

    cart_product_form = CardAddProductForm()

    context = {
        'product': product,
        'cart_product_form': cart_product_form,
    }
    return render(request, 'shop/product/detail.html', context)
