import pandas as pd

class SchedulePresenter:
    """Display and analyze schedules"""
    def __init__(self, data_collector, conflict_checker):
        self.data_collector = data_collector
        self.conflict_checker = conflict_checker

    def get_schedule_as_dataframe(self, individual):
        """Convert schedule to DataFrame for display"""
        days_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
        # Create empty DataFrame
        time_slots_str = [f"{slot[0].strftime('%H:%M')}-{slot[1].strftime('%H:%M')}" for slot in self.data_collector.time_slots]
        df = pd.DataFrame(index=time_slots_str, columns=days_names)
        # Fill DataFrame with data
        for slot in individual:
            day = days_names[slot['day']]
            time_slot = f"{slot['start_time'].strftime('%H:%M')}-{slot['end_time'].strftime('%H:%M')}"
            # Format cell content
            cell_content = f"{slot['course'].name}\n{slot['teacher'].name}\n{slot['classroom'].name}"
            df.at[time_slot, day] = cell_content
        return df

    def analyze_conflicts(self, individual):
        """Analyze conflicts in schedule"""
        conflicts = {
            'teacher_conflicts': [],
            'classroom_conflicts': [],
            'year_conflicts': [],
            'external_conflicts': [],
            'availability_violations': []
        }
        used_teacher_slots = set()
        used_classroom_slots = set()
        used_year_slots = set()
        for i, slot in enumerate(individual):
            key_teacher = (slot['teacher'].id, slot['day'], slot['start_time'], slot['end_time'])
            key_classroom = (slot['classroom'].id, slot['day'], slot['start_time'], slot['end_time'])
            key_year = (self.data_collector.academic_year_id, slot['day'], slot['start_time'], slot['end_time'])

            # Teacher conflicts
            if key_teacher in used_teacher_slots:
                conflicts['teacher_conflicts'].append({
                    'slot_index': i,
                    'teacher': slot['teacher'].name,
                    'day': slot['day'],
                    'time': f"{slot['start_time']}-{slot['end_time']}"
                })
            else:
                used_teacher_slots.add(key_teacher)

            # Classroom conflicts
            if key_classroom in used_classroom_slots:
                conflicts['classroom_conflicts'].append({
                    'slot_index': i,
                    'classroom': slot['classroom'].name,
                    'day': slot['day'],
                    'time': f"{slot['start_time']}-{slot['end_time']}"
                })
            else:
                used_classroom_slots.add(key_classroom)

            # Year conflicts
            if key_year in used_year_slots:
                conflicts['year_conflicts'].append({
                    'slot_index': i,
                    'course': slot['course'].name,
                    'year': self.data_collector.academic_year_id,
                    'day': slot['day'],
                    'time': f"{slot['start_time']}-{slot['end_time']}"
                })
            else:
                used_year_slots.add(key_year)

            # External conflicts
            teacher_id = slot['teacher'].id
            day = slot['day']
            time_slot = (slot['start_time'], slot['end_time'])
            if (teacher_id in self.data_collector.external_conflicts_map and 
                day in self.data_collector.external_conflicts_map[teacher_id] and 
                time_slot in self.data_collector.external_conflicts_map[teacher_id][day]):
                conflicts['external_conflicts'].append({
                    'slot_index': i,
                    'teacher': slot['teacher'].name,
                    'day': slot['day'],
                    'time': f"{slot['start_time']}-{slot['end_time']}"
                })

            # Availability violations
            valid_slots = self.individual_generator.get_available_time_slots(slot['teacher'].id, slot['day']) # This needs to be passed or accessed differently
            # For now, we'll re-calculate it here as a quick fix, but ideally it should be passed from the generator or recalculated efficiently
            base_slots = self.data_collector.teacher_slot_map.get(slot['teacher'].id, {}).get(slot['day'], [])
            available_slots = []
            for slot_start, slot_end in base_slots:
                if slot['teacher'].id in self.data_collector.external_conflicts_map and slot['day'] in self.data_collector.external_conflicts_map[slot['teacher'].id]:
                    if (slot_start, slot_end) in self.data_collector.external_conflicts_map[slot['teacher'].id][slot['day']]:
                        continue
                if not self.conflict_checker.check_real_time_conflicts(slot['teacher'].id, slot['day'], slot_start, slot_end):
                    available_slots.append((slot_start, slot_end))

            if (slot['start_time'], slot['end_time']) not in available_slots:
                conflicts['availability_violations'].append({
                    'slot_index': i,
                    'teacher': slot['teacher'].name,
                    'day': slot['day'],
                    'time': f"{slot['start_time']}-{slot['end_time']}"
                })
        return conflicts

    def print_conflicts_analysis(self, individual):
        """Print conflict analysis"""
        conflicts = self.analyze_conflicts(individual)
        print("=== Conflict Analysis ===")
        print(f"Teacher conflicts: {len(conflicts['teacher_conflicts'])}")
        print(f"Classroom conflicts: {len(conflicts['classroom_conflicts'])}")
        print(f"Year conflicts: {len(conflicts['year_conflicts'])}")
        print(f"External conflicts: {len(conflicts['external_conflicts'])}")
        print(f"Availability violations: {len(conflicts['availability_violations'])}")
        if conflicts['external_conflicts']:
            print("\nExternal conflicts:")
            for conflict in conflicts['external_conflicts']:
                print(f"  - Teacher {conflict['teacher']} on day {conflict['day']} at time {conflict['time']}")
        return conflicts

    def display_schedule_details(self, individual):
        """Display schedule details"""
        if not individual:
            print("Schedule is empty!")
            return
        print("=== Schedule Details ===")
        print(f"Number of slots: {len(individual)}")
        print()
        days_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
        # Group slots by day
        schedule_by_day = {day: [] for day in range(7)}
        for slot in individual:
            day = slot['day']
            schedule_by_day[day].append(slot)
        # Display detailed schedule
        for day in range(5):
            day_name = days_names[day]
            slots = schedule_by_day[day]
            if slots:
                print(f"\n{day_name}:")
                # Sort slots by time
                slots.sort(key=lambda x: x['start_time'])
                for slot in slots:
                    start_time = slot['start_time'].strftime('%H:%M')
                    end_time = slot['end_time'].strftime('%H:%M')
                    course_name = slot['course'].name
                    teacher_name = slot['teacher'].name
                    classroom_name = slot['classroom'].name
                    print(f"  {start_time}-{end_time}: {course_name}")
                    print(f"    Teacher: {teacher_name}")
                    print(f"    Classroom: {classroom_name}")
            else:
                print(f"\n{day_name}: No lectures")
        # Analyze conflicts
        conflicts = self.analyze_conflicts(individual)
        print(f"\n=== Conflict Analysis ===")
        print(f"Teacher conflicts: {len(conflicts['teacher_conflicts'])}")
        print(f"Classroom conflicts: {len(conflicts['classroom_conflicts'])}")
        print(f"Year conflicts: {len(conflicts['year_conflicts'])}")
        print(f"External conflicts: {len(conflicts['external_conflicts'])}")
        print(f"Availability violations: {len(conflicts['availability_violations'])}")
        # Calculate fitness score
        # Note: FitnessCalculator is needed here, assuming it's passed or imported
        # fitness = self.fitness_calculator.calculate_fitness(individual) # This would need access to FitnessCalculator
        # print(f"\nFitness score: {fitness:.4f}")
        # if fitness == 1.0:
        #     print("🎉 Perfect schedule! No conflicts.")
        # elif fitness > 0.8:
        #     print("✅ Schedule is very good.")
        # elif fitness > 0.6:
        #     print("⚠️ Schedule is acceptable with some conflicts.")
        # else:
        #     print("❌ Schedule needs improvement.")