from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass


class Customer(models.Model):
    CUSTOMER_TYPES = [("تاجر", "تاجر"), ("زبون", "زبون")]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default="زبون")
    address = models.CharField(max_length=200, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_added"]

    def __str__(self):
        return self.name


class Car(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="cars")
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    license_plate = models.CharField(max_length=20, blank=True, null=True)
    vin = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_added"]

    def __str__(self):
        plate = self.license_plate or "بدون لوحة"
        return f"{self.make} {self.model or ''} - {plate}".strip()


class Worker(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    salary = models.FloatField(default=0.0)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    TYPE_CHOICES = [("قطع غيار", "قطع غيار"), ("زيوت", "زيوت")]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(default=0.0)
    price_bought = models.FloatField(default=0.0)
    wholesale_price = models.FloatField(default=0.0)
    retail_price = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    product_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="قطع غيار")
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def profit(self):
        return self.price - self.price_bought

    @property
    def profit_percentage(self):
        if self.price_bought > 0:
            return ((self.price - self.price_bought) / self.price_bought) * 100
        return 0

    @property
    def total_profit(self):
        total = 0
        for item in self.repair_items.filter(repair__status="completed").select_related("repair"):
            if item.price_type == "wholesale":
                profit_per_item = self.wholesale_price - self.price_bought
            elif item.price_type == "retail":
                profit_per_item = self.retail_price - self.price_bought
            else:
                profit_per_item = item.price - self.price_bought
            total += profit_per_item * item.quantity
        return total


class Repair(models.Model):
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "قيد الانتظار"),
        (STATUS_IN_PROGRESS, "قيد التنفيذ"),
        (STATUS_COMPLETED, "مكتمل"),
        (STATUS_CANCELLED, "ملغي"),
    ]

    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name="repairs")
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True, related_name="repairs")
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    date = models.DateField(default=timezone.now)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    total_cost = models.FloatField(default=0.0)
    mileage = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-date_created"]

    def __str__(self):
        return f"Repair #{self.pk} - {self.car}"

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_COMPLETED and not self.date_completed:
            self.date_completed = timezone.now()
        if self.status != self.STATUS_COMPLETED:
            self.date_completed = None
        super().save(*args, **kwargs)

    def recalculate_total(self):
        self.total_cost = sum(item.total for item in self.items.all())
        self.save(update_fields=["total_cost"])


class RepairItem(models.Model):
    TYPE_CHOICES = [("قطع غيار", "قطع غيار"), ("زيوت", "زيوت"), ("خدمات", "خدمات / أجور يد"), ("أخرى", "أخرى")]
    PRICE_TYPE_CHOICES = [("wholesale", "جملة"), ("retail", "قطاعي")]

    repair = models.ForeignKey(Repair, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()
    total = models.FloatField(default=0.0)
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="قطع غيار")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True, related_name="repair_items")
    price_type = models.CharField(max_length=20, choices=PRICE_TYPE_CHOICES, null=True, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.description

    def clean(self):
        if self.product and self.quantity > self.product.quantity and not self.pk:
            raise ValidationError("الكمية المطلوبة غير متوفرة في المخزون.")

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)


class WorkerSalary(models.Model):
    STATUS_CHOICES = [("محفوظ", "محفوظ"), ("مدفوع", "مدفوع"), ("مخصوم", "مخصوم")]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="salaries")
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True, related_name="worker_salaries")
    repair = models.ForeignKey(Repair, on_delete=models.SET_NULL, null=True, blank=True, related_name="worker_salaries")
    amount = models.FloatField()
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="محفوظ")
    payment_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-date", "-pk"]

    def __str__(self):
        return f"{self.worker.name} - {self.amount}"
