# Generated migration for raw input fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0006_remove_assessment_ankle_dorsiflexion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='single_leg_stand_left',
            field=models.FloatField(default=0, help_text='Single Leg Stand - Left leg (seconds 0-20)'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='single_leg_stand_right',
            field=models.FloatField(default=0, help_text='Single Leg Stand - Right leg (seconds 0-20)'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='sit_to_stand_reps',
            field=models.IntegerField(default=0, help_text='Sit-to-Stand reps completed (0-10)'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='push_up_reps',
            field=models.IntegerField(default=0, help_text='Push-Ups reps completed (0-10)'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='front_back_lunges_left_reps',
            field=models.IntegerField(default=0, help_text='Front/Back Lunges - Left side (0-4)'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='front_back_lunges_right_reps',
            field=models.IntegerField(default=0, help_text='Front/Back Lunges - Right side (0-4)'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='plank_hold_duration',
            field=models.FloatField(default=0, help_text='Plank Hold duration (seconds 0-60)'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='deep_squat_hold_duration',
            field=models.FloatField(default=0, help_text='Deep Squat Hold duration (seconds 0-20)'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='clock_steps_left',
            field=models.IntegerField(default=0, help_text='Clock Steps - Left side (0-6)'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='clock_steps_right',
            field=models.IntegerField(default=0, help_text='Clock Steps - Right side (0-6)'),
        ),
    ]
