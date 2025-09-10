from sqlalchemy.orm import Session
from db.models import ScheduleSlot, Schedule

class ConflictChecker:
    """Check conflicts within schedule or with external schedules"""
    def __init__(self, data_collector):
        self.data_collector = data_collector
        self.session = data_collector.session

    def check_internal_conflicts(self, individual):
        """Check conflicts within schedule (teacher, classroom, year)"""
        penalty = 0
        used_teacher_slots = set()
        used_classroom_slots = set()
        used_year_slots = set()
        
        for slot in individual:
            key_teacher = (slot['teacher'].id, slot['day'], slot['start_time'], slot['end_time'])
            key_classroom = (slot['classroom'].id, slot['day'], slot['start_time'], slot['end_time'])
            key_year = (self.data_collector.academic_year_id, slot['day'], slot['start_time'], slot['end_time'])
    
            if key_teacher in used_teacher_slots:
                penalty += 5  # was 10
            else:
                used_teacher_slots.add(key_teacher)
    
            if key_classroom in used_classroom_slots:
                penalty += 3  # was 6
            else:
                used_classroom_slots.add(key_classroom)
    
            if key_year in used_year_slots:
                penalty += 2  # was 5
            else:
                used_year_slots.add(key_year)
    
        return penalty

    def check_teacher_availability(self, slot, available_time_slots):
        """Check teacher availability for specified slot"""

        if (slot['start_time'], slot['end_time']) not in available_time_slots:
            return 8
        return 0

    def check_external_conflicts(self, slot, external_conflicts_map):
        """Check conflicts with external schedules"""
        # External conflict (teacher teaching other year in same slot)
        teacher_id = slot['teacher'].id
        day = slot['day']
        time_slot = (slot['start_time'], slot['end_time'])
        if (teacher_id in external_conflicts_map and 
            day in external_conflicts_map[teacher_id] and 
            time_slot in external_conflicts_map[teacher_id][day]):
            return 10
        return 0

    def check_real_time_conflicts(self, teacher_id, day, start_time, end_time):
        """Check actual conflicts in database"""
        # Check conflicts from all saved schedules
        conflicting_slots = self.session.query(ScheduleSlot).join(Schedule).filter(
            ScheduleSlot.teacher_id == teacher_id,
            ScheduleSlot.day_of_week == day,
            ScheduleSlot.start_time == start_time,
            ScheduleSlot.end_time == end_time
        ).all()
        if len(conflicting_slots) > 0:
            return 15  
        return 0

    def check_app_conflicts(self):
        """Check conflicts in application directly"""
        print("=== Checking Application Conflicts ===")

        all_schedules = self.session.query(ScheduleSlot).join(Schedule).all()
        # Group conflicts by teacher and time
        conflicts_by_teacher = {}
        for slot in all_schedules:
            teacher_id = slot.teacher_id
            day = slot.day_of_week
            start_time = slot.start_time
            end_time = slot.end_time
            key = (teacher_id, day, start_time, end_time)
            if key not in conflicts_by_teacher:
                conflicts_by_teacher[key] = []
            conflicts_by_teacher[key].append({
                'schedule_id': slot.schedule_id,
                'schedule_name': slot.schedule.name,
                'course_id': slot.course_id,
                'course_name': getattr(slot, 'course', None) and slot.course.name or "Unknown",
                'academic_year_id': slot.schedule.academic_year_id
            })

        total_conflicts = 0
        for (teacher_id, day, start_time, end_time), schedules in conflicts_by_teacher.items():
            if len(schedules) > 1:
                total_conflicts += 1
                teacher_name = next((t.name for t in self.data_collector.teachers if t.id == teacher_id), "Unknown")
                print(f"\nConflict for teacher {teacher_name}:")
                print(f"  Day: {day}")
                print(f"  Time: {start_time} - {end_time}")
                print(f"  Number of conflicting schedules: {len(schedules)}")
                for i, schedule in enumerate(schedules, 1):
                    print(f"  {i}. Schedule: {schedule['schedule_name']}")
                    print(f"     Course: {schedule['course_name']}")
                    print(f"     Academic year: {schedule['academic_year_id']}")
                    print(f"     Schedule ID: {schedule['schedule_id']}")
        print(f"\nTotal conflicts: {total_conflicts}")
        if total_conflicts == 0:
            print("✅ No conflicts in application!")
        else:
            print("❌ Conflicts found in application!")
        return conflicts_by_teacher

    def check_all_current_conflicts(self):
        """Check all current conflicts in database"""
        print("=== Checking All Current Conflicts ===")

        all_schedules = self.session.query(ScheduleSlot).join(Schedule).all()

        teacher_conflicts = {}
        for slot in all_schedules:
            teacher_id = slot.teacher_id
            day = slot.day_of_week
            time_slot = (slot.start_time, slot.end_time)
            schedule_name = slot.schedule.name
            course_name = slot.course.name if hasattr(slot, 'course') else "Unknown"
            key = (teacher_id, day, time_slot)
            if key not in teacher_conflicts:
                teacher_conflicts[key] = []
            teacher_conflicts[key].append({
                'schedule_name': schedule_name,
                'course_name': course_name,
                'schedule_id': slot.schedule_id
            })

        conflict_count = 0
        for (teacher_id, day, time_slot), schedules in teacher_conflicts.items():
            if len(schedules) > 1:
                conflict_count += 1
                teacher_name = next((t.name for t in self.data_collector.teachers if t.id == teacher_id), "Unknown")
                print(f"\nConflict for teacher {teacher_name} on day {day} at time {time_slot[0]}-{time_slot[1]}:")
                for schedule in schedules:
                    print(f"  - Schedule: {schedule['schedule_name']}")
                    print(f"    Course: {schedule['course_name']}")
                    print(f"    Schedule ID: {schedule['schedule_id']}")
        print(f"\nTotal conflicts: {conflict_count}")
        return teacher_conflicts