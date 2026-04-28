# Al-Khawarizmi Car System — System Overview & Description

## 1. System Identity

| Property | Value |
|---|---|
| **System Name** | نظام الخوارزمي لإدارة ورشة السيارات (Al-Khawarizmi Car System) |
| **Project Name** | `alkhawarizmi_system` |
| **System Type** | Auto Repair Shop Management (POS) |
| **Language** | Arabic (RTL) — all UI strings are Arabic |
| **Currency** | Libyan Dinar (د.ل) |
| **Target Users** | Car repair shop owners and workers |

## 2. Purpose

A complete Point-of-Sale and workshop management system for car repair shops. It tracks customers, their cars, repair orders, inventory (spare parts & oils), worker assignments, worker salaries, invoicing, and earnings analytics — all from a single web application.

## 3. Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| **Backend** | Python / Django 4.2+ | Django framework with class-based and function-based views |
| **ORM** | Django ORM | Built-in model layer with migrations |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Default `db.sqlite3`, switchable via `settings.py` |
| **Auth** | Django `django.contrib.auth` | Built-in User model with `make_password` / `check_password` or custom User model |
| **Session** | Django server-side sessions | `django.contrib.sessions` middleware |
| **Frontend** | Django Templates, Bootstrap 5 (RTL), jQuery 3.6, Font Awesome, Google Material Icons | All assets served locally from `static/` |
| **Font** | Tajawal (Google Fonts, served locally from `static/vendor/fonts/`) | — |
| **Alerts** | SweetAlert2 (local bundle) | — |
| **Production Server** | Gunicorn + Nginx (Linux) / Waitress (Windows) | — |
| **Config** | `settings.py` + `.env` via `python-decouple` or `django-environ` | — |

### `requirements.txt`
```
Django>=4.2,<5.0
gunicorn>=21.2.0
python-decouple>=3.8
Pillow>=10.0.0          # If image uploads needed
whitenoise>=6.5.0       # Serve static files in production
```

## 4. Project Directory Structure

```
alkhawarizmi_system/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env                               # Environment variables
├── .env.example                       # Example env file
├── db.sqlite3                         # SQLite database (development)
│
├── alkhawarizmi/                      # Django project settings package
│   ├── __init__.py
│   ├── settings.py                    # Django settings
│   ├── urls.py                        # Root URL configuration
│   ├── wsgi.py                        # WSGI entry point
│   └── asgi.py                        # ASGI entry point
│
├── core/                              # Main Django app
│   ├── __init__.py
│   ├── models.py                      # All ORM models
│   ├── views.py                       # All views (routes)
│   ├── urls.py                        # App URL patterns
│   ├── forms.py                       # Django forms
│   ├── admin.py                       # Django admin configuration
│   ├── decorators.py                  # Custom decorators (login_required etc.)
│   ├── context_processors.py          # Template context processors
│   ├── templatetags/                  # Custom template tags
│   │   └── arabic_filters.py         # Arabic date formatting filters
│   └── migrations/                    # Database migrations
│
├── static/
│   ├── css/
│   │   ├── style.css                  # Main custom styles
│   │   ├── topbar.css                 # Topbar navigation styles
│   │   └── fixes.css                  # CSS overrides and fixes
│   ├── js/
│   │   ├── script.js                  # Main custom JavaScript
│   │   └── arabic-date.js            # Arabic date formatting utilities
│   └── vendor/
│       ├── css/                       # Bootstrap RTL, FontAwesome, Material Icons, SweetAlert2, Tajawal font
│       ├── js/                        # Bootstrap bundle, jQuery, SweetAlert2
│       ├── fonts/                     # Tajawal font files
│       └── webfonts/                  # FontAwesome webfonts
│
├── templates/                         # Django HTML templates
│   ├── base.html                      # Base layout with topbar navigation
│   ├── login.html                     # Standalone login page
│   ├── dashboard.html
│   └── ...                            # (32 templates total, see doc 04)
│
└── uploads/                           # User uploads directory (MEDIA_ROOT)
```

## 5. Django Settings Configuration

