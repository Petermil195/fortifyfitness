from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile information with intake form data"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Basic Information
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say'),
        ],
        blank=True
    )
    
    # Safety & Medical Information
    medical_conditions = models.TextField(
        blank=True,
        help_text="Comma-separated list of medical conditions (e.g., diabetes, hypertension)"
    )
    current_medications = models.TextField(
        blank=True,
        help_text="Comma-separated list of current medications"
    )
    injuries = models.TextField(
        blank=True,
        help_text="Comma-separated list of current or past injuries"
    )
    pain_areas = models.TextField(
        blank=True,
        help_text="Comma-separated list of areas with pain or discomfort"
    )
    exercise_restrictions = models.TextField(
        blank=True,
        help_text="Any doctor-imposed exercise restrictions"
    )
    
    # Fitness Goals & Preferences
    primary_goal = models.CharField(
        max_length=50,
        choices=[
            ('weight_loss', 'Weight Loss'),
            ('muscle_gain', 'Muscle Gain'),
            ('general_fitness', 'General Fitness'),
            ('rehabilitation', 'Rehabilitation'),
            ('athletic_performance', 'Athletic Performance'),
            ('flexibility', 'Flexibility'),
        ],
        blank=True
    )
    workout_frequency = models.IntegerField(
        null=True,
        blank=True,
        help_text="Desired workouts per week"
    )
    workout_duration = models.IntegerField(
        null=True,
        blank=True,
        help_text="Preferred workout duration in minutes"
    )
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def age(self):
        """Calculate user's age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    class Meta:
        db_table = 'user_profiles'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

