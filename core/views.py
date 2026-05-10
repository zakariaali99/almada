from pathlib import Path
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import ProtectedError, Q
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import rate_limit
from .forms import (
    CarForm,
    CustomerForm,
    LoginForm,
    ProductForm,
    RepairForm,
    RepairItemForm,
    RestoreDatabaseForm,
    WorkerForm,
    WorkerSalaryForm,
)
from .models import Car, Customer, Product, Repair, RepairItem, Worker, WorkerSalary
from .services import (
    create_backup_copy,
    delete_repair_item as delete_repair_item_service,
    earnings_snapshot,
    get_dashboard_context,
    invoice_number,
    merge_or_create_repair_item,
    recalculate_repair_total,
    require_restore_permission,
    restore_sqlite_database,
    update_repair_item,
    upsert_repair_items_from_post,
    validate_item_price,
    generate_invoice_pdf,
)


def index(request) -> HttpResponse:
    return redirect("dashboard" if request.user.is_authenticated else "login")


@rate_limit("login", max_attempts=5, window_seconds=300)
def login_view(request) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "تم تسجيل الدخول بنجاح")
        return redirect("dashboard")
    return render(request, "login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "تم تسجيل الخروج")
    return redirect("login")


@login_required
def dashboard(request):
    return render(request, "dashboard.html", get_dashboard_context())


@login_required
def customers(request):
    query = request.GET.get("q", "").strip()
    items = Customer.objects.all()
    if query:
        items = items.filter(Q(name__icontains=query) | Q(phone__icontains=query))
    
    # Pagination
    paginator = Paginator(items, 25)  # Show 25 customers per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "customers.html", {"page_obj": page_obj, "query": query})


@login_required
def add_customer(request):
    return _handle_form(
        request,
        form_class=CustomerForm,
        template_name="add_customer.html",
        page_title="إضافة عميل",
        page_subtitle="إدخال بيانات عميل جديد",
        submit_label="إضافة العميل",
        success_message="تمت إضافة العميل بنجاح",
        redirect_name="customers",
    )


@login_required
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return _handle_form(
        request,
        form_class=CustomerForm,
        template_name="edit_customer.html",
        instance=customer,
        page_title="تعديل عميل",
        page_subtitle=customer.name,
        submit_label="حفظ التعديلات",
        success_message="تم تحديث بيانات العميل",
        redirect_name="customer_details",
        redirect_kwargs={"pk": customer.pk},
    )


@login_required
@require_POST
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    try:
        if customer.cars.exists():
            raise ProtectedError("protected", None)
        customer.delete()
        messages.success(request, "تم حذف العميل")
    except ProtectedError:
        messages.error(request, "لا يمكن حذف عميل مرتبط بسيارات")
    return redirect("customers")


@login_required
def customer_details(request, pk):
    customer = get_object_or_404(Customer.objects.prefetch_related("cars__repairs"), pk=pk)
    return render(request, "customer_details.html", {"customer": customer})


@login_required
def cars(request):
    items = Car.objects.select_related("customer")
    
    # Pagination
    paginator = Paginator(items, 25)  # Show 25 cars per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "cars.html", {"page_obj": page_obj})


@login_required
def add_car(request):
    return _handle_form(
        request,
        CarForm,
        "add_car.html",
        page_title="إضافة سيارة",
        page_subtitle="ربط السيارة بعميل",
        submit_label="إضافة السيارة",
        success_message="تمت إضافة السيارة",
        redirect_name="cars",
    )


@login_required
def edit_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    return _handle_form(
        request,
        CarForm,
        "edit_car.html",
        instance=car,
        page_title="تعديل سيارة",
        page_subtitle=str(car),
        submit_label="حفظ التعديلات",
        success_message="تم تحديث بيانات السيارة",
        redirect_name="car_details",
        redirect_kwargs={"pk": car.pk},
    )


@login_required
@require_POST
def delete_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    try:
        if car.repairs.exists():
            raise ProtectedError("protected", None)
        car.delete()
        messages.success(request, "تم حذف السيارة")
    except ProtectedError:
        messages.error(request, "لا يمكن حذف سيارة مرتبطة بإصلاحات")
    return redirect("cars")


@login_required
def car_details(request, pk):
    car = get_object_or_404(Car.objects.select_related("customer").prefetch_related("repairs__items"), pk=pk)
    return render(request, "car_details.html", {"car": car})


@login_required
def repairs(request):
    items = Repair.objects.select_related("car__customer", "worker")
    if request.GET.get("status"):
        items = items.filter(status=request.GET["status"])
    if request.GET.get("customer"):
        items = items.filter(car__customer_id=request.GET["customer"])
    if request.GET.get("worker"):
        items = items.filter(worker_id=request.GET["worker"])
    if request.GET.get("start_date"):
        items = items.filter(date__gte=request.GET["start_date"])
    if request.GET.get("end_date"):
        items = items.filter(date__lte=request.GET["end_date"])
    
    # Pagination
    paginator = Paginator(items, 25)  # Show 25 repairs per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(
        request,
        "repairs.html",
        {
            "page_obj": page_obj,
            "customers": Customer.objects.all(),
            "workers": Worker.objects.all(),
            "status_choices": Repair.STATUS_CHOICES,
        },
    )


