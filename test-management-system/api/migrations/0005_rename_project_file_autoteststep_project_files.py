# Generated by Django 4.0.4 on 2023-11-08 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_autoteststep'),
    ]

    operations = [
        migrations.RenameField(
            model_name='autoteststep',
            old_name='project_file',
            new_name='project_files',
        ),
    ]
