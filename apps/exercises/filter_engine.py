"""
Filter Engine for Exercise Selection

This module contains the logic for filtering exercises based on
available equipment and other criteria.
"""


class FilterEngine:
    """
    Filter exercises based on equipment and other criteria.
    
    This class applies various filters to narrow down exercise selection
    based on user's available equipment and preferences.
    """
    
    def __init__(self, available_equipment=None):
        """
        Initialize the filter engine.
        
        Args:
            available_equipment: List of available equipment
        """
        self.available_equipment = available_equipment or []
    
    def filter_by_equipment(self, exercises):
        """
        Filter exercises by available equipment.
        
        Args:
            exercises: QuerySet or list of Exercise objects
            
        Returns:
            list: Filtered exercises matching equipment constraints
        """
        if not self.available_equipment:
            # If no equipment specified, return bodyweight exercises
            return [
                ex for ex in exercises 
                if 'bodyweight' in [e.lower() for e in ex.equipment]
            ]
        
        filtered_exercises = []
        
        for exercise in exercises:
            # Check if exercise requires only available equipment
            exercise_equipment = [e.lower() for e in exercise.equipment]
            available_equipment_lower = [e.lower() for e in self.available_equipment]
            
            # Allow if all required equipment is available or exercise is bodyweight
            if (all(eq in available_equipment_lower for eq in exercise_equipment) or
                'bodyweight' in exercise_equipment):
                filtered_exercises.append(exercise)
        
        return filtered_exercises
    
    def filter_by_tags(self, exercises, required_tags=None, excluded_tags=None):
        """
        Filter exercises by tags.
        
        Args:
            exercises: QuerySet or list of Exercise objects
            required_tags: List of tags that must be present
            excluded_tags: List of tags that must not be present
            
        Returns:
            list: Filtered exercises
        """
        required_tags = required_tags or []
        excluded_tags = excluded_tags or []
        
        filtered_exercises = []
        
        for exercise in exercises:
            exercise_tags = [tag.lower() for tag in exercise.tags]
            
            # Check required tags
            has_required = all(
                tag.lower() in exercise_tags 
                for tag in required_tags
            )
            
            # Check excluded tags
            has_excluded = any(
                tag.lower() in exercise_tags 
                for tag in excluded_tags
            )
            
            if has_required and not has_excluded:
                filtered_exercises.append(exercise)
        
        return filtered_exercises
    
    def filter_by_fitness_level(self, exercises, fitness_level):
        """
        Filter exercises appropriate for fitness level.
        
        Args:
            exercises: QuerySet or list of Exercise objects
            fitness_level: String ('beginner', 'intermediate', 'advanced')
            
        Returns:
            list: Filtered exercises
        """
        # Filter by difficulty tags matching fitness level
        level_tags = {
            'beginner': ['beginner', 'easy'],
            'intermediate': ['beginner', 'intermediate', 'moderate'],
            'advanced': ['intermediate', 'advanced', 'difficult'],
        }
        
        appropriate_tags = level_tags.get(fitness_level, ['beginner'])
        
        filtered_exercises = []
        
        for exercise in exercises:
            exercise_tags = [tag.lower() for tag in exercise.tags]
            
            # Include exercise if it has any appropriate difficulty tag
            if any(tag in exercise_tags for tag in appropriate_tags):
                filtered_exercises.append(exercise)
        
        return filtered_exercises
    
    def apply_all_filters(self, exercises, fitness_level=None, 
                         required_tags=None, excluded_tags=None):
        """
        Apply all filters in sequence.
        
        Args:
            exercises: QuerySet or list of Exercise objects
            fitness_level: Fitness level string
            required_tags: List of required tags
            excluded_tags: List of excluded tags
            
        Returns:
            list: Fully filtered exercises
        """
        # Apply equipment filter
        filtered = self.filter_by_equipment(exercises)
        
        # Apply fitness level filter
        if fitness_level:
            filtered = self.filter_by_fitness_level(filtered, fitness_level)
        
        # Apply tag filters
        if required_tags or excluded_tags:
            filtered = self.filter_by_tags(
                filtered, 
                required_tags=required_tags,
                excluded_tags=excluded_tags
            )
        
        return filtered
