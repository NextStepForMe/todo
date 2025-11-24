from rest_framework import serializers
from .models import Todo, Category, TodoAttachment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'created_at']
        read_only_fields = ['user']


class TodoAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoAttachment
        fields = ['id', 'file', 'file_name', 'uploaded_at']


class TodoSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    attachments = TodoAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'description', 'created_at', 'updated_at', 
            'due_date', 'priority', 'status', 'completed_at', 
            'category', 'category_id', 'attachments', 'is_shared'
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id, user=self.context['request'].user)
            except Category.DoesNotExist:
                pass
        
        todo = Todo.objects.create(**validated_data, user=self.context['request'].user, category=category)
        return todo

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id is not None:
            try:
                category = Category.objects.get(id=category_id, user=self.context['request'].user)
                instance.category = category
            except Category.DoesNotExist:
                instance.category = None
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance