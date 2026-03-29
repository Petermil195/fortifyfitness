"""
Scoring Engine for Fitness Assessments

Implements the composite scoring formula:
- Assessment (7 Fortify movements, 0-21 scale) → 40% weight
- Questionnaire (training background, goals, equipment, readiness, 0-27 scale) → 30% weight
- Recovery (sleep, stress, GLP-1, 0-12 scale) → 30% weight

Composite Score = (Assessment% × 0.4) + (Questionnaire% × 0.3) + (Recovery% × 0.3)

Competency Levels (based on composite score):
- Level 1 (Rebuild): 0-39
- Level 2 (Foundation): 40-59
- Level 3 (Build): 60-79
- Level 4 (Perform): 80-100

Flags override levels:
- Any moderate/severe injury → cap level to 2
- Any severe injury (safety mode) → cap level to 1
"""

from .exercise_calculators import ExerciseCalculatorFactory


class ScoringEngine:
    """Calculate competency level from 7-movement (Fortify) assessment + questionnaire + recovery data."""

    ASSESSMENT_WEIGHT = 0.4
    QUESTIONNAIRE_WEIGHT = 0.3
    RECOVERY_WEIGHT = 0.3
    
    COMPETENCY_LEVELS = {
        1: {'min': 0, 'max': 39, 'label': 'Rebuild'},
        2: {'min': 40, 'max': 59, 'label': 'Foundation'},
        3: {'min': 60, 'max': 79, 'label': 'Build'},
        4: {'min': 80, 'max': 100, 'label': 'Perform'},
    }
    
    def __init__(self, assessment):
        """Initialize scoring engine with an assessment."""
        self.assessment = assessment
        self.assessment_score = 0
        self.questionnaire_score = 0
        self.recovery_score = 0
        self.assessment_percent = 0
        self.questionnaire_percent = 0
        self.recovery_percent = 0
        self.composite_score = 0
        self.competency_level = 1
        self.competency_label = 'Rebuild'
        self.flag_count = 0
        self.safety_mode_count = 0
        self.injury_flags = {}
        self.calculation_details = {}
    
    def calculate_assessment_score(self):
        """Calculate movement assessment total (0-21) - Fortify 7 movements using raw inputs"""
        self.calculation_details = {}

        # Single Leg Stand (dual input: left, right seconds)
        try:
            calc = ExerciseCalculatorFactory.get_calculator('single_leg_stand')
            result = calc.calculate(
                self.assessment.single_leg_stand_left,
                self.assessment.single_leg_stand_right
            )
            self.assessment.single_leg_stand = result['score']
            self.calculation_details['single_leg_stand'] = result
        except ValueError as e:
            self.assessment.single_leg_stand = 0
            self.calculation_details['single_leg_stand'] = {'error': str(e), 'score': 0}

        # Sit to Stand (reps: 0-10)
        try:
            calc = ExerciseCalculatorFactory.get_calculator('sit_to_stand')
            result = calc.calculate(self.assessment.sit_to_stand_reps)
            self.assessment.sit_to_stand = result['score']
            self.calculation_details['sit_to_stand'] = result
        except ValueError as e:
            self.assessment.sit_to_stand = 0
            self.calculation_details['sit_to_stand'] = {'error': str(e), 'score': 0}

        # Push Ups (reps: 0-10)
        try:
            calc = ExerciseCalculatorFactory.get_calculator('push_up')
            result = calc.calculate(self.assessment.push_up_reps)
            self.assessment.push_up = result['score']
            self.calculation_details['push_up'] = result
        except ValueError as e:
            self.assessment.push_up = 0
            self.calculation_details['push_up'] = {'error': str(e), 'score': 0}

        # Front/Back Lunges (dual input: left, right reps out of 4)
        try:
            calc = ExerciseCalculatorFactory.get_calculator('front_back_lunges')
            result = calc.calculate(
                self.assessment.front_back_lunges_left_reps,
                self.assessment.front_back_lunges_right_reps
            )
            self.assessment.front_back_lunges = result['score']
            self.calculation_details['front_back_lunges'] = result
        except ValueError as e:
            self.assessment.front_back_lunges = 0
            self.calculation_details['front_back_lunges'] = {'error': str(e), 'score': 0}

        # Plank Hold (time: 0-60 seconds)
        try:
            calc = ExerciseCalculatorFactory.get_calculator('plank_hold')
            result = calc.calculate(self.assessment.plank_hold_duration)
            self.assessment.plank_hold = result['score']
            self.calculation_details['plank_hold'] = result
        except ValueError as e:
            self.assessment.plank_hold = 0
            self.calculation_details['plank_hold'] = {'error': str(e), 'score': 0}

        # Deep Squat Hold (time: 0-20 seconds)
        try:
            calc = ExerciseCalculatorFactory.get_calculator('deep_squat_hold')
            result = calc.calculate(self.assessment.deep_squat_hold_duration)
            self.assessment.deep_squat_hold = result['score']
            self.calculation_details['deep_squat_hold'] = result
        except ValueError as e:
            self.assessment.deep_squat_hold = 0
            self.calculation_details['deep_squat_hold'] = {'error': str(e), 'score': 0}

        # Clock Steps (dual input: left, right steps out of 6 each = 12 total)
        try:
            calc = ExerciseCalculatorFactory.get_calculator('clock_steps')
            result = calc.calculate(
                self.assessment.clock_steps_left,
                self.assessment.clock_steps_right
            )
            self.assessment.clock_steps = result['score']
            self.calculation_details['clock_steps'] = result
        except ValueError as e:
            self.assessment.clock_steps = 0
            self.calculation_details['clock_steps'] = {'error': str(e), 'score': 0}

        # Sum all individual scores
        self.assessment_score = (
            self.assessment.single_leg_stand +
            self.assessment.sit_to_stand +
            self.assessment.front_back_lunges +
            self.assessment.push_up +
            self.assessment.plank_hold +
            self.assessment.deep_squat_hold +
            self.assessment.clock_steps
        )
        self.assessment_score = max(0, min(21, self.assessment_score))  # Clamp 0-21
        return self.assessment_score
    
    def calculate_questionnaire_score(self):
        """Calculate questionnaire total (0-27 actual max for current 7 fields)"""
        self.questionnaire_score = self.assessment.get_questionnaire_total()
        # Actual max with current fields: Activity(4) + Experience(4) + Gym(4) + Goal(5) + Timeline(3) + Equipment(3) + Fatigue(4) = 27
        self.questionnaire_score = max(0, min(27, self.questionnaire_score))  # Clamp 0-27
        return self.questionnaire_score
    
    def calculate_recovery_score(self):
        """Calculate recovery total (0-12)"""
        self.recovery_score = self.assessment.get_recovery_total()
        self.recovery_score = max(0, min(12, self.recovery_score))  # Clamp 0-12
        return self.recovery_score
    
    def normalize_to_percent(self):
        """Normalize each domain to 0-100 percentage"""
        self.assessment_percent = (self.assessment_score / 21.0) * 100
        self.questionnaire_percent = (self.questionnaire_score / 27.0) * 100  # Fixed: was 40, actual max is 27
        self.recovery_percent = (self.recovery_score / 12.0) * 100
        
        # Clamp percentages
        self.assessment_percent = max(0, min(100, self.assessment_percent))
        self.questionnaire_percent = max(0, min(100, self.questionnaire_percent))
        self.recovery_percent = max(0, min(100, self.recovery_percent))
    
    def calculate_composite_score(self):
        """Calculate weighted composite score (0-100)"""
        self.composite_score = (
            (self.assessment_percent * self.ASSESSMENT_WEIGHT) +
            (self.questionnaire_percent * self.QUESTIONNAIRE_WEIGHT) +
            (self.recovery_percent * self.RECOVERY_WEIGHT)
        )
        self.composite_score = max(0, min(100, round(self.composite_score, 1)))
        return self.composite_score
    
    def identify_injury_flags(self):
        """Identify flagged injury areas (moderate pain or severe)"""
        self.injury_flags = self.assessment.get_injury_flags()
        
        # Count flags and safety modes
        for area, status in self.injury_flags.items():
            if status == 'moderate':
                self.flag_count += 1
            elif status == 'severe':
                self.safety_mode_count += 1
    
    def assign_competency_level(self):
        """Assign competency level based on composite score with flag overrides"""
        # Find base level from composite score
        for level, config in self.COMPETENCY_LEVELS.items():
            if config['min'] <= self.composite_score <= config['max']:
                self.competency_level = level
                break
        
        # Apply flag overrides
        if self.safety_mode_count > 0:
            # Safety mode caps at level 1
            self.competency_level = 1
        elif self.flag_count > 0:
            # Injury flags cap at level 2
            self.competency_level = min(self.competency_level, 2)

        # Ensure label always matches the final level after overrides.
        self.competency_label = self.COMPETENCY_LEVELS[self.competency_level]['label']
        
        return self.competency_level, self.competency_label
    
    def get_recommendations(self):
        """Generate recommendations based on assessment results"""
        recommendations = []
        
        if self.competency_level == 1:
            recommendations.append('Focus on foundational movement patterns and building basic fitness capacity.')
        elif self.competency_level == 2:
            recommendations.append('Continue building strength and movement quality before progressing intensity.')
        elif self.competency_level == 3:
            recommendations.append('You are ready for more challenging training with progressive overload.')
        else:  # Level 4
            recommendations.append('You have a strong fitness foundation. Challenge yourself with advanced training.')
        
        # Add assessment-specific recommendations
        if self.assessment_percent < 50:
            recommendations.append('Prioritize movement quality and stability work.')
        
        if self.questionnaire_percent < 50:
            recommendations.append('Build training consistency and progressive exposure to load.')
        
        if self.recovery_percent < 50:
            recommendations.append('Improve sleep quality and stress management for better recovery.')
        
        # Add injury-specific notes
        if self.injury_flags:
            recommendations.append(f'Assessment identified concerns in: {", ".join(self.injury_flags.keys())}. These areas will be considered when designing your program.')
        
        return recommendations
    
    def process(self):
        """Run complete scoring process and return results"""
        # Calculate all components
        self.calculate_assessment_score()
        self.calculate_questionnaire_score()
        self.calculate_recovery_score()
        
        # Store in assessment
        self.assessment.assessment_score = self.assessment_score
        self.assessment.questionnaire_score = self.questionnaire_score
        self.assessment.recovery_score = self.recovery_score
        
        # Normalize
        self.normalize_to_percent()
        
        # Calculate composite
        self.calculate_composite_score()
        self.assessment.composite_score = self.composite_score
        
        # Identify injury flags
        self.identify_injury_flags()
        self.assessment.flag_count = self.flag_count
        self.assessment.safety_mode_count = self.safety_mode_count
        
        # Assign competency level
        self.assign_competency_level()
        self.assessment.competency_level = self.competency_level
        # Persist lowercase value to match Django model choices.
        self.assessment.competency_label = self.competency_label.lower()
        
        # Save assessment
        self.assessment.save()
        
        # Get recommendations
        recommendations = self.get_recommendations()
        
        return {
            'assessment_score': self.assessment_score,
            'assessment_percent': round(self.assessment_percent, 1),
            'questionnaire_score': self.questionnaire_score,
            'questionnaire_percent': round(self.questionnaire_percent, 1),
            'recovery_score': self.recovery_score,
            'recovery_percent': round(self.recovery_percent, 1),
            'composite_score': self.composite_score,
            'competency_level': self.competency_level,
            'competency_label': self.competency_label,
            'injury_flags': self.injury_flags,
            'flag_count': self.flag_count,
            'safety_mode_count': self.safety_mode_count,
            'recommendations': recommendations,
            'calculation_details': self.calculation_details,
        }
