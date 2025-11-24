from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from .models import Todo, Category, TodoAttachment, TodoShare
from .utils import export_todos_to_json, export_todos_to_csv, import_todos_from_json, import_todos_from_csv
from django.contrib.auth.models import User
from django.utils import timezone
import json


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'todo/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'todo/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('todo_list')
    
    return render(request, 'todo/register.html')


@login_required
def todo_list(request):
    todos = Todo.objects.filter(
        Q(user=request.user) | Q(shares__shared_with=request.user)
    ).distinct().order_by('-created_at')
    
    categories = Category.objects.filter(user=request.user)
    
    # Get query parameters for filtering
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    if status_filter:
        todos = todos.filter(status=status_filter)
    
    if category_filter:
        todos = todos.filter(category_id=category_filter)
    
    if search_query:
        todos = todos.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'todos': todos,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    return render(request, 'todo/todo_list.html', context)


@login_required
def todo_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST.get('description', '')
        due_date = request.POST.get('due_date', None)
        priority = request.POST.get('priority', 'medium')
        category_id = request.POST.get('category', None)
        
        todo = Todo.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            user=request.user
        )
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id, user=request.user)
                todo.category = category
                todo.save()
            except Category.DoesNotExist:
                pass
        
        # Handle file attachments
        if request.FILES.getlist('attachments'):
            for file in request.FILES.getlist('attachments'):
                TodoAttachment.objects.create(
                    todo=todo,
                    file=file,
                    file_name=file.name
                )
        
        messages.success(request, 'Todo created successfully!')
        return redirect('todo_list')
    
    categories = Category.objects.filter(user=request.user)
    return render(request, 'todo/todo_form.html', {'categories': categories, 'action': 'Create'})


