"""
Simple script to load sample exercises into the database.
Run this from the fitnessPlatform directory with:
python load_exercises.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitnessPlatform.settings')
django.setup()

from apps.exercises.models import Exercise

# Sample exercises data
SAMPLE_EXERCISES = [
    {
        "name": "Bodyweight Squat",
        "description": "A fundamental lower body exercise that strengthens legs and glutes",
        "instructions": "Stand with feet shoulder-width apart. Lower your body by bending knees and hips. Keep chest up and knees tracking over toes. Return to starting position.",
        "difficulty_level": "beginner",
        "equipment": ["bodyweight"],
        "tags": ["lower_body", "compound", "squat_pattern"],
        "contraindications": ["knee_injury", "severe_back_pain"],
        "video_url": "https://www.youtube.com/embed/aclHkVaku9U",
    },
    {
        "name": "Push-Up",
        "description": "Classic upper body exercise targeting chest, shoulders, and triceps",
        "instructions": "Start in plank position. Lower body until chest nearly touches floor. Push back up to starting position. Keep core tight throughout.",
        "difficulty_level": "beginner",
        "equipment": ["bodyweight"],
        "tags": ["upper_body", "push", "chest"],
        "contraindications": ["shoulder_injury", "wrist_pain"],
        "video_url": "https://www.youtube.com/embed/IODxDxX7oi4",
    },
    {
        "name": "Plank",
        "description": "Isometric core strengthening exercise",
        "instructions": "Start in forearm plank position. Keep body in straight line from head to heels. Hold position while breathing normally.",
        "difficulty_level": "beginner",
        "equipment": ["bodyweight"],
        "tags": ["core", "isometric", "stability"],
        "contraindications": ["severe_back_pain", "shoulder_injury"],
        "video_url": "https://www.youtube.com/embed/pSHjTRCQxIw",
    },
    {
        "name": "Dumbbell Goblet Squat",
        "description": "Lower body exercise with added resistance",
        "instructions": "Hold dumbbell at chest level. Perform squat while keeping dumbbell close to body. Drive through heels to return to start.",
        "difficulty_level": "intermediate",
        "equipment": ["dumbbells"],
        "tags": ["lower_body", "compound", "squat_pattern"],
        "contraindications": ["knee_injury", "severe_back_pain"],
        "video_url": "https://www.youtube.com/embed/MeIiIdhvXT4",
    },
    {
        "name": "Dumbbell Bench Press",
        "description": "Upper body pressing exercise for chest development",
        "instructions": "Lie on bench with dumbbells. Press dumbbells up until arms are extended. Lower with control to chest level.",
        "difficulty_level": "intermediate",
        "equipment": ["dumbbells", "bench"],
        "tags": ["upper_body", "push", "chest"],
        "contraindications": ["shoulder_injury"],
        "video_url": "https://www.youtube.com/embed/QsYre__-aro",
    },
    {
        "name": "Barbell Deadlift",
        "description": "Compound exercise targeting posterior chain",
        "instructions": "Stand with feet hip-width apart, bar over mid-foot. Grip bar, keep back straight. Drive through heels to stand up with bar. Lower with control.",
        "difficulty_level": "advanced",
        "equipment": ["barbell"],
        "tags": ["lower_body", "compound", "hinge_pattern", "posterior_chain"],
        "contraindications": ["severe_back_pain", "herniated_disc"],
        "video_url": "https://www.youtube.com/embed/ytGaGIn3SjE",
    },
    {
        "name": "Pull-Up",
        "description": "Upper body pulling exercise for back and biceps",
        "instructions": "Hang from bar with overhand grip. Pull body up until chin clears bar. Lower with control to full hang.",
        "difficulty_level": "advanced",
        "equipment": ["pull-up bar"],
        "tags": ["upper_body", "pull", "back", "vertical_pull"],
        "contraindications": ["shoulder_injury", "elbow_pain"],
        "video_url": "https://www.youtube.com/embed/eGo4IYlbE5g",
    },
    {
        "name": "Walking Lunges",
        "description": "Dynamic lower body exercise for legs and balance",
        "instructions": "Step forward into lunge position. Back knee nearly touches ground. Push through front heel to step into next lunge.",
        "difficulty_level": "intermediate",
        "equipment": ["bodyweight"],
        "tags": ["lower_body", "unilateral", "lunge_pattern"],
        "contraindications": ["knee_injury", "balance_issues"],
        "video_url": "https://www.youtube.com/embed/L8fvypPrzzs",
    },
    {
        "name": "Resistance Band Rows",
        "description": "Upper body pulling exercise using resistance bands",
        "instructions": "Anchor band at chest height. Pull handles toward chest, squeezing shoulder blades together. Return with control.",
        "difficulty_level": "beginner",
        "equipment": ["resistance bands"],
        "tags": ["upper_body", "pull", "back", "horizontal_pull"],
        "contraindications": ["shoulder_injury"],
        "video_url": "https://www.youtube.com/embed/Z5JG1IoRYjQ",
    },
    {
        "name": "Kettlebell Swing",
        "description": "Dynamic hip hinge exercise for power development",
        "instructions": "Stand with kettlebell between feet. Hinge at hips and swing kettlebell between legs. Drive hips forward to swing kettlebell to chest height.",
        "difficulty_level": "intermediate",
        "equipment": ["kettlebell"],
        "tags": ["lower_body", "power", "hinge_pattern", "posterior_chain"],
        "contraindications": ["severe_back_pain", "shoulder_injury"],
        "video_url": "https://www.youtube.com/embed/YSxHifyI6s8",
    },
    {
        "name": "Mountain Climbers",
        "description": "Dynamic cardio and core exercise",
        "instructions": "Start in plank position. Alternately drive knees toward chest in running motion. Maintain stable plank throughout.",
        "difficulty_level": "intermediate",
        "equipment": ["bodyweight"],
        "tags": ["cardio", "core", "full_body"],
        "contraindications": ["wrist_pain", "severe_back_pain"],
        "video_url": "https://www.youtube.com/embed/kLh-uczlPLg",
    },
    {
        "name": "Dumbbell Shoulder Press",
        "description": "Upper body pressing exercise for shoulder development",
        "instructions": "Stand or sit with dumbbells at shoulder height. Press dumbbells overhead until arms are extended. Lower with control.",
        "difficulty_level": "intermediate",
        "equipment": ["dumbbells"],
        "tags": ["upper_body", "push", "shoulders", "vertical_press"],
        "contraindications": ["shoulder_injury", "rotator_cuff_issues"],
        "video_url": "https://www.youtube.com/embed/qEwKCR5JCog",
    },
    {
        "name": "Bicycle Crunches",
        "description": "Core exercise targeting obliques and abs",
        "instructions": "Lie on back with hands behind head. Bring opposite elbow to opposite knee while extending other leg. Alternate sides in cycling motion.",
        "difficulty_level": "beginner",
        "equipment": ["bodyweight"],
        "tags": ["core", "abs", "rotation"],
        "contraindications": ["neck_pain", "severe_back_pain"],
        "video_url": "https://www.youtube.com/embed/Iwyvozckjak",
    },
    {
        "name": "Barbell Back Squat",
        "description": "Compound lower body exercise with barbell across upper back",
        "instructions": "Position barbell on upper back. Stand with feet shoulder-width apart. Squat down keeping chest up. Drive through heels to stand.",
        "difficulty_level": "advanced",
        "equipment": ["barbell", "squat rack"],
        "tags": ["lower_body", "compound", "squat_pattern"],
        "contraindications": ["knee_injury", "severe_back_pain", "shoulder_mobility_issues"],
        "video_url": "https://www.youtube.com/embed/ultWZbUMPL8",
    },
    {
        "name": "TRX Rows",
        "description": "Suspension trainer exercise for back and core",
        "instructions": "Hold TRX handles, lean back with straight body. Pull chest to handles, squeezing shoulder blades. Lower with control.",
        "difficulty_level": "intermediate",
        "equipment": ["suspension trainer"],
        "tags": ["upper_body", "pull", "back", "horizontal_pull", "core"],
        "contraindications": ["shoulder_injury"],
        "video_url": "https://www.youtube.com/embed/3XDriUn0udo",
    },
]


def load_exercises():
    """Load sample exercises into database"""
    print("Loading sample exercises...")
    
    # Clear existing exercises (optional - comment out if you want to keep existing)
    # Exercise.objects.all().delete()
    # print("Cleared existing exercises")
    
    created_count = 0
    skipped_count = 0
    
    for exercise_data in SAMPLE_EXERCISES:
        # Check if exercise already exists
        if Exercise.objects.filter(name=exercise_data['name']).exists():
            print(f"  Skipped: {exercise_data['name']} (already exists)")
            skipped_count += 1
            continue
        
        # Create exercise
        exercise = Exercise.objects.create(**exercise_data)
        print(f"  Created: {exercise.name}")
        created_count += 1
    
    print(f"\n✅ Done! Created {created_count} exercises, skipped {skipped_count} existing exercises.")
    print(f"Total exercises in database: {Exercise.objects.count()}")


if __name__ == "__main__":
    load_exercises()
