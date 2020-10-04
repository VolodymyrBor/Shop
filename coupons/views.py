from django.utils import timezone
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Coupon
from .forms import CouponApplyForm


@require_POST
def coupon_apply(request: HttpRequest):
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True)
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    return redirect('cart:cart_detail')
