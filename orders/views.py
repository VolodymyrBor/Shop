import os

import weasyprint
from django.urls import reverse
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from .tasks import order_created
from .forms import OrderCreateForm
from .models import Order, OrderItem
from cart.cart import Cart


def order_create(request: HttpRequest):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order: Order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            cart.clear()

            order_created.delay(order.pk)
            request.session['order_id'] = order.pk
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()

    context = {
        'cart': cart,
        'form': form,
    }

    return render(request, 'orders/order/create.html', context)


@staff_member_required
def admin_order_detail(request: HttpRequest, order_id):
    order = get_object_or_404(Order, pk=order_id)

    context = {
        'order': order,
    }
    return render(request, 'admin/orders/order/detail.html', context)


@staff_member_required
def admin_order_pdf(request: HttpRequest, order_id):
    order: Order = get_object_or_404(Order, pk=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename={order.pk}.pdf'

    stylesheet = weasyprint.CSS(os.path.join(settings.STATIC_ROOT, 'css/pdf.css'))
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[stylesheet])
    return response
