# Al-Khawarizmi Car System — Views, URLs & Classes

## Overview

The application follows Django conventions:
- **Models** → `core/models.py`
- **Views** → `core/views.py` (function-based or class-based views)
- **URLs** → `core/urls.py` (included by `alkhawarizmi/urls.py`)
- **Forms** → `core/forms.py` (Django ModelForms)
- **Templates** → `templates/` directory

---

## Model Classes Summary

(Full definitions with Django field types are in `02_database_schema.md`)

### `Customer`
- Fields: `name`, `phone`, `customer_type`, `address`, `date_added`
- Relations: `cars` (reverse from Car)

### `Car`
- Fields: `customer` (FK), `make`, `model`, `year`, `license_plate`, `vin`, `color`, `date_added`
- Relations: `repairs` (reverse from Repair)

### `Repair`
- Fields: `car` (FK), `worker` (FK), `description`, `status`, `date`, `date_created`, `date_completed`, `total_cost`, `mileage`, `notes`
- Relations: `items` (reverse from RepairItem, `on_delete=CASCADE`)
- Custom `save()`: auto-sets `date_completed` on status `'completed'`

### `RepairItem`
- Fields: `repair` (FK, CASCADE), `description`, `quantity`, `price`, `total`, `item_type`, `product` (FK, SET_NULL), `price_type`
- Custom `save()`: auto-calculates `total = quantity × price`

### `Product`
- Fields: `name`, `description`, `price`, `price_bought`, `wholesale_price`, `retail_price`, `quantity`, `product_type`, `date_added`
- Properties: `profit`, `profit_percentage`, `total_profit`

### `Worker`
- Fields: `name`, `phone`, `address`, `salary`, `date_added`
- Relations: `repairs`, `salaries`

### `WorkerSalary`
- Fields: `worker` (FK), `car` (FK, optional), `repair` (FK, optional), `amount`, `date`, `status`, `payment_date`, `notes`

### `User`
- Use `django.contrib.auth.models.User` or custom `AbstractUser` subclass
- Built-in: `username`, `password`, `is_active`, `date_joined`

---

## Django Forms (`core/forms.py`)

```python
from django import forms
from .models import Customer, Car, Repair, RepairItem, Product, Worker, WorkerSalary

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'customer_type', 'address']

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['customer', 'make', 'model', 'year', 'license_plate', 'vin', 'color']

class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ['car', 'worker', 'description', 'status', 'date', 'mileage', 'notes']

class RepairItemForm(forms.ModelForm):
    class Meta:
        model = RepairItem
        fields = ['description', 'quantity', 'price', 'item_type', 'product', 'price_type']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price_bought', 'wholesale_price', 'retail_price',
                  'quantity', 'product_type']

class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['name', 'phone', 'address', 'salary']

class WorkerSalaryForm(forms.ModelForm):
    class Meta:
        model = WorkerSalary
        fields = ['worker', 'car', 'repair', 'amount', 'date', 'status', 'notes']
```

---

## URL Configuration

