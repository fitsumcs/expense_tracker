from rest_framework import serializers
from .models import Expense
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

    def to_representation(self, instance):
        """
        Customize the fields returned in the response.
        """
        representation = super().to_representation(instance)

        request = self.context.get('request')  
        if request and request.user.role != 'admin':
            representation.pop('user', None)

        return representation



User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'role']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        read_only_fields = ['username']  # Prevent updating the username

