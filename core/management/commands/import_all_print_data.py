import csv
import os
from django.core.management.base import BaseCommand
from core.models import (
    Category, Shape, Size, Laminate, Material, Paper,
    Service, ServiceOption, ServicePrice
)

class Command(BaseCommand):
    help = 'Import ALL print data (9 files) from dataprint_extracted for sieutoc'

    def handle(self, *args, **options):
        base_dir = os.path.join(os.getcwd(), 'dataprint_extracted')

        def import_model(model, filename, fields):
            with open(os.path.join(base_dir, filename), encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    defaults = {}
                    for field in fields:
                        value = row[field].strip()
                        if value == "":
                            continue
                        if field in ['show_on_homepage']:  # thêm các field boolean khác nếu có
                            value = value.lower() in ['1', 'true', 'yes']
                        defaults[field] = value                   
                    
                    obj, created = model.objects.update_or_create(
                        id=int(row['id']),
                        defaults=defaults
                    )
                    count += 1
                self.stdout.write(self.style.SUCCESS(f'✔ Imported {count} rows for {model.__name__}'))

        # 1️⃣ Import basic models
        import_model(Category, 'categories.csv', ['name', 'show_on_homepage'])
        import_model(Shape, 'shape.csv', ['name'])
        import_model(Size, 'size.csv', ['name'])
        import_model(Laminate, 'laminate.csv', ['name'])
        import_model(Material, 'material.csv', ['name'])
        import_model(Paper, 'paper.csv', ['name'])

        # 2️⃣ Import Services
        with open(os.path.join(base_dir, 'services.csv'), encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                cat_ids = [int(i) for i in row['category_ids'].split(',') if i]
                cat = Category.objects.filter(id__in=cat_ids).first() if cat_ids else None
                obj, created = Service.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'].strip(),
                        'title': row['title'].strip() or None,
                        'description': row['description'].strip() or None,
                        'is_featured': bool(row.get('is_featured') in ['1', 'True', 'true']),
                        'category': cat,
                    }
                )
                count += 1
            self.stdout.write(self.style.SUCCESS(f'✔ Imported {count} Services'))

        # 3️⃣ Import ServiceOptions
        with open(os.path.join(base_dir, 'service_options_full.csv'), encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                service = Service.objects.filter(name=row['service_name'].strip()).first()
                if not service:
                    continue

                def get_fk(model, val):
                    return model.objects.filter(name=val.strip()).first() if val.strip() else None

                obj, created = ServiceOption.objects.update_or_create(
                    service=service,
                    paper=get_fk(Paper, row['paper_name']),
                    material=get_fk(Material, row['material_name']),
                    shape=get_fk(Shape, row['shape_name']),
                    size=get_fk(Size, row['size_name']),
                    laminate=get_fk(Laminate, row['laminate_name']),
                )
                count += 1
            self.stdout.write(self.style.SUCCESS(f'✔ Imported {count} ServiceOptions'))

        # 4️⃣ Import ServiceOption
        with open(os.path.join(base_dir, 'service_option_prices.csv'), encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                service = Service.objects.filter(name=row['service_name'].strip()).first()
                if not service:
                    continue

                def get_fk(model, val):
                    return model.objects.filter(name=val.strip()).first() if val.strip() else None
                quantity = int(row.get('quantity', 0) or 0)
                price = float(row.get('price', 0) or 0)

                obj, created = ServicePrice.objects.update_or_create(
                    service=service,
                    paper=get_fk(Paper, row['paper_name']),
                    material=get_fk(Material, row['material_name']),
                    shape=get_fk(Shape, row['shape_name']),
                    size=get_fk(Size, row['size_name']),
                    laminate=get_fk(Laminate, row['laminate_name']),
                    quantity=int(row['quantity']),
                    defaults={'price': float(row['price'] or 0)},
                )
                count += 1
            self.stdout.write(self.style.SUCCESS(f'✔ Imported {count} ServiceOptionPrices'))

        self.stdout.write(self.style.SUCCESS('🎉 Hoàn thành import toàn bộ dữ liệu in ấn!'))
