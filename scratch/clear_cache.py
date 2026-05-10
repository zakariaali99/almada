import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alkhawarizmi.settings')
django.setup()

from django.core.cache import cache
cache.clear()
print("Cache cleared successfully.")
