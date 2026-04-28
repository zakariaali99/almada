def navigation_links(request):
    return {
        "navigation_links": [
            {"label": "لوحة التحكم", "icon": "dashboard", "url_name": "dashboard"},
            {"label": "الإصلاحات", "icon": "handyman", "url_name": "repairs"},
            {"label": "الفواتير", "icon": "receipt", "url_name": "invoices"},
            {"label": "الأرباح", "icon": "analytics", "url_name": "earnings"},
            {"label": "العملاء", "icon": "people", "url_name": "customers"},
            {"label": "السيارات", "icon": "directions_car", "url_name": "cars"},
            {"label": "العمال", "icon": "engineering", "url_name": "workers"},
            {"label": "المنتجات", "icon": "inventory_2", "url_name": "products"},
        ]
    }
