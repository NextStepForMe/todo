import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from todo.models import Todo, Category

def create_sample_data():
    # Create a sample user if one doesn't exist
    user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('demopass123')
        user.save()
        print("Created demo user: demo / demopass123")
    else:
        print("Demo user already exists")
    
    # Create sample categories
    categories_data = [
        {'name': 'Work', 'color': '#0d6efd'},
        {'name': 'Personal', 'color': '#198754'},
        {'name': 'Shopping', 'color': '#fd7e14'},
        {'name': 'Health', 'color': '#dc3545'},
        {'name': 'Learning', 'color': '#6f42c1'},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            user=user,
            defaults={'color': cat_data['color']}
        )
        if created:
            print(f"Created category: {cat_data['name']}")
        else:
            print(f"Category {cat_data['name']} already exists")
    
    # Create sample todos
    sample_todos = [
        {
            'title': 'Complete project proposal',
            'description': 'Finish the proposal document for the new client project',
            'priority': 'high',
            'status': 'pending',
        },
        {
            'title': 'Buy groceries',
            'description': 'Milk, eggs, bread, fruits, and vegetables',
            'priority': 'medium',
            'status': 'pending',
        },
        {
            'title': 'Schedule dentist appointment',
            'description': 'Call Dr. Smith to schedule a checkup',
            'priority': 'low',
            'status': 'in_progress',
        },
        {
            'title': 'Read Django documentation',
            'description': 'Read the latest Django documentation to learn about new features',
            'priority': 'medium',
            'status': 'completed',
        },
        {
            'title': 'Plan weekend trip',
            'description': 'Research and plan the weekend getaway',
            'priority': 'high',
            'status': 'pending',
        },
    ]
    
    for todo_data in sample_todos:
        todo, created = Todo.objects.get_or_create(
            title=todo_data['title'],
            user=user,
            defaults={
                'description': todo_data['description'],
                'priority': todo_data['priority'],
                'status': todo_data['status'],
            }
        )
        if created:
            print(f"Created todo: {todo_data['title']}")
        else:
            print(f"Todo {todo_data['title']} already exists")
    
    print("\nSample data initialization complete!")
    print("You can now log in with:")
    print(" Username: demo")
    print("  Password: demopass123")

if __name__ == '__main__':
    create_sample_data()