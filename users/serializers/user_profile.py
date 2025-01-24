from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        read_only_fields = ['username']  # Prevent updating the username