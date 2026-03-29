from django.db import models


class Exercise(models.Model):
    """Exercise database with assessment and workout types"""
    
    EXERCISE_TYPE_CHOICES = [
        ('assessment', 'Assessment Protocol'),
        ('workout', 'Workout Exercise'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    exercise_type = models.CharField(
        max_length=20,
        choices=EXERCISE_TYPE_CHOICES,
        default='workout',
        help_text="Assessment Protocol exercises teach users how to perform & score FMS movements. Workout exercises are for program delivery."
    )
    video_url = models.URLField(blank=True, null=True)
    instructions = models.TextField(blank=True)
    tags = models.JSONField(default=list, help_text="List of exercise tags")
    contraindications = models.JSONField(default=list, help_text="List of contraindications")
    equipment = models.JSONField(default=list, help_text="Required equipment")
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_exercise_type_display()})"
    
    class Meta:
        db_table = 'exercises'
        ordering = ['name']


class ExerciseTag(models.Model):
    """Tags for categorizing exercises"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'exercise_tags'
        ordering = ['name']
