# Generated by Django 3.2 on 2021-05-23 15:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0016_customeruser_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeruser',
            name='auth_user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customeruser', to=settings.AUTH_USER_MODEL),
        ),
    ]
