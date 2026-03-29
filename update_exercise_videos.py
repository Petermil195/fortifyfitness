"""
Update exercises with YouTube video URLs
Run this from the fitnessPlatform directory with:
python update_exercise_videos.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitnessPlatform.settings')
django.setup()

from apps.exercises.models import Exercise

# Exercise name to video URL mapping
VIDEO_URLS = {
    "Bodyweight Squat": "https://www.youtube.com/embed/aclHkVaku9U",
    "Push-Up": "https://www.youtube.com/embed/IODxDxX7oi4",
    "Plank": "https://www.youtube.com/embed/pSHjTRCQxIw",
    "Dumbbell Goblet Squat": "https://www.youtube.com/embed/MeIiIdhvXT4",
    "Dumbbell Bench Press": "https://www.youtube.com/embed/QsYre__-aro",
    "Barbell Deadlift": "https://www.youtube.com/embed/ytGaGIn3SjE",
    "Pull-Up": "https://www.youtube.com/embed/eGo4IYlbE5g",
    "Walking Lunges": "https://www.youtube.com/embed/L8fvypPrzzs",
    "Resistance Band Rows": "https://www.youtube.com/embed/Z5JG1IoRYjQ",
    "Kettlebell Swing": "https://www.youtube.com/embed/YSxHifyI6s8",
    "Mountain Climbers": "https://www.youtube.com/embed/kLh-uczlPLg",
    "Dumbbell Shoulder Press": "https://www.youtube.com/embed/qEwKCR5JCog",
    "Bicycle Crunches": "https://www.youtube.com/embed/Iwyvozckjak",
    "Barbell Back Squat": "https://www.youtube.com/embed/ultWZbUMPL8",
    "TRX Rows": "https://www.youtube.com/embed/3XDriUn0udo",
}

def update_video_urls():
    """Update exercises with video URLs"""
    print("Updating exercises with YouTube video URLs...")
    
    updated_count = 0
    not_found_count = 0
    
    for name, video_url in VIDEO_URLS.items():
        try:
            exercise = Exercise.objects.get(name=name)
            exercise.video_url = video_url
            exercise.save()
            print(f"  ✅ Updated: {name}")
            updated_count += 1
        except Exercise.DoesNotExist:
            print(f"  ⚠️  Not found: {name}")
            not_found_count += 1
    
    print(f"\n✅ Done! Updated {updated_count} exercises")
    if not_found_count > 0:
        print(f"⚠️  Could not find {not_found_count} exercises")


if __name__ == '__main__':
    update_video_urls()
