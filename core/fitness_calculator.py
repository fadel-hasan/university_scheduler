class FitnessCalculator:
    """Calculate fitness score for schedule"""
    def __init__(self, conflict_checker, individual_generator, data_collector):
        self.conflict_checker = conflict_checker
        self.individual_generator = individual_generator
        self.data_collector = data_collector

    def calculate_fitness(self, individual):
        """Calculate fitness score for schedule with balanced penalties"""
        penalty = 0

        # total_courses = len(self.data_collector.courses)
        # scheduled_courses = len(set(slot['course'].id for slot in individual))
        # missing_courses = total_courses - scheduled_courses
        # penalty += missing_courses * 20  # High penalty still for missing courses


        penalty += self.conflict_checker.check_internal_conflicts(individual)


        for slot in individual:
            valid_slots = self.individual_generator.get_available_time_slots(slot['teacher'].id, slot['day'])
            penalty += self.conflict_checker.check_teacher_availability(slot, valid_slots) // 2  # was 8, now 4

            penalty += self.conflict_checker.check_external_conflicts(slot, self.data_collector.external_conflicts_map) // 2  # was 10, now 5

            penalty += self.conflict_checker.check_real_time_conflicts(
                slot['teacher'].id, slot['day'], slot['start_time'], slot['end_time']
            ) // 2  

        result = 1 / (1 + penalty)

        if not isinstance(result, (int, float)) or isinstance(result, bool):
            print(f"Warning: Invalid result from calculate_fitness: {result}, data type: {type(result)}")
            return 0.0
        return result
