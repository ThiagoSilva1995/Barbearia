# Generated by Django 5.1.1 on 2024-10-04 02:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controle', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='agendamento',
            name='pago',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='agendamento',
            name='tipo_corte',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='controle.tipocorte'),
        ),
    ]
