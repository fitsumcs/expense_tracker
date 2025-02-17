from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend

from expenses.filters.expense import ExpenseFilter
from expenses.serializers.expense import ExpenseCreateSerializer, ExpenseSerializer
from expenses.services.expense import ExpenseService


class ExpenseListCreateView(ListAPIView):
    permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExpenseFilter

    def get_queryset(self):
        return ExpenseService.get_expenses(self.request.user)

    def get_serializer_context(self):
        # Pass the request to the serializer context
        return {'request': self.request}

    def post(self, request):
        serializer = ExpenseCreateSerializer(data=request.data)
        if serializer.is_valid():
            expense = ExpenseService.create_expense(serializer.validated_data, request.user)
            return Response(ExpenseCreateSerializer(expense, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExpenseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """
        Retrieve an expense by ID.
        """
        expense = ExpenseService.get_expense(id, request.user)
        serializer = ExpenseSerializer(expense, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        """
        Update an expense by ID.
        """
        expense = ExpenseService.update_expense(id, request.user, request.data)
        serializer = ExpenseSerializer(expense, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        """
        Delete an expense by ID.
        """
        response_message = ExpenseService.delete_expense(id, request.user)
        return Response(response_message, status=status.HTTP_204_NO_CONTENT)

class ExportExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        try:
            # Validate the date range
            ExpenseService.validate_date_range(start_date, end_date)

            # Fetch expenses
            admin = request.user.role == 'admin'
            expenses = ExpenseService.get_expenses_for_export(start_date, end_date, request.user, admin)

            # Generate the CSV content
            csv_content = ExpenseService.generate_csv(expenses, include_user=admin)

            # Create the HTTP response with the CSV file
            response = HttpResponse(csv_content, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="expenses_{start_date}_to_{end_date}.csv"'

            return response

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ExpenseAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            analytics = ExpenseService.generate_analytics(request.user)
            return Response(analytics)
        except Exception as e:
            return Response({"error": str(e)}, status=500)