# Generated by Django 5.1.1 on 2024-10-22 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controle', '0006_alter_produto_preco_alter_produto_quantidade'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produto',
            name='quantidade',
        ),
        migrations.AddField(
            model_name='produto',
            name='estoque',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='produto',
            name='preco',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]