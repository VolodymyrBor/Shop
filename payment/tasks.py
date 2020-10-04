import os
from io import BytesIO

import weasyprint
from celery import task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from orders.models import Order


@task
def payment_completed(order_id):
    """
    Task to send e-email notification when an order is successfully created.
    :param order_id:
    """

    order = Order.objects.get(id=order_id)

    subject = f'My Shop - EE Invoice no. {order.id}'
    message = 'Please, find attached the invoice for you recent purchase.'
    email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [order.email])

    out = BytesIO()
    html = render_to_string('orders/order/pdf.html', {'order': order})
    stylesheet = weasyprint.CSS(os.path.join(settings.STATIC_ROOT, 'css/pdf.css'))
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=[stylesheet])

    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    email.send()
