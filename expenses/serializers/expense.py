from rest_framework import serializers

from expenses.models import Expense


class ExpenseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        exclude = ['user']  # Exclude the user field for POST requests

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