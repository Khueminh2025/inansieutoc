from django.shortcuts import render, get_object_or_404,redirect
from .models import ServiceCategory, Service, Order
from .forms import OrderForm
from django.contrib import messages
from django.http import HttpResponse
from core.asset_utils import get_asset_url
from core.models import Service, Shape, Size, Laminate, Material, ServiceOption, Paper,ServicePrice
from django.db.models import Q

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
    options = ServiceOption.objects.filter(service=service)

    # Lọc ra các tùy chọn thực sự tồn tại
    shapes = Shape.objects.filter(id__in=options.values_list('shape_id', flat=True).distinct(), name__isnull=False)
    sizes = Size.objects.filter(id__in=options.values_list('size_id', flat=True).distinct(), name__isnull=False)
    laminates = Laminate.objects.filter(id__in=options.values_list('laminate_id', flat=True).distinct(), name__isnull=False)
    papers = Paper.objects.filter(id__in=options.values_list('paper_id', flat=True).distinct(), name__isnull=False)
    materials = Material.objects.filter(id__in=options.values_list('material_id', flat=True).distinct(), name__isnull=False)

    return render(request, "core/service_detail.html", {
        "service": service,
        "shapes": shapes,
        "sizes": sizes,
        "laminates": laminates,
        "papers": papers,
        "materials": materials,
    })
    
def order_payment(request, order_code):
    order = get_object_or_404(Order, order_code=order_code)

    # Chuỗi nội dung chuyển khoản
    transfer_note = f"{order.order_code}-{order.phone}"

    return render(request, 'core/order_payment.html', {
        'order': order,
        'transfer_note': transfer_note,
        # đường dẫn tĩnh đến QR ngân hàng
        'bank_qr_path': 'images/qr-bank.png',
    })

def order_verify(request):
    order = None
    code = request.GET.get('code')
    phone = request.GET.get('phone')

    if code and phone:
        try:
            order = Order.objects.get(order_code=code, phone=phone)
        except Order.DoesNotExist:
            order = None

    return render(request, 'core/order_verify.html', {'order': order})
def home(request):
    categories = ServiceCategory.objects.all()
    featured_services = Service.objects.filter(is_featured=True)[:6]
    banner_url = get_asset_url("banner-home")
    banner_mid_url = get_asset_url("banner-home-mid")

    return render(request, 'core/home.html', {
        'categories': categories,
        'featured_services': featured_services,
        'banner_url': banner_url,
        'banner_mid_url': banner_mid_url
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

# core/views.py (thêm vào cuối file)
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Order,OrderItem, Service  # Service nếu có
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_order(request, service_id):
    if request.method == 'POST':
        try:
            # 1. Tạo đơn hàng (chỉ lưu thông tin KH + tổng tiền)
            order = Order.objects.create(
                customer_name=request.POST.get('name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                delivery_method=request.POST.get('shipping'),
                address_city=request.POST.get('city'),
                address_district=request.POST.get('district'),
                address_detail=request.POST.get('address'),
                total_price=int(request.POST.get('total_price')),
                receive_time='Lấy ngay',  # có thể tùy chỉnh
            )

            # 2. Tạo dòng chi tiết đơn hàng
            OrderItem.objects.create(
                order=order,
                service_id=service_id,
                shape=request.POST.get('shape'),
                size=request.POST.get('size'),
                paper_type=request.POST.get('paper'),
                material=request.POST.get('material'),
                laminate=request.POST.get('laminate'),
                quantity=int(request.POST.get('quantity')),
                price=int(request.POST.get('total_price')),
            )

            return JsonResponse({
                'success': True,
                'redirect_url': f'/thanh-toan/{order.order_code}/'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Yêu cầu không hợp lệ'})

def checkout(request, order_code):
    order = get_object_or_404(Order, order_code=order_code)
    return render(request, 'core/checkout.html', {'order': order})
