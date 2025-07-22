# myapp/management/commands/import_services.py

import csv
from django.core.management.base import BaseCommand
from core.models import ServiceCategory, Service, PrintMaterial, PrintOption
from core.slug_utils import unique_slugify


class Command(BaseCommand):
    help = 'Import dữ liệu dịch vụ và in nhanh màu từ CSV, tự tạo slug không trùng'

    def handle(self, *args, **kwargs):
        # ==== Import ServiceCategory và Service ====
        try:
            with open('data/du-lieu-cty-in-Sieu-Toc1.csv', newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    category_name = row['category'].strip()

                    category, created = ServiceCategory.objects.get_or_create(name=category_name)
                    if created or not category.slug:
                        category.slug = unique_slugify(category, category_name)
                        category.save()

                    service_name = row['name'].strip()
                    service = Service(
                        category=category,
                        name=service_name,
                        unit=row['unit'].strip(),
                        price=int(row['price'])
                    )
                    service.slug = unique_slugify(service, service_name)
                    service.save()

                    self.stdout.write(self.style.SUCCESS(f"✔ Tạo Service: {service.name}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Lỗi khi import Service: {str(e)}"))

        # ==== Import PrintMaterial và PrintOption ====
        try:
            with open('data/in-nhanh-mau1.csv', newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    material_name = row['material'].strip()
                    material, _ = PrintMaterial.objects.get_or_create(name=material_name)

                    PrintOption.objects.create(
                        material=material,
                        size=row['size'].strip(),
                        price=int(row['price'])
                    )

                    self.stdout.write(self.style.SUCCESS(f"✔ Tạo PrintOption: {material.name} - {row['size']}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Lỗi khi import PrintOption: {str(e)}"))