@login_required
def add_repair(request):
    form = RepairForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        repair = form.save()
        try:
            upsert_repair_items_from_post(repair, request.POST)
            messages.success(request, "تم إنشاء الإصلاح بنجاح")
            return redirect("repair_details", pk=repair.pk)
        except ValidationError as exc:
            repair.delete()
            form.add_error(None, exc.message)
    return render(request, "add_repair.html", _repair_form_context(form, page_title="إضافة إصلاح", page_subtitle="تسجيل أمر صيانة جديد", submit_label="حفظ الإصلاح"))


@login_required
def edit_repair(request, pk):
    repair = get_object_or_404(Repair.objects.prefetch_related("items"), pk=pk)
    form = RepairForm(request.POST or None, instance=repair)
    if request.method == "POST" and form.is_valid():
        repair = form.save()
        try:
            upsert_repair_items_from_post(repair, request.POST)
            messages.success(request, "تم تحديث الإصلاح بنجاح")
            return redirect("repair_details", pk=repair.pk)
        except ValidationError as exc:
            form.add_error(None, exc.message)
    return render(request, "edit_repair.html", _repair_form_context(form, repair, page_title="تعديل إصلاح", page_subtitle=f"إصلاح #{repair.pk}", submit_label="حفظ التعديلات"))