### `settings.py` key settings:
```python
import os
from decouple import config

SECRET_KEY = config('SECRET_KEY', default='change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=lambda v: v.split(','))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# For production with PostgreSQL:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='5432'),
#     }
# }

LANGUAGE_CODE = 'ar'
USE_I18N = True
USE_L10N = True
TIME_ZONE = 'Africa/Tripoli'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/uploads/'
MEDIA_ROOT = BASE_DIR / 'uploads'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### `.env` example:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

## 6. Application Startup

### Development
```bash
python manage.py migrate
python manage.py createsuperuser    # Create admin user
python manage.py runserver 0.0.0.0:5007
```

### Production (Linux)
```bash
python manage.py collectstatic --noinput
gunicorn alkhawarizmi.wsgi:application -w 4 -b 0.0.0.0:5007
```

### On startup, Django does:
1. Loads `settings.py` (reads `.env` via `python-decouple`)
2. Initializes all installed apps and middleware
3. Connects to the database and applies migrations
4. Serves the application

## 7. Authentication System

- **Mechanism**: Django's built-in `django.contrib.auth` with `@login_required` decorator or custom session-based auth.
- **User Model**: Either Django's built-in `User` or a custom model extending `AbstractUser`.
- **Password hashing**: Django uses PBKDF2 by default (configurable via `PASSWORD_HASHERS`). No column length issues.
- **Session**: `django.contrib.sessions` middleware handles server-side sessions.

### Recommended approach — Custom User model:
```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_active = models.BooleanField(default=True)
    # username and password are inherited from AbstractUser
```

### Default Credentials
Created via `python manage.py createsuperuser` or a management command.

## 8. Core Business Modules

| Module | Description |
|---|---|
| **Customers** | Customer CRUD with type (تاجر/زبون), phone, address |
| **Cars** | Car CRUD linked to customers. Includes make, model, year, license plate, VIN, color |
| **Repairs** | Repair orders linked to cars and workers. Status workflow: pending → in_progress → completed / cancelled |
| **Repair Items** | Line items within repairs: parts, oils, services. Links to product inventory with wholesale/retail pricing |
| **Products** | Inventory of spare parts and oils with purchase price, wholesale price, retail price, quantity tracking |
| **Workers** | Worker profiles with phone, address, salary |
| **Worker Salaries** | Salary records linked to workers, optionally linked to specific cars/repairs |
| **Invoices** | View/create invoices from repairs, with printable template |
| **Earnings** | Analytics dashboard: profit breakdown by spare parts, oils, and services, with time filters (daily/weekly/monthly/yearly) |
| **Database Management** | Backup download and restore from the dashboard |

## 9. Key Business Rules

1. **Inventory tracking**: When a repair item is added with a linked product, the product's `quantity` is decremented. When deleted, it's restored.
2. **Price types**: Products have `wholesale_price` and `retail_price`. The system validates that the selected price type matches the expected price.
3. **Duplicate product detection**: If the same product with the same price type already exists in a repair, the quantity is incremented instead of creating a duplicate.
4. **Cascade delete**: Deleting a repair cascades to delete all its RepairItems (via `on_delete=models.CASCADE`).
5. **Protected deletes**: Customers with cars, cars with repairs, workers with repairs, and products used in repairs cannot be deleted. Use `on_delete=models.PROTECT` where appropriate.
6. **Earnings calculation**: Profit = Revenue - Cost. For products: cost = `price_bought × quantity`. For services: cost = total worker salaries paid in the same period.
7. **Auto-completion date**: When a repair status changes to `completed`, `date_completed` is auto-set to `timezone.now()` if not provided.

## 10. Django-Specific Implementation Notes

| Topic | Recommendation |
|---|---|
| **Migrations** | Use `python manage.py makemigrations` and `python manage.py migrate` for all schema changes |
| **Admin Panel** | Register all models in `admin.py` for quick data management via `/admin/` |
| **Forms** | Use `django.forms.ModelForm` for all CRUD forms with built-in validation |
| **CSRF Protection** | Django includes CSRF middleware by default — all POST forms must include `{% csrf_token %}` |
| **Static Files** | Use `{% load static %}` and `{% static 'path' %}` in templates |
| **URL Routing** | Use `path()` and `include()` in `urls.py` with named URL patterns |
| **Template Engine** | Django templates use `{% %}` and `{{ }}` — very similar to Jinja2 but with minor syntax differences |
| **Management Commands** | Create custom commands in `core/management/commands/` for tasks like user creation |
