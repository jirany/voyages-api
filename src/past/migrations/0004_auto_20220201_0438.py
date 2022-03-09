# Generated by Django 3.2.6 on 2022-02-01 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('past', '0003_auto_20220201_0420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enslaved',
            name='id',
        ),
        migrations.AlterField(
            model_name='enslavedinrelation',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enslaved_person', to='past.enslavementrelation'),
        ),
    ]
