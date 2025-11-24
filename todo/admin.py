from django.contrib import admin
from .models import Todo, Category, TodoAttachment, TodoShare

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at', 'due_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name']


@admin.register(TodoAttachment)
class TodoAttachmentAdmin(admin.ModelAdmin):
    list_display = ['todo', 'file_name', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['file_name', 'todo__title']


@admin.register(TodoShare)
class TodoShareAdmin(admin.ModelAdmin):
    list_display = ['todo', 'shared_by', 'shared_with', 'can_edit', 'shared_at']
    list_filter = ['can_edit', 'shared_at']
    search_fields = ['shared_by__username', 'shared_with__username', 'todo__title']