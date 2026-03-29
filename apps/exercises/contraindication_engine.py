"""
Contraindication Engine for Exercise Filtering

This module contains comprehensive logic for filtering exercises based on
user injuries, medical conditions, and safety contraindication.
"""


class ContraindicationEngine:
    """Filter exercises based on user contraindications, injuries, and medical conditions."""
    
    INJURY_CONTRAINDICATIONS = {
        'knee': ['squats', 'lunges', 'running', 'jumping', 'leg press', 'box jumps', 'burpees', 'jump rope', 'step-ups', 'high knees'],
        'shoulder': ['overhead press', 'pull-ups', 'shoulder press', 'handstands', 'bench press', 'dips', 'upright rows', 'lateral raises', 'overhead squats', 'snatch'],
        'back': ['deadlifts', 'bent-over rows', 'heavy lifting', 'good mornings', 'hyperextensions', 'heavy squats', 'clean and jerk', 'sit-ups'],
        'lower back': ['deadlifts', 'bent-over rows', 'good mornings', 'heavy squats', 'leg press', 'sit-ups', 'toe touches'],
        'ankle': ['running', 'jumping', 'calf raises', 'box jumps', 'jump rope', 'burpees', 'high knees', 'sprinting'],
        'wrist': ['push-ups', 'planks', 'handstands', 'burpees', 'mountain climbers', 'bench press', 'front squats'],
        'elbow':['pull-ups', 'chin-ups', 'tricep dips', 'bench press', 'overhead press', 'bicep curls', 'tricep extensions'],
        'hip': ['squats', 'lunges', 'leg press', 'running', 'deadlifts', 'step-ups', 'jumping', 'hip thrusts'],
        'neck': ['overhead press', 'shoulder shrugs', 'upright rows', 'heavy back squats', 'inverted rows'],
    }
    
    MEDICAL_CONTRAINDICATIONS = {
        'hypertension': ['heavy lifting', 'isometric holds', 'valsalva maneuver', 'max effort lifts'],
        'high blood pressure': ['heavy lifting', 'isometric holds', 'max effort lifts'],
        'heart condition': ['high intensity', 'sprinting', 'max effort', 'heavy lifting', 'intense cardio'],
        'diabetes': ['prolonged fasting exercise', 'extreme endurance'],
        'asthma': ['intense cardio', 'cold weather outdoor', 'swimming in chlorine'],
        'osteoporosis': ['high impact', 'jumping', 'twisting', 'forward bending', 'heavy compression loads'],
        'arthritis': ['high impact', 'jumping', 'heavy weights', 'deep squats'],
        'pregnancy': ['lying on back', 'contact sports', 'high fall risk', 'intense abdominal work', 'heavy lifting'],
    }
    
    PAIN_AREA_CONTRAINDICATIONS = {
        'lower back pain': ['deadlifts', 'bent-over rows', 'sit-ups', 'toe touches', 'heavy squats', 'good mornings'],
        'shoulder pain': ['overhead press', 'pull-ups', 'bench press', 'dips', 'lateral raises', 'upright rows'],
        'knee pain': ['squats', 'lunges', 'running', 'jumping', 'leg press', 'step-ups'],
    }
    
    def __init__(self, user_injuries=None, medical_conditions=None, pain_areas=None):
        """Initialize the contraindication engine."""
        self.user_injuries = self._parse_input(user_injuries)
        self.medical_conditions = self._parse_input(medical_conditions)
        self.pain_areas = self._parse_input(pain_areas)
        self.contraindicated_tags = set()
        self.contraindication_reasons = {}
    
    def _parse_input(self, input_data):
        """Parse input that could be string or list"""
        if not input_data:
            return []
        if isinstance(input_data, str):
            return [item.strip().lower() for item in input_data.split(',') if item.strip()]
        elif isinstance(input_data, list):
            return [item.strip().lower() for item in input_data if item]
        return []
    
    def identify_contraindications(self):
        """Identify all exercise tags that should be avoided."""
        for injury in self.user_injuries:
            injury_lower = injury.lower()
            for key, tags in self.INJURY_CONTRAINDICATIONS.items():
                if key in injury_lower:
                    for tag in tags:
                        self.contraindicated_tags.add(tag.lower())
                        self.contraindication_reasons[tag.lower()] = f"Injury: {injury}"
        
        for condition in self.medical_conditions:
            condition_lower = condition.lower()
            for key, tags in self.MEDICAL_CONTRAINDICATIONS.items():
                if key in condition_lower:
                    for tag in tags:
                        self.contraindicated_tags.add(tag.lower())
                        self.contraindication_reasons[tag.lower()] = f"Medical: {condition}"
        
        for pain in self.pain_areas:
            pain_lower = pain.lower()
            for key, tags in self.PAIN_AREA_CONTRAINDICATIONS.items():
                if key in pain_lower:
                    for tag in tags:
                        self.contraindicated_tags.add(tag.lower())
                        self.contraindication_reasons[tag.lower()] = f"Pain: {pain}"
        
        return self.contraindicated_tags
    
    def filter_exercises(self, exercises):
        """Filter out exercises that are contraindicated."""
        if not self.contraindicated_tags:
            self.identify_contraindications()
        safe_exercises = []
        for exercise in exercises:
            if self.check_exercise_safety(exercise):
                safe_exercises.append(exercise)
        return safe_exercises
    
    def check_exercise_safety(self, exercise):
        """Check if a single exercise is safe for the user."""
        if not self.contraindicated_tags:
            self.identify_contraindications()
        
        exercise_name_lower = exercise.name.lower()
        if any(tag in exercise_name_lower for tag in self.contraindicated_tags):
            return False
        
        exercise_tags = [tag.lower() for tag in exercise.tags]
        if any(tag in exercise_tags for tag in self.contraindicated_tags):
            return False
        
        exercise_contraindications = [c.lower() for c in exercise.contraindications]
        all_user_conditions = (
            self.user_injuries + 
            self.medical_conditions + 
            self.pain_areas
        )
        
        for condition in all_user_conditions:
            if any(contraindication in condition for contraindication in exercise_contraindications):
                return False
        
        return True
    
    def get_safety_report(self):
        """Generate a safety report with all contraindications"""
        self.identify_contraindications()
        return {
            'contraindicated_movements': list(self.contraindicated_tags),
            'reasons': self.contraindication_reasons,
            'injury_count': len(self.user_injuries),
            'medical_condition_count': len(self.medical_conditions),
            'pain_area_count': len(self.pain_areas),
        }
    
    def get_exercise_safety_score(self, exercise):
        """Get a safety score for an exercise (0-100, higher is safer)"""
        if not self.contraindicated_tags:
            self.identify_contraindications()
        
        if not self.check_exercise_safety(exercise):
            return 0
        
        risk_score = 100
        exercise_tags = [tag.lower() for tag in exercise.tags]
        exercise_name_lower = exercise.name.lower()
        
        for contraindication in self.contraindicated_tags:
            contraindication_words = set(contraindication.split())
            name_words = set(exercise_name_lower.split())
            tag_words = set(' '.join(exercise_tags).split())
            
            name_overlap = len(contraindication_words & name_words)
            tag_overlap = len(contraindication_words & tag_words)
            
            if name_overlap > 0:
                risk_score -= (name_overlap * 15)
            if tag_overlap > 0:
                risk_score -= (tag_overlap * 10)
        
        return max(0, min(100, risk_score))
