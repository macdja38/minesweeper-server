# Generated by Django 2.1.5 on 2019-02-04 05:37

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import game.models.game


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='game_state',
            field=models.CharField(choices=[('S', 'Started'), ('W', 'Won'), ('L', 'Lost')], default='S', max_length=1),
        ),
        migrations.AddField(
            model_name='game',
            name='height',
            field=models.IntegerField(default=8, validators=[django.core.validators.MaxValueValidator(32), django.core.validators.MinValueValidator(8)]),
        ),
        migrations.AddField(
            model_name='game',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='state',
            field=models.CharField(default=game.models.game.generate_serialized_game_with_defaults, max_length=4096),
        ),
        migrations.AddField(
            model_name='game',
            name='width',
            field=models.IntegerField(default=8, validators=[django.core.validators.MaxValueValidator(32), django.core.validators.MinValueValidator(8)]),
        ),
    ]
