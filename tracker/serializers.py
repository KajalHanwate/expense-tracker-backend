from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MonthlyIncome
from .models import Expense, Category, MonthlyIncome


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class MonthlyIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyIncome
        fields = ["id", "user", "month", "income", "is_locked"]
        read_only_fields = ["user", "is_locked"] 


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Expense
        fields = ["id", "user", "title", "amount", "category", "category_name", "date", "month"]
        read_only_fields = ["user", "category_name"]
