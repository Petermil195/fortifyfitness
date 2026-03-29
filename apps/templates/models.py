from django.db import models


class Template(models.Model):
    """Workout program template"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fitness_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    duration_weeks = models.IntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.fitness_level})"
    
    class Meta:
        db_table = 'templates'
        ordering = ['name']


class TemplateSlot(models.Model):
    """Slot within a template for exercise type"""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='slots')
    name = models.CharField(max_length=100)
    exercise_type = models.CharField(max_length=50, help_text="Type of exercise for this slot")
    required_tags = models.JSONField(default=list, help_text="Required exercise tags")
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=12)
    rest_seconds = models.IntegerField(default=60)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} in {self.template.name}"
    
    class Meta:
        db_table = 'template_slots'
        ordering = ['order']
