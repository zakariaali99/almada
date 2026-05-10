import random
import sys
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from core.models import Customer, Car, Worker, Product, Repair, RepairItem, WorkerSalary

try:
    from faker import Faker
except ImportError:
    Faker = None

class Command(BaseCommand):
    help = 'Simulates 10 years of business data'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before simulating')
        parser.add_argument('--days', type=int, default=3650, help='Number of days to simulate (default 3650 for 10 years)')
        parser.add_argument('--repairs-per-day', type=int, default=2, help='Average repairs per day')

    @transaction.atomic
    def handle(self, *args, **options):
        if not Faker:
            self.stdout.write(self.style.ERROR('Faker library is not installed. Please install it using: pip install faker'))
            sys.exit(1)

        clear = options['clear']
        total_days = options['days']
        repairs_per_day = options['repairs_per_day']

        fake = Faker('ar_EG')

        if clear:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            WorkerSalary.objects.all().delete()
            RepairItem.objects.all().delete()
            Repair.objects.all().delete()
            Car.objects.all().delete()
            Customer.objects.all().delete()
            Worker.objects.all().delete()
            Product.objects.all().delete()

        self.stdout.write('Generating Base Entities...')
        
        # Create Workers
        workers = []
        for _ in range(8):
            workers.append(Worker(
                name=fake.name(),
                phone=fake.phone_number()[:20],
                address=fake.address()[:200],
                salary=Decimal(random.randint(1000, 3000))
            ))
        Worker.objects.bulk_create(workers)
        workers = list(Worker.objects.all())

        # Create Products
        products = []
        product_types = ['oil', 'spare_part', 'accessory']
        for i in range(100):
            price_bought = Decimal(random.randint(10, 500))
            products.append(Product(
                name=f"{fake.word()} {fake.word()}",
                description=fake.sentence(),
                price=price_bought * Decimal('1.4'),
                price_bought=price_bought,
                wholesale_price=price_bought * Decimal('1.2'),
                retail_price=price_bought * Decimal('1.5'),
                quantity=1000000,  # massive stock to prevent issues
                product_type=random.choice(product_types)
            ))
        Product.objects.bulk_create(products)
        products = list(Product.objects.all())

        # Create Customers and Cars
        customers = []
        for _ in range(500):
            customers.append(Customer(
                name=fake.name(),
                phone=fake.phone_number()[:20],
                address=fake.address()[:200],
                customer_type=random.choice(['retail', 'wholesale', 'company'])
            ))
        Customer.objects.bulk_create(customers)
        customers = list(Customer.objects.all())

        cars = []
        makes = ['تويوتا', 'هيونداي', 'كيا', 'مرسيدس', 'بي إم دبليو', 'نيسان', 'مازدا']
        models = ['كامري', 'إلنترا', 'سيراتو', 'كورولا', 'سوناتا', 'سيارة عائلية', 'شاحنة صغيرة']
        for c in customers:
            num_cars = random.randint(1, 3)
            for _ in range(num_cars):
                cars.append(Car(
                    customer=c,
                    make=random.choice(makes),
                    model=random.choice(models),
                    year=random.randint(2000, 2026),
                    license_plate=f"{random.randint(10, 99)}-{random.randint(10000, 99999)}"[:20],
                    vin=fake.pystr(min_chars=17, max_chars=17).upper(),
                    color=fake.safe_color_name()
                ))
        Car.objects.bulk_create(cars)
        cars = list(Car.objects.all())

        self.stdout.write('Starting 10-year timeline simulation...')
        start_date = timezone.now() - timedelta(days=total_days)
        
        repairs_to_create = []
        current_date = start_date

        # Create Repairs day by day
        for day_offset in range(total_days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Add some randomness to daily repairs
            daily_repairs = random.randint(0, repairs_per_day * 2)
            
            for _ in range(daily_repairs):
                is_direct = random.random() < 0.2
                status = random.choices(
                    ['pending', 'in_progress', 'completed', 'cancelled'],
                    weights=[0.05, 0.05, 0.85, 0.05]
                )[0]
                
                r = Repair(
                    car=None if is_direct else random.choice(cars),
                    customer=random.choice(customers) if is_direct else None,
                    is_direct_sale=is_direct,
                    worker=random.choice(workers) if random.random() < 0.8 else None,
                    description=fake.sentence(),
                    status=status,
                    date=current_date.date(),
                    mileage=random.randint(10000, 300000) if not is_direct else None,
                    notes=fake.sentence() if random.random() < 0.3 else '',
                    total_cost=Decimal('0.00'),  # updated later
                    date_created=current_date,
                )
                if status == 'completed':
                    r.date_completed = current_date + timedelta(hours=random.randint(1, 48))
                
                repairs_to_create.append(r)
            
            if day_offset > 0 and day_offset % 365 == 0:
                self.stdout.write(f'Simulating year {int(day_offset/365)}/10 ...')

        # Bulk create repairs
        self.stdout.write(f'Saving {len(repairs_to_create)} repairs to DB...')
        Repair.objects.bulk_create(repairs_to_create, batch_size=2000)
        
        # We need to fetch repairs back to assign items (since bulk_create doesn't return PKs reliably on sqlite)
        all_repairs = list(Repair.objects.all())
        
        self.stdout.write('Generating Repair Items (this might take a minute)...')
        items_to_create = []
        
        # Pre-calculate to avoid updating DB continuously
        repair_totals = {r.id: Decimal('0.00') for r in all_repairs}
        
        for idx, r in enumerate(all_repairs):
            num_items = random.randint(1, 5)
            r_total = Decimal('0.00')
            for _ in range(num_items):
                item_type = random.choice(['part', 'service', 'oil'])
                qty = random.randint(1, 4)
                
                if item_type == 'service':
                    price = Decimal(random.randint(20, 300))
                    item = RepairItem(
                        repair=r,
                        description=f"خدمة {fake.word()}",
                        quantity=qty,
                        price=price,
                        item_type=item_type,
                    )
                else:
                    prod = random.choice(products)
                    price = prod.retail_price
                    item = RepairItem(
                        repair=r,
                        description=prod.name,
                        quantity=qty,
                        price=price,
                        item_type=item_type,
                        product=prod,
                        price_type='retail'
                    )
                
                items_to_create.append(item)
                r_total += item.total
            
            repair_totals[r.id] = r_total
            
            if idx > 0 and idx % 5000 == 0:
                self.stdout.write(f'Prepared items for {idx} repairs...')

        self.stdout.write(f'Saving {len(items_to_create)} repair items to DB...')
        RepairItem.objects.bulk_create(items_to_create, batch_size=5000)
        
        self.stdout.write('Updating repair totals...')
        # We need to update totals
        repairs_to_update = []
        for r in all_repairs:
            if repair_totals.get(r.id):
                r.total_cost = repair_totals[r.id]
                repairs_to_update.append(r)
        
        Repair.objects.bulk_update(repairs_to_update, ['total_cost'], batch_size=2000)

        self.stdout.write(self.style.SUCCESS('Successfully simulated 10 years of data!'))
