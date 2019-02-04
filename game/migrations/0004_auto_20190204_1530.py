# Generated by Django 2.1.5 on 2019-02-04 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_game_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='game_state',
            field=models.CharField(choices=[('C', 'Created'), ('S', 'Started'), ('W', 'Won'), ('L', 'Lost')], default='C', max_length=1),
        ),
        migrations.AlterField(
            model_name='game',
            name='start_time',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='state',
            field=models.CharField(default='', max_length=4096),
        ),
    ]