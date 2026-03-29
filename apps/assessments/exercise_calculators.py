"""
Exercise Calculator Classes for Assessment Scoring

Each calculator implements the specific calculation logic for a type of exercise:
- DualInputCalculator: Average two inputs, floor, then apply thresholds (Single Leg Stand, Lunges, Clock Steps)
- RepsCalculator: Apply rep thresholds directly (Sit to Stand, Push Ups)
- TimeCalculator: Apply time thresholds directly (Plank Hold, Deep Squat Hold)
"""

import math
from abc import ABC, abstractmethod
from .assessment_scoring_rules import get_exercise_rule


class BaseExerciseCalculator(ABC):
    """Base calculator with common functionality"""

    def __init__(self, exercise_id):
        self.exercise_id = exercise_id
        self.rule = get_exercise_rule(exercise_id)
        if not self.rule:
            raise ValueError(f"Unknown exercise: {exercise_id}")

    def get_score_for_value(self, value):
        """Apply thresholds to get score"""
        value = float(value)
        for threshold in self.rule['thresholds']:
            if threshold['min'] <= value <= threshold['max']:
                return threshold['score']
        return 0

    @abstractmethod
    def calculate(self, inputs):
        """Calculate score from inputs. Raise ValueError if inputs invalid"""
        pass


class DualInputCalculator(BaseExerciseCalculator):
    """
    For exercises with two inputs (left/right) that need to be averaged
    Examples: Single Leg Stand, Front/Back Lunges, Clock Steps
    """

    def calculate(self, left_input, right_input):
        """
        Average both inputs, floor if decimal, then apply threshold

        Returns: {
            'raw_left': float,
            'raw_right': float,
            'averaged': float,
            'floored': int,
            'score': 0-3,
        }
        """
        left_val = float(left_input)
        right_val = float(right_input)

        # Validate ranges
        max_val = self.rule['max_input']
        if not (0 <= left_val <= max_val):
            raise ValueError(f"{self.exercise_id}: left input {left_val} out of range [0-{max_val}]")
        if not (0 <= right_val <= max_val):
            raise ValueError(f"{self.exercise_id}: right input {right_val} out of range [0-{max_val}]")

        # Calculate average
        averaged = (left_val + right_val) / 2.0
        floored = int(math.floor(averaged))

        # Get score from floored value
        score = self.get_score_for_value(floored)

        return {
            'raw_left': left_val,
            'raw_right': right_val,
            'averaged': averaged,
            'floored': floored,
            'score': score,
        }


class RepsCalculator(BaseExerciseCalculator):
    """
    For rep-based exercises with fixed max reps
    Examples: Sit to Stand (10 reps max), Push Ups (10 reps max)
    """

    def calculate(self, reps):
        """
        Apply rep thresholds directly

        Returns: {
            'reps': int,
            'score': 0-3,
        }
        """
        reps_val = int(reps)

        # Validate range
        max_reps = self.rule['max_input']
        if not (0 <= reps_val <= max_reps):
            raise ValueError(f"{self.exercise_id}: reps {reps_val} out of range [0-{max_reps}]")

        # Get score
        score = self.get_score_for_value(reps_val)

        return {
            'reps': reps_val,
            'score': score,
        }


class TimeCalculator(BaseExerciseCalculator):
    """
    For time-based exercises
    Examples: Plank Hold (0-60 sec), Deep Squat Hold (0-20 sec)
    """

    def calculate(self, duration):
        """
        Apply time thresholds directly

        Returns: {
            'duration': float,
            'score': 0-3,
        }
        """
        duration_val = float(duration)

        # Validate range
        max_duration = self.rule['max_input']
        if not (0 <= duration_val <= max_duration):
            raise ValueError(f"{self.exercise_id}: duration {duration_val} out of range [0-{max_duration}]")

        # Get score
        score = self.get_score_for_value(duration_val)

        return {
            'duration': duration_val,
            'score': score,
        }


class ExerciseCalculatorFactory:
    """Factory to get appropriate calculator for an exercise"""

    @staticmethod
    def get_calculator(exercise_id):
        """Get calculator instance for exercise"""
        rule = get_exercise_rule(exercise_id)
        if not rule:
            raise ValueError(f"Unknown exercise: {exercise_id}")

        if rule['type'] in ['dual_input_time', 'dual_input_reps']:
            return DualInputCalculator(exercise_id)
        elif rule['type'] == 'reps':
            return RepsCalculator(exercise_id)
        elif rule['type'] == 'time':
            return TimeCalculator(exercise_id)
        else:
            raise ValueError(f"Unknown exercise type: {rule['type']}")
