from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dich-vu/', views.service_categories, name='service_categories'),
    path('dich-vu/<slug:slug>/', views.service_list, name='service_list'),
    path('san-pham/<slug:slug>/', views.service_detail, name='service_detail'),
    path('thanh-toan/<order_code>/', views.order_payment, name='order_payment'),
    path('tra-cuu-don/', views.order_verify, name='order_verify'),
    # path('dat-hang/', views.order_create_view, name='order_create'),
    path('order/new/', views.order_create_view, name='order_form'),
    path('order/payment/<str:order_code>/', views.order_payment, name='order_payment'),
    path('dat-hang/', views.order_create_ajax, name='order_create_ajax'),
    path('orders/create/<int:service_id>/', views.order_create_ajax, name='order_create_ajax'),
    path('thanh-toan/<str:order_code>/', views.order_payment, name='order_payment'),
]
