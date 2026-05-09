from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Car, Customer, Product, Repair, RepairItem, Worker, WorkerSalary


class ArabicDateInput(forms.DateInput):
    input_type = "date"


class ArabicTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {})
        kwargs["attrs"].setdefault("rows", 3)
        super().__init__(*args, **kwargs)


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={"placeholder": "أدخل اسم المستخدم..."})
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={"placeholder": "أدخل كلمة المرور..."})
    )


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "customer_type", "address"]
        labels = {
            "name": "اسم العميل",
            "phone": "رقم الهاتف",
            "customer_type": "نوع العميل",
            "address": "العنوان",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "اسم العميل الرباعي..."}),
            "phone": forms.TextInput(attrs={"placeholder": "رقم الهاتف (اختياري)..."}),
            "address": ArabicTextarea(attrs={"placeholder": "العنوان بالتفصيل..."}),
        }


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["customer", "make", "model", "year", "license_plate", "vin", "color"]
        labels = {
            "customer": "العميل",
            "make": "الشركة المصنعة",
            "model": "الموديل",
            "year": "سنة الصنع",
            "license_plate": "رقم اللوحة",
            "vin": "رقم الهيكل (VIN)",
            "color": "اللون",
        }
        widgets = {
            "make": forms.TextInput(attrs={"placeholder": "مثلاً: تويوتا، هيونداي..."}),
            "model": forms.TextInput(attrs={"placeholder": "مثلاً: كامري، أكسنت..."}),
            "year": forms.NumberInput(attrs={"placeholder": "سنة الصنع (مثلاً: 2022)..."}),
            "license_plate": forms.TextInput(attrs={"placeholder": "رقم اللوحة..."}),
            "vin": forms.TextInput(attrs={"placeholder": "رقم الهيكل المكون من 17 رمزاً..."}),
            "color": forms.TextInput(attrs={"placeholder": "لون السيارة..."}),
        }


class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ["car", "worker", "description", "status", "date", "mileage", "notes"]
        labels = {
            "car": "السيارة",
            "worker": "الميكانيكي المسؤول",
            "description": "وصف المشكلة",
            "status": "حالة الإصلاح",
            "date": "التاريخ",
            "mileage": "عداد المسافة",
            "notes": "ملاحظات إضافية",
        }
        widgets = {
            "date": ArabicDateInput(),
            "description": ArabicTextarea(attrs={"placeholder": "وصف المشكلة التي يعاني منها العميل..."}),
            "notes": ArabicTextarea(attrs={"placeholder": "أي ملاحظات إضافية أو قطع غيار مطلوبة..."}),
            "mileage": forms.NumberInput(attrs={"placeholder": "قراءة العداد الحالية..."}),
        }


class RepairItemForm(forms.ModelForm):
    class Meta:
        model = RepairItem
        fields = ["description", "quantity", "price", "item_type", "product", "price_type"]
        labels = {
            "description": "الوصف",
            "quantity": "الكمية",
            "price": "السعر",
            "item_type": "نوع العنصر",
            "product": "المنتج المرتبط",
            "price_type": "فئة السعر",
        }
        widgets = {
            "description": forms.TextInput(attrs={"placeholder": "وصف القطعة أو الخدمة..."}),
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "price": forms.NumberInput(attrs={"placeholder": "0.00"}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "price_bought", "wholesale_price", "retail_price", "quantity", "product_type"]
        labels = {
            "name": "اسم المنتج",
            "description": "الوصف",
            "price": "سعر البيع الافتراضي",
            "price_bought": "سعر الشراء",
            "wholesale_price": "سعر الجملة",
            "retail_price": "سعر القطاعي",
            "quantity": "الكمية في المخزن",
            "product_type": "نوع المنتج",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "اسم القطعة أو الزيت..."}),
            "description": ArabicTextarea(attrs={"placeholder": "تفاصيل إضافية عن المنتج..."}),
            "price": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
            "price_bought": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
            "wholesale_price": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
            "retail_price": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
        }


class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["name", "phone", "address", "salary"]
        labels = {
            "name": "اسم العامل",
            "phone": "رقم الهاتف",
            "address": "العنوان",
            "salary": "الراتب الأساسي",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "اسم العامل بالكامل..."}),
            "phone": forms.TextInput(attrs={"placeholder": "رقم الهاتف..."}),
            "address": ArabicTextarea(attrs={"placeholder": "عنوان السكن..."}),
            "salary": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
        }


class WorkerSalaryForm(forms.ModelForm):
    class Meta:
        model = WorkerSalary
        fields = ["worker", "car", "repair", "amount", "date", "status", "notes"]
        labels = {
            "worker": "العامل",
            "car": "السيارة",
            "repair": "الإصلاح المرتبط",
            "amount": "المبلغ المدفوع",
            "date": "التاريخ",
            "status": "الحالة",
            "notes": "ملاحظات",
        }
        widgets = {
            "date": ArabicDateInput(),
            "notes": ArabicTextarea(attrs={"placeholder": "ملاحظات عن صرف الراتب أو المكافأة..."}),
            "amount": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
        }


class RestoreDatabaseForm(forms.Form):
    database_file = forms.FileField(label="ملف قاعدة البيانات")
