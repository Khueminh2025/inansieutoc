# core/management/commands/recover_site_assets.py

# from django.core.management.base import BaseCommand
# from core.models import SiteAsset
# from cloudinary.api import resource
# import cloudinary
# import cloudinary.uploader

# class Command(BaseCommand):
#     help = "Khôi phục URL ảnh từ Cloudinary theo key"

#     def handle(self, *args, **kwargs):
#         success = 0
#         fail = 0

#         for asset in SiteAsset.objects.all():
#             if asset.image and "res.cloudinary.com" in asset.image.url:
#                 self.stdout.write(f"Bỏ qua: {asset.key}")
#                 continue

#             # Đúng đường dẫn cloudinary đã sinh ra
#             public_id = f"sieutoc/banners/sieutoc/banners/{asset.key}"
#             try:
#                 result = resource(public_id, resource_type='image')
#                 asset.image = result["secure_url"]
#                 asset.save()
#                 self.stdout.write(self.style.SUCCESS(f"✅ Cập nhật: {asset.key}"))
#                 success += 1
#             except cloudinary.exceptions.NotFound:
#                 self.stdout.write(self.style.WARNING(f"❌ Không tìm thấy: {asset.key}"))
#                 fail += 1

#         self.stdout.write(self.style.SUCCESS(f"\n✅ Thành công: {success}, ❌ Thất bại: {fail}"))

from django.core.management.base import BaseCommand
from cloudinary.api import resources
from cloudinary.utils import cloudinary_url
from core.models import SiteAsset, ServiceCategory, Service
from slugify import slugify


class Command(BaseCommand):
    help = "Khôi phục dữ liệu từ Cloudinary dựa trên folder và key"

    def handle(self, *args, **options):
        folder_map = {
            "sieutoc/banners": SiteAsset,
            "sieutoc/category": ServiceCategory,
            "sieutoc/service": Service
        }

        for folder, model in folder_map.items():
            self.stdout.write(f"📂 Đang quét folder Cloudinary: {folder}")
            self.recover_from_folder(folder, model)

    def recover_from_folder(self, folder, model_class):
        # Lấy tài nguyên từ folder
        result = resources(type="upload", prefix=folder, max_results=100)

        for res in result.get("resources", []):
            public_id = res.get("public_id")  # vd: sieutoc/banners/banner-home
            secure_url = res.get("secure_url")

            # Lấy slug hoặc key từ public_id
            try:
                key_or_slug = public_id.split("/")[-1]
                key_or_slug = key_or_slug.replace(".jpg", "")  # optional
            except IndexError:
                continue

            if model_class == SiteAsset:
                obj, created = SiteAsset.objects.get_or_create(
                    key=key_or_slug,
                    defaults={"image": secure_url}
                )
            elif model_class == ServiceCategory:
                obj, created = ServiceCategory.objects.get_or_create(
                    slug=key_or_slug,
                    defaults={
                        "name": key_or_slug.replace("-", " ").title(),
                        "image": secure_url
                    }
                )
            elif model_class == Service:
                category = ServiceCategory.objects.first()  # gán đại danh mục
                obj, created = Service.objects.get_or_create(
                    slug=key_or_slug,
                    defaults={
                        "name": key_or_slug.replace("-", " ").title(),
                        "image": secure_url,
                        "price": 10000,
                        "category": category
                    }
                )

            if created:
                self.stdout.write(f"✅ Đã tạo: {model_class.__name__} -> {key_or_slug}")
            else:
                self.stdout.write(f"⚠️ Đã tồn tại: {model_class.__name__} -> {key_or_slug}")
