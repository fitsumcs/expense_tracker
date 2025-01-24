from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncWeek

from ..models import Expense


class ExpenseRepository:
    @staticmethod
    def create_expense(data):
        """
        Save an expense to the database.
        """
        return Expense.objects.create(**data)
    
    @staticmethod
    def get_all_expenses():
        """
        Retrieve all expenses.
        """
        return Expense.objects.all()

    @staticmethod
    def get_user_expenses(user):
        """
        Retrieve expenses for a specific user.
        """
        return Expense.objects.filter(user=user)
    
    @staticmethod
    def get_expense_by_id(expense_id, user=None, admin=False):
        """
        Retrieve an expense by ID.
        If admin, ignore the user filter.
        """
        if admin:
            return get_object_or_404(Expense, id=expense_id)
        return get_object_or_404(Expense, id=expense_id, user=user)

    @staticmethod
    def update_expense(expense, data):
        """
        Update an expense with the given data.
        """
        for field, value in data.items():
            setattr(expense, field, value)
        expense.save()
        return expense

    @staticmethod
    def delete_expense(expense):
        """
        Delete the given expense.
        """
        expense.delete()

    @staticmethod
    def get_expenses_by_date_range(start_date, end_date, user=None, admin=False):
        """
        Retrieve expenses within a date range.
        If admin, ignore the user filter.
        """
        query = Expense.objects.filter(date__range=[start_date, end_date])
        if not admin:
            query = query.filter(user=user)
        return query

    @staticmethod
    def get_expenses_by_category(user=None, admin=False):
        """
        Aggregate total expenses per category.
        """
        query = Expense.objects
        if not admin:
            query = query.filter(user=user)
        return query.values('category').annotate(total=Sum('amount'))

    @staticmethod
    def get_monthly_totals(current_year, user=None, admin=False):
        """
        Aggregate total expenses by month for the current year.
        """
        query = Expense.objects.filter(date__year=current_year)
        if not admin:
            query = query.filter(user=user)
        return query.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')

    @staticmethod
    def get_weekly_trends(last_month, user=None, admin=False):
        """
        Aggregate total expenses by week for the last month.
        """
        query = Expense.objects.filter(date__month=last_month)
        if not admin:
            query = query.filter(user=user)
        return query.annotate(week=TruncWeek('date')).values('week').annotate(total=Sum('amount')).order_by('week')

    @staticmethod
    def get_highest_spending_category(user=None, admin=False):
        """
        Get the category with the highest total spending.
        """
        return ExpenseRepository.get_expenses_by_category(user=user, admin=admin).order_by('-total').first()

    @staticmethod
    def get_highest_single_expense(user=None, admin=False):
        """
        Get the expense with the highest amount.
        """
        query = Expense.objects
        if not admin:
            query = query.filter(user=user)
        return query.order_by('-amount').first()
    


   
