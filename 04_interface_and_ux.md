# Al-Khawarizmi Car System — Interface Pages & UI/UX Description

## Global Design System

### Layout Architecture
- **Direction**: RTL (Right-to-Left) for Arabic — `<html lang="ar" dir="rtl">`
- **Base Template**: `base.html` — all pages except `login.html` extend this via `{% extends 'base.html' %}`
- **Navigation**: Top bar (horizontal), replaces traditional sidebar
- **Content**: Centered container below topbar with `margin-top: 90px`
- **Flash Messages**: Django `messages` framework rendered as Bootstrap dismissable alerts
- **Static Files**: All loaded via `{% load static %}` and `{% static 'path' %}`
- **CSRF**: All POST forms must include `{% csrf_token %}`

### Design Tokens (CSS Variables)
```css
:root {
    --topbar-primary-color: #4361ee;
    --topbar-primary-color-light: #4895ef;
    --topbar-secondary-color: #3f37c9;
    --topbar-success-color: #4cc9f0;
    --topbar-info-color: #4895ef;
    --topbar-warning-color: #f72585;
    --topbar-danger-color: #7209b7;
    --topbar-light-bg: #f0f2f5;
    --topbar-border-radius: 10px;
    --topbar-box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    --topbar-transition: all 0.3s ease;
}
```

### Typography
- **Font Family**: `'Tajawal', sans-serif` (Google Fonts, served locally from `static/vendor/fonts/`)
- **Font Weights**: 400 (regular), 500 (medium), 700 (bold)

### Color Palette for Gradient Cards
| Purpose | Gradient |
|---|---|
| Customers | `#4361ee → #3a0ca3` (deep blue) |
| Cars | `#4cc9f0 → #4895ef` (cyan-blue) |
| Repairs / In Progress | `#f72585 → #b5179e` (pink-purple) |
| Revenue / Analytics | `#7209b7 → #560bad` (deep purple) |
| Completed | `#2ec4b6 → #3a86ff` (teal-blue) |
| Cancelled | `#e63946 → #d62828` (red) |
| Database / Success | `#28a745 → #20c997` (green) |
| Pending | `#6c757d → #495057` (grey) |

### Component Libraries (all served locally from `static/vendor/`)
| Library | File | Purpose |
|---|---|---|
| Bootstrap 5 RTL | `vendor/css/bootstrap.rtl.min.css` | CSS framework with RTL support |
| Bootstrap JS | `vendor/js/bootstrap.bundle.min.js` | Bootstrap interactive components |
| jQuery 3.6 | `vendor/js/jquery-3.6.0.min.js` | DOM manipulation, AJAX |
| Font Awesome 5 | `vendor/css/all.min.css` + `vendor/webfonts/` | Icon library |
| Material Icons Round | `vendor/css/material-icons.css` + `vendor/fonts/` | Google Material icons |
| SweetAlert2 | `vendor/css/sweetalert2.min.css` + `vendor/js/sweetalert2.all.min.js` | Modal alert dialogs |
| Tajawal Font | `vendor/css/tajawal.css` + `vendor/fonts/` | Arabic web font |

### Custom CSS Files (`static/css/`)
| File | Purpose |
|---|---|
| `style.css` (4.8 KB) | Main styles: cards, tables, badges, hover effects, transitions, custom utility classes (`.hover-scale`, `.w-fit-content`, `.hover-row`) |
| `topbar.css` (2.5 KB) | Top navigation bar: layout, responsive mobile menu, brand styling |
| `fixes.css` (1.8 KB) | CSS overrides and bug fixes |

### Custom JS Files (`static/js/`)
| File | Purpose |
|---|---|
| `script.js` (756 B) | Flash message auto-hide (5s), Bootstrap tooltip initialization |
| `arabic-date.js` (5.2 KB) | Converts English dates to Arabic format (Arabic month names, Arabic numerals ٠١٢٣٤٥٦٧٨٩) |

---

## Base Template (`base.html`)

All authenticated pages extend this. Key structure:

