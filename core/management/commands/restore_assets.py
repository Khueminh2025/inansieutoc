from django.core.management.base import BaseCommand
from cloudinary.api import resources, resource
from core.models import (
    SiteAsset, Category, Service, Shape, Size,
    Material, Paper, Laminate, ServiceOption, ServiceCategory
)
from django.db import IntegrityError
from slugify import slugify


def get_expected_banner_keys():
    static_keys = ['banner-home', 'banner-home-mid']
    dynamic_keys = [
        f'banner-{cat.slug}'
        for cat in ServiceCategory.objects.all()
    ]
    return static_keys + dynamic_keys


class Command(BaseCommand):
    help = "Khôi phục hình ảnh cho tất cả các model từ Cloudinary"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("🔁 Bắt đầu khôi phục dữ liệu từ Cloudinary..."))

        self.restore_site_assets_from_cloudinary()

        model_configs = [
            (Category, "slug", "sieutoc/category"),
            (Service, "slug", "sieutoc/service"),
            (Shape, "slug", "sieutoc/shape"),
            (Size, "slug", "sieutoc/size"),
            (Material, "slug", "sieutoc/material"),
            (Paper, "slug", "sieutoc/paper"),
            (Laminate, "slug", "sieutoc/laminate"),
            # (ServiceOption, "slug", "sieutoc/service-option"),
        ]

        for model, field, folder in model_configs:
            self.recover_images(model, field, folder)

    def restore_site_assets_from_cloudinary(self):
        self.stdout.write(self.style.NOTICE("\n📂 Đang quét folder Cloudinary: sieutoc/banners"))
        created = updated = skipped = failed = 0

        for key in get_expected_banner_keys():
            slug = slugify(key)
            public_id = f"sieutoc/banners/sieutoc/banners/{slug}"

            try:
                res = resource(public_id)
                image_url = res["secure_url"]
            except Exception:
                self.stdout.write(self.style.ERROR(f"🚫 Không tìm thấy SiteAsset với key: {key}"))
                failed += 1
                continue

            obj, created_obj = SiteAsset.objects.get_or_create(
                key=key,
                defaults={"slug": slug, "image": image_url}
            )

            if created_obj:
                self.stdout.write(self.style.SUCCESS(f"✅ Tạo mới: {key}"))
                created += 1
            else:
                if not obj.image:
                    obj.image = image_url
                    obj.save()
                    self.stdout.write(self.style.SUCCESS(f"🔁 Cập nhật ảnh cho: {key}"))
                    updated += 1
                else:
                    self.stdout.write(f"⚠️ Đã có ảnh: {key}")
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(f"\n📊 Tổng kết: SiteAsset từ folder 'sieutoc/banners'"))
        self.stdout.write(f"✅ Tạo mới: {created}")
        self.stdout.write(f"🔁 Cập nhật: {updated}")
        self.stdout.write(f"⚠️ Đã có ảnh: {skipped}")
        self.stdout.write(f"❌ Thất bại: {failed}")

    def recover_images(self, model, field_name, folder):
        from cloudinary.api import resources

        self.stdout.write(self.style.NOTICE(f"\n📂 Đang quét folder Cloudinary: {folder}"))

        try:
            result = resources(type="upload", prefix=folder + "/", max_results=100)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Không thể truy cập folder {folder}: {e}"))
            return

        created = updated = skipped = failed = 0
        existing_objs = {getattr(obj, field_name): obj for obj in model.objects.all()}

        for res in result.get("resources", []):
            public_id = res.get("public_id", "")
            secure_url = res.get("secure_url", "")

            slug = public_id.split("/")[-1].replace(".jpg", "").replace(".png", "").lower()

            if slug not in existing_objs:
                self.stdout.write(self.style.WARNING(f"🚫 Bỏ qua file không khớp slug DB: {slug}"))
                continue

            obj = existing_objs[slug]

            if not obj.image:
                obj.image = secure_url
                try:
                    obj.save()
                    self.stdout.write(self.style.SUCCESS(f"✅ Cập nhật ảnh cho {model.__name__}: {slug}"))
                    updated += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Lỗi khi lưu {model.__name__} ({slug}): {e}"))
                    failed += 1
            else:
                skipped += 1
                self.stdout.write(f"⚠️ Đã có ảnh: {slug}")

        self.stdout.write(self.style.SUCCESS(f"\n📊 Tổng kết: {model.__name__} từ folder '{folder}'"))
        self.stdout.write(f"✅ Cập nhật: {updated}")
        self.stdout.write(f"⚠️ Đã có ảnh: {skipped}")
        self.stdout.write(f"❌ Thất bại: {failed}")
        self.stdout.write(f"🚫 Bỏ qua: {len(result.get('resources', [])) - updated - skipped - failed}")
