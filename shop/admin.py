from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount', 'stock', 'rating', 'is_featured', 'is_popular', 'created_at')
    list_filter = ('category', 'is_featured', 'is_popular', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'discount', 'stock', 'is_featured', 'is_popular')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'full_name', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'full_name', 'phone', 'address')
    list_editable = ('status',)
    inlines = [OrderItemInline]