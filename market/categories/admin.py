from django.contrib import admin
from django.contrib.admin.decorators import register

from .models import Category, SubCategory


@register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'is_active', 'sort_index']
    list_display = ['name', 'is_active', 'sort_index']
    list_filter = ['is_active']


@register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    fields = ['parent_id', 'name', 'is_active', 'sort_index']
    list_display = ['name', 'parent_id', 'is_active', 'sort_index']
    list_filter = ['is_active', 'parent_id']