```html
{% load static %}
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة ورشة تصليح السيارات</title>
    <!-- Tajawal Font -->
    <link rel="stylesheet" href="{% static 'vendor/css/tajawal.css' %}">
    <!-- Bootstrap RTL -->
    <link rel="stylesheet" href="{% static 'vendor/css/bootstrap.rtl.min.css' %}">
    <!-- Material Icons -->
    <link rel="stylesheet" href="{% static 'vendor/css/material-icons.css' %}">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="{% static 'vendor/css/all.min.css' %}">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    <link rel="stylesheet" href="{% static 'css/topbar.css' %}">
    <link rel="stylesheet" href="{% static 'css/fixes.css' %}">
    <!-- SweetAlert2 -->
    <link rel="stylesheet" href="{% static 'vendor/css/sweetalert2.min.css' %}">
    <script src="{% static 'vendor/js/sweetalert2.all.min.js' %}"></script>
    {% block styles %}{% endblock %}
</head>
<body>
    <!-- Topbar Navigation -->
    <div class="topbar" id="topbar">...</div>

    <!-- Flash Messages (Django messages framework) -->
    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
    </div>

    <!-- Content Block -->
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <!-- Scripts -->
    <script src="{% static 'vendor/js/bootstrap.bundle.min.js' %}"></script>
    <script src="{% static 'vendor/js/jquery-3.6.0.min.js' %}"></script>
    <script src="{% static 'js/script.js' %}"></script>
    <script src="{% static 'js/arabic-date.js' %}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

> **Django Note**: Replace Jinja2 `{{ url_for('route') }}` with Django `{% url 'route_name' %}`. Replace `{{ url_for('static', filename='...') }}` with `{% static '...' %}`.

---

## Page-by-Page Reference

---

### 1. Login Page — `login.html`

**URL**: `/login/`  
**View**: `login_view`  
**Template**: Standalone (does NOT extend `base.html`)

**Layout**:
- Full-screen gradient background (`#667eea → #764ba2`)
- Centered white card (max-width 450px) with glassmorphism (`backdrop-filter: blur(10px)`)
- Animated floating circles in background (3 shapes with CSS `@keyframes float`)
- Fade-in-up entrance animation (0.6s)

**Components**:
- **Logo**: Circular gradient icon (80×80px) with wrench icon (`fas fa-tools`)
- **Title**: "نظام الخوارزمي" (Al-Khawarizmi System) — `h1`, 1.8rem, 700 weight
- **Subtitle**: "نظام إدارة ورشة السيارات" — `p`, 1rem, grey
- **Username Input**: Text input with floating `fas fa-user` icon on right side
- **Password Input**: Password input with floating `fas fa-lock` icon on right side
- **Submit Button**: Full-width gradient button (`#667eea → #764ba2`), 12px border-radius, hover lifts 2px with enhanced shadow
- **Footer**: "نظام آمن ومحمي" with shield icon
- **Error Display**: Gradient red alert (`#ff6b6b → #ee5a52`) for failed login

**Input styling**: 2px border, 12px border-radius, focus changes border to `#667eea` with blue glow

---

### 2. Dashboard — `dashboard.html`

**URL**: `/dashboard/`  
**View**: `dashboard`

**Layout**: Multi-row responsive Bootstrap grid

#### Section 1: Page Header
- Left: "لوحة التحكم" title with gradient Material icon
- Right: Current date in Arabic (white pill badge with calendar icon)

#### Section 2: Quick Stats (4 gradient cards in `col-md-3`)

| Card | Variable | Gradient | Icon |
|---|---|---|---|
| Total Customers | `{{ customer_count }}` | `#4361ee → #3a0ca3` | `people` |
| Total Cars | `{{ car_count }}` | `#4cc9f0 → #4895ef` | `directions_car` |
| In-Progress Repairs | `{{ in_progress_count }}` | `#f72585 → #b5179e` | `build` |
| Today's Revenue | `{{ total_revenue }} د.ل` | `#7209b7 → #560bad` | `payments` |

