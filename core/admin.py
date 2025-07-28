from django.contrib import admin
from django.utils.html import format_html
import cloudinary.uploader
from django import forms
from django.utils.html import format_html

from .models import (
    Category,
    Service,
    ServiceOption,
    Shape,
    Size,
    Laminate,
    Material,
    Paper,SiteAsset,ServiceCategory,ServicePrice,
    Order,OrderItem
)
from core.slug_utils import unique_slugify
from core.utils.cloudinary_helpers import generate_unique_public_id

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'image_thumbnail',
        'name',
        'title',
        'description',
        'is_featured',        
    ]
    list_editable = ['is_featured']
    search_fields = ['name']
    list_filter = ['is_featured', 'category']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = [
        'image_thumbnail',
        'image_preview',
    ]
    fieldsets = (
        (None, {
            'fields': ('name', 'title','slug', 'description','category', 'is_featured', )
        }),
        ('Hình ảnh & Mô tả', {
            'fields': ('image', 'image_thumbnail', 'image_preview', )
        }),
    )

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" ' \
                'style="object-fit:cover;border-radius:6px;"/>',
                obj.image.url
            )
        return '-'
    image_thumbnail.short_description = 'Ảnh nhỏ'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px; ' \
                'border:1px solid #ddd; border-radius:4px; padding:2px;"/>',
                obj.image.url
            )
        return 'No image'
    image_preview.short_description = 'Ảnh preview'

    def save_model(self, request, obj, form, change):
        # Giữ nguyên logic slug
        if not obj.slug:
            obj.slug = unique_slugify(obj, obj.name)
        # Upload ảnh lên Cloudinary nếu thay đổi
        if 'image' in form.changed_data and obj.image:
            upload_result = cloudinary.uploader.upload(
                obj.image,
                public_id=generate_unique_public_id('sieutoc/service', obj.slug),
                folder='sieutoc/service',
                overwrite=True,
                resource_type='image'
            )
            obj.image = upload_result['secure_url']
        super().save_model(request, obj, form, change)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['image_thumbnail', 'name', 'show_on_homepage']
    search_fields = ['name']
    list_filter = ['show_on_homepage']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_thumbnail', 'image_preview']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'show_on_homepage')
        }),
        ('Hình ảnh', {
            'fields': ('image', 'image_thumbnail', 'image_preview')
        }),
    )

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" ' \
                'style="object-fit:cover;border-radius:6px;"/>',
                obj.image.url
            )
        return '-'
    image_thumbnail.short_description = 'Ảnh nhỏ'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px; ' \
                'border:1px solid #ddd; border-radius:4px; padding:2px;"/>',
                obj.image.url
            )
        return 'No image'
    image_preview.short_description = 'Ảnh preview'
    
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from core.slug_utils import unique_slugify
            obj.slug = unique_slugify(obj, obj.name)

        if 'image' in form.changed_data and obj.image:
            upload_result = cloudinary.uploader.upload(
                obj.image,
                public_id=generate_unique_public_id("sieutoc/category", obj.slug),
                folder="sieutoc/category",
                overwrite=True,
                resource_type="image"
            )
            obj.image = upload_result["secure_url"]

        super().save_model(request, obj, form, change)

@admin.register(ServiceOption)
class ServiceOptionAdmin(admin.ModelAdmin):
    list_display = ('service', 'paper', 'material', 'shape', 'size', 'laminate')
    list_filter = ('service', 'paper', 'material', 'shape', 'size', 'laminate')
    search_fields = ['service__name']

# Đăng ký các bảng phụ
admin.site.register(Shape)
admin.site.register(Size)
admin.site.register(Laminate)
admin.site.register(Material)
admin.site.register(Paper) 

@admin.register(ServicePrice)
class ServicePriceAdmin(admin.ModelAdmin):
    list_display = ('service', 'paper', 'material', 'shape', 'size', 'laminate', 'quantity', 'price')
    list_filter = ('service', 'paper', 'material', 'shape', 'size', 'laminate', 'quantity')
    search_fields = ('service__name',)

class SiteAssetForm(forms.ModelForm):
    class Meta:
        model = SiteAsset
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Lấy danh sách key
        static_keys = [('banner-home', 'Trang chủ'),('banner-home-mid', 'Trang chủ ở giữa')]
        dynamic_keys = [
            (f'banner-{cat.slug}', f'Banner - {cat.name}')
            for cat in ServiceCategory.objects.all()
        ]
        choices = static_keys + dynamic_keys

        # Nếu đang chỉnh sửa, thêm key hiện tại vào choices nếu chưa có
        if self.instance and self.instance.pk:
            current_key = self.instance.key
            if current_key not in [c[0] for c in choices]:
                choices.append((current_key, current_key))  # fallback

        self.fields['key'].widget = forms.Select(choices=choices)

        # Nếu đang chỉnh sửa thì disable field key để tránh đổi key
        if self.instance and self.instance.pk:
            self.fields['key'].disabled = True

    class Meta:
        model = SiteAsset
        fields = '__all__'

@admin.register(SiteAsset)
class SiteAssetAdmin(admin.ModelAdmin):
    form = SiteAssetForm
    list_display = ['key', 'image']
    search_fields = ['key', 'description']

    def save_model(self, request, obj, form, change):
        from slugify import slugify
        from cloudinary.uploader import upload

        if 'image' in form.changed_data and obj.image:
            folder = "sieutoc/banners"
            public_id = f"{folder}/{slugify(obj.key)}"

            upload_result = upload(
                obj.image,
                public_id=public_id,
                folder=folder,
                overwrite=True,
                resource_type="image"
            )
            obj.image = upload_result["secure_url"]

        super().save_model(request, obj, form, change)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('shape', 'size', 'paper_type', 'material', 'laminate', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_code', 'customer_name', 'phone', 'item_count','status', 'total_price']
    list_filter = ('status',)
    list_editable = ['status']
    search_fields = ('order_code', 'customer_name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('order_code', 'created_at')
    inlines = [OrderItemInline]
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "SL Sản phẩm"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_info', 'quantity', 'price')
    search_fields = ('order__order_code',)
    def order_info(self, obj):
            return f"Đơn hàng {obj.order.order_code}"
    order_info.short_description = "Đơn hàng"

