from django.db import models
from django.contrib.auth.models import User


class Assessment(models.Model):
    """Fitness Assessment with Fortify 7-movement protocol, questionnaire, and recovery scoring"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')

    # ===== RAW INPUT VALUES: Fortify 7-movement tests =====
    # Single Leg Stand - time in seconds for each leg
    single_leg_stand_left = models.FloatField(default=0, help_text="Single Leg Stand - Left leg (seconds 0-20)")
    single_leg_stand_right = models.FloatField(default=0, help_text="Single Leg Stand - Right leg (seconds 0-20)")

    # Sit to Stand - reps completed (max 10)
    sit_to_stand_reps = models.IntegerField(default=0, help_text="Sit-to-Stand reps completed (0-10)")

    # Push Ups - reps completed (max 10)
    push_up_reps = models.IntegerField(default=0, help_text="Push-Ups reps completed (0-10)")

    # Front/Back Lunges - successful reps per side (max 4 per side)
    front_back_lunges_left_reps = models.IntegerField(default=0, help_text="Front/Back Lunges - Left side (0-4)")
    front_back_lunges_right_reps = models.IntegerField(default=0, help_text="Front/Back Lunges - Right side (0-4)")

    # Plank Hold - duration in seconds (max 60)
    plank_hold_duration = models.FloatField(default=0, help_text="Plank Hold duration (seconds 0-60)")

    # Deep Squat Hold - duration in seconds (max 20)
    deep_squat_hold_duration = models.FloatField(default=0, help_text="Deep Squat Hold duration (seconds 0-20)")

    # Clock Steps - steps completed on each side (max 12 total, 6 per side)
    clock_steps_left = models.IntegerField(default=0, help_text="Clock Steps - Left side (0-6)")
    clock_steps_right = models.IntegerField(default=0, help_text="Clock Steps - Right side (0-6)")

    # ===== CALCULATED SCORES: Fortify 7-movement tests (0-21 scale) =====
    single_leg_stand = models.IntegerField(default=0, help_text="Single Leg Stand (0-3)")
    sit_to_stand = models.IntegerField(default=0, help_text="Sit-to-Stand (10 reps) (0-3)")
    front_back_lunges = models.IntegerField(default=0, help_text="Front/Back Lunges (4 per side) (0-3)")
    push_up = models.IntegerField(default=0, help_text="Push-Ups (max 10) (0-3)")
    plank_hold = models.IntegerField(default=0, help_text="Plank Hold (0-3)")
    deep_squat_hold = models.IntegerField(default=0, help_text="Deep Squat Hold (parallel, heels down) (0-3)")
    clock_steps = models.IntegerField(default=0, help_text="Clock Steps (2 rounds) (0-3)")
    
    # ===== QUESTIONNAIRE SECTION: Training Background & Goals (0-27 scale - 7 fields) =====
    current_activity_level = models.IntegerField(default=0, help_text="Current activity level (0-4)")
    weight_training_experience = models.IntegerField(default=0, help_text="Weight training experience (0-4)")
    gym_confidence = models.IntegerField(default=0, help_text="Gym confidence (0-4)")
    primary_goal = models.IntegerField(default=0, help_text="Primary fitness goal (0-5)")
    timeline_urgency = models.IntegerField(default=0, help_text="Timeline urgency (0-3)")
    equipment_access = models.IntegerField(default=0, help_text="Equipment access (0-3)")
    readiness_fatigue = models.IntegerField(default=0, help_text="Post-activity fatigue level (0-4)")
    
    # ===== RECOVERY SECTION: Sleep, Stress, GLP-1 (0-12 scale) =====
    sleep_quality = models.IntegerField(default=0, help_text="Sleep quality hours (0-4)")
    stress_level = models.IntegerField(default=0, help_text="Stress level (0-3)")
    glp1_usage = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No'),
            ('recent', 'Recently started'),
            ('longterm', 'Long-term use'),
        ],
        default='none',
        help_text="GLP-1 medication usage"
    )
    
    # ===== INJURY FLAGS =====
    shoulder_status = models.CharField(
        max_length=50,
        choices=[
            ('none', 'No issue'),
            ('past', 'Past resolved'),
            ('mild', 'Mild discomfort'),
            ('moderate', 'Moderate pain'),
            ('severe', 'Severe/diagnosed'),
        ],
        default='none'
    )
    knee_status = models.CharField(
        max_length=50,
        choices=[
            ('none', 'No issue'),
            ('past', 'Past resolved'),
            ('mild', 'Mild discomfort'),
            ('moderate', 'Moderate pain'),
            ('severe', 'Severe/diagnosed'),
        ],
        default='none'
    )
    hip_status = models.CharField(
        max_length=50,
        choices=[
            ('none', 'No issue'),
            ('past', 'Past resolved'),
            ('mild', 'Mild discomfort'),
            ('moderate', 'Moderate pain'),
            ('severe', 'Severe/diagnosed'),
        ],
        default='none'
    )
    back_status = models.CharField(
        max_length=50,
        choices=[
            ('none', 'No issue'),
            ('past', 'Past resolved'),
            ('mild', 'Mild discomfort'),
            ('moderate', 'Moderate pain'),
            ('severe', 'Severe/diagnosed'),
        ],
        default='none'
    )
    
    # ===== CALCULATED RESULTS =====
    assessment_score = models.IntegerField(default=0, help_text="Movement assessment total (0-21)")
    questionnaire_score = models.IntegerField(default=0, help_text="Questionnaire total (0-27 actual max for 7 fields)")
    recovery_score = models.IntegerField(default=0, help_text="Recovery total (0-12)")
    
    composite_score = models.FloatField(default=0, help_text="Weighted composite score (0-100)")
    competency_level = models.IntegerField(default=1, help_text="Competency level (1-4)")
    competency_label = models.CharField(
        max_length=20,
        choices=[
            ('rebuild', 'Rebuild'),
            ('foundation', 'Foundation'),
            ('build', 'Build'),
            ('perform', 'Perform'),
        ],
        default='rebuild'
    )
    
    # ===== FLAGS =====
    flag_count = models.IntegerField(default=0, help_text="Number of injury flags (moderate pain)")
    safety_mode_count = models.IntegerField(default=0, help_text="Number of safety flags (severe)")
    
    # ===== METADATA =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Assessment by {self.user.username} on {self.created_at.date()}"
    
    def get_assessment_total(self):
        """Calculate total movement assessment score (0-21) - Fortify 7 movements"""
        return (
            self.single_leg_stand + self.sit_to_stand + self.front_back_lunges +
            self.push_up + self.plank_hold + self.deep_squat_hold + self.clock_steps
        )
    
    def get_questionnaire_total(self):
        """Calculate total questionnaire score (0-27): 4+4+4+5+3+3+4"""
        return (
            self.current_activity_level + self.weight_training_experience +
            self.gym_confidence + self.primary_goal + self.timeline_urgency +
            self.equipment_access + self.readiness_fatigue
        )
    
    def get_recovery_total(self):
        """Calculate total recovery score (0-12)"""
        return self.sleep_quality + self.stress_level + (1 if self.glp1_usage != 'none' else 0)
    
    def get_injury_flags(self):
        """Return dict of flagged injury areas"""
        flags = {}
        for area, status in [
            ('shoulder', self.shoulder_status),
            ('knee', self.knee_status),
            ('hip', self.hip_status),
            ('back', self.back_status),
        ]:
            if status in ['moderate', 'severe']:
                flags[area] = status
        return flags
    
    class Meta:
        db_table = 'assessments'
        ordering = ['-created_at']


class MovementTest(models.Model):
    """Individual movement test results within an assessment"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='movement_tests')
    name = models.CharField(max_length=100)
    score = models.IntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - Score: {self.score}"
    
    class Meta:
        db_table = 'movement_tests'
