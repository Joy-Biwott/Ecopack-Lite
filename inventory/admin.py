from django.contrib import admin
from .models import FinishedBag, Client, Order

# Register your models here.
class FinishedBagAdmin(admin.ModelAdmin):
    list_display = ('variety', 'color', 'gsm', 'quantity_bales', 'location', 'last_updated')
    last_filter = ('variety', 'color', 'gsm', 'location')
    search_fields = ('variety', 'color', 'location')
    list_editable = ('quantity_bales',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'bag', 'quantity_ordered', 'order_date')
    list_filter = ('order_date',)
    search_fields = ('client__name', 'bag__variety')

# Register the models with their custom admin classes
admin.site.register(FinishedBag, FinishedBagAdmin)
admin.site.register(Client)
admin.site.register(Order, OrderAdmin)

# Change the header of the admin site
admin.site.site_header = "Ecopack Administration"
admin.site.site_title = "Ecopack Admin Portal"
admin.site.index_title = "Welcome to Ecopack Inventory Management"
