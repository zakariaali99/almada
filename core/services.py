import shutil
from collections import defaultdict
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models, transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Car, Customer, Product, Repair, RepairItem, Worker, WorkerSalary


def validate_item_price(product, submitted_price, price_type):
    if not product or not price_type:
        return
    expected = product.wholesale_price if price_type == "wholesale" else product.retail_price
    if round(float(submitted_price), 2) != round(float(expected), 2):
        raise ValidationError("سعر المنتج لا يطابق نوع السعر المختار.")


def recalculate_repair_total(repair):
    repair.total_cost = sum(item.total for item in repair.items.all())
    repair.save(update_fields=["total_cost"])


def adjust_product_stock(product, delta):
    if not product:
        return
    # Use select_for_update to prevent race conditions
    with transaction.atomic():
        p = Product.objects.select_for_update().get(pk=product.pk)
        updated_quantity = p.quantity + delta
        if updated_quantity < 0:
            raise ValidationError(f"الكمية غير كافية للمنتج: {p.name}")
        p.quantity = updated_quantity
        p.save(update_fields=["quantity"])
        # Update the original object reference if needed
        product.quantity = p.quantity


def merge_or_create_repair_item(repair, description, quantity, price, item_type, product=None, price_type=None):
    existing = None
    if product:
        existing = repair.items.filter(product=product, price_type=price_type).first()
    if existing:
        adjust_product_stock(product, -quantity)
        existing.quantity += quantity
        existing.price = price
        existing.description = description
        existing.item_type = item_type
        existing.save()
        recalculate_repair_total(repair)
        return existing, False
    item = RepairItem.objects.create(
        repair=repair,
        description=description,
        quantity=quantity,
        price=price,
        item_type=item_type,
        product=product,
        price_type=price_type,
    )
    if product:
        adjust_product_stock(product, -quantity)
    recalculate_repair_total(repair)
    return item, True


@transaction.atomic
def upsert_repair_items_from_post(repair, post_data):
    item_ids = post_data.getlist("item_id[]")
    descriptions = post_data.getlist("item_description[]")
    quantities = post_data.getlist("item_quantity[]")
    prices = post_data.getlist("item_price[]")
    products = post_data.getlist("item_product[]")
    item_types = post_data.getlist("item_type[]")
    price_types = post_data.getlist("item_price_type[]")

    processed_ids = set()
    existing_items = {str(item.pk): item for item in repair.items.select_related("product")}

    for index, description in enumerate(descriptions):
        if not description.strip():
            continue
        quantity = int(quantities[index] or 1)
        price = float(prices[index] or 0)
        product = Product.objects.filter(pk=products[index]).first() if index < len(products) and products[index] else None
        item_type = item_types[index] if index < len(item_types) and item_types[index] else "قطع غيار"
        price_type = price_types[index] if index < len(price_types) and price_types[index] else None
        if product:
            validate_item_price(product, price, price_type)

        item_id = item_ids[index] if index < len(item_ids) else ""
        if item_id and item_id in existing_items:
            item = existing_items[item_id]
            old_product = item.product
            old_quantity = item.quantity
            if old_product:
                adjust_product_stock(old_product, old_quantity)
            item.description = description
            item.quantity = quantity
            item.price = price
            item.item_type = item_type
            item.product = product
            item.price_type = price_type
            item.save()
            if product:
                adjust_product_stock(product, -quantity)
            processed_ids.add(item.pk)
            continue

        new_item, _ = merge_or_create_repair_item(
            repair=repair,
            description=description,
            quantity=quantity,
            price=price,
            item_type=item_type,
            product=product,
            price_type=price_type,
        )
        processed_ids.add(new_item.pk)

    for item in repair.items.exclude(pk__in=processed_ids).select_related("product"):
        if item.product:
            adjust_product_stock(item.product, item.quantity)
        item.delete()

    recalculate_repair_total(repair)


def delete_repair_item(item):
    with transaction.atomic():
        repair = item.repair
        if item.product:
            adjust_product_stock(item.product, item.quantity)
        item.delete()
        recalculate_repair_total(repair)


def date_window(filter_type):
    now = timezone.now()
    if filter_type == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif filter_type == "weekly":
        start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif filter_type == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start + timedelta(days=32)).replace(day=1)
    elif filter_type == "yearly":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(year=start.year + 1)
    else:
        start = end = None
    return start, end


