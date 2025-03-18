from django.urls import path
from .views import RegisterView, SigninView, SignOutView, GenerateOTPView, ResetPasswordView
from .views import AddMonthlyIncomeView, LockMonthlyIncomeView, ViewIncomeView, ViewExpensesView
from .views import AddCategoryView, AddExpenseView, EditExpenseView, DeleteExpenseView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('signout/', SignOutView.as_view(), name='signout'),
    path('generate_otp/', GenerateOTPView.as_view(), name='generate_otp'),
    path('reset_password/', ResetPasswordView.as_view(), name='reset_password'),
    path('add_income/', AddMonthlyIncomeView.as_view(), name='add_income'),
    path('lock_income/<str:month>/', LockMonthlyIncomeView.as_view(), name='lock_income'),
    path('add_category/', AddCategoryView.as_view(), name='add_category'),
    path('add_expense/', AddExpenseView.as_view(), name='add_expense'),
    path('edit_expense/<int:expense_id>/', EditExpenseView.as_view(), name='edit_expense'),
    path('delete_expense/<int:expense_id>/', DeleteExpenseView.as_view(), name='delete_expense'),
    path("view_income/", ViewIncomeView.as_view(), name="view_income"),
    path("view_expenses/", ViewExpensesView.as_view(), name="view_expenses"),
]


