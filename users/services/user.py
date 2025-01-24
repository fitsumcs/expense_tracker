from users.repositories.user import UserRepository


class UserService:
    @staticmethod
    def register_user(data):
        """
        Register a new user.
        """
        return UserRepository.create_user(data)

    @staticmethod
    def update_user_profile(user_id, data):
        """
        Update a user's profile.
        """
        user = UserRepository.get_user_by_id(user_id)
        return UserRepository.update_user(user, data)
