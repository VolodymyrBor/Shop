from django.urls import reverse
from django.http import HttpRequest
from django.shortcuts import render, redirect

from .tasks import order_created
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart


def order_create(request: HttpRequest):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order: Order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            cart.clear()

            order_created.delay(order.id)
            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()

    context = {
        'cart': cart,
        'form': form,
    }

    return render(request, 'orders/order/create.html', context)
