# Generated by Django 4.0.4 on 2023-10-26 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teststep',
            options={'ordering': ['number', 'id']},
        ),
        migrations.RenameField(
            model_name='projecttest',
            old_name='text',
            new_name='comment',
        ),
        migrations.AddField(
            model_name='projecttest',
            name='last_line',
            field=models.PositiveIntegerField(default=None, verbose_name='Last line number'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projecttest',
            name='start_line',
            field=models.PositiveIntegerField(default=None, verbose_name='First line number'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teststep',
            name='number',
            field=models.IntegerField(default=0, verbose_name='Step number'),
        ),
    ]