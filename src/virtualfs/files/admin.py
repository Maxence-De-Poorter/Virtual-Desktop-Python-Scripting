from django.contrib import admin
from .models import Folder, File, Video

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("name", "folder")

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "folder", "file")

