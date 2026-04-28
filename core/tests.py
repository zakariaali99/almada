from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Car, Customer, Product, Repair, RepairItem, Worker, WorkerSalary
from .services import earnings_snapshot, merge_or_create_repair_item, upsert_repair_items_from_post


class BaseDataMixin:
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="pass123456")
        self.admin = get_user_model().objects.create_superuser(username="admin", password="pass123456")
        self.customer = Customer.objects.create(name="عميل", phone="0911111111")
        self.car = Car.objects.create(customer=self.customer, make="Toyota", model="Corolla")
        self.worker = Worker.objects.create(name="عامل", salary=100)
        self.product = Product.objects.create(
            name="فلتر زيت",
            price=20,
            price_bought=10,
            wholesale_price=18,
            retail_price=20,
            quantity=10,
            product_type="قطع غيار",
        )


class ModelTests(BaseDataMixin, TestCase):
    def test_completed_repair_sets_completion_date(self):
        repair = Repair.objects.create(car=self.car, worker=self.worker, description="desc", status=Repair.STATUS_COMPLETED)
        self.assertIsNotNone(repair.date_completed)

    def test_item_total_is_calculated(self):
        repair = Repair.objects.create(car=self.car, description="desc")
        item = RepairItem.objects.create(repair=repair, description="x", quantity=2, price=5)
        self.assertEqual(item.total, 10)

    def test_duplicate_product_merges(self):
        repair = Repair.objects.create(car=self.car, description="desc")
        merge_or_create_repair_item(repair, "فلتر زيت", 1, 18, "قطع غيار", self.product, "wholesale")
        merge_or_create_repair_item(repair, "فلتر زيت", 2, 18, "قطع غيار", self.product, "wholesale")
        item = repair.items.get()
        self.assertEqual(item.quantity, 3)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 7)


class ViewTests(BaseDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.login(username="tester", password="pass123456")

    def test_login_redirect(self):
        guest = Client()
        response = guest.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_add_customer(self):
        response = self.client.post(reverse("add_customer"), {"name": "اختبار", "phone": "22", "customer_type": "زبون", "address": "طرابلس"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Customer.objects.filter(name="اختبار").exists())

    def test_repair_edit_flow(self):
        repair = Repair.objects.create(car=self.car, description="desc")
        item = RepairItem.objects.create(repair=repair, description="x", quantity=1, price=18, product=self.product, price_type="wholesale")
        payload = {
            "car": self.car.pk,
            "worker": self.worker.pk,
            "description": "updated",
            "status": Repair.STATUS_IN_PROGRESS,
            "date": timezone.localdate(),
            "mileage": 120000,
            "notes": "notes",
            "item_id[]": [str(item.pk), ""],
            "item_description[]": ["فلتر زيت", "خدمة تنظيف"],
            "item_quantity[]": ["2", "1"],
            "item_price[]": ["18", "30"],
            "item_product[]": [str(self.product.pk), ""],
            "item_type[]": ["قطع غيار", "أخرى"],
            "item_price_type[]": ["wholesale", ""],
        }
        response = self.client.post(reverse("edit_repair", args=[repair.pk]), payload)
        self.assertEqual(response.status_code, 302)
        repair.refresh_from_db()
        self.assertEqual(repair.items.count(), 2)

    def test_invoice_page(self):
        repair = Repair.objects.create(car=self.car, description="desc")
        response = self.client.get(reverse("view_invoice", args=[repair.pk]))
        self.assertContains(response, "فاتورة")

    def test_earnings_page(self):
        repair = Repair.objects.create(car=self.car, description="desc", status=Repair.STATUS_COMPLETED)
        RepairItem.objects.create(repair=repair, description="فلتر", quantity=1, price=20, item_type="قطع غيار", product=self.product, price_type="retail")
        response = self.client.get(reverse("earnings") + "?filter=all")
        self.assertEqual(response.status_code, 200)

    def test_restore_requires_admin(self):
        file = SimpleUploadedFile("db.sqlite3", b"sqlite")
        response = self.client.post(reverse("restore_database"), {"database_file": file}, follow=True)
        self.assertContains(response, "ليس لديك صلاحية", status_code=200)
