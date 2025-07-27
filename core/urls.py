from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Dịch vụ
    path('dich-vu/', views.service_categories, name='service_categories'),
    path('dich-vu/<slug:slug>/', views.service_list, name='service_list'),
    path('san-pham/<slug:slug>/', views.service_detail, name='service_detail'),

    # Đơn hàng
    path('orders/create/<int:service_id>/', views.create_order, name='create_order'),   # ✅ AJAX gửi POST về đây
    path('thanh-toan/<str:order_code>/', views.checkout, name='checkout'),             # ✅ Trang hiển thị đơn đã tạo

    # Nếu có hỗ trợ tra cứu đơn bằng mã code
    path('tra-cuu-don/', views.order_verify, name='order_verify'),

    # Nếu bạn dùng order_code (chuỗi mã đơn)
    # path('thanh-toan/<str:order_code>/', views.order_payment, name='order_payment'),

    # Nếu bạn có thêm form tạo đơn bằng tay
    # path('order/new/', views.order_create_view, name='order_form'),

    # ❌ Bỏ dòng này vì không có view `order_create_ajax`
    # path('dat-hang/', views.order_create_ajax, name='order_create_ajax'),
]
