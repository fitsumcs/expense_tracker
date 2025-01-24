from django_filters import rest_framework as filters

from expenses.models import Expense

class ExpenseFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="date", lookup_expr="lte")
    min_amount = filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr="lte")
    category = filters.CharFilter(field_name="category", lookup_expr="icontains")

    class Meta:
        model = Expense
        fields = ['category', 'start_date', 'end_date', 'min_amount', 'max_amount']