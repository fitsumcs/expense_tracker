from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Expense
from .serializers import ExpenseSerializer, UserProfileUpdateSerializer, UserRegistrationSerializer
import csv
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ExpenseFilter
from django.db.models import Sum, F, Max
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import timedelta, date

User = get_user_model()

class ExpenseListCreateView(ListAPIView):
    permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExpenseFilter

    def get_queryset(self):
        # Admins see all expenses; regular users see only their own
        if self.request.user.role == 'admin':
            return Expense.objects.all()
        return Expense.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        # Pass the request to the serializer context
        return {'request': self.request}

    def post(self, request):
        # Create a new expense
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = ExpenseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExpenseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, expense_id, user):
        if user.role == 'admin':
            # Admins can access any expense
            return get_object_or_404(Expense, id=expense_id)
        else:
            # Regular users can only access their own expenses
            return get_object_or_404(Expense, id=expense_id, user=user)

    def get(self, request, id):
        # Retrieve a single expense by ID
        expense = self.get_object(id, request.user)
        serializer = ExpenseSerializer(expense, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        # Update an expense
        expense = self.get_object(id, request.user)
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        # Delete an expense
        expense = self.get_object(id, request.user)
        expense.delete()
        return Response({"message": "Expense deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

class ExportExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Validate date parameters
        if not start_date or not end_date:
            return Response(
                {"error": "Please provide both start_date and end_date in the format YYYY-MM-DD."},
                status=400
            )

        try:
            # Filter expenses based on user role and date range
            if request.user.role == 'admin':
                expenses = Expense.objects.filter(date__range=[start_date, end_date])
                include_user = True  # Include the username in the CSV
            else:
                expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date])
                include_user = False  # Do not include the username in the CSV

            # Create the CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="expenses_{start_date}_to_{end_date}.csv"'

            # Write to CSV
            writer = csv.writer(response)
            if include_user:
                writer.writerow(['Title', 'Amount', 'Category', 'Date', 'User'])  # CSV header for admin
            else:
                writer.writerow(['Title', 'Amount', 'Category', 'Date'])  # CSV header for regular users

            for expense in expenses:
                if include_user:
                    writer.writerow([expense.title, expense.amount, expense.category, expense.date, expense.user.username])
                else:
                    writer.writerow([expense.title, expense.amount, expense.category, expense.date])

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ExpenseAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Base queryset: Filter by user unless the user is an admin
        if request.user.role == 'admin':
            expenses = Expense.objects.all()
        else:
            expenses = Expense.objects.filter(user=request.user)

        # 1. Total expenses per category
        category_summary = expenses.values('category').annotate(total=Sum('amount'))

        # 2. Monthly totals for the current year
        current_year = date.today().year
        monthly_summary = expenses.filter(date__year=current_year).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(total=Sum('amount')).order_by('month')

        # 3. Weekly trends for the last month
        last_month = (date.today().replace(day=1) - timedelta(days=1)).month
        weekly_trends = expenses.filter(date__month=last_month).annotate(
            week=TruncWeek('date')
        ).values('week').annotate(total=Sum('amount')).order_by('week')

        # 4. Highest spending category
        highest_spending_category = category_summary.order_by('-total').first()

        # 5. Highest single expense
        highest_single_expense = expenses.order_by('-amount').first()

        # Format the response
        response_data = {
            "category_summary": {entry['category']: entry['total'] for entry in category_summary},
            "monthly_summary": {
                entry['month'].strftime('%B'): entry['total'] for entry in monthly_summary
            },
            "weekly_trends": [
                {"week": entry['week'].strftime('%Y-%m-%d'), "total": entry['total']}
                for entry in weekly_trends
            ],
            "highest_spending_category": highest_spending_category['category'] if highest_spending_category else None,
            "highest_single_expense": {
                "title": highest_single_expense.title,
                "amount": highest_single_expense.amount,
                "category": highest_single_expense.category,
                "date": highest_single_expense.date
            } if highest_single_expense else None,
        }

        return Response(response_data)

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        # Check if the admin is updating another user's profile
        if request.user.role == 'admin' and 'user_id' in request.data:
            user = get_object_or_404(User, id=request.data['user_id'])
        else:
            # Regular users can only update their own profile
            user = request.user

        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)