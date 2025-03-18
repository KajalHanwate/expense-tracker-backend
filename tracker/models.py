from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


User = get_user_model()

class MonthlyIncome(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="monthly_incomes")
    month = models.CharField(max_length=20)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    is_locked = models.BooleanField(default=False)
    remaining_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.pk:  
            self.remaining_income = self.income   
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    month = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.title} - {self.amount}"

