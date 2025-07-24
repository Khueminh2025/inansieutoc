import csv
import os
from django.core.management.base import BaseCommand
from core.models import (
    Category, Shape, Size, Laminate,
    Material, Paper, Service, ServiceOption
)

class Command(BaseCommand):
    help = 'Import initial print data from CSV files'

    def handle(self, *args, **options):
        base_dir = os.path.join(os.getcwd(), 'dataprint_extracted')

        # 1. Import Categories
        with open(os.path.join(base_dir, 'categories.csv'), encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Category.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'].strip(),
                        'show_on_homepage': bool(row.get('show_on_homepage') in ['1', 'True', 'true']),
                    }
                )
        self.stdout.write(self.style.SUCCESS('✔ Đã import Categories'))

        # 2. Import Shapes, Sizes, Laminates, Materials, Papers
        for model, fname in [
            (Shape, 'shape.csv'),
            (Size, 'size.csv'),
            (Laminate, 'laminate.csv'),
            (Material, 'material.csv'),
            (Paper, 'paper.csv'),
        ]:
            with open(os.path.join(base_dir, fname), encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    model.objects.update_or_create(
                        id=int(row['id']),
                        defaults={'name': row['name'].strip()}
                    )
            self.stdout.write(self.style.SUCCESS(f'✔ Đã import {model.__name__}'))

        # 3. Import Services
        with open(os.path.join(base_dir, 'services.csv'), encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cat_ids = [int(i) for i in row['category_ids'].split(',') if i]
                cat = Category.objects.filter(id__in=cat_ids).first() if cat_ids else None
                Service.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'].strip(),
                        'title': row['title'].strip() or None,
                        'description': row['description'].strip() or None,
                        'is_featured': bool(row.get('is_featured') in ['1', 'True', 'true']),
                        'category': cat,
                        'price': 0,           # nếu bạn muốn có giá mặc định
                    }
                )
        self.stdout.write(self.style.SUCCESS('✔ Đã import Services'))

        # 4. Import ServiceOptions
        with open(os.path.join(base_dir, 'service_options_full.csv'), encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                svc = Service.objects.get(name=row['service_name'])
                def get_fk(model, val):
                    return model.objects.filter(name=val.strip()).first() if val else None

                ServiceOption.objects.create(
                    service=svc,
                    paper=get_fk(Paper, row['paper_name']),
                    material=get_fk(Material, row['material_name']),
                    shape=get_fk(Shape, row['shape_name']),
                    size=get_fk(Size, row['size_name']),
                    laminate=get_fk(Laminate, row['laminate_name']),
                    quantity=int(row['quantity']),
                    price=float(row['price'] or 0),
                )
        self.stdout.write(self.style.SUCCESS('✔ Đã import ServiceOptions'))

        self.stdout.write(self.style.SUCCESS('🎉 Hoàn thành import dữ liệu!'))
