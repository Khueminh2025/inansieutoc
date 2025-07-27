from django.core.management.base import BaseCommand
from cloudinary.api import resources
from core.models import SiteAsset, Category, Service
from django.db import IntegrityError
from slugify import slugify


class Command(BaseCommand):
    help = "Khôi phục dữ liệu từ Cloudinary dựa trên folder và key"

    def handle(self, *args, **options):
        folder_map = {
            "sieutoc/banners/sieutoc/banners": SiteAsset,
            "sieutoc/category": Category,
            "sieutoc/service": Service
        }

        for folder, model in folder_map.items():
            self.stdout.write(self.style.NOTICE(f"\n📂 Đang quét folder Cloudinary: {folder}"))
            self.recover_from_folder(folder, model)

    def recover_from_folder(self, folder, model_class):
        prefix = folder if folder.endswith('/') else folder + '/'
        result = resources(type="upload", prefix=prefix, max_results=100)

        created_count = 0
        existed_count = 0
        failed_count = 0

        for res in result.get("resources", []):
            public_id = res.get("public_id")
            secure_url = res.get("secure_url")

            try:
                key_or_slug = public_id.split("/")[-1].replace(".jpg", "").lower()
            except IndexError:
                failed_count += 1
                continue

            try:
                if model_class == SiteAsset:
                    obj, created = SiteAsset.objects.get_or_create(
                        key=key_or_slug,
                        defaults={"image": secure_url}
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✅ SiteAsset mới: {key_or_slug}"))
                        created_count += 1
                    else:
                        self.stdout.write(f"⚠️ SiteAsset đã tồn tại: {key_or_slug}")
                        existed_count += 1

                elif model_class == Category:
                    obj, created = Category.objects.get_or_create(
                        slug=key_or_slug,
                        defaults={
                            "name": key_or_slug.replace("-", " ").title(),
                            "image": secure_url
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✅ Category mới: {key_or_slug}"))
                        created_count += 1
                    else:
                        self.stdout.write(f"⚠️ Category đã tồn tại: {key_or_slug}")
                        existed_count += 1

                elif model_class == Service:
                    category = Category.objects.first()
                    if not category:
                        self.stdout.write(self.style.ERROR(f"❌ Không có Category nào để gán cho Service: {key_or_slug}"))
                        failed_count += 1
                        continue

                    obj, created = Service.objects.get_or_create(
                        slug=key_or_slug,
                        defaults={
                            "name": key_or_slug.replace("-", " ").title(),
                            "image": secure_url,
                            "category": category
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✅ Service mới: {key_or_slug}"))
                        created_count += 1
                    else:
                        self.stdout.write(f"⚠️ Service đã tồn tại: {key_or_slug}")
                        existed_count += 1

            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"❌ IntegrityError ({key_or_slug}): {e}"))
                failed_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Lỗi không xác định ({key_or_slug}): {e}"))
                failed_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n📊 Tổng kết: {model_class.__name__} từ folder '{folder}'"))
        self.stdout.write(self.style.SUCCESS(f"✅ Tạo mới: {created_count}"))
        self.stdout.write(self.style.NOTICE(f"⚠️ Đã tồn tại: {existed_count}"))
        self.stdout.write(self.style.ERROR(f"❌ Thất bại: {failed_count}"))
