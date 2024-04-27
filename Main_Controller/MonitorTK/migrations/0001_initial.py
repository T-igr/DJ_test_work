# Generated by Django 5.0.4 on 2024-04-26 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BDProductions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('workshop', models.IntegerField()),
                ('area', models.IntegerField()),
                ('product', models.CharField(max_length=15)),
                ('operation', models.IntegerField()),
                ('operation_name', models.CharField(max_length=30)),
                ('equipment', models.CharField(max_length=15)),
                ('worker_name', models.CharField(max_length=40)),
                ('master_name_request', models.CharField(max_length=40)),
                ('master_name', models.CharField(max_length=40)),
                ('controller_name_response', models.CharField(max_length=40, null=True)),
                ('decision', models.CharField(max_length=40, null=True)),
                ('decision_text', models.CharField(blank=True, max_length=2000, null=True)),
                ('priority', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(max_length=40, null=True)),
                ('datetime_master_request', models.DateTimeField(null=True)),
                ('datetime_controller_request', models.DateTimeField(null=True)),
                ('datetime_controller_response', models.DateTimeField(null=True)),
                ('datetime_controller_in_work', models.DateTimeField(null=True)),
                ('value', models.FloatField(blank=True, null=True)),
                ('controller_name_result', models.CharField(max_length=40, null=True)),
                ('value_fact', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]
