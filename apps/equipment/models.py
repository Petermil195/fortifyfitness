from django.db import models


class Equipment(models.Model):
    """Equipment available for exercises"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'equipment'
        ordering = ['name']
        verbose_name_plural = 'Equipment'
