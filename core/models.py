from django.db import models
from cloudinary.models import CloudinaryField
from core.slug_utils import unique_slugify
from core.utils.cloudinary_helpers import generate_unique_public_id
import uuid


def get_banner_key_choices():
    static_keys = [('banner-home', 'Trang chủ')]
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
        if not self.slug and self.name:
            self.slug = unique_slugify(self, self.name)
        # if self.image and not getattr(self.image, 'public_id', None):
        #     self.image.public_id = generate_unique_public_id("sieutoc/category", self.slug)
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
        if not self.slug and self.name:
            self.slug = unique_slugify(self, self.name)
        # if self.image and not getattr(self.image, 'public_id', None):
        #     self.image.public_id = generate_unique_public_id("sieutoc/service", self.slug)
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
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    notes = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"



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