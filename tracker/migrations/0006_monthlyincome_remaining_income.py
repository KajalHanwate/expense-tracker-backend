# Generated by Django 4.2.20 on 2025-03-13 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0005_monthlyincome_is_locked_alter_monthlyincome_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlyincome',
            name='remaining_income',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
