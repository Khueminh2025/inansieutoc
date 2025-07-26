from django.db import models
from cloudinary.models import CloudinaryField
from core.slug_utils import unique_slugify
from core.utils.cloudinary_helpers import generate_unique_public_id
import uuid
from django.utils import timezone


def get_banner_key_choices():
    static_keys = [('banner-home', 'Trang chủ'),('banner-home-mid', 'Trang chủ ờ giữa')]
    dynamic_keys = [
        (f'banner-{cat.slug}', f'Banner - {cat.name}')
        for cat in ServiceCategory.objects.all()
    ]
    return static_keys + dynamic_keys

class SiteAsset(models.Model):
    key = models.CharField(max_length=100, unique=True,null=True, blank=True,  help_text="Khóa để phân biệt asset (ví dụ 'logo-header')")
    image = CloudinaryField('image', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.key



def generate_order_code():
    today_str = now().strftime('%Y%m%d')
    count_today = Order.objects.filter(created_at__date=now().date()).count() + 1
    return f"{today_str}-{count_today}"

# Alias for backward compatibility
ServiceCategory = None  # deprecated, use Category instead

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    image = CloudinaryField('Hình Ảnh', blank=True, null=True, folder='sieutoc/category/')
    show_on_homepage = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục dịch vụ"

    def save(self, *args, **kwargs):
        from core.utils.cloudinary_helpers import upload_image_to_cloudinary

        if not self.slug and self.name:
            self.slug = unique_slugify(self, self.name)

        if self.image and not getattr(self.image, 'public_id', None):
            uploaded_url = upload_image_to_cloudinary(
             self.image, "sieutoc/category", self.slug
        )
        self.image = uploaded_url

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Assign alias after class definition
ServiceCategory = Category

class Shape(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Hình dạng"
        verbose_name_plural = "Các hình dạng"

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Kích thước"
        verbose_name_plural = "Các kích thước"

    def __str__(self):
        return self.name

class Laminate(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Cán màng"
        verbose_name_plural = "Các loại cán màng"

    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Chất liệu"
        verbose_name_plural = "Các chất liệu"

    def __str__(self):
        return self.name

class Paper(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Giấy"
        verbose_name_plural = "Các loại giấy"

    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services',verbose_name="Danh mục")
    name = models.CharField("Tên dịch vụ", max_length=255)
    slug = models.SlugField("Slug", unique=True, null=True, blank=True)
    title = models.CharField("Tiêu đề", max_length=255, blank=True, null=True)
    description = models.TextField("Mô tả", blank=True, null=True)
    image = CloudinaryField('Hình Ảnh', blank=True, null=True, folder='sieutoc/service/')
    is_featured = models.BooleanField("Phổ biến", default=False)

    class Meta:
        verbose_name = "Dịch vụ"
        verbose_name_plural = "Các dịch vụ"

    def save(self, *args, **kwargs):
        from core.utils.cloudinary_helpers import upload_image_to_cloudinary

        if not self.slug and self.name:
            self.slug = unique_slugify(self, self.name)

        if self.image and not getattr(self.image, 'public_id', None):
            uploaded_url = upload_image_to_cloudinary(
                self.image, "sieutoc/service", self.slug
            )
            self.image = uploaded_url

        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

class ServiceOption(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="Dịch vụ"
    )
    paper = models.ForeignKey(
        Paper,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Giấy"
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Chất liệu"
    )
    shape = models.ForeignKey(
        Shape,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Hình dạng"
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Kích thước"
    )
    laminate = models.ForeignKey(
        Laminate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cán màng"
    )

    class Meta:
        verbose_name = "Tùy chọn dịch vụ"
        verbose_name_plural = "Các tùy chọn dịch vụ"

    def __str__(self):
        parts = [self.service.name]
        if self.paper:
            parts.append(self.paper.name)
        if self.material:
            parts.append(self.material.name)
        if self.shape:
            parts.append(self.shape.name)
        if self.size:
            parts.append(self.size.name)
        if self.laminate:
            parts.append(self.laminate.name)
        return " - ".join(parts)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('canceled', 'Đã hủy'),
        ('printing', 'Đang tiến hành'),
        ('printed', 'Đã hoàn thành'),
    ]
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    address_city = models.CharField(max_length=100, blank=True, null=True)
    address_district = models.CharField(max_length=100, blank=True, null=True)
    address_detail = models.TextField(blank=True, null=True)

    delivery_method = models.CharField(max_length=50)
    receive_time = models.CharField(max_length=50, default='Lấy ngay')
    total_price = models.PositiveIntegerField(default=0)

    order_code = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, default='pending', choices=STATUS_CHOICES )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_code:
            today_str = timezone.now().strftime("%y%m%d")
            count_today = Order.objects.filter(order_code__startswith=today_str).count() + 1
            self.order_code = f"{today_str}-{count_today}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    shape = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    paper_type = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=50, blank=True)
    laminate = models.CharField(max_length=50, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.order.order_code} - {self.service.name if self.service else 'Sản phẩm'}"


class ServicePrice(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Dịch vụ")
    paper = models.ForeignKey(Paper, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Loại giấy")
    size = models.ForeignKey(Size, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Kích thước")
    shape = models.ForeignKey(Shape, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Hình dạng")
    laminate = models.ForeignKey(Laminate, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Cán màng")
    material = models.ForeignKey(Material, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Chất liệu")
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá (VND)")

    class Meta:
        verbose_name = "Bảng giá dịch vụ"
        verbose_name_plural = "Bảng giá dịch vụ"
        unique_together = ("service", "paper", "size", "laminate", "material", "quantity")

    def __str__(self):
        return f"{self.service.name} | {self.paper} | {self.size} | {self.laminate} | {self.material} | {self.quantity} | {self.price} VND"
    

    