from django.shortcuts import get_object_or_404

from users.models import CustomUser

class UserRepository:
    @staticmethod
    def create_user(data):
        """
        Create a new user in the database.
        """
        return CustomUser.objects.create_user(**data)

    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve a user by ID.
        """
        return get_object_or_404(CustomUser, id=user_id)

    @staticmethod
    def update_user(user, data):
        """
        Update user details.
        """
        for field, value in data.items():
            setattr(user, field, value)
        user.save()
        return user
