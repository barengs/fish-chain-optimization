from django.contrib import admin
from .models import FishingArea

@admin.register(FishingArea)
class FishingAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')