@login_required
@require_POST
def delete_repair(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    repair.delete()
    messages.success(request, "تم حذف الإصلاح")
    return redirect("repairs")


@login_required
def repair_details(request, pk):
    repair = get_object_or_404(
        Repair.objects.select_related("car__customer", "worker").prefetch_related("items__product"),
        pk=pk,
    )
    return render(request, "repair_details.html", {"repair": repair, "invoice_number": invoice_number(repair)})


@login_required
def add_repair_item(request, repair_pk):
    repair = get_object_or_404(Repair, pk=repair_pk)
    form = RepairItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.repair = repair
        try:
            if item.product:
                validate_item_price(item.product, item.price, item.price_type)
            merge_or_create_repair_item(
                repair=repair,
                description=item.description,
                quantity=item.quantity,
                price=item.price,
                item_type=item.item_type,
                product=item.product,
                price_type=item.price_type,
            )
            messages.success(request, "تمت إضافة العنصر")
            return redirect("repair_details", pk=repair.pk)
        except ValidationError as exc:
            form.add_error(None, exc.message)
    return render(request, "add_repair_item.html", {"form": form, "repair": repair, "page_title": "إضافة عنصر", "page_subtitle": f"إصلاح #{repair.pk}", "submit_label": "إضافة العنصر"})


@login_required
def edit_repair_item(request, repair_pk, item_pk):
    repair = get_object_or_404(Repair, pk=repair_pk)
    item = get_object_or_404(RepairItem, pk=item_pk, repair=repair)
    form = RepairItemForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        try:
            update_repair_item(
                item=item,
                description=item.description,
                quantity=item.quantity,
                price=item.price,
                item_type=item.item_type,
                product=item.product,
                price_type=item.price_type,
            )
            messages.success(request, "تم تحديث العنصر")
            return redirect("repair_details", pk=repair.pk)
        except ValidationError as exc:
            form.add_error(None, exc.message)
    return render(request, "edit_repair_item.html", {"form": form, "repair": repair, "item": item, "page_title": "تعديل عنصر", "page_subtitle": f"إصلاح #{repair.pk}", "submit_label": "حفظ العنصر"})


@login_required
@require_POST
def delete_repair_item(request, pk):
    item = get_object_or_404(RepairItem.objects.select_related("repair", "product"), pk=pk)
    delete_repair_item_service(item)
    messages.success(request, "تم حذف العنصر")
    return redirect("repair_details", pk=item.repair.pk)


@login_required
def invoices(request):
    records = Repair.objects.select_related("car__customer", "worker", "customer").order_by("-date", "-id")
    if request.GET.get("customer"):
        records = records.filter(car__customer_id=request.GET["customer"])
    if request.GET.get("start_date"):
        records = records.filter(date__gte=request.GET["start_date"])
    if request.GET.get("end_date"):
        records = records.filter(date__lte=request.GET["end_date"])
    
    # Pagination
    paginator = Paginator(records, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(
        request,
        "invoices.html",
        {"page_obj": page_obj, "customers": Customer.objects.all()},
    )


@login_required
def view_invoice(request, repair_pk):
    repair = get_object_or_404(
        Repair.objects.select_related("car__customer", "worker").prefetch_related("items__product"),
        pk=repair_pk,
    )
    return render(request, "invoice_template.html", {"repair": repair, "invoice_number": invoice_number(repair)})


@login_required
def add_invoice(request):
    form = RepairForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        repair = form.save()
        try:
            upsert_repair_items_from_post(repair, request.POST)
            messages.success(request, "تم إنشاء الفاتورة بنجاح")
            return redirect("view_invoice", repair_pk=repair.pk)
        except ValidationError as exc:
            repair.delete()
            form.add_error(None, exc.message)
    return render(request, "add_invoice.html", _repair_form_context(form, page_title="إضافة فاتورة", page_subtitle="إنشاء فاتورة من إصلاح جديد", submit_label="حفظ الفاتورة"))


@login_required
def create_direct_invoice(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer")
        customer = Customer.objects.filter(pk=customer_id).first() if customer_id else None
        
        repair = Repair.objects.create(
            customer=customer,
            description="فاتورة مبيعات مباشرة",
            status=Repair.STATUS_COMPLETED,
            date=timezone.now().date(),
            is_direct_sale=True
        )
        try:
            upsert_repair_items_from_post(repair, request.POST)
            messages.success(request, "تم إنشاء فاتورة المبيعات بنجاح")
            return redirect("view_invoice", repair_pk=repair.pk)
        except ValidationError as exc:
            repair.delete()
            messages.error(request, f"خطأ: {exc.message}")
            
    context = {
        "customers": Customer.objects.all(),
        "products": Product.objects.filter(is_active=True),
        "page_title": "مبيعات مباشرة (نقطة بيع)",
        "page_subtitle": "إنشاء فاتورة سريعة بدون مركبة",
        "submit_label": "إصدار الفاتورة",
    }
    return render(request, "create_direct_invoice.html", context)


@login_required
def products(request):
    query = request.GET.get("q", "").strip()
    items = Product.objects.all()
    if query:
        items = items.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(product_type__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(items, 25)  # Show 25 products per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "products.html", {"page_obj": page_obj, "query": query})


@login_required
def add_product(request):
    return _handle_form(
        request,
        ProductForm,
        "add_product.html",
        page_title="إضافة منتج",
        page_subtitle="إضافة صنف جديد إلى المخزون",
        submit_label="إضافة المنتج",
        success_message="تمت إضافة المنتج",
        redirect_name="products",
    )


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return _handle_form(
        request,
        ProductForm,
        "edit_product.html",
        instance=product,
        page_title="تعديل منتج",
        page_subtitle=product.name,
        submit_label="حفظ التعديلات",
        success_message="تم تحديث المنتج",
        redirect_name="product_details",
        redirect_kwargs={"pk": product.pk},
    )


@login_required
@require_POST
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        product.delete()
        messages.success(request, "تم حذف المنتج")
    except ProtectedError:
        messages.error(request, "لا يمكن حذف منتج مستخدم داخل الإصلاحات")
    return redirect("products")


@login_required
def product_details(request, pk):
    product = get_object_or_404(Product.objects.prefetch_related("repair_items__repair__car__customer"), pk=pk)
    return render(request, "product_details.html", {"product": product})


@login_required
def get_products_by_type(request, product_type):
    products = Product.objects.filter(product_type=product_type)
    data = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "wholesale_price": p.wholesale_price,
            "retail_price": p.retail_price,
            "description": p.description or "",
            "product_type": p.product_type,
            "quantity": p.quantity,
        }
        for p in products
    ]
    return JsonResponse(data, safe=False)


@login_required
def workers(request):
    items = Worker.objects.all()
    
    # Pagination
    paginator = Paginator(items, 25)  # Show 25 workers per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "workers.html", {"page_obj": page_obj})


@login_required
def add_worker(request):
    return _handle_form(
        request,
        WorkerForm,
        "add_worker.html",
        page_title="إضافة عامل",
        page_subtitle="ملف عامل جديد",
        submit_label="إضافة العامل",
        success_message="تمت إضافة العامل",
        redirect_name="workers",
    )


@login_required
def edit_worker(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    return _handle_form(
        request,
        WorkerForm,
        "edit_worker.html",
        instance=worker,
        page_title="تعديل عامل",
        page_subtitle=worker.name,
        submit_label="حفظ التعديلات",
        success_message="تم تحديث بيانات العامل",
        redirect_name="worker_details",
        redirect_kwargs={"pk": worker.pk},
    )


@login_required
@require_POST
def delete_worker(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    try:
        if worker.repairs.exists():
            raise ProtectedError("protected", None)
        worker.delete()
        messages.success(request, "تم حذف العامل")
    except ProtectedError:
        messages.error(request, "لا يمكن حذف عامل مرتبط بإصلاحات أو رواتب")
    return redirect("workers")


@login_required
def worker_details(request, pk):
    worker = get_object_or_404(Worker.objects.prefetch_related("salaries", "repairs__car__customer"), pk=pk)
    return render(request, "worker_details.html", {"worker": worker})


@login_required
def add_worker_salary(request, worker_pk):
    worker = get_object_or_404(Worker, pk=worker_pk)
    form = WorkerSalaryForm(request.POST or None, initial={"worker": worker}, instance=None)
    form.fields["worker"].queryset = Worker.objects.filter(pk=worker.pk)
    if request.method == "POST" and form.is_valid():
        salary = form.save(commit=False)
        if salary.status == "مدفوع" and not salary.payment_date:
            salary.payment_date = timezone.now()
        elif salary.status != "مدفوع":
            salary.payment_date = None
        salary.save()
        messages.success(request, "تم حفظ سجل الراتب")
        return redirect("worker_details", pk=worker.pk)
    return render(request, "add_worker_salary.html", {"form": form, "worker": worker, "page_title": "إضافة راتب", "page_subtitle": worker.name, "submit_label": "حفظ الراتب"})


@login_required
@require_POST
def delete_worker_salary(request, pk):
    salary = get_object_or_404(WorkerSalary, pk=pk)
    worker_pk = salary.worker.pk
    salary.delete()
    messages.success(request, "تم حذف سجل الراتب")
    return redirect("worker_details", pk=worker_pk)


@login_required
@require_POST
def reactivate_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = True
    product.save(update_fields=["is_active"])
    messages.success(request, "تم إعادة تفعيل المنتج")
    return redirect("products")


@login_required
def edit_worker_salary(request, pk):
    salary = get_object_or_404(WorkerSalary, pk=pk)
    worker = salary.worker
    if request.method == "POST":
        form = WorkerSalaryForm(request.POST, instance=salary)
        if form.is_valid():
            salary = form.save(commit=False)
            if salary.status == "مدفوع" and not salary.payment_date:
                salary.payment_date = timezone.now()
            elif salary.status != "مدفوع":
                salary.payment_date = None
            salary.save()
            messages.success(request, "تم تحديث سجل الراتب بنجاح")
            return redirect("worker_details", pk=worker.pk)
    else:
        form = WorkerSalaryForm(instance=salary)
        form.fields["worker"].queryset = Worker.objects.filter(pk=worker.pk)
    
    return render(request, "edit_worker_salary.html", {
        "form": form,
        "worker": worker,
        "salary": salary,
        "page_title": "تعديل راتب",
        "page_subtitle": f"{worker.name} - {salary.amount}",
        "submit_label": "حفظ التعديلات"
    })


@login_required
def earnings(request):
    filter_type = request.GET.get("filter", "all")
    snapshot = earnings_snapshot(filter_type)
    return render(request, "earnings.html", {"earnings": snapshot, "filter_type": filter_type})


@login_required
def earnings_details(request, category):
    filter_type = request.GET.get("filter", "all")
    snapshot = earnings_snapshot(filter_type)
    if category not in {"spare_parts", "oils", "services"}:
        raise PermissionDenied("نوع تفاصيل الأرباح غير صالح")
    return render(
        request,
        "earnings_details.html",
        {
            "category": category,
            "details": snapshot[category],
            "salary_records": snapshot["salary_records"],
            "filter_type": filter_type,
        },
    )


@login_required
def global_search(request):
    query = request.GET.get("q", "").strip()
    results = {
        "customers": [],
        "cars": [],
        "repairs": [],
    }
    if query:
        results["customers"] = Customer.objects.filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        )[:5]
        results["cars"] = Car.objects.filter(
            Q(make__icontains=query) | Q(model__icontains=query) | Q(license_plate__icontains=query)
        ).select_related("customer")[:5]
        results["repairs"] = Repair.objects.filter(
            Q(pk__icontains=query) | Q(description__icontains=query) | Q(car__license_plate__icontains=query)
        ).select_related("car__customer")[:5]

    return render(request, "search_results.html", {"results": results, "query": query})


@login_required
def download_database(request):
    create_backup_copy()
    db_path = Path(settings.DATABASES["default"]["NAME"])
    return FileResponse(db_path.open("rb"), as_attachment=True, filename=db_path.name)


@login_required
def restore_database(request):
    try:
        require_restore_permission(request.user)
    except PermissionDenied as exc:
        messages.error(request, str(exc))
        return redirect("dashboard")

    form = RestoreDatabaseForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        restore_sqlite_database(form.cleaned_data["database_file"])
        messages.success(request, "تمت استعادة قاعدة البيانات مع إنشاء نسخة احتياطية تلقائية")
        return redirect("dashboard")
    return render(request, "restore_database.html", {"form": form})


def _handle_form(request, form_class, template_name, success_message, redirect_name, instance=None, redirect_kwargs=None, page_title="", page_subtitle="", submit_label="حفظ"):
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, success_message)
        return redirect(redirect_name, **(redirect_kwargs or {}))
    return render(request, template_name, {"form": form, "object": instance, "page_title": page_title, "page_subtitle": page_subtitle, "submit_label": submit_label})


def _repair_form_context(form, repair=None, page_title="", page_subtitle="", submit_label="حفظ"):
    return {
        "form": form,
        "repair": repair,
        "products": Product.objects.all(),
        "items": repair.items.select_related("product").all() if repair else [],
        "page_title": page_title,
        "page_subtitle": page_subtitle,
        "submit_label": submit_label,
    }
