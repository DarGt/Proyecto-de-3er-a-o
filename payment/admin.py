from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem
from unfold.admin import ModelAdmin, TabularInline

class OrderItemInline(TabularInline):  
    model = OrderItem
    extra = 0

@admin.register(ShippingAddress)
class ShippingAddressAdmin(ModelAdmin):
    list_display = [field.name for field in ShippingAddress._meta.fields]

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = ["user", "full_name", "email", "shipping_address", "amount_paid", "date_ordered", "shipped", "date_shipped"]
    inlines = [OrderItemInline]
    list_display = [field.name for field in Order._meta.fields]
    search_fields = ["user__username", "email"]
    list_filter = ["shipped", "date_ordered"]

# Si quieres registrar OrderItem también:
@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = [field.name for field in OrderItem._meta.fields]