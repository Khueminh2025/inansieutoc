from django.db import models
from cloudinary.models import CloudinaryField
from django.utils.timezone import now
from django.db.models import Count
import uuid
from core.slug_utils import unique_slugify 
from core.utils.cloudinary_helpers import generate_unique_public_id

def get_banner_key_choices():
    static_keys = [('banner-home', 'Trang chủ')]
    dynamic_keys = [
        (f'banner-{cat.slug}', f'Banner - {cat.name}')
        for cat in ServiceCategory.objects.all()
    ]
    return static_keys + dynamic_keys

class SiteAsset(models.Model):
    key = models.CharField(max_length=100, unique=True, )
    image = CloudinaryField('image', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.key


# ==== CATEGORY ====
class ServiceCategory(models.Model):
    name = models.CharField("Tên Dịch Vụ",max_length=255)
    slug = models.SlugField(unique=True,null=True, blank=True)
    image = CloudinaryField('Hình Ảnh', blank=True, null=True, folder='sieutoc/category/')
    show_on_homepage = models.BooleanField(default=False, verbose_name="Hiển thị ở trang chủ")
    def save(self, *args, **kwargs):
        if not self.slug:
             self.slug = unique_slugify(self, self.name)
        # if self.image and not getattr(self.image, 'public_id', None):
        #     self.image.public_id = generate_unique_public_id("sieutoc/category", self.slug)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Dịch vụ"
        verbose_name_plural = "Các dịch vụ"

# ==== SERVICE ====
class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,null=True, blank=True)
    unit = models.CharField(max_length=50)  # A4, A3,...
    price = models.PositiveIntegerField()
    image = CloudinaryField('image', blank=True, null=True, folder='sieutoc/service/')
    is_featured = models.BooleanField("Phổ biến", default=False)
    def save(self, *args, **kwargs):
        if not self.slug:
             self.slug = unique_slugify(self, self.name)
        # if self.image and not getattr(self.image, 'public_id', None):
        #     self.image.public_id = generate_unique_public_id("sieutoc/service", self.slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.unit}"
    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Các sản phẩm"
    

# ==== PRINTING OPTIONS (for in nhanh màu) ====
class PrintMaterial(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class PrintOption(models.Model):
    material = models.ForeignKey(PrintMaterial, on_delete=models.CASCADE, related_name='options')
    size = models.CharField(max_length=50)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.material.name} - {self.size}"

# ==== ORDER ====
ORDER_STATUS = [
    ('pending', 'Chưa thanh toán'),
    ('paid', 'Đã thanh toán'),
    ('processing', 'Đang tiến hành'),
    ('completed', 'Đã hoàn thành'),
]

def generate_order_code():
    today_str = now().strftime('%Y%m%d')
    count_today = Order.objects.filter(created_at__date=now().date()).count() + 1
    return f"{today_str}-{count_today}"

class Order(models.Model):
    order_code = models.CharField(max_length=20, default=generate_order_code, unique=True)
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    # Có thể đặt 1 trong 2 kiểu dịch vụ
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    print_option = models.ForeignKey(PrintOption, on_delete=models.SET_NULL, null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    

    def save(self, *args, **kwargs):
        if not self.total_price:
            price = 0
            if self.service:
                price = self.service.price
            elif self.print_option:
                price = self.print_option.price
            self.total_price = price * self.quantity
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.order_code} - {self.customer_name}"
    class Meta:
        verbose_name = "Đơn Hàng"
        verbose_name_plural = "Các đơn hàng"

