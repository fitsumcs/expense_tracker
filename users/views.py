from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.serializers.user_profile import UserProfileUpdateSerializer
from users.serializers.user_registration import UserRegistrationSerializer
from users.services.user import UserService


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            UserService.register_user(serializer.validated_data)
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            user_id = request.data.get('user_id') if request.user.role == 'admin' else request.user.id
            updated_user = UserService.update_user_profile(user_id, request.data)
            serializer = UserProfileUpdateSerializer(updated_user)
            return Response({"message": "Profile updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
