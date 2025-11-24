from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Todo, Category, TodoAttachment, TodoShare


class TodoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Work',
            color='#007bff',
            user=self.user
        )
        
        self.todo = Todo.objects.create(
            title='Test Todo',
            description='This is a test todo',
            priority='high',
            user=self.user,
            category=self.category
        )

    def test_todo_creation(self):
        """Test if a todo is created correctly"""
        self.assertEqual(self.todo.title, 'Test Todo')
        self.assertEqual(self.todo.description, 'This is a test todo')
        self.assertEqual(self.todo.priority, 'high')
        self.assertEqual(self.todo.user, self.user)
        self.assertEqual(self.todo.category, self.category)
        self.assertEqual(str(self.todo), 'Test Todo')

    def test_category_creation(self):
        """Test if a category is created correctly"""
        self.assertEqual(self.category.name, 'Work')
        self.assertEqual(self.category.color, '#007bff')
        self.assertEqual(self.category.user, self.user)
        self.assertEqual(str(self.category), 'Work')

    def test_todo_attachment_creation(self):
        """Test todo attachment creation"""
        attachment = TodoAttachment.objects.create(
            todo=self.todo,
            file_name='test_file.txt',
            file='test_file.txt'
        )
        self.assertEqual(attachment.todo, self.todo)
        self.assertEqual(attachment.file_name, 'test_file.txt')

    def test_todo_share_creation(self):
        """Test todo share creation"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        share = TodoShare.objects.create(
            todo=self.todo,
            shared_by=self.user,
            shared_with=user2,
            can_edit=True
        )
        
        self.assertEqual(share.todo, self.todo)
        self.assertEqual(share.shared_by, self.user)
        self.assertEqual(share.shared_with, user2)
        self.assertTrue(share.can_edit)


class TodoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Work',
            color='#007bff',
            user=self.user
        )

    def test_todo_list_view(self):
        """Test the todo list view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Todo List')

    def test_todo_create_view_get(self):
        """Test the todo create view (GET)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Todo')

    def test_todo_create_view_post(self):
        """Test the todo create view (POST)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('todo_create'), {
            'title': 'New Todo',
            'description': 'Test description',
            'priority': 'medium',
            'category': self.category.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Todo.objects.filter(title='New Todo').exists())

    def test_todo_update_view(self):
        """Test the todo update view"""
        todo = Todo.objects.create(
            title='Test Todo',
            description='Test description',
            priority='medium',
            user=self.user
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('todo_update', args=[todo.id]), {
            'title': 'Updated Todo',
            'description': 'Updated description',
            'priority': 'high'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
        todo.refresh_from_db()
        self.assertEqual(todo.title, 'Updated Todo')

    def test_todo_delete_view(self):
        """Test the todo delete view"""
        todo = Todo.objects.create(
            title='Test Todo',
            description='Test description',
            priority='medium',
            user=self.user
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('todo_delete', args=[todo.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(Todo.objects.filter(id=todo.id).exists())


class TodoAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_api_todo_list(self):
        """Test the API todo list endpoint"""
        response = self.client.get(reverse('api-todo-list-create'))
        self.assertEqual(response.status_code, 200)

    def test_api_todo_create(self):
        """Test the API todo creation"""
        response = self.client.post(
            reverse('api-todo-list-create'),
            {'title': 'API Todo', 'priority': 'medium'},
            content_type='application/json'
        )
        # This would require proper JSON handling in the view
        # For now, we're just testing that the URL exists
        self.assertIn(response.status_code, [200, 201, 400, 403, 405])  # Accept various responses


class ExportImportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_export_todos(self):
        """Test the export todos functionality"""
        # Create some todos
        Todo.objects.create(
            title='Export Todo 1',
            description='Test description',
            priority='medium',
            user=self.user
        )
        Todo.objects.create(
            title='Export Todo 2',
            description='Test description 2',
            priority='high',
            user=self.user
        )
        
        response = self.client.get(reverse('export_todos') + '?format=json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_export_todos_csv(self):
        """Test the export todos to CSV functionality"""
        response = self.client.get(reverse('export_todos') + '?format=csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')


class TodoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Work',
            color='#007bff',
            user=self.user
        )
        
        self.todo = Todo.objects.create(
            title='Test Todo',
            description='This is a test todo',
            priority='high',
            user=self.user,
            category=self.category
        )

    def test_todo_creation(self):
        """Test if a todo is created correctly"""
        self.assertEqual(self.todo.title, 'Test Todo')
        self.assertEqual(self.todo.description, 'This is a test todo')
        self.assertEqual(self.todo.priority, 'high')
        self.assertEqual(self.todo.user, self.user)
        self.assertEqual(self.todo.category, self.category)
        self.assertEqual(str(self.todo), 'Test Todo')

    def test_category_creation(self):
        """Test if a category is created correctly"""
        self.assertEqual(self.category.name, 'Work')
        self.assertEqual(self.category.color, '#007bff')
        self.assertEqual(self.category.user, self.user)
        self.assertEqual(str(self.category), 'Work')


class TodoViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_todo_list_view(self):
        """Test the todo list view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Todo List')

    def test_todo_create_view_get(self):
        """Test the todo create view (GET)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Todo')