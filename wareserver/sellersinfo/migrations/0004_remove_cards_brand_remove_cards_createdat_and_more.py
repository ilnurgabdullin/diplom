# Generated by Django 5.1.5 on 2025-03-31 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sellersinfo', '0003_alter_warehouse_owner_storage_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cards',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='cards',
            name='createdat',
        ),
        migrations.RemoveField(
            model_name='cards',
            name='description',
        ),
        migrations.RemoveField(
            model_name='cards',
            name='imtid',
        ),
        migrations.RemoveField(
            model_name='cards',
            name='needkiz',
        ),
        migrations.RemoveField(
            model_name='cards',
            name='nmid',
        ),
        migrations.RemoveField(
            model_name='cards',
            name='nmuuid',
        ),
        migrations.RemoveField(
            model_name='cards',
            name='subjectid',
        ),
        migrations.RemoveField(
            model_name='cards',
            name='title',
        ),
        migrations.RemoveField(
            model_name='cards',
            name='updatedat',
        ),
    ]
