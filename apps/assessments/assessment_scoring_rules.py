"""
Scoring Rules and Thresholds for Fitness Assessment

Defines the calculation logic and scoring thresholds for each exercise
"""

EXERCISE_SCORING_RULES = {
    'single_leg_stand': {
        'type': 'dual_input_time',
        'unit': 'seconds',
        'max_input': 20,
        'inputs': ['left', 'right'],
        'calculation': 'average_and_floor',
        'thresholds': [
            {'min': 0, 'max': 5, 'score': 0},
            {'min': 6, 'max': 10, 'score': 1},
            {'min': 11, 'max': 15, 'score': 2},
            {'min': 16, 'max': 20, 'score': 3},
        ],
        'description': 'Average both legs, floor decimal, then apply score thresholds',
    },
    'sit_to_stand': {
        'type': 'reps',
        'max_input': 10,
        'calculation': 'threshold_based',
        'thresholds': [
            {'min': 0, 'max': 3, 'score': 0},
            {'min': 4, 'max': 6, 'score': 1},
            {'min': 7, 'max': 9, 'score': 2},
            {'min': 10, 'max': 10, 'score': 3},
        ],
        'description': '0-3 reps = 0, 4-6 = 1, 7-9 = 2, 10 = 3',
    },
    'push_up': {
        'type': 'reps',
        'max_input': 10,
        'calculation': 'threshold_based',
        'thresholds': [
            {'min': 0, 'max': 3, 'score': 0},
            {'min': 4, 'max': 6, 'score': 1},
            {'min': 7, 'max': 9, 'score': 2},
            {'min': 10, 'max': 10, 'score': 3},
        ],
        'description': '0-3 reps = 0, 4-6 = 1, 7-9 = 2, 10 = 3',
    },
    'front_back_lunges': {
        'type': 'dual_input_reps',
        'max_input': 4,
        'inputs': ['left', 'right'],
        'calculation': 'average_and_floor',
        'thresholds': [
            {'min': 0, 'max': 0, 'score': 0},
            {'min': 1, 'max': 1, 'score': 0},
            {'min': 2, 'max': 2, 'score': 1},
            {'min': 3, 'max': 3, 'score': 2},
            {'min': 4, 'max': 4, 'score': 3},
        ],
        'description': 'Average both sides, floor decimal, then apply score thresholds. 1=0, 2=1, 3=2, 4=3',
    },
    'plank_hold': {
        'type': 'time',
        'unit': 'seconds',
        'max_input': 60,
        'calculation': 'threshold_based',
        'thresholds': [
            {'min': 0, 'max': 30, 'score': 0},
            {'min': 31, 'max': 45, 'score': 1},
            {'min': 46, 'max': 59, 'score': 2},
            {'min': 60, 'max': 120, 'score': 3},
        ],
        'description': '0-30s = 0, 31-45s = 1, 46-59s = 2, 60+ = 3',
    },
    'deep_squat_hold': {
        'type': 'time',
        'unit': 'seconds',
        'max_input': 20,
        'calculation': 'threshold_based',
        'thresholds': [
            {'min': 0, 'max': 5, 'score': 0},
            {'min': 6, 'max': 14, 'score': 1},
            {'min': 15, 'max': 19, 'score': 2},
            {'min': 20, 'max': 120, 'score': 3},
        ],
        'description': '0-5s = 0, 6-14s = 1, 15-19s = 2, 20+ = 3',
    },
    'clock_steps': {
        'type': 'dual_input_reps',
        'max_input': 12,
        'inputs': ['left', 'right'],
        'calculation': 'average_and_floor',
        'thresholds': [
            {'min': 0,  'max': 3,  'score': 0},
            {'min': 4,  'max': 7,  'score': 1},
            {'min': 8,  'max': 11, 'score': 2},
            {'min': 12, 'max': 12, 'score': 3},
        ],
        'description': 'Average both sides (each 0-12), floor decimal. 0-3=0, 4-7=1, 8-11=2, 12=3',
    },
}


def get_exercise_rule(exercise_id):
    """Get scoring rule for an exercise"""
    return EXERCISE_SCORING_RULES.get(exercise_id, None)


def validate_input_range(exercise_id, value):
    """Validate that input is within allowed range for exercise"""
    rule = get_exercise_rule(exercise_id)
    if not rule:
        raise ValueError(f"Unknown exercise: {exercise_id}")

    max_val = rule.get('max_input', 0)
    if not (0 <= value <= max_val):
        raise ValueError(f"{exercise_id}: value must be between 0 and {max_val}, got {value}")
    return True