@login_required
def todo_update(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    
    # Check if user has permission to edit this todo
    if todo.user != request.user and not todo.shares.filter(shared_with=request.user, can_edit=True).exists():
        messages.error(request, 'You do not have permission to edit this todo.')
        return redirect('todo_list')
    
    if request.method == 'POST':
        todo.title = request.POST['title']
        todo.description = request.POST.get('description', '')
        todo.due_date = request.POST.get('due_date', None)
        todo.priority = request.POST.get('priority', 'medium')
        todo.status = request.POST.get('status', 'pending')
        
        if 'completed' in request.POST:
            if request.POST['completed'] == 'true' and todo.status != 'completed':
                todo.status = 'completed'
                todo.completed_at = timezone.now()
            elif request.POST['completed'] == 'false':
                todo.status = 'pending'
                todo.completed_at = None
        
        category_id = request.POST.get('category', None)
        if category_id:
            try:
                category = Category.objects.get(id=category_id, user=request.user)
                todo.category = category
            except Category.DoesNotExist:
                pass
        else:
            todo.category = None
        
        todo.save()
        
        # Handle file attachments
        if request.FILES.getlist('attachments'):
            for file in request.FILES.getlist('attachments'):
                TodoAttachment.objects.create(
                    todo=todo,
                    file=file,
                    file_name=file.name
                )
        
        messages.success(request, 'Todo updated successfully!')
        return redirect('todo_list')
    
    categories = Category.objects.filter(user=request.user)
    return render(request, 'todo/todo_form.html', {
        'todo': todo, 
        'categories': categories, 
        'action': 'Update'
    })


@login_required
def todo_delete(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    
    # Check if user has permission to delete this todo
    if todo.user != request.user and not todo.shares.filter(shared_with=request.user).exists():
        messages.error(request, 'You do not have permission to delete this todo.')
        return redirect('todo_list')
    
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Todo deleted successfully!')
        return redirect('todo_list')
    
    return render(request, 'todo/todo_confirm_delete.html', {'todo': todo})


@login_required
def todo_toggle_complete(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    
    # Check if user has permission to edit this todo
    if todo.user != request.user and not todo.shares.filter(shared_with=request.user, can_edit=True).exists():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if todo.status == 'completed':
        todo.status = 'pending'
        todo.completed_at = None
    else:
        todo.status = 'completed'
        todo.completed_at = timezone.now()
    
    todo.save()
    return JsonResponse({'status': todo.status, 'completed_at': todo.completed_at.isoformat() if todo.completed_at else None})


@login_required
def category_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        color = request.POST.get('color', '#007bff')
        
        Category.objects.create(
            name=name,
            color=color,
            user=request.user
        )
        
        messages.success(request, 'Category created successfully!')
        return redirect('todo_list')
    
    return redirect('todo_list')


@login_required
def share_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    
    # Only the owner can share the todo
    if todo.user != request.user:
        messages.error(request, 'You can only share todos you created.')
        return redirect('todo_list')
    
    if request.method == 'POST':
        username = request.POST['username']
        can_edit = request.POST.get('can_edit', 'false') == 'true'
        
        try:
            shared_with_user = User.objects.get(username=username)
            
            # Check if already shared
            share, created = TodoShare.objects.get_or_create(
                todo=todo,
                shared_with=shared_with_user,
                defaults={
                    'shared_by': request.user,
                    'can_edit': can_edit
                }
            )
            
            if created:
                messages.success(request, f'Todo shared with {username} successfully!')
            else:
                share.can_edit = can_edit
                share.save()
                messages.success(request, f'Sharing permissions updated for {username}!')
                
        except User.DoesNotExist:
            messages.error(request, f'User {username} does not exist.')
    
    return redirect('todo_list')


@login_required
@require_http_methods(["GET"])
def todo_search(request):
    query = request.GET.get('q', '')
    if query:
        todos = Todo.objects.filter(
            Q(user=request.user) | Q(shares__shared_with=request.user),
            Q(title__icontains=query) | Q(description__icontains=query)
        ).distinct()
        
        results = []
        for todo in todos:
            results.append({
                'id': todo.id,
                'title': todo.title,
                'description': todo.description,
                'status': todo.status,
                'priority': todo.priority,
                'due_date': todo.due_date.isoformat() if todo.due_date else None,
                'category': todo.category.name if todo.category else None,
            })
        
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})


@login_required
def export_todos(request):
    """Export todos to JSON or CSV format"""
    export_format = request.GET.get('format', 'json')
    include_completed = request.GET.get('completed', 'true').lower() == 'true'
    
    if export_format == 'csv':
        return export_todos_to_csv(request.user, include_completed)
    else:  # default to json
        json_data = export_todos_to_json(request.user, include_completed)
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="todos_{request.user.username}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response


@login_required
def import_todos(request):
    """Import todos from JSON or CSV file"""
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            messages.error(request, 'No file uploaded')
            return redirect('todo_list')
        
        file_name = uploaded_file.name
        imported_count = 0
        
        try:
            if file_name.endswith('.json'):
                # Read and decode the JSON file
                json_data = uploaded_file.read().decode('utf-8')
                imported_count = import_todos_from_json(request.user, json_data)
            elif file_name.endswith('.csv'):
                imported_count = import_todos_from_csv(request.user, uploaded_file)
            else:
                messages.error(request, 'Unsupported file format. Please upload a JSON or CSV file.')
                return redirect('todo_list')
            
            messages.success(request, f'Successfully imported {imported_count} todos!')
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
    
def bad_request(request, exception):
    """400 Bad Request handler"""
    return render(request, 'todo/400.html', status=40)


def permission_denied(request, exception):
    """403 Permission Denied handler"""
    return render(request, 'todo/403.html', status=403)


def page_not_found(request, exception):
    """404 Page Not Found handler"""
    return render(request, 'todo/404.html', status=404)


def server_error(request):
    """500 Server Error handler"""
    return render(request, 'todo/500.html', status=500)
    return redirect('todo_list')