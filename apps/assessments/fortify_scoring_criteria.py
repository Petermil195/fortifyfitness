"""
Fortify 7 Assessment Scoring Criteria

Complete scoring definitions for all 7 exercises, with detailed descriptions 
for each score level (0-3) to guide assessment administrators and validate client responses.

Each exercise is scored 0-3, for a total possible score of 21.
"""

FORTIFY_7_EXERCISES = {
    'single_leg_stand': {
        'name': 'Single Leg Stand',
        'order': 1,
        'max_score': 3,
        'scoring_criteria': {
            0: 'Cannot maintain balance for 5 sec',
            1: '5–10 sec with instability',
            2: '10–20 sec controlled',
            3: '20+ sec stable'
        },
        'notes': 'Test balance and proprioception. Client stands on one leg without support.',
    },
    'sit_to_stand': {
        'name': 'Sit-to-Stand (10 reps)',
        'order': 2,
        'max_score': 3,
        'scoring_criteria': {
            0: 'Cannot complete 10 reps',
            1: '10 reps but feet shift multiple times',
            2: '10 reps with 1–2 small shifts',
            3: '10 reps without feet moving'
        },
        'notes': 'Tests functional leg strength and stability. Client performs 10 repetitions.',
    },
    'front_back_lunges': {
        'name': 'Front / Back Lunges (4 per side)',
        'order': 3,
        'max_score': 3,
        'scoring_criteria': {
            0: 'Cannot perform safely',
            1: 'Multiple shifts of planted foot',
            2: '1–2 shifts during test',
            3: 'All reps without moving planted foot'
        },
        'notes': 'Tests dynamic balance and leg strength. 4 forward lunges and 4 backward lunges per leg.',
    },
    'push_up': {
        'name': 'Push-Ups (max 10)',
        'order': 4,
        'max_score': 3,
        'scoring_criteria': {
            0: '0–1 reps',
            1: '2–4 reps',
            2: '5–7 reps',
            3: '8–10 reps'
        },
        'notes': 'Tests upper body and core strength. Client performs standard or modified push-ups (max 10).',
    },
    'plank_hold': {
        'name': 'Plank Hold',
        'order': 5,
        'max_score': 3,
        'scoring_criteria': {
            0: '<10 sec',
            1: '10–20 sec',
            2: '20–40 sec',
            3: '40+ sec'
        },
        'notes': 'Tests core stability and endurance. Client holds a standard front plank position.',
    },
    'deep_squat_hold': {
        'name': 'Deep Squat Hold (parallel, heels down)',
        'order': 6,
        'max_score': 3,
        'scoring_criteria': {
            0: 'Cannot reach parallel without heels lifting',
            1: 'Parallel but heels lift / unstable',
            2: 'Hold 10–20 sec with heels down',
            3: 'Hold 20+ sec stable'
        },
        'notes': 'Tests ankle mobility, hip flexibility, and squat depth. Heels must remain down throughout.',
    },
    'clock_steps': {
        'name': 'Clock Steps (2 rounds)',
        'order': 7,
        'max_score': 3,
        'scoring_criteria': {
            0: 'Cannot complete one round',
            1: 'One round but standing foot moves',
            2: 'Two rounds with some movement',
            3: 'Two rounds without moving standing foot'
        },
        'notes': 'Tests balance, stability, and spatial awareness. Client steps to 12, 3, 6, 9 o\'clock positions around standing foot.',
    },
}

def get_exercise_by_id(exercise_id):
    """Retrieve exercise definition by exercise ID"""
    return FORTIFY_7_EXERCISES.get(exercise_id)

def get_exercise_score_description(exercise_id, score):
    """Get the description for a specific exercise and score"""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise:
        return None
    return exercise['scoring_criteria'].get(score)

def get_all_exercises():
    """Return sorted list of all exercises by order"""
    exercises = list(FORTIFY_7_EXERCISES.values())
    return sorted(exercises, key=lambda x: x['order'])

def validate_exercise_score(exercise_id, score):
    """Validate if a score is valid for an exercise"""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise:
        return False
    return 0 <= score <= exercise['max_score']

def get_assessment_summary(assessment_data):
    """
    Generate a summary of assessment results with exercise-level details
    
    Args:
        assessment_data: dict with keys matching exercise IDs and score values
    
    Returns:
        dict with summary information
    """
    summary = {
        'total_score': 0,
        'max_score': 21,
        'exercises': []
    }
    
    for exercise in get_all_exercises():
        exercise_id = None
        for key in FORTIFY_7_EXERCISES:
            if FORTIFY_7_EXERCISES[key] == exercise:
                exercise_id = key
                break
        
        score = assessment_data.get(exercise_id, 0)
        summary['total_score'] += score
        
        summary['exercises'].append({
            'id': exercise_id,
            'name': exercise['name'],
            'score': score,
            'max': exercise['max_score'],
            'description': exercise['scoring_criteria'][score],
            'percentage': (score / exercise['max_score'] * 100) if exercise['max_score'] > 0 else 0
        })
    
    summary['percentage'] = (summary['total_score'] / summary['max_score'] * 100) if summary['max_score'] > 0 else 0
    
    return summary
