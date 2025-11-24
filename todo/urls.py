from django.urls import path
from . import views

urlpatterns = [
    path('', views.todo_list, name='todo_list'),
    path('create/', views.todo_create, name='todo_create'),
    path('update/<int:todo_id>/', views.todo_update, name='todo_update'),
    path('delete/<int:todo_id>/', views.todo_delete, name='todo_delete'),
    path('toggle-complete/<int:todo_id>/', views.todo_toggle_complete, name='todo_toggle_complete'),
    path('share/<int:todo_id>/', views.share_todo, name='share_todo'),
    path('search/', views.todo_search, name='todo_search'),
    path('category/create/', views.category_create, name='category_create'),
    path('export/', views.export_todos, name='export_todos'),
    path('import/', views.import_todos, name='import_todos'),
    path('register/', views.register_view, name='register'),
]