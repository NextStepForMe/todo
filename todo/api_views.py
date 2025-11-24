from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Todo, Category, TodoAttachment
from .serializers import TodoSerializer, CategorySerializer


class TodoPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TodoListCreateView(generics.ListCreateAPIView):
    serializer_class = TodoSerializer
    pagination_class = TodoPagination

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(
            Q(user=user) | Q(shares__shared_with=user)
        ).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(
            Q(user=user) | Q(shares__shared_with=user)
        ).distinct()


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_todo_status(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    
    # Check if user has permission to edit this todo
    if todo.user != request.user and not todo.shares.filter(shared_with=request.user, can_edit=True).exists():
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if todo.status == 'completed':
        todo.status = 'pending'
        todo.completed_at = None
    else:
        todo.status = 'completed'
        from django.utils import timezone
        todo.completed_at = timezone.now()
    
    todo.save()
    serializer = TodoSerializer(todo, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_todos(request):
    query = request.GET.get('q', '')
    if query:
        todos = Todo.objects.filter(
            Q(user=request.user) | Q(shares__shared_with=request.user),
            Q(title__icontains=query) | Q(description__icontains=query)
        ).distinct()
        
        paginator = TodoPagination()
        page = paginator.paginate_queryset(todos, request)
        
        if page is not None:
            serializer = TodoSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = TodoSerializer(todos, many=True, context={'request': request})
        return Response(serializer.data)
    
    return Response([])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def todo_stats(request):
    user = request.user
    todos = Todo.objects.filter(
        Q(user=user) | Q(shares__shared_with=user)
    ).distinct()
    
    total = todos.count()
    completed = todos.filter(status='completed').count()
    pending = todos.filter(status='pending').count()
    in_progress = todos.filter(status='in_progress').count()
    high_priority = todos.filter(priority='high').count()
    
    return Response({
        'total': total,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'high_priority': high_priority
    })