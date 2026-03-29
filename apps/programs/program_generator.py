"""
Program Generator

This module contains the logic for generating personalized workout programs
based on user assessments, fitness level, and available exercises.

Process:
1. Calculate fitness level from assessment
2. Select appropriate exercises using ExerciseSelectionEngine
3. Distribute exercises across workout days
4. Apply injury flag modifications
5. Create program with structured day/exercise data
"""

from apps.assessments.scoring_engine import ScoringEngine
from apps.exercises.contraindication_engine import ContraindicationEngine
from apps.programs.exercise_selection_engine import ExerciseSelectionEngine


class ProgramGenerator:
    """
    Generate personalized workout programs.
    
    This class orchestrates the program generation process:
    1. Calculate fitness level from assessment
    2. Select appropriate exercises intelligently
    3. Distribute across workout days
    4. Apply injury-based modifications
    5. Create structured program
    """
    
    # Template structure by competency level
    TEMPLATES = {
        1: {  # Rebuild: 3x/week, full-body focus
            'name': 'Foundation Full-Body',
            'frequency': 3,
            'days': [
                {'day': 1, 'focus': 'Full Body A', 'exercises_per_day': 6},
                {'day': 3, 'focus': 'Full Body B', 'exercises_per_day': 6},
                {'day': 5, 'focus': 'Full Body C', 'exercises_per_day': 6},
            ],
            'total_exercises': 10,
        },
        2: {  # Foundation: 4x/week, upper/lower split
            'name': 'Foundation Upper/Lower',
            'frequency': 4,
            'days': [
                {'day': 1, 'focus': 'Upper Body Push', 'exercises_per_day': 5},
                {'day': 2, 'focus': 'Lower Body', 'exercises_per_day': 5},
                {'day': 4, 'focus': 'Upper Body Pull', 'exercises_per_day': 5},
                {'day': 5, 'focus': 'Lower Body', 'exercises_per_day': 5},
            ],
            'total_exercises': 12,
        },
        3: {  # Build: 4x/week, push/pull/legs/core
            'name': 'Build Push/Pull/Legs',
            'frequency': 4,
            'days': [
                {'day': 1, 'focus': 'Push Day', 'exercises_per_day': 5},
                {'day': 2, 'focus': 'Pull Day', 'exercises_per_day': 5},
                {'day': 4, 'focus': 'Leg Day', 'exercises_per_day': 5},
                {'day': 5, 'focus': 'Accessories', 'exercises_per_day': 5},
            ],
            'total_exercises': 15,
        },
        4: {  # Perform: 5x/week, advanced split
            'name': 'Perform Advanced Split',
            'frequency': 5,
            'days': [
                {'day': 1, 'focus': 'Upper Body A', 'exercises_per_day': 5},
                {'day': 2, 'focus': 'Lower Body A', 'exercises_per_day': 5},
                {'day': 3, 'focus': 'Upper Body B', 'exercises_per_day': 5},
                {'day': 4, 'focus': 'Lower Body B', 'exercises_per_day': 5},
                {'day': 5, 'focus': 'Accessories/Core', 'exercises_per_day': 4},
            ],
            'total_exercises': 18,
        },
    }
    
    def __init__(self, user, assessment):
        """
        Initialize the program generator.
        
        Args:
            user: User model instance
            assessment: Assessment model instance
        """
        self.user = user
        self.assessment = assessment
        self.competency_level = assessment.competency_level
        self.selected_exercises = []
        self.program = None
    
    def get_template(self):
        """
        Get program template for user's competency level.
        
        Returns:
            dict: Template structure with days and exercise distribution
        """
        return self.TEMPLATES.get(self.competency_level, self.TEMPLATES[1])
    
    def select_exercises(self):
        """
        Use ExerciseSelectionEngine to intelligently select exercises.
        
        Returns:
            list: Selected Exercise objects
        """
        selection_engine = ExerciseSelectionEngine(self.user, self.assessment)
        template = self.get_template()
        
        # Select exercises appropriate for competency level
        self.selected_exercises = selection_engine.select_exercises(
            count=template['total_exercises']
        )
        
        return self.selected_exercises
    
    def create_program(self):
        """
        Create the program model.
        
        Returns:
            Program: Created program instance
        """
        from apps.programs.models import Program
        
        template = self.get_template()
        
        # Build program_data structure
        program_data = {
            'weeks': [{
                'week_number': 1,
                'days': [
                    {
                        'day_number': day_info['day'],
                        'focus': day_info['focus'],
                        'exercises': [],
                        'num_exercises': day_info['exercises_per_day'],
                    }
                    for day_info in template['days']
                ],
            }],
        }
        
        self.program = Program.objects.create(
            user=self.user,
            name=f"{template['name']} - Week 1",
            description=f"Personalized {self.assessment.competency_label} level program",
            template_name=template['name'],
            frequency=template['frequency'],
            competency_level=self.competency_level,
            program_data=program_data,
        )
        
        return self.program
    
    def distribute_exercises_to_days(self):
        """
        Distribute selected exercises across workout days.
        
        Assigns exercises to days based on:
        - Day focus (push/pull/legs/core)
        - Exercise category
        - Rest periods
        """
        from apps.programs.models import ProgramDay, DayExercise
        
        if not self.program:
            raise ValueError("Program must be created first")
        
        template = self.get_template()
        exercise_index = 0
        
        for day_info in template['days']:
            day_num = day_info['day']
            focus = day_info['focus']
            exercises_per_day = day_info['exercises_per_day']
            
            # Create program day
            program_day = ProgramDay.objects.create(
                program=self.program,
                day_number=day_num,
                focus=focus,
            )
            
            # Assign exercises to this day
            for order in range(exercises_per_day):
                if exercise_index >= len(self.selected_exercises):
                    break
                
                exercise = self.selected_exercises[exercise_index]
                
                # Determine sets/reps based on competency and exercise focus
                sets, reps = self._get_sets_reps(exercise, focus)
                
                DayExercise.objects.create(
                    day=program_day,
                    exercise=exercise,
                    order=order,
                    sets=sets,
                    reps=reps,
                    rest_seconds=60,
                )
                
                exercise_index += 1
                
                # Update program_data with exercises
                day_data = next(
                    d for d in self.program.program_data['weeks'][0]['days']
                    if d['day_number'] == day_num
                )
                day_data['exercises'].append({
                    'id': exercise.id,
                    'name': exercise.name,
                    'sets': sets,
                    'reps': reps,
                    'rest_seconds': 60,
                })
        
        self.program.save()
    
    def _get_sets_reps(self, exercise, day_focus):
        """
        Determine appropriate sets/reps based on competency and exercise.
        
        Args:
            exercise: Exercise object
            day_focus: Day focus (e.g., 'Lower Body')
            
        Returns:
            tuple: (sets, reps)
        """
        # Competency determines volume
        volume_map = {
            1: (2, 10),   # Rebuild: 2x8-10 (moderate volume)
            2: (3, 8),    # Foundation: 3x8 (higher volume)
            3: (3, 6),    # Build: 3x6 (strength focus)
            4: (4, 5),    # Perform: 4x5 (advanced)
        }
        
        # Get base sets/reps from competency
        base_sets, base_reps = volume_map.get(self.competency_level, (3, 10))
        
        # Adjust for exercise type if needed
        if 'mobility' in [tag.lower() for tag in exercise.tags]:
            return 1, 12  # Mobility: 1x12 (higher reps)
        
        return base_sets, base_reps
    
    def apply_injury_modifications(self):
        """
        Apply modifications to program based on injury flags.
        
        This is handled by the exercise selection engine which already
        filters out contraindicated exercises. This method documents
        injury flags for the user's awareness.
        """
        injury_flags = self.assessment.get_injury_flags()
        
        if injury_flags:
            # Add injury notes to program
            flag_text = "⚠️ Injury Flags: " + ", ".join(
                f"{area} ({status})"
                for area, status in injury_flags.items()
            )
            
            current_desc = self.program.description or ""
            self.program.description = f"{current_desc}\n\n{flag_text}"
            self.program.save()
    
    def generate_program(self):
        """
        Run complete program generation process.
        
        Returns:
            Program: Generated program with structured days and exercises
        """
        # Step 1: Select exercises
        self.select_exercises()
        
        # Step 2: Create program
        self.create_program()
        
        # Step 3: Distribute exercises to days
        self.distribute_exercises_to_days()
        
        # Step 4: Apply injury modifications
        self.apply_injury_modifications()
        
        return self.program