Each card: 25px padding, 15px border-radius, watermark icon at 15% opacity (4rem), `display-4` number, "عرض التفاصيل" pill link

#### Section 3: Database Management Card
- Green gradient header (`#28a745 → #20c997`)
- Two columns: Download Backup (green button) / Restore Backup (yellow button)
- Info alert: "Auto-backup is created before restore"

#### Section 4: Two side-by-side tables (`col-md-6`)

**Left — Today's Completed Repairs**:
- Gradient blue header
- Table columns: Date (custom mini-calendar cell: month bar + day number), Customer (avatar circle with initial), Car (icon + make/model), Status (colored pill badge), Cost (bold + د.ل)
- Empty state: Large faded `check_circle` icon + message

**Right — Recent Customers**:
- Gradient cyan header
- Table columns: Name (gradient avatar), Phone (icon), Registration Date (icon), Car Count (gradient pill badge)

#### Section 5: Analytics row

**Left — Repair Status Statistics**:
- 4 colored boxes in a row:
  - Pending (grey `#6c757d`), In Progress (pink `#f72585`), Completed (teal `#2ec4b6`), Cancelled (red `#e63946`)
  - Each: icon, count number, label text

**Right — Cancelled Repairs Table**:
- Pink gradient header
- Table: Date, Customer, Car, Cancellation reason

#### Section 6: Top Cars
- Purple gradient header
- Table: Brand (with gradient car icon), Model, Repair Count (progress bar + count badge)
- Progress bar width is percentage relative to most-repaired car

**JavaScript**:
- Arabic date conversion on page load
- Progress bar animation via `data-percentage` attribute

---

### 3. Customers List — `customers.html`

**URL**: `/customers/`

- Page title: "العملاء" with `fas fa-users` icon
- "إضافة عميل جديد" button (primary, `fas fa-plus-circle`)
- Card with gradient header showing count badge
- Table columns: Name (avatar circle), Phone (icon), Type (تاجر/زبون badge), Address, Actions (View/Edit/Delete with icons)

---

### 4. Add Customer — `add_customer.html`

**URL**: `/add_customer/`

**Form Fields** (Bootstrap card with gradient header):
- Name (`CharField`, required)
- Phone (`CharField`)
- Customer Type (`select`: تاجر / زبون)
- Address (`CharField`)
- Submit: "إضافة العميل" button

> **Django**: `<form method="POST">{% csrf_token %}{{ form.as_p }}</form>` or render fields manually

---

### 5. Edit Customer — `edit_customer.html`

Same layout as Add Customer, pre-filled with `{{ form.instance }}` values.

---

### 6. Customer Details — `customer_details.html`

- Customer info card (name, phone, type, address, date)
- Cars table listing all customer's cars with links
- Repair history for each car

---

### 7–10. Cars Pages

**`cars.html`** — List: Make, Model, Year, License Plate, Customer Name, Actions  
**`add_car.html`** — Form: Customer (select), Make, Model, Year, License Plate, VIN, Color  
**`edit_car.html`** — Same as add, pre-filled  
**`car_details.html`** — Car info card + repair history table with status badges

---

### 11. Repairs List — `repairs.html`

**URL**: `/repairs/`

**Filters** (form at top of page):
- Status dropdown (pending/in_progress/completed/cancelled)
- Customer dropdown
- Worker dropdown
- Start Date / End Date pickers
- Filter button

**Table**: Date, Car, Customer, Worker, Status (colored pill badges), Cost (bold), Actions (View/Edit/Delete)

---

### 12. Add Repair — `add_repair.html`

**URL**: `/add_repair/`

**Layout**: Two-column form + items table below

**Left Column** (Bootstrap input-groups with prepended icons):
| Field | Type | Icon |
|---|---|---|
| Car | Select dropdown | `fas fa-car` |
| Repair Date | Date input | `fas fa-calendar-alt` |
| Problem Description | Textarea | `fas fa-exclamation-triangle` |

