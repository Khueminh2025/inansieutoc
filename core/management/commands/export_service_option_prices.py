import csv
import os
from itertools import product
from collections import defaultdict
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Export consolidated combinations for service_option_prices.csv"

    def handle(self, *args, **options):
        base_dir = os.path.join(os.getcwd(), 'dataprint_extracted')
        input_file = os.path.join(base_dir, 'service_options_full.csv')
        output_file = os.path.join(base_dir, 'service_option_prices.csv')

        if not os.path.exists(input_file):
            self.stdout.write(self.style.ERROR(f"❌ Không tìm thấy {input_file}, vui lòng kiểm tra lại"))
            return

        # 1️⃣ Gom dữ liệu thành dict { (service_name, quantity): {field_name: set(values)} }
        service_data = defaultdict(lambda: defaultdict(set))

        with open(input_file, encoding='utf-8-sig') as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                key = (row.get('service_name', '').strip(), row.get('quantity', '').strip())
                for field in ['paper_name', 'material_name', 'shape_name', 'size_name', 'laminate_name']:
                    val = row.get(field, '').strip()
                    if val:
                        service_data[key][field].add(val)

        # 2️⃣ Sinh tổ hợp cartesian product
        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as f_out:
            fieldnames = ['service_name', 'paper_name', 'material_name', 'shape_name', 'size_name', 'laminate_name', 'quantity', 'price']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for (service_name, quantity), options in service_data.items():
                option_lists = []
                option_fields = ['paper_name', 'material_name', 'shape_name', 'size_name', 'laminate_name']
                for field in option_fields:
                    vals = list(options.get(field, []))
                    if vals:
                        option_lists.append([(field, v) for v in vals])
                    else:
                        option_lists.append([(field, '')])  # giữ cấu trúc

                for combination in product(*option_lists):
                    row = {
                        'service_name': service_name,
                        'quantity': quantity,
                        'price': '',  # để bạn điền tay hoặc xử lý sau
                    }
                    for field, value in combination:
                        row[field] = value
                    writer.writerow(row)

        self.stdout.write(self.style.SUCCESS(f"🎉 Đã export tổ hợp giá vào {output_file}"))

