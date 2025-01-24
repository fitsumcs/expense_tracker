from django.urls import path

from .views import ExpenseAnalyticsView, ExpenseDetailView, ExpenseListCreateView, ExportExpensesView

urlpatterns = [
    path('expenses/', ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('expenses/<int:id>/', ExpenseDetailView.as_view(), name='expense-detail'),
    path('expenses/export/', ExportExpensesView.as_view(), name='expense-export'),

    path('analytics/', ExpenseAnalyticsView.as_view(), name='expense-analytics'),
]


