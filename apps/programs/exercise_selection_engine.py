"""
Exercise Selection Engine for Personalized Program Generation

This module intelligently selects exercises based on:
- User's competency level (1-4)
- Injury flags and contraindications
- Available equipment
- Exercise variety and progression

Algorithm:
1. Filter exercises by competency level match
2. Apply safety filters (remove contraindicated exercises)
3. Balance exercise categories (push/pull/legs/core)
4. Ensure exercise variety (avoid repetition)
5. Assign exercises to template slots
6. Apply progressive difficulty if multi-week program
"""

from collections import defaultdict
import random
from apps.exercises.models import Exercise
from apps.exercises.contraindication_engine import ContraindicationEngine


class ExerciseSelectionEngine:
    """
    Intelligently select exercises for personalized programs.
    
    Handles:
    - Competency-level filtering
    - Safety contraindication filtering
    - Category balancing (push/pull/legs/core)
    - Exercise novelty
    - Template slot fulfillment
    """
    
    # Exercise categories for balancing
    EXERCISE_CATEGORIES = {
        'upper_push': ['push', 'press', 'dips', 'bench'],
        'upper_pull': ['pull', 'row', 'chin', 'lat'],
        'lower': ['squat', 'lunge', 'leg', 'deadlift', 'hip'],
        'core': ['plank', 'core', 'abs', 'rotation', 'anti'],
        'mobility': ['mobility', 'stretch', 'flexibility', 'foam'],
    }
    
    # Competency level to exercise difficulty mapping
    COMPETENCY_TO_DIFFICULTY = {
        1: ['beginner'],  # Rebuild: beginner only
        2: ['beginner', 'intermediate'],  # Foundation: beginner + intermediate
        3: ['intermediate', 'advanced'],  # Build: intermediate + advanced
        4: ['advanced'],  # Perform: advanced only
    }
    
    def __init__(self, user, assessment):
        """
        Initialize the exercise selection engine.
        
        Args:
            user: User model instance
            assessment: Assessment model instance with competency_level
        """
        self.user = user
        self.assessment = assessment
        self.competency_level = assessment.competency_level
        self.injury_flags = assessment.get_injury_flags()
        self.selected_exercises = []
        self.category_count = defaultdict(int)
    
    def get_difficulty_tags(self):
        """
        Get exercise difficulty tags appropriate for user's level.
        
        Returns:
            list: Difficulty tags (e.g., ['beginner', 'intermediate'])
        """
        return self.COMPETENCY_TO_DIFFICULTY.get(self.competency_level, ['beginner'])
    
    def filter_by_competency(self, exercises):
        """
        Filter exercises by competency level.
        
        Args:
            exercises: QuerySet or list of Exercise objects
            
        Returns:
            list: Exercises matching user's competency level
        """
        appropriate_difficulties = self.get_difficulty_tags()
        filtered = []
        
        for exercise in exercises:
            exercise_tags = [tag.lower() for tag in exercise.tags]
            
            # Include if exercise has appropriate difficulty tag
            if any(tag in exercise_tags for tag in appropriate_difficulties):
                filtered.append(exercise)
        
        return filtered
    
    def filter_by_safety(self, exercises):
        """
        Remove exercises contraindicated by injury flags.
        
        Args:
            exercises: QuerySet or list of Exercise objects
            
        Returns:
            list: Safe exercises for user
        """
        contraindication_engine = ContraindicationEngine(
            user_injuries=self.assessment.get_injury_flags(),
            medical_conditions=getattr(self.user.profile, 'medical_conditions', ''),
            pain_areas=getattr(self.user.profile, 'pain_areas', '')
        )
        
        return contraindication_engine.filter_exercises(exercises)
    
    def get_category(self, exercise):
        """
        Determine exercise category based on tags.
        
        Args:
            exercise: Exercise object
            
        Returns:
            str: Category name ('upper_push', 'upper_pull', 'lower', 'core', 'mobility', 'other')
        """
        exercise_tags = [tag.lower() for tag in exercise.tags]
        exercise_tags_str = ' '.join(exercise_tags)
        
        for category, keywords in self.EXERCISE_CATEGORIES.items():
            # Check if any keyword appears in the exercise tags (substring match)
            if any(keyword in tag for tag in exercise_tags for keyword in keywords):
                return category
        
        return 'other'
    
    def select_balanced_exercises(self, exercises, count=10):
        """
        Select exercises while balancing categories.
        
        Tries to maintain even distribution across:
        - Upper Push (1-2 exercises)
        - Upper Pull (1-2 exercises)
        - Lower Body (2-3 exercises)
        - Core (1-2 exercises)
        - Mobility (1 exercise)
        
        Args:
            exercises: Filtered list of safe, competency-appropriate exercises
            count: Total number of exercises to select
            
        Returns:
            list: Balanced selection of exercises
        """
        selected = []
        category_count = defaultdict(int)
        used_exercise_ids = set()
        
        # Target distribution by category
        targets = {
            'upper_push': max(1, count // 6),
            'upper_pull': max(1, count // 6),
            'lower': max(2, count // 3),
            'core': max(1, count // 6),
            'mobility': max(1, count // 8),
        }
        
        # Priority 1: Fill major categories first
        major_categories = ['lower', 'upper_push', 'upper_pull', 'core']
        
        for category in major_categories:
            target = targets[category]
            matching = [
                ex for ex in exercises 
                if self.get_category(ex) == category and ex.id not in used_exercise_ids
            ]
            
            selected_count = min(target, len(matching))
            for ex in matching[:selected_count]:
                selected.append(ex)
                category_count[category] += 1
                used_exercise_ids.add(ex.id)
        
        # Priority 2: Add mobility/accessory exercises
        mobility_exercises = [
            ex for ex in exercises 
            if self.get_category(ex) == 'mobility' and ex.id not in used_exercise_ids
        ]
        remaining_target = count - len(selected)
        for ex in mobility_exercises[:remaining_target]:
            selected.append(ex)
            category_count['mobility'] += 1
            used_exercise_ids.add(ex.id)
        
        # Priority 3: Fill remaining slots with most appropriate
        remaining_target = count - len(selected)
        for category in major_categories:
            if remaining_target <= 0:
                break
            matching = [
                ex for ex in exercises 
                if self.get_category(ex) == category and ex.id not in used_exercise_ids
            ]
            for ex in matching[:remaining_target]:
                selected.append(ex)
                remaining_target -= 1
                used_exercise_ids.add(ex.id)
        
        return selected[:count]
    
    def apply_equipment_filter(self, exercises):
        """
        Filter exercises by available equipment.
        
        Args:
            exercises: QuerySet or list of Exercise objects
            
        Returns:
            list: Exercises matching available equipment
        """
        equipment = getattr(self.assessment, 'equipment', '')
        
        if not equipment:
            # No equipment specified - return bodyweight only
            return [
                ex for ex in exercises 
                if 'bodyweight' in [tag.lower() for tag in ex.tags]
            ]
        
        if isinstance(equipment, str):
            available = [e.strip().lower() for e in equipment.split(',')]
        else:
            available = equipment
        
        filtered = []
        for exercise in exercises:
            exercise_tags = [tag.lower() for tag in exercise.tags]
            exercise_equipment = [eq.lower() for eq in getattr(exercise, 'equipment', [])]
            
            # Include if equipment is available or exercise is bodyweight
            if (all(eq in available for eq in exercise_equipment) or 
                'bodyweight' in exercise_tags):
                filtered.append(exercise)
        
        return filtered
    
    def select_exercises(self, count=10):
        """
        Run complete exercise selection process.
        
        Args:
            count: Number of exercises to select
            
        Returns:
            list: Selected Exercise objects
        """
        # Get all exercises
        all_exercises = Exercise.objects.filter(exercise_type='workout')
        
        # Step 1: Apply competency filter
        exercises = self.filter_by_competency(all_exercises)
        
        # Step 2: Apply equipment filter
        exercises = self.apply_equipment_filter(exercises)
        
        # Step 3: Apply safety filters
        exercises = self.filter_by_safety(exercises)
        
        # Step 4: Select balanced exercises
        self.selected_exercises = self.select_balanced_exercises(exercises, count)
        
        return self.selected_exercises
    
    def get_selection_summary(self):
        """
        Get summary of selected exercises by category.
        
        Returns:
            dict: Category breakdown of selections
        """
        summary = defaultdict(list)
        
        for exercise in self.selected_exercises:
            category = self.get_category(exercise)
            summary[category].append({
                'id': exercise.id,
                'name': exercise.name,
                'difficulty': exercise.difficulty_level,
            })
        
        return dict(summary)
