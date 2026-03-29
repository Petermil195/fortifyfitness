from django.db import models
from django.contrib.auth.models import User


class Video(models.Model):
    """Assessment videos uploaded by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    assessment = models.ForeignKey('assessments.Assessment', on_delete=models.CASCADE, related_name='videos', null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)
    file_path = models.CharField(max_length=500)
    url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Video by {self.user.username} - {self.uploaded_at.date()}"
    
    class Meta:
        db_table = 'videos'
        ordering = ['-uploaded_at']