### Root URLs (`alkhawarizmi/urls.py`)
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
```

### App URLs (`core/urls.py`)
```python
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Customers
    path('customers/', views.customers, name='customers'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('edit_customer/<int:pk>/', views.edit_customer, name='edit_customer'),
    path('delete_customer/<int:pk>/', views.delete_customer, name='delete_customer'),
    path('customer_details/<int:pk>/', views.customer_details, name='customer_details'),

    # Cars
    path('cars/', views.cars, name='cars'),
    path('add_car/', views.add_car, name='add_car'),
    path('edit_car/<int:pk>/', views.edit_car, name='edit_car'),
    path('delete_car/<int:pk>/', views.delete_car, name='delete_car'),
    path('car_details/<int:pk>/', views.car_details, name='car_details'),

    # Repairs
    path('repairs/', views.repairs, name='repairs'),
    path('add_repair/', views.add_repair, name='add_repair'),
    path('edit_repair/<int:pk>/', views.edit_repair, name='edit_repair'),
    path('delete_repair/<int:pk>/', views.delete_repair, name='delete_repair'),
    path('repair_details/<int:pk>/', views.repair_details, name='repair_details'),

    # Repair Items
    path('add_repair_item/<int:repair_pk>/', views.add_repair_item, name='add_repair_item'),
    path('edit_repair_item/<int:repair_pk>/<int:item_pk>/', views.edit_repair_item, name='edit_repair_item'),
    path('delete_repair_item/<int:pk>/', views.delete_repair_item, name='delete_repair_item'),

    # Invoices
    path('invoices/', views.invoices, name='invoices'),
    path('invoice/<int:repair_pk>/', views.view_invoice, name='view_invoice'),
    path('add_invoice/', views.add_invoice, name='add_invoice'),

    # Products
    path('products/', views.products, name='products'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:pk>/', views.delete_product, name='delete_product'),
    path('product_details/<int:pk>/', views.product_details, name='product_details'),

    # Products API (JSON)
    path('api/products/<str:product_type>/', views.get_products_by_type, name='api_products_by_type'),

    # Workers
    path('workers/', views.workers, name='workers'),
    path('add_worker/', views.add_worker, name='add_worker'),
    path('edit_worker/<int:pk>/', views.edit_worker, name='edit_worker'),
    path('delete_worker/<int:pk>/', views.delete_worker, name='delete_worker'),
    path('worker_details/<int:pk>/', views.worker_details, name='worker_details'),

    # Worker Salaries
    path('add_worker_salary/<int:worker_pk>/', views.add_worker_salary, name='add_worker_salary'),
    path('delete_worker_salary/<int:pk>/', views.delete_worker_salary, name='delete_worker_salary'),

    # Earnings
    path('earnings/', views.earnings, name='earnings'),
    path('earnings/details/<str:category>/', views.earnings_details, name='earnings_details'),

    # Database Management
    path('download_database/', views.download_database, name='download_database'),
    path('restore_database/', views.restore_database, name='restore_database'),
]
```

---

## All Views (API Reference)

### Authentication

| Method | URL | View Function | Auth | Description |
|---|---|---|---|---|
| GET/POST | `/login/` | `login_view` | No | Login page. POST validates credentials, logs in via `django.contrib.auth.login()` |
| GET | `/logout/` | `logout_view` | No | Calls `django.contrib.auth.logout()`, redirects to login |
| GET | `/` | `index` | No | Redirects to `/dashboard/` if authenticated, else `/login/` |

#### Implementation Example:
```python
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, 'تم تسجيل الدخول بنجاح')
            return redirect('dashboard')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    return render(request, 'login.html')
```

---

### Dashboard

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET | `/dashboard/` | `dashboard` | `@login_required` | Main dashboard with stats |

**Context variables:**
- `customer_count`, `car_count`
- `pending_count`, `in_progress_count`, `completed_count`, `cancelled_count`
- `product_count`, `worker_count`
- `recent_repairs` (today's completed)
- `recent_customers` (latest 5)
- `total_revenue` (today's)
- `top_cars` (top 5 most repaired make/models)
- `cancelled_repairs`
- `now` (current datetime)

---

### Customers CRUD

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET | `/customers/` | `customers` | `@login_required` | List all customers |
| GET/POST | `/add_customer/` | `add_customer` | `@login_required` | Add customer using `CustomerForm` |
| GET/POST | `/edit_customer/<pk>/` | `edit_customer` | `@login_required` | Edit using `CustomerForm(instance=customer)` |
| GET | `/delete_customer/<pk>/` | `delete_customer` | `@login_required` | Delete (blocked if `customer.cars.exists()`) |
| GET | `/customer_details/<pk>/` | `customer_details` | `@login_required` | Customer details with cars and repairs |

---

### Cars CRUD

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET | `/cars/` | `cars` | `@login_required` | List all cars |
| GET/POST | `/add_car/` | `add_car` | `@login_required` | Add car (select customer) |
| GET/POST | `/edit_car/<pk>/` | `edit_car` | `@login_required` | Edit car |
| GET | `/delete_car/<pk>/` | `delete_car` | `@login_required` | Delete (blocked if `car.repairs.exists()`) |
| GET | `/car_details/<pk>/` | `car_details` | `@login_required` | Car details with repair history |

---

### Repairs CRUD

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET | `/repairs/` | `repairs` | `@login_required` | List with filters (status, customer, worker, date range) |
| GET/POST | `/add_repair/` | `add_repair` | `@login_required` | Create repair with inline items |
| GET/POST | `/edit_repair/<pk>/` | `edit_repair` | `@login_required` | Edit repair; sync items (add/update/delete) |
| GET | `/delete_repair/<pk>/` | `delete_repair` | `@login_required` | Delete (cascades to items) |
| GET | `/repair_details/<pk>/` | `repair_details` | `@login_required` | View repair with all items |

---

### Repair Items (Individual)

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET/POST | `/add_repair_item/<repair_pk>/` | `add_repair_item` | `@login_required` | Add item. Handles inventory, duplicates, price validation |
| GET/POST | `/edit_repair_item/<repair_pk>/<item_pk>/` | `edit_repair_item` | `@login_required` | Edit item. Handles inventory rollback |
| GET | `/delete_repair_item/<pk>/` | `delete_repair_item` | `@login_required` | Delete item. Restores inventory |

---

### Invoices

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET | `/invoices/` | `invoices` | `@login_required` | List with filters |
| GET | `/invoice/<repair_pk>/` | `view_invoice` | `@login_required` | Printable invoice |
| GET/POST | `/add_invoice/` | `add_invoice` | `@login_required` | Create invoice (creates Repair + items) |

---

### Products CRUD

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET | `/products/` | `products` | `@login_required` | List all products |
| GET/POST | `/add_product/` | `add_product` | `@login_required` | Add product |
| GET/POST | `/edit_product/<pk>/` | `edit_product` | `@login_required` | Edit product |
| GET | `/delete_product/<pk>/` | `delete_product` | `@login_required` | Delete (blocked if used in repairs) |
| GET | `/product_details/<pk>/` | `product_details` | `@login_required` | Details with earnings breakdown |

### Products API (JSON)

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET | `/api/products/<product_type>/` | `get_products_by_type` | No | JSON: returns products filtered by type |

```python
from django.http import JsonResponse

