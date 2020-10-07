from django.conf import settings
from django.core.mail import send_mail

from .models import Order
from myShop.celery_shop import app


@app.task
def order_created(order_id: int):
    """
    Task to send an e-mail notification when order is successfully created.
    :param order_id: Order pk
    """
    order = Order.objects.get(pk=order_id)
    subject = f'Order nr. {order.pk}'
    message = f'Dear {order.first_name},\n\n' \
              f'You have successfully placed an order.' \
              f'Your order ID is {order.pk}'
    mail_sent = send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [order.email],
        auth_user=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD,
    )
    return mail_sent
