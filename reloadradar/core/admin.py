# Django Libraries
from django.contrib import admin

# Project Modules
from core.models import Link, Manufacturer, Pricing, Propellant, Supplier

admin.site.register(Manufacturer)
admin.site.register(Supplier)
admin.site.register(Propellant)
admin.site.register(Pricing)
admin.site.register(Link)
