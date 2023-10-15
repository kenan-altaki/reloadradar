# Third Party Libraries
from core.models import Link, Manufacturer, Pricing, Propellant, Supplier

# Django Libraries
from django.contrib import admin

# Register your models here.

admin.site.register(Manufacturer)
admin.site.register(Supplier)
admin.site.register(Propellant)
admin.site.register(Pricing)
admin.site.register(Link)
