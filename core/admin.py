from django.contrib import admin
from .models import *
from django import forms

import cloudinary.uploader
from core.utils.cloudinary_helpers import generate_unique_public_id
from django.utils.html import format_html

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_code', 'customer_name', 'phone', 'status', 'created_at']
    list_editable = ['status']  # ✅ Cho phép chỉnh trực tiếp
    list_filter = ['status', 'created_at']
    search_fields = ['order_code', 'customer_name', 'phone']
    readonly_fields = ['order_code', 'total_price', 'created_at']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['image_thumbnail','name', 'unit', 'price', 'is_featured']
    list_editable = ['is_featured']
    search_fields = ['name']
    list_filter = ['is_featured', 'category']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_thumbnail']
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:6px;">', obj.image.url)
        return "-"
    image_thumbnail.short_description = "Hình ảnh"

    def save_model(self, request, obj, form, change):
        # Nếu slug chưa có → tạo từ tên
        if not obj.slug:
            from core.slug_utils import unique_slugify  # hoặc chỗ bạn định nghĩa
            obj.slug = unique_slugify(obj, obj.name)

        if 'image' in form.changed_data and obj.image:
            # Upload ảnh lên Cloudinary với public_id dựa trên slug
            upload_result = cloudinary.uploader.upload(
                obj.image,
                public_id=generate_unique_public_id("sieutoc/service", obj.slug),
                folder="sieutoc/service",
                overwrite=True,
                resource_type="image"
            )
            # Gán lại image = public_id
            obj.image = upload_result["secure_url"]

        super().save_model(request, obj, form, change)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['image_thumbnail','name','show_on_homepage']
    readonly_fields = ['image_thumbnail']
    list_editable = ['show_on_homepage']
    prepopulated_fields = {'slug': ('name',)}
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:6px;">', obj.image.url)
        return "-"
    image_thumbnail.short_description = "Hình ảnh"

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

# admin.site.register(ServiceCategory)
# admin.site.register(Service)
admin.site.register(PrintMaterial)
admin.site.register(PrintOption)
# admin.site.register(Order)

class SiteAssetForm(forms.ModelForm):
    class Meta:
        model = SiteAsset
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Lấy danh sách key
        static_keys = [('banner_home', 'Trang chủ')]
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