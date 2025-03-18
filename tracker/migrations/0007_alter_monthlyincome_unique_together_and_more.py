# Generated by Django 4.2.20 on 2025-03-13 06:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0006_monthlyincome_remaining_income'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='monthlyincome',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='monthlyincome',
            name='remaining_income',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='monthlyincome',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='monthlyincome',
            name='is_locked',
        ),
    ]