def earnings_snapshot(filter_type="all"):
    start, end = date_window(filter_type)
    item_qs = RepairItem.objects.filter(repair__status=Repair.STATUS_COMPLETED).select_related("product", "repair__car__customer")
    salary_qs = WorkerSalary.objects.filter(status="مدفوع")

    if start and end:
        item_qs = item_qs.filter(repair__date_completed__gte=start, repair__date_completed__lt=end)
        salary_qs = salary_qs.filter(payment_date__gte=start, payment_date__lt=end)

    categories = {
        "spare_parts": item_qs.filter(item_type="قطع غيار"),
        "oils": item_qs.filter(item_type="زيوت"),
        "services": item_qs.filter(Q(item_type="خدمات") | Q(product__isnull=True)),
    }

    earnings = {}
    total_revenue = 0
    total_cost = 0
    for key, qs in categories.items():
        revenue = qs.aggregate(total=Sum("total"))["total"] or 0
        if key == "services":
            cost = salary_qs.aggregate(total=Sum("amount"))["total"] or 0
        else:
            cost = sum((item.product.price_bought if item.product else 0) * item.quantity for item in qs)
        profit = revenue - cost
        earnings[key] = {
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "items_count": qs.count(),
            "items": qs,
        }
        total_revenue += revenue
        total_cost += cost

    earnings["summary"] = {
        "revenue": total_revenue,
        "cost": total_cost,
        "profit": total_revenue - total_cost,
    }
    earnings["salary_records"] = salary_qs
    return earnings


def get_dashboard_context():
    today = timezone.localdate()
    repairs = Repair.objects.select_related("car__customer", "worker")
    top_cars = (
        Car.objects.annotate(repair_count=Count("repairs"))
        .filter(repair_count__gt=0)
        .order_by("-repair_count", "make")[:5]
    )
    completed_today = repairs.filter(status=Repair.STATUS_COMPLETED, date_completed__date=today)
    return {
        "customer_count": Customer.objects.count(),
        "car_count": Car.objects.count(),
        "pending_count": repairs.filter(status=Repair.STATUS_PENDING).count(),
        "in_progress_count": repairs.filter(status=Repair.STATUS_IN_PROGRESS).count(),
        "completed_count": repairs.filter(status=Repair.STATUS_COMPLETED).count(),
        "cancelled_count": repairs.filter(status=Repair.STATUS_CANCELLED).count(),
        "product_count": Product.objects.count(),
        "worker_count": Worker.objects.count(),
        "recent_repairs": completed_today[:5],
        "recent_customers": Customer.objects.prefetch_related("cars").all()[:5],
        "total_revenue": completed_today.aggregate(total=Sum("total_cost"))["total"] or 0,
        "top_cars": top_cars,
        "cancelled_repairs": repairs.filter(status=Repair.STATUS_CANCELLED)[:5],
        "now": timezone.now(),
    }


def invoice_number(repair):
    return f"INV-{repair.pk:04d}"


def require_restore_permission(user):
    if not user.is_superuser and not user.is_staff:
        raise PermissionDenied("ليس لديك صلاحية لاستعادة قاعدة البيانات.")


def create_backup_copy():
    db_path = Path(settings.DATABASES["default"]["NAME"])
    backup_dir = Path(settings.BASE_DIR) / "uploads" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = timezone.now().strftime("%Y%m%d%H%M%S")
    backup_path = backup_dir / f"db-backup-{stamp}.sqlite3"
    shutil.copy2(db_path, backup_path)
    return backup_path


def restore_sqlite_database(uploaded_file):
    db_path = Path(settings.DATABASES["default"]["NAME"])
    create_backup_copy()
    with db_path.open("wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return db_path


@transaction.atomic
def update_repair_item(item, description, quantity, price, item_type, product=None, price_type=None):
    if product:
        validate_item_price(product, price, price_type)
    if item.product:
        adjust_product_stock(item.product, item.quantity)
    item.description = description
    item.quantity = quantity
    item.price = price
    item.item_type = item_type
    item.product = product
    item.price_type = price_type
    item.save()
    if product:
        adjust_product_stock(product, -quantity)
    recalculate_repair_total(item.repair)
    return item
