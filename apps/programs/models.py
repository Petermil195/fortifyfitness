from django.db import models
from django.contrib.auth.models import User
from apps.exercises.models import Exercise
from apps.templates.models import Template


class Program(models.Model):
    """Generated workout program for user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template = models.ForeignKey('templates.Template', on_delete=models.SET_NULL, null=True, blank=True)
    template_name = models.CharField(max_length=100, default='Custom Program')
    frequency = models.IntegerField(default=4, help_text="Workouts per week")
    competency_level = models.IntegerField(default=1, help_text="User competency at program creation")
    program_data = models.JSONField(default=dict, help_text="Structured program data with weeks/days")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} for {self.user.username}"
    
    class Meta:
        db_table = 'programs'
        ordering = ['-created_at']


class ProgramDay(models.Model):
    """Workout day within a program"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='days')
    day_number = models.IntegerField(help_text="Day 1-7 of the week")
    focus = models.CharField(max_length=100, default='General', help_text="e.g., Lower Body, Upper Push")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'program_days'
        ordering = ['day_number']
        unique_together = ['program', 'day_number']
    
    def __str__(self):
        return f"{self.program.name} - Day {self.day_number}: {self.focus}"


class DayExercise(models.Model):
    """Exercise within a specific program day"""
    day = models.ForeignKey(ProgramDay, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.IntegerField(default=0, help_text="Execution order within the day")
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=12)
    rest_seconds = models.IntegerField(default=60)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'day_exercises'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.exercise.name} on {self.day}"


class ProgramExercise(models.Model):
    """Exercises assigned to a program"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='program_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=12)
    rest_seconds = models.IntegerField(default=60)
    order = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.exercise.name} in {self.program.name}"
    
    class Meta:
        db_table = 'program_exercises'
        ordering = ['order']
