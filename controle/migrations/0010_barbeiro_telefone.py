# Generated by Django 5.1.1 on 2024-10-23 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controle', '0009_delete_agendamentoproduto'),
    ]

    operations = [
        migrations.AddField(
            model_name='barbeiro',
            name='telefone',
            field=models.CharField(default='000000000', max_length=15),
        ),
    ]