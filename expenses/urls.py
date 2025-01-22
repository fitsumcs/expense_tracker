from django.urls import path
from .views import ExpenseAnalyticsView, ExpenseDetailView, ExpenseListCreateView, ExportExpensesView, UserProfileUpdateView, UserRegistrationView

urlpatterns = [
    path('expenses/', ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('expenses/<int:id>/', ExpenseDetailView.as_view(), name='expense-detail'),
    path('expenses/export/', ExportExpensesView.as_view(), name='expense-export'),

    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('user/profile/', UserProfileUpdateView.as_view(), name='user-profile-update'),

    path('analytics/', ExpenseAnalyticsView.as_view(), name='expense-analytics'),
]