**Right Column**:
| Field | Type | Icon |
|---|---|---|
| Worker | Select dropdown | `fas fa-user-cog` |
| Status | Select (pending/in_progress/completed/cancelled) | `fas fa-tasks` |
| Mileage | Number input | `fas fa-tachometer-alt` |
| Completion Date | Date input | `fas fa-calendar-check` |
| Notes | Textarea | `fas fa-sticky-note` |

**Items Table** (full width, below form):
| Column | Input Type | Notes |
|---|---|---|
| Type | Select (قطع غيار/زيوت/أخرى) | Filters product dropdown |
| Product | Select | Populated via JS based on type |
| Description | Text input | Auto-filled from product |
| Quantity | Number input | — |
| Price | Number input | Auto-filled from product |
| Total | Readonly text | Auto-calculated: qty × price |
| Remove | Red button | Removes row |

- "إضافة عنصر" (Add Item) button clones a new empty row
- Hidden `total_cost` field auto-calculated as sum of all row totals

**JavaScript Behaviors**:
1. **Product filter**: When item type changes → fetch products via `/api/products/<type>/` or filter `<option>` elements by `data-type` attribute
2. **Product selection**: When product selected → auto-fill description field with product name, fill price with wholesale or retail price
3. **Row calculation**: On quantity or price change → `total = quantity × price`, update grand total
4. **Row cloning**: Clone first `<tr>`, clear all values, append to tbody, attach event listeners
5. **Row removal**: Remove `<tr>`, recalculate grand total

---

### 13. Edit Repair — `edit_repair.html`

**URL**: `/edit_repair/<pk>/`

Same layout as Add Repair with these additions:
- All form fields **pre-filled** with existing repair data
- Existing items rendered in the table with their current values
- **Hidden field per item**: `<input type="hidden" name="item_id[]" value="{{ item.id }}">` — this is **critical** for the backend to identify which items to update vs. create
- New items added via "Add Item" button have empty `item_id[]`
- Removing a row means the backend will delete that item (not present in form submission)

> **CRITICAL**: The `item_id[]` hidden field is essential. Without it, the backend cannot distinguish between existing and new items, causing data corruption.

---

### 14. Repair Details — `repair_details.html`

**URL**: `/repair_details/<pk>/`

**Card 1: Repair Info**
- Two columns:
  - Left: Car (link), Customer (link), Worker (link), Mileage
  - Right: Status (colored badge), Is Temporary badge, Date Created, Date Completed
- Problem description in `alert-secondary` box
- Notes in `alert-light` box
- Actions: Edit Repair (warning btn), View Invoice (success btn), Print (info btn)

**Card 2: Parts & Services**
- Header: "قطع الغيار والخدمات" + "إضافة عنصر" button
- Table with dark header:
  | Column | Content |
  |---|---|
  | # | Row number |
  | Type | Color-coded badge (info=قطع غيار, warning=زيوت, secondary=أخرى) |
  | Description | Item description + product name in muted small text |
  | Quantity | Number |
  | Unit Price | Formatted to 2 decimal places |
  | Total | Formatted to 2 decimal places |
  | Actions | Edit + Delete buttons (hidden on print) |
- Footer: Subtotal row + Grand Total row (dark background)

**Print CSS** (`@media print`):
- Hide all buttons and `.no-print` elements
- Convert colored headers to light grey
- Convert badges to bordered text

---

### 15–16. Repair Item Pages

**`add_repair_item.html`** — Standalone form: Type, Product (filtered), Price Type (wholesale/retail), Description, Quantity, Price  
**`edit_repair_item.html`** — Same, pre-filled

---

### 17. Invoices List — `invoices.html`

**URL**: `/invoices/`

**Filters**: Customer dropdown, Date range (start/end)
**Table**: Invoice #, Date, Customer, Car, Status, Total, "View Invoice" button

---

### 18. Add Invoice — `add_invoice.html`

**URL**: `/add_invoice/`

