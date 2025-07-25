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

# def service_detail(request, slug):
#     service = get_object_or_404(Service, slug=slug)
#     form = OrderForm()

#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             order = form.save(commit=False)
#             order.service = service
#             order.total_price = service.price * order.quantity
#             order.save()
#             return redirect('order_payment', order_code=order.order_code)

#     return render(request, 'core/service_detail.html', {
#         'service': service,
#         'form': form
#     })
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
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Service, ServicePrice, Order

@csrf_exempt
def order_create_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        # --- 1. Lấy service từ slug ---
        service_slug = request.POST.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)

        # --- 2. Lấy lựa chọn của khách ---
        opts = {
            'paper_id':    request.POST.get('paper'),
            'size_id':     request.POST.get('size'),
            'shape_id':    request.POST.get('shape'),
            'laminate_id': request.POST.get('laminate'),
            'material_id': request.POST.get('material'),
        }
        quantity = int(request.POST.get('quantity', 1))

        # --- 3. Tìm giá ---
        price_obj = ServicePrice.objects.filter(service=service, **opts).first()
        if not price_obj:
            return JsonResponse({'error': 'Không tìm thấy giá phù hợp.'}, status=400)
        total_price = price_obj.price * quantity

        # --- 4. Lấy thông tin liên hệ ---
        name    = request.POST.get('name', '').strip()
        phone   = request.POST.get('phone', '').strip()
        email   = request.POST.get('email', '').strip()
        notes   = request.POST.get('notes', '')
        shipping = request.POST.get('shipping', 'pickup')  # 'delivery' hoặc 'pickup'

        # --- 5. Lấy địa chỉ nếu có giao hàng ---
        city     = request.POST.get('city', '')
        district = request.POST.get('district', '')
        address  = request.POST.get('address', '')

        # --- 6. Tạo đơn hàng ---
        order = Order.objects.create(
            service       = service,
            paper_id      = opts['paper_id'],
            size_id       = opts['size_id'],
            shape_id      = opts['shape_id'],
            laminate_id   = opts['laminate_id'],
            material_id   = opts['material_id'],
            quantity      = quantity,
            total_price   = total_price,
            customer_name = name,
            phone         = phone,
            email         = email,
            notes         = notes,
            shipping      = shipping,
            city          = city,
            district      = district,
            address_detail= address,
            # order_code, status, etc nếu bạn có default
        )

        # --- 7. Trả về redirect URL ---
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('order_payment', args=[order.order_code])
        })

    except Exception as e:
        return JsonResponse({'error': f'Lỗi hệ thống: {str(e)}'}, status=500)
