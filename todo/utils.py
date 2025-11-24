import json
import csv
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Todo, Category


def export_todos_to_json(user, include_completed=True):
    """Export user's todos to JSON format"""
    todos = Todo.objects.filter(user=user)
    if not include_completed:
        todos = todos.exclude(status='completed')
    
    data = []
    for todo in todos:
        todo_data = {
            'title': todo.title,
            'description': todo.description,
            'created_at': todo.created_at.isoformat() if todo.created_at else None,
            'updated_at': todo.updated_at.isoformat() if todo.updated_at else None,
            'due_date': todo.due_date.isoformat() if todo.due_date else None,
            'priority': todo.priority,
            'status': todo.status,
            'completed_at': todo.completed_at.isoformat() if todo.completed_at else None,
            'category': todo.category.name if todo.category else None,
            'is_shared': todo.is_shared,
        }
        data.append(todo_data)
    
    return json.dumps(data, indent=2)


def export_todos_to_csv(user, include_completed=True):
    """Export user's todos to CSV format"""
    todos = Todo.objects.filter(user=user)
    if not include_completed:
        todos = todos.exclude(status='completed')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="todos_{user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Title', 'Description', 'Created At', 'Updated At', 'Due Date', 
        'Priority', 'Status', 'Completed At', 'Category', 'Is Shared'
    ])
    
    for todo in todos:
        writer.writerow([
            todo.title,
            todo.description,
            todo.created_at.strftime('%Y-%m-%d %H:%M:%S') if todo.created_at else '',
            todo.updated_at.strftime('%Y-%m-%d %H:%M:%S') if todo.updated_at else '',
            todo.due_date.strftime('%Y-%m-%d %H:%M:%S') if todo.due_date else '',
            todo.priority,
            todo.status,
            todo.completed_at.strftime('%Y-%m-%d %H:%M:%S') if todo.completed_at else '',
            todo.category.name if todo.category else '',
            todo.is_shared
        ])
    
    return response


def import_todos_from_json(user, json_data):
    """Import todos from JSON data"""
    try:
        data = json.loads(json_data)
        imported_count = 0
        
        for item in data:
            # Find or create category
            category = None
            if item.get('category'):
                category, created = Category.objects.get_or_create(
                    name=item['category'],
                    user=user,
                    defaults={'color': '#007bff'}  # default color
                )
            
            # Create the todo
            Todo.objects.get_or_create(
                title=item['title'],
                user=user,
                defaults={
                    'description': item.get('description', ''),
                    'due_date': item.get('due_date'),
                    'priority': item.get('priority', 'medium'),
                    'status': item.get('status', 'pending'),
                    'completed_at': item.get('completed_at'),
                    'category': category,
                    'is_shared': item.get('is_shared', False),
                }
            )
            imported_count += 1
        
        return imported_count
    except json.JSONDecodeError:
        return 0
    except Exception:
        return 0


def import_todos_from_csv(user, csv_file):
    """Import todos from CSV file"""
    try:
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        imported_count = 0
        for row in reader:
            # Find or create category
            category = None
            if row.get('Category'):
                category, created = Category.objects.get_or_create(
                    name=row['Category'],
                    user=user,
                    defaults={'color': '#007bff'}  # default color
                )
            
            # Create the todo
            Todo.objects.get_or_create(
                title=row['Title'],
                user=user,
                defaults={
                    'description': row.get('Description', ''),
                    'due_date': row.get('Due Date'),
                    'priority': row.get('Priority', 'medium'),
                    'status': row.get('Status', 'pending'),
                    'completed_at': row.get('Completed At') or None,
                    'category': category,
                    'is_shared': row.get('Is Shared', 'False').lower() == 'true',
                }
            )
            imported_count += 1
        
        return imported_count
    except Exception:
        return 0