Similar to Add Repair:
- Two columns: Customer/Car/Worker info | Description/Status/Mileage/Notes
- Items table with inline editing
- Customer select filters the Car dropdown (shows only that customer's cars)
- Same JS behaviors as Add Repair

---

### 19. Invoice Template — `invoice_template.html`

**URL**: `/invoice/<repair_pk>/`

Printable invoice:
- Invoice header: "فاتورة" + Invoice number `INV-XXXX`
- Customer details block, Car details block, Worker, Dates
- Items table with totals
- Print-optimized CSS (no buttons, clean layout)
- `window.print()` button

---

### 20–23. Product Pages

**`products.html`** — List: Name, Type (badge), Purchase Price, Wholesale Price, Retail Price, Stock Quantity, Actions  
**`add_product.html`** — Form: Name, Description, Type (select), Purchase Price, Wholesale Price, Retail Price, Quantity  
**`edit_product.html`** — Same, pre-filled  
**`product_details.html`** — Product info with all prices + Earnings breakdown table (lists every completed repair using this product: customer, car, date, qty, price type, profit per unit, total profit)

---

### 24–26. Worker Pages

**`workers.html`** — List table: Name (avatar with initial), Phone (icon), Address (icon), Salary (bold + د.ل), Repair Count (badge), Actions (View/Edit/Delete with tooltips)  
- Custom avatar circle (36×36px, bg-primary, white text, bold, rounded-50%)
- Action buttons: 32×32px, inline-flex centered, hover lifts 2px with shadow

**`add_worker.html`** — Form: Name, Phone, Address  
**`edit_worker.html`** — Same + Salary field

---

### 27. Worker Details — `worker_details.html`

- Worker info card (name, phone, address, salary)
- "إضافة راتب" (Add Salary) button
- Salary records table: Amount, Date, Car (if linked), Repair (if linked), Status badge (محفوظ/مدفوع/مخصوم), Delete button
- Repair assignments table: list of repairs assigned to this worker

---

### 28. Add Worker Salary — `add_worker_salary.html`

**Form Fields**:
- Amount (number, required)
- Date (date, required, default: today)
- Car (select, optional — all cars)
- Repair (select, optional — completed/in-progress repairs, ordered by date desc)
- Status (select: محفوظ / مدفوع / مخصوم)
- Notes (textarea)

---

### 29. Earnings Overview — `earnings.html`

**URL**: `/earnings/`

**Time Filter Buttons**: اليوم (daily) | هذا الأسبوع (weekly) | هذا الشهر (monthly) | هذا العام (yearly) | جميع الفترات (all)
- Active filter highlighted as primary button
- Filter passed as `?filter=daily|weekly|monthly|yearly|all`

**Three Earnings Cards** (side by side):

| Card | Title | Data |
|---|---|---|
| Spare Parts (قطع غيار) | Revenue, Purchase Cost, Net Profit, Items Count | `earnings.spare_parts.*` |
| Oils (زيوت) | Revenue, Purchase Cost, Net Profit, Items Count | `earnings.oils.*` |
| Services (خدمات) | Revenue, Worker Salaries (as cost), Net Profit, Items Count | `earnings.services.*` |

**Summary Card** (full width):
- Total Revenue, Total Cost, **Total Profit** (highlighted)

Each card has a "عرض التفاصيل" link to earnings details page.

---

### 30. Earnings Details — `earnings_details.html`

**URL**: `/earnings/details/<category>/`

**Summary Bar** (4 metric cards):
- Total Revenue, Total Cost, Total Profit, Items Count

**Time Filters**: Same as earnings overview

**Detailed Table**: Each RepairItem row with:
- Repair ID (link), Customer, Car, Date, Description, Quantity, Unit Price, Item Total, Cost (price_bought × qty), Net Profit

For **Services** category: additional Worker Salaries table below showing individual salary payments deducted as cost.

---

### 31. Restore Database — `restore_database.html`

**URL**: `/restore_database/`

- Warning card explaining that restore replaces current data
- File input accepting `.db` files only
- "استعادة" (Restore) submit button
- Note: auto-backup of current DB is created before restore

---

## Navigation Structure (Topbar in `base.html`)

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔧 نظام الخوارزمي │ لوحة التحكم │ الإصلاحات │ الفواتير │ الأرباح │ العملاء │ السيارات │ العمال │ المنتجات │ خروج │
└───────────────────────────────────────────────────────────────────────────┘
```

| Material Icon | Arabic Label | Django URL Name |
|---|---|---|
| `build` | نظام الخوارزمي (brand) | `dashboard` |
| `dashboard` | لوحة التحكم | `dashboard` |
| `handyman` | الإصلاحات | `repairs` |
| `receipt` | الفواتير | `invoices` |
| `analytics` | الأرباح | `earnings` |
| `people` | العملاء | `customers` |
| `directions_car` | السيارات | `cars` |
| `engineering` | العمال | `workers` |
| `inventory_2` | المنتجات | `products` |
| `logout` | تسجيل الخروج | `logout` |

**Mobile (< 992px)**: Hamburger menu button (`topbar-toggle`), menu slides down. Click outside closes menu.  
**Active Highlighting**: JavaScript compares `window.location.pathname` with each link's `href`, adds `.active` class to matching link.

---

## Responsive Design Notes

- All tables use `.table-responsive` wrapper for horizontal scrolling on mobile
- Cards use Bootstrap grid (`col-md-3`, `col-md-6`) — stacks vertically on small screens
- Topbar collapses to hamburger menu below 992px
- Login page is centered via `display: flex; align-items: center; justify-content: center; min-height: 100vh`
- Form inputs use Bootstrap input-groups with prepended icons

---

## Interaction Patterns Summary

| Pattern | How It Works |
|---|---|
| **Delete Confirmation** | Native `confirm('هل أنت متأكد من حذف هذا العنصر؟')` — returns false to cancel |
| **Flash Messages** | Django `messages.success/error/warning` → Bootstrap alerts, auto-hidden after 5 seconds via JS |
| **Dynamic Form Rows** | JS clones first `<tr>`, clears input values, appends to `<tbody>`, re-attaches event listeners |
| **Product Auto-fill** | `<select>` options have `data-price`, `data-wholesale`, `data-retail`, `data-type` attributes. On change → fills description + price fields |
| **Product Type Filter** | When item type `<select>` changes → hide/show `<option>` elements in product `<select>` based on matching `data-type` |
| **Real-time Totals** | On `input` event for quantity/price → `row_total = qty × price`, then `grand_total = Σ(all row totals)` |
| **Print** | `window.print()` with `@media print` CSS hiding navigation, buttons, and `.no-print` elements |
| **Arabic Dates** | `arabic-date.js` on DOM load: finds `[data-date]` elements, replaces content with Arabic month names and Arabic numerals |
| **Customer→Car Filter** | On Add Invoice: selecting a customer filters the car dropdown to show only that customer's cars |
| **Tooltips** | Bootstrap 5 tooltips initialized on `[data-bs-toggle="tooltip"]` elements via `new bootstrap.Tooltip()` |

---

## Django Template Syntax Mapping

When porting from the existing codebase (which uses Jinja2), apply these conversions:

| Jinja2 (Flask) | Django Template |
|---|---|
| `{{ url_for('route_name') }}` | `{% url 'route_name' %}` |
| `{{ url_for('route', id=x) }}` | `{% url 'route_name' pk=x %}` |
| `{{ url_for('static', filename='css/style.css') }}` | `{% static 'css/style.css' %}` |
| `{% extends 'base.html' %}` | `{% extends 'base.html' %}` (same) |
| `{% block content %}` | `{% block content %}` (same) |
| `{{ variable }}` | `{{ variable }}` (same) |
| `{% for item in list %}` | `{% for item in list %}` (same) |
| `{% if condition %}` | `{% if condition %}` (same) |
| `{{ list\|length }}` | `{{ list\|length }}` (same) |
| `{{ value\|format("%.2f") }}` | `{{ value\|floatformat:2 }}` |
| `get_flashed_messages(with_categories=true)` | `{% if messages %}{% for msg in messages %}` |
| No equivalent | `{% load static %}` (required at top) |
| No equivalent | `{% csrf_token %}` (required in forms) |
