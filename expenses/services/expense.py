
import csv
from io import StringIO
from datetime import date, timedelta

from expenses.repositories.expense import ExpenseRepository


class ExpenseService:
    @staticmethod
    def create_expense(data, user):
        """
        Prepare expense data and create it using the repository.
        """
        # Add the user to the data
        data['user'] = user
        # Call the repository to save the expense
        return ExpenseRepository.create_expense(data)
    
    @staticmethod
    def get_expenses(user):
        """
        Retrieve expenses based on the user's role.
        """
        if user.role == 'admin':
            return ExpenseRepository.get_all_expenses()
        return ExpenseRepository.get_user_expenses(user)
    
    @staticmethod
    def get_expense(expense_id, user):
        """
        Retrieve an expense by ID, considering the user's role.
        """
        admin = user.role == 'admin'
        return ExpenseRepository.get_expense_by_id(expense_id, user=user, admin=admin)

    @staticmethod
    def update_expense(expense_id, user, data):
        """
        Update an expense after validating permissions.
        """
        expense = ExpenseService.get_expense(expense_id, user)
        return ExpenseRepository.update_expense(expense, data)

    @staticmethod
    def delete_expense(expense_id, user):
        """
        Delete an expense after validating permissions.
        """
        expense = ExpenseService.get_expense(expense_id, user)
        ExpenseRepository.delete_expense(expense)
        return {"message": "Expense deleted successfully!"}

    @staticmethod
    def validate_date_range(start_date, end_date):
        """
        Validate that the date range is provided and correctly formatted.
        """
        if not start_date or not end_date:
            raise ValueError("Both start_date and end_date are required.")

    @staticmethod
    def get_expenses_for_export(start_date, end_date, user, admin):
        """
        Fetch expenses for the given date range and user context.
        """
        return ExpenseRepository.get_expenses_by_date_range(
            start_date=start_date, end_date=end_date, user=user, admin=admin
        )

    @staticmethod
    def generate_csv(expenses, include_user=False):
        """
        Generate a CSV from the provided expenses.
        """
        # Use StringIO to write to an in-memory string buffer
        output = StringIO()
        writer = csv.writer(output)

        # Write the header row
        if include_user:
            writer.writerow(['Title', 'Amount', 'Category', 'Date', 'User'])
        else:
            writer.writerow(['Title', 'Amount', 'Category', 'Date'])

        # Write the expense rows
        for expense in expenses:
            row = [expense.title, expense.amount, expense.category, expense.date]
            if include_user:
                row.append(expense.user.username)
            writer.writerow(row)

        # Return the CSV content as a string
        return output.getvalue()

    @staticmethod
    def generate_analytics(user):
        """
        Generate analytics data.
        """
        admin = user.role == 'admin'

        # 1. Total expenses per category
        category_summary = ExpenseRepository.get_expenses_by_category(user=user, admin=admin)

        # 2. Monthly totals for the current year
        current_year = date.today().year
        monthly_summary = ExpenseRepository.get_monthly_totals(current_year, user=user, admin=admin)

        # 3. Weekly trends for the last month
        last_month = (date.today().replace(day=1) - timedelta(days=1)).month
        weekly_trends = ExpenseRepository.get_weekly_trends(last_month, user=user, admin=admin)

        # 4. Highest spending category
        highest_category = ExpenseRepository.get_highest_spending_category(user=user, admin=admin)

        # 5. Highest single expense
        highest_expense = ExpenseRepository.get_highest_single_expense(user=user, admin=admin)

        # Format the response
        return {
            "category_summary": {entry['category']: entry['total'] for entry in category_summary},
            "monthly_summary": {
                entry['month'].strftime('%B'): entry['total'] for entry in monthly_summary
            },
            "weekly_trends": [
                {"week": entry['week'].strftime('%Y-%m-%d'), "total": entry['total']}
                for entry in weekly_trends
            ],
            "highest_spending_category": highest_category['category'] if highest_category else None,
            "highest_single_expense": {
                "title": highest_expense.title,
                "amount": highest_expense.amount,
                "category": highest_expense.category,
                "date": highest_expense.date
            } if highest_expense else None,
        }