def get_products_by_type(request, product_type):
    products = Product.objects.filter(product_type=product_type)
    data = [{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'wholesale_price': p.wholesale_price,
        'retail_price': p.retail_price,
        'description': p.description or '',
        'product_type': p.product_type,
        'quantity': p.quantity,
    } for p in products]
    return JsonResponse(data, safe=False)
```

---

### Workers CRUD

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET | `/workers/` | `workers` | `@login_required` | List all workers |
| GET/POST | `/add_worker/` | `add_worker` | `@login_required` | Add worker |
| GET/POST | `/edit_worker/<pk>/` | `edit_worker` | `@login_required` | Edit worker |
| GET | `/delete_worker/<pk>/` | `delete_worker` | `@login_required` | Delete (blocked if has repairs) |
| GET | `/worker_details/<pk>/` | `worker_details` | `@login_required` | Worker profile with salary and repair history |

---

### Worker Salaries

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET/POST | `/add_worker_salary/<worker_pk>/` | `add_worker_salary` | `@login_required` | Add salary record |
| GET | `/delete_worker_salary/<pk>/` | `delete_worker_salary` | `@login_required` | Delete salary record |

---

### Earnings

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET | `/earnings/` | `earnings` | `@login_required` | Earnings overview with filter `?filter=daily|weekly|monthly|yearly|all` |
| GET | `/earnings/details/<category>/` | `earnings_details` | `@login_required` | Details for `spare_parts`, `oils`, or `services` |

---

### Database Management

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| GET | `/download_database/` | `download_database` | `@login_required` | Download SQLite DB as backup |
| GET/POST | `/restore_database/` | `restore_database` | `@login_required` | Upload and restore DB |

---

## Key Algorithm: Edit Repair Item Sync

```python
@login_required
def edit_repair(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    
    if request.method == 'POST':
        # Update repair fields...
        
        # Get form arrays
        item_ids = request.POST.getlist('item_id[]')
        descriptions = request.POST.getlist('item_description[]')
        quantities = request.POST.getlist('item_quantity[]')
        prices = request.POST.getlist('item_price[]')
        totals = request.POST.getlist('item_total[]')
        products = request.POST.getlist('item_product[]')
        item_types = request.POST.getlist('item_type[]')
        
        processed_ids = set()
        
        for i in range(len(descriptions)):
            item_id = item_ids[i] if i < len(item_ids) else ''
            
            if item_id and item_id.isdigit():
                # UPDATE existing item
                try:
                    item = RepairItem.objects.get(pk=int(item_id), repair=repair)
                    item.description = descriptions[i]
                    item.quantity = int(quantities[i])
                    item.price = float(prices[i])
                    item.total = float(totals[i])
                    item.item_type = item_types[i] if i < len(item_types) else 'قطع غيار'
                    item.product_id = int(products[i]) if products[i] else None
                    item.save()
                    processed_ids.add(item.pk)
                except RepairItem.DoesNotExist:
                    pass
            else:
                # CREATE new item
                new_item = RepairItem.objects.create(
                    repair=repair,
                    description=descriptions[i],
                    quantity=int(quantities[i]),
                    price=float(prices[i]),
                    total=float(totals[i]),
                    item_type=item_types[i] if i < len(item_types) else 'قطع غيار',
                    product_id=int(products[i]) if products[i] else None,
                )
                processed_ids.add(new_item.pk)
        
        # DELETE items not in form
        repair.items.exclude(pk__in=processed_ids).delete()
        
        # Recalculate total
        repair.total_cost = sum(item.total for item in repair.items.all())
        repair.save()
        
        messages.success(request, 'تم تحديث الإصلاح بنجاح!')
        return redirect('repair_details', pk=repair.pk)
    
    context = {
        'repair': repair,
        'cars': Car.objects.all(),
        'workers': Worker.objects.all(),
        'products': Product.objects.all(),
    }
    return render(request, 'edit_repair.html', context)
```

---

## Key Algorithm: Inventory Management

### On Add Repair Item:
```python
if product_id:
    product = get_object_or_404(Product, pk=product_id)
    if product.quantity >= quantity:
        product.quantity -= quantity
        product.save()
    else:
        messages.error(request, 'الكمية المطلوبة غير متوفرة في المخزون!')
        return redirect(...)
```

### On Delete Repair Item:
```python
if item.product:
    item.product.quantity += item.quantity
    item.product.save()
repair.total_cost -= item.total
repair.save()
item.delete()
```

---

## Key Algorithm: Earnings Calculation

```python
from django.db.models import Sum, F, Q
from datetime import datetime, timedelta

def earnings(request):
    filter_type = request.GET.get('filter', 'all')
    
    # Build date range...
    base_qs = RepairItem.objects.filter(repair__status='completed')
    if start_date and end_date:
        base_qs = base_qs.filter(
            repair__date_completed__gte=start_date,
            repair__date_completed__lt=end_date
        )
    
    # Spare parts
    spare_items = base_qs.filter(item_type='قطع غيار')
    spare_revenue = spare_items.aggregate(total=Sum('total'))['total'] or 0
    spare_cost = sum(
        item.product.price_bought * item.quantity
        for item in spare_items if item.product
    )
    
    # Oils
    oil_items = base_qs.filter(item_type='زيوت')
    oil_revenue = oil_items.aggregate(total=Sum('total'))['total'] or 0
    oil_cost = sum(
        item.product.price_bought * item.quantity
        for item in oil_items if item.product
    )
    
    # Services (items with no product link)
    service_items = base_qs.filter(product__isnull=True)
    service_revenue = service_items.aggregate(total=Sum('total'))['total'] or 0
    
    # Worker salaries as service cost
    salary_qs = WorkerSalary.objects.filter(status='مدفوع')
    if start_date and end_date:
        salary_qs = salary_qs.filter(
            payment_date__gte=start_date,
            payment_date__lt=end_date
        )
    total_salaries = salary_qs.aggregate(total=Sum('amount'))['total'] or 0
    
    # Profits
    spare_profit = spare_revenue - spare_cost
    oil_profit = oil_revenue - oil_cost
    service_profit = service_revenue - total_salaries
    total_profit = spare_profit + oil_profit + service_profit
```

---

## Django Admin Registration (`core/admin.py`)

```python
from django.contrib import admin
from .models import Customer, Car, Repair, RepairItem, Product, Worker, WorkerSalary

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'customer_type', 'date_added']
    search_fields = ['name', 'phone']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['make', 'model', 'year', 'license_plate', 'customer']
    search_fields = ['make', 'model', 'license_plate']

@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = ['id', 'car', 'worker', 'status', 'total_cost', 'date']
    list_filter = ['status']

class RepairItemInline(admin.TabularInline):
    model = RepairItem
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_type', 'price_bought', 'wholesale_price', 'retail_price', 'quantity']
    list_filter = ['product_type']

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'salary']

@admin.register(WorkerSalary)
class WorkerSalaryAdmin(admin.ModelAdmin):
    list_display = ['worker', 'amount', 'date', 'status']
    list_filter = ['status']
```
