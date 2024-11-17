from django.contrib import admin

# Register your models here.
from .models import Document, DocumentPhoto


class EntryPhotoInline(admin.TabularInline):
    model = DocumentPhoto


@admin.register(Document)
class EntryAdmin(admin.ModelAdmin):
    inlines = [EntryPhotoInline]
