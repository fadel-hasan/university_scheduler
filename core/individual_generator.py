import random


class IndividualGenerator:
    """Create and modify schedules (individuals)"""
    def __init__(self, data_collector, conflict_checker):
        self.data_collector = data_collector
        self.conflict_checker = conflict_checker

    def get_available_time_slots(self, teacher_id, day):
        """Get available time slots while avoiding actual conflicts"""
        base_slots = self.data_collector.teacher_slot_map.get(teacher_id, {}).get(day, [])
        available_slots = []
        
        for slot_start, slot_end in base_slots:
            # Check external conflicts from map
            if teacher_id in self.data_collector.external_conflicts_map and day in self.data_collector.external_conflicts_map[teacher_id]:
                if (slot_start, slot_end) in self.data_collector.external_conflicts_map[teacher_id][day]:
                    continue  # Skip this slot if it conflicts
                
            # Check real-time conflicts
            if not self.conflict_checker.check_real_time_conflicts(teacher_id, day, slot_start, slot_end):
                available_slots.append((slot_start, slot_end))
        return available_slots

    def generate_individual(self):
        """Generate a random schedule (individual) with repair to ensure completeness"""
        individual = []
        max_attempts_per_course = 50  

        for course in self.data_collector.courses:
            slot_added = False
            attempts = 0
            while not slot_added and attempts < max_attempts_per_course:
                attempts += 1
                # اختيار مدرس متاح
                teacher = random.choice(course.teachers)
                # اختيار يوم عشوائي
                day = random.choice(self.data_collector.days)
                # الحصول على الأوقات المتاحة للمدرس في هذا اليوم
                available_slots = self.get_available_time_slots(teacher.id, day)
                # إزالة slots التي فيها conflicts خارجية
                teacher_conflicts = self.data_collector.external_conflicts_map.get(teacher.id, {}).get(day, set())
                available_slots = [slot for slot in available_slots if slot not in teacher_conflicts]

                if available_slots:
                    start_time, end_time = random.choice(available_slots)
                    classroom = random.choice(self.data_collector.classrooms)
                    individual.append({
                        'course': course,
                        'teacher': teacher,
                        'classroom': classroom,
                        'day': day,
                        'start_time': start_time,
                        'end_time': end_time
                    })
                    slot_added = True

            # **Repair:** إذا لم ينجح الاختيار العشوائي، نجرب كل المدرسين وكل الأيام
            if not slot_added:
                for teacher in course.teachers:
                    for day in self.data_collector.days:
                        available_slots = self.get_available_time_slots(teacher.id, day)
                        teacher_conflicts = self.data_collector.external_conflicts_map.get(teacher.id, {}).get(day, set())
                        available_slots = [slot for slot in available_slots if slot not in teacher_conflicts]
                        if available_slots:
                            start_time, end_time = random.choice(available_slots)
                            classroom = random.choice(self.data_collector.classrooms)
                            individual.append({
                                'course': course,
                                'teacher': teacher,
                                'classroom': classroom,
                                'day': day,
                                'start_time': start_time,
                                'end_time': end_time
                            })
                            slot_added = True
                            break
                    if slot_added:
                        break

            # إذا لم نتمكن من وضع الحصة، نضعها مؤقتًا على أي يوم/وقت/مدرس للقضاء على المادة المفقودة
            if not slot_added:
                teacher = random.choice(course.teachers)
                day = random.choice(self.data_collector.days)
                start_time, end_time = random.choice(self.data_collector.time_slots)
                classroom = random.choice(self.data_collector.classrooms)
                individual.append({
                    'course': course,
                    'teacher': teacher,
                    'classroom': classroom,
                    'day': day,
                    'start_time': start_time,
                    'end_time': end_time
                })
        return individual

    def mutate(self, individual, mutation_rate):
        """Apply mutation to schedule"""
        for slot in individual:
            if random.random() < mutation_rate:
                day = random.choice(self.data_collector.days)
                teacher = random.choice(slot['course'].teachers)
                valid_slots = self.get_available_time_slots(teacher.id, day)
                # Avoid external conflicts
                teacher_id = teacher.id
                if teacher_id in self.data_collector.external_conflicts_map and day in self.data_collector.external_conflicts_map[teacher_id]:
                    external_conflicts = self.data_collector.external_conflicts_map[teacher_id][day]
                    valid_slots = [slot for slot in valid_slots if slot not in external_conflicts]
                if valid_slots:
                    slot['day'] = day
                    slot['start_time'], slot['end_time'] = random.choice(valid_slots)
                    slot['classroom'] = random.choice(self.data_collector.classrooms)
                    slot['teacher'] = teacher
        return individual