from django.contrib import admin

from .models import Car, Customer, Product, Repair, RepairItem, User, Worker, WorkerSalary


class RepairItemInline(admin.TabularInline):
    model = RepairItem
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "is_staff", "is_active", "date_joined"]
    search_fields = ["username", "first_name", "last_name"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "customer_type", "date_added"]
    search_fields = ["name", "phone"]
    list_filter = ["customer_type"]


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ["make", "model", "year", "license_plate", "customer"]
    search_fields = ["make", "model", "license_plate", "customer__name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "product_type", "price_bought", "wholesale_price", "retail_price", "quantity"]
    search_fields = ["name"]
    list_filter = ["product_type"]


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "salary"]
    search_fields = ["name", "phone"]


@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = ["id", "car", "worker", "status", "total_cost", "date"]
    list_filter = ["status", "date"]
    search_fields = ["car__make", "car__model", "car__customer__name"]
    inlines = [RepairItemInline]


@admin.register(WorkerSalary)
class WorkerSalaryAdmin(admin.ModelAdmin):
    list_display = ["worker", "amount", "date", "status"]
    list_filter = ["status"]
    search_fields = ["worker__name"]
