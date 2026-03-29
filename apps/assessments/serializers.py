from rest_framework import serializers
from .models import Assessment, MovementTest
from .scoring_engine import ScoringEngine
from .exercise_calculators import ExerciseCalculatorFactory


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for Assessment model with Fortify 7-movement protocol - accepts RAW inputs"""

    class Meta:
        model = Assessment
        fields = [
            'id', 'user',
            # Assessment - RAW INPUT VALUES (not scores)
            'single_leg_stand_left', 'single_leg_stand_right',
            'sit_to_stand_reps',
            'front_back_lunges_left_reps', 'front_back_lunges_right_reps',
            'push_up_reps',
            'plank_hold_duration',
            'deep_squat_hold_duration',
            'clock_steps_left', 'clock_steps_right',
            # Assessment - CALCULATED SCORES (read-only)
            'single_leg_stand', 'sit_to_stand', 'front_back_lunges',
            'push_up', 'plank_hold', 'deep_squat_hold', 'clock_steps',
            # Questionnaire
            'current_activity_level', 'weight_training_experience', 'gym_confidence',
            'primary_goal', 'timeline_urgency', 'equipment_access', 'readiness_fatigue',
            # Recovery
            'sleep_quality', 'stress_level', 'glp1_usage',
            # Injury Flags
            'shoulder_status', 'knee_status', 'hip_status', 'back_status',
            # Results
            'assessment_score', 'questionnaire_score', 'recovery_score',
            'composite_score', 'competency_level', 'competency_label',
            'flag_count', 'safety_mode_count',
            # Metadata
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user',
            # Calculated scores (not rawvalues)
            'single_leg_stand', 'sit_to_stand', 'front_back_lunges',
            'push_up', 'plank_hold', 'deep_squat_hold', 'clock_steps',
            # Result scores
            'assessment_score', 'questionnaire_score', 'recovery_score',
            'composite_score', 'competency_level', 'competency_label',
            'flag_count', 'safety_mode_count', 'created_at', 'updated_at'
        ]

    # === RAW INPUT VALIDATORS ===

    def validate_single_leg_stand_left(self, value):
        """Validate Single Leg Stand left input (0-20 seconds)"""
        if not (0 <= value <= 20):
            raise serializers.ValidationError("Single Leg Stand left must be 0-20 seconds.")
        return value

    def validate_single_leg_stand_right(self, value):
        """Validate Single Leg Stand right input (0-20 seconds)"""
        if not (0 <= value <= 20):
            raise serializers.ValidationError("Single Leg Stand right must be 0-20 seconds.")
        return value

    def validate_sit_to_stand_reps(self, value):
        """Validate Sit-to-Stand reps (0-10)"""
        if not (0 <= value <= 10):
            raise serializers.ValidationError("Sit-to-Stand reps must be 0-10.")
        return value

    def validate_push_up_reps(self, value):
        """Validate Push-Up reps (0-10)"""
        if not (0 <= value <= 10):
            raise serializers.ValidationError("Push-Up reps must be 0-10.")
        return value

    def validate_front_back_lunges_left_reps(self, value):
        """Validate Front/Back Lunges left reps (0-4)"""
        if not (0 <= value <= 4):
            raise serializers.ValidationError("Front/Back Lunges left must be 0-4 reps.")
        return value

    def validate_front_back_lunges_right_reps(self, value):
        """Validate Front/Back Lunges right reps (0-4)"""
        if not (0 <= value <= 4):
            raise serializers.ValidationError("Front/Back Lunges right must be 0-4 reps.")
        return value

    def validate_plank_hold_duration(self, value):
        """Validate Plank Hold duration (0-60 seconds)"""
        if not (0 <= value <= 60):
            raise serializers.ValidationError("Plank Hold duration must be 0-60 seconds.")
        return value

    def validate_deep_squat_hold_duration(self, value):
        """Validate Deep Squat Hold duration (0-20 seconds)"""
        if not (0 <= value <= 20):
            raise serializers.ValidationError("Deep Squat Hold duration must be 0-20 seconds.")
        return value

    def validate_clock_steps_left(self, value):
        """Validate Clock Steps left (0-6 steps)"""
        if not (0 <= value <= 6):
            raise serializers.ValidationError("Clock Steps left must be 0-6 steps.")
        return value

    def validate_clock_steps_right(self, value):
        """Validate Clock Steps right (0-6 steps)"""
        if not (0 <= value <= 6):
            raise serializers.ValidationError("Clock Steps right must be 0-6 steps.")
        return value

    def validate_questionnaire_score(self, value, field_name, max_val):
        """Validate questionnaire component scores"""
        if not (0 <= value <= max_val):
            raise serializers.ValidationError(f"{field_name} must be between 0 and {max_val}.")
        return value

    def validate_current_activity_level(self, value):
        return self.validate_questionnaire_score(value, 'Activity level', 4)

    def validate_weight_training_experience(self, value):
        return self.validate_questionnaire_score(value, 'Weight training', 4)

    def validate_gym_confidence(self, value):
        return self.validate_questionnaire_score(value, 'Gym confidence', 4)

    def validate_primary_goal(self, value):
        return self.validate_questionnaire_score(value, 'Primary goal', 5)

    def validate_timeline_urgency(self, value):
        return self.validate_questionnaire_score(value, 'Timeline urgency', 3)

    def validate_equipment_access(self, value):
        return self.validate_questionnaire_score(value, 'Equipment access', 3)

    def validate_readiness_fatigue(self, value):
        return self.validate_questionnaire_score(value, 'Readiness/fatigue', 4)

    def validate_sleep_quality(self, value):
        return self.validate_questionnaire_score(value, 'Sleep quality', 4)

    def validate_stress_level(self, value):
        return self.validate_questionnaire_score(value, 'Stress level', 3)
    
    def create(self, validated_data):
        """Create assessment and calculate scores"""
        assessment = Assessment.objects.create(**validated_data)
        
        # Calculate scores using ScoringEngine
        scoring_engine = ScoringEngine(assessment)
        # The engine calls assessment.save() internally
        scoring_engine.process()
        
        return assessment


class AssessmentResultSerializer(serializers.Serializer):
    """Serializer for assessment results and recommendations"""
    assessment = AssessmentSerializer()
    assessment_score = serializers.IntegerField()
    assessment_percent = serializers.FloatField()
    questionnaire_score = serializers.IntegerField()
    questionnaire_percent = serializers.FloatField()
    recovery_score = serializers.IntegerField()
    recovery_percent = serializers.FloatField()
    composite_score = serializers.FloatField()
    competency_level = serializers.IntegerField()
    competency_label = serializers.CharField()
    injury_flags = serializers.DictField()
    flag_count = serializers.IntegerField()
    safety_mode_count = serializers.IntegerField()
    recommendations = serializers.ListField(child=serializers.CharField())
    calculation_details = serializers.DictField(required=False)


class QuickAssessmentSerializer(serializers.ModelSerializer):
    """Simplified serializer for quick assessment summaries"""
    
    class Meta:
        model = Assessment
        fields = [
            'id', 'composite_score', 'competency_level', 'competency_label',
            'injury_flags', 'created_at'
        ]
        read_only_fields = fields
