# Generated by Django 3.1.1 on 2020-10-02 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='braintree_id',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
