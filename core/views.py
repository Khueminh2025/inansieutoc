from django.shortcuts import render, get_object_or_404,redirect
from .models import ServiceCategory, Service, Order
from .forms import OrderForm
from django.contrib import messages
from django.http import HttpResponse
from core.asset_utils import get_asset_url

def service_categories(request):
    categories = ServiceCategory.objects.all()
    
    return render(request, 'core/service_categories.html', {'categories': categories})

def service_list(request, slug):
    category = get_object_or_404(ServiceCategory, slug=slug)
    banner_url = get_asset_url(f"banner-{category.slug}")
    services = category.services.all()
    return render(request, 'core/service_list.html', {'category': category, 'services': services,'banner_url':banner_url})

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    form = OrderForm()

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.service = service
            order.total_price = service.price * order.quantity
            order.save()
            return redirect('order_payment', order_code=order.order_code)

    return render(request, 'core/service_detail.html', {
        'service': service,
        'form': form
    })

def order_payment(request, order_code):
    order = get_object_or_404(Order, order_code=order_code)
    return render(request, 'core/order_payment.html', {'order': order})

def order_verify(request):
    code = request.GET.get("code")
    phone = request.GET.get("phone")
    order = None

    if code and phone:
        order = Order.objects.filter(order_code=code, phone=phone).first()

    return render(request, 'core/order_verify.html', {
        'order': order,
        'code': code,
        'phone': phone,
    })
def home(request):
    categories = ServiceCategory.objects.all()
    featured_services = Service.objects.filter(is_featured=True)[:6]
    banner_url = get_asset_url("home-banner")

    return render(request, 'core/home.html', {
        'categories': categories,
        'featured_services': featured_services,
        'banner_url': banner_url,
    })

def order_create_view(request):
    slug = request.POST.get('service_slug') or request.GET.get('service_slug')
    service = get_object_or_404(Service, slug=slug)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.service = service
            order.total_price = service.price * order.quantity
            order.save()
            return redirect('order_payment', order_code=order.order_code)
    else:
        form = OrderForm()

    return render(request, 'core/order_form.html', {
        'form': form,
        'service': service,
    })