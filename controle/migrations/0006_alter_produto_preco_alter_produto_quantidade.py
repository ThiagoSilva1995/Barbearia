# Generated by Django 5.1.1 on 2024-10-22 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controle', '0005_produto_quantidade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='preco',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='produto',
            name='quantidade',
            field=models.PositiveIntegerField(),
        ),
    ]
