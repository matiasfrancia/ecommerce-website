# Generated by Django 3.1.6 on 2021-03-10 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category_filter',
            field=models.CharField(default='', max_length=120),
        ),
    ]
