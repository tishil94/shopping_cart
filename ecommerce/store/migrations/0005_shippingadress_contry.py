# Generated by Django 3.2 on 2020-10-04 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_order_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingadress',
            name='contry',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
