# Generated by Django 4.0.4 on 2023-10-27 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_teststep_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='projecttest',
            options={'ordering': ['start_line', 'id']},
        ),
        migrations.AddField(
            model_name='projecttest',
            name='needs_expanded_view',
            field=models.BooleanField(default=False, verbose_name='needs expanded view'),
        ),
    ]