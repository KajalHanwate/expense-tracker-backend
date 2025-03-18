import random
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import MonthlyIncome
from .serializers import MonthlyIncomeSerializer
from .models import Expense, Category, MonthlyIncome
from .serializers import ExpenseSerializer, CategorySerializer
from decimal import Decimal
from rest_framework.decorators import APIView
from django.utils.text import capfirst
from django.db.models import Sum



User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class SigninView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class SignOutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Signout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token or token already used"}, status=status.HTTP_400_BAD_REQUEST)


class GenerateOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)


        otp = str(random.randint(100000, 999999))
        
        cache.set(f"otp_{email}", otp, timeout=300)

        return Response({"message": "OTP sent successfully", "otp": otp}, status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not all([email, otp, new_password, confirm_password]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        stored_otp = cache.get(f"otp_{email}")
        if not stored_otp:
            return Response({"error": "OTP expired or invalid"}, status=status.HTTP_400_BAD_REQUEST)

        if otp != stored_otp:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            cache.delete(f"otp_{email}")

            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class AddMonthlyIncomeView(generics.CreateAPIView):
    serializer_class = MonthlyIncomeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        month = request.data.get("month")
        income = request.data.get("income")

        if not month or not income:
            return Response({"error": "Month and income are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            monthly_income = MonthlyIncome.objects.get(user=user, month=month)
            if monthly_income.is_locked:
                return Response({"error": "Income for this month is locked and cannot be updated."}, status=status.HTTP_400_BAD_REQUEST)
            
            monthly_income.income = income
            monthly_income.save()
            return Response({"message": "Income updated successfully", "data": MonthlyIncomeSerializer(monthly_income).data}, status=status.HTTP_200_OK)
        
        except MonthlyIncome.DoesNotExist:
            new_income = MonthlyIncome.objects.create(user=user, month=month, income=income)
            return Response({"message": "Income added successfully", "data": MonthlyIncomeSerializer(new_income).data}, status=status.HTTP_201_CREATED)


class LockMonthlyIncomeView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, month):
        user = request.user
        try:
            monthly_income = MonthlyIncome.objects.get(user=user, month=month)
            monthly_income.is_locked = True
            monthly_income.save()
            return Response({"message": "Income locked successfully"}, status=status.HTTP_200_OK)
        except MonthlyIncome.DoesNotExist:
            return Response({"error": "No income found for this month"}, status=status.HTTP_404_NOT_FOUND)


class AddCategoryView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")
        budget = request.data.get("budget")

        if not name:
            return Response({"error": "Category name is required"}, status=status.HTTP_400_BAD_REQUEST)

        if budget is None or budget == "":
            budget = Decimal("0.00")  
        else:
            try:
                budget = Decimal(str(budget))  
            except:
                return Response({"error": "Invalid budget format"}, status=status.HTTP_400_BAD_REQUEST)

        category, created = Category.objects.get_or_create(name=name, defaults={"budget": budget})

        return Response(
            {"message": "Category added successfully", "data": CategorySerializer(category).data},
            status=status.HTTP_201_CREATED
        )


class AddExpenseView(generics.CreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        title = request.data.get("title")
        amount = request.data.get("amount")
        category_id = request.data.get("category")
        date = request.data.get("date")
        month = request.data.get("month")

        if not all([title, amount, date, month]):
            return Response({"error": "Title, amount, date, and month are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id) if category_id else None
        except Category.DoesNotExist:
            return Response({"error": "Invalid category ID"}, status=status.HTTP_400_BAD_REQUEST)

        monthly_income = MonthlyIncome.objects.filter(user=user, month=month).first()

        if not monthly_income:
            return Response({"error": "No income record found for this month"}, status=status.HTTP_400_BAD_REQUEST)

        if monthly_income.remaining_income < Decimal(amount):
            return Response({"error": "Not enough balance!"}, status=status.HTTP_400_BAD_REQUEST)

        monthly_income.remaining_income -= Decimal(amount)
        monthly_income.save()

        expense = Expense.objects.create(
            user=user, title=title, amount=amount, category=category, date=date, month=month
        )

        return Response({"message": "Expense added successfully", "data": ExpenseSerializer(expense).data}, status=status.HTTP_201_CREATED)

            
class EditExpenseView(generics.UpdateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, expense_id):
        user = request.user
        try:
            expense = Expense.objects.get(id=expense_id, user=user)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Expense updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteExpenseView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, expense_id):
        user = request.user
        try:
            expense = Expense.objects.get(id=expense_id, user=user)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)

        expense.delete()
        return Response({"message": "Expense deleted successfully"}, status=status.HTTP_200_OK)



class ViewIncomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        month = capfirst(request.query_params.get("month", "").strip().lower())  # Normalize month

        if not month:
            return Response({"error": "Month is required"}, status=400)

        total_income = MonthlyIncome.objects.filter(user=user, month__iexact=month).aggregate(total=Sum('income'))['total'] or 0

        total_expenses = Expense.objects.filter(user=user, month__iexact=month).aggregate(total=Sum('amount'))['total'] or 0

        remaining_income = total_income - total_expenses

        return Response({
            "month": month,
            "income": float(total_income),  
            "remaining_income": float(remaining_income)  
        })



class ViewExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        month = request.query_params.get("month")

        if not month:
            return Response({"error": "Month is required"}, status=400)

        expenses = Expense.objects.filter(user=user, month=month)

        total_expenses = sum(exp.amount for exp in expenses)

        expenses_list = [
            {
                "title": exp.title,
                "amount": float(exp.amount),  
                "category": exp.category.name,  
                "date": exp.date.strftime("%Y-%m-%d")  
            }
            for exp in expenses
        ]

        return Response({
            "month": month,
            "total_expenses": float(total_expenses),
            "expenses": expenses_list
        })
