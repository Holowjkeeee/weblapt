from django.contrib import admin
from .models import Brand, ProcessorBrand, ProcessorFamily, Laptop, Review

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(ProcessorBrand)
class ProcessorBrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(ProcessorFamily)
class ProcessorFamilyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'brand']
    list_filter = ['brand']

@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'brand', 'processor_family', 'processor_model', 'price', 'ram', 'storage']
    list_filter = ['brand', 'processor_family']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'author_name', 'laptop']