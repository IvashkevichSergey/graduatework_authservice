# Generated by Django 4.2.7 on 2023-11-29 09:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_user_invite_code_alter_user_invited_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='password',
        ),
        migrations.AlterField(
            model_name='user',
            name='invite_code',
            field=models.CharField(help_text='Инвайт-код пользователя', max_length=6, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='invited_by',
            field=models.ForeignKey(help_text='Инвайт-код пригласившего пользователя', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, to_field='invite_code'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.PositiveBigIntegerField(help_text='Номер телефона', unique=True),
        ),
    ]