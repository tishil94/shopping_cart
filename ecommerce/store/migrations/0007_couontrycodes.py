# Generated by Django 3.1.1 on 2020-10-04 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20201004_0610'),
    ]

    operations = [
        migrations.CreateModel(
            name='CouontryCodes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=200, null=True)),
                ('code', models.CharField(max_length=200, null=True)),
            ],
        ),
    ]