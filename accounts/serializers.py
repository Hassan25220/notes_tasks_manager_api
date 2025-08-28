from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Task, Note




class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, min_length = 6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    # Custom create serializers function for password hash
    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password= validated_data['password']
        )
        return user
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class TaskSerializer(serializers.ModelSerializer):
    # response me username show hoga; write time par user auto-assign hoga view me
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Task
        fields = ['id', 'user', 'title', 'description', 'completed', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class NoteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Note
        fields = ['id', 'user', 'title', 'content', 'is_archived', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']