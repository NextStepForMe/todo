from django.urls import path
from . import api_views

urlpatterns = [
    # Todo endpoints
    path('todos/', api_views.TodoListCreateView.as_view(), name='api-todo-list-create'),
    path('todos/<int:pk>/', api_views.TodoDetailView.as_view(), name='api-todo-detail'),
    path('todos/<int:pk>/toggle-status/', api_views.toggle_todo_status, name='api-todo-toggle-status'),
    path('todos/search/', api_views.search_todos, name='api-todo-search'),
    path('todos/stats/', api_views.todo_stats, name='api-todo-stats'),
    
    # Category endpoints
    path('categories/', api_views.CategoryListCreateView.as_view(), name='api-category-list-create'),
    path('categories/<int:pk>/', api_views.CategoryDetailView.as_view(), name='api-category-detail'),
]