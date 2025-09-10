import random
from datetime import time
from sqlalchemy.orm import Session
from db.models import Teacher, Course, Classroom, AcademicYear, TeacherAvailability, Schedule, ScheduleSlot

class DataCollector:
    """Collect necessary data from database and prepare the algorithm"""
    def __init__(self, session: Session, academic_year_id: int):
        self.session = session
        self.academic_year_id = academic_year_id
        self.academic_year = session.query(AcademicYear).get(academic_year_id)
        self.courses = session.query(Course).join(Course.academic_years).filter(AcademicYear.id == academic_year_id).all()
        self.teachers = session.query(Teacher).join(Teacher.courses).join(Course.academic_years).filter(AcademicYear.id == academic_year_id).distinct().all()
        self.classrooms = session.query(Classroom).join(Classroom.academic_years).filter(AcademicYear.id == academic_year_id).all()
        self.time_slots = [
            (time(8, 0), time(10, 0)),
            (time(10, 0), time(12, 0)),
            (time(12, 0), time(14, 0)),
            (time(14, 0), time(16, 0)),
            (time(16, 0), time(18, 0)),
        ]
        self.days = list(range(5))
        self.teacher_slot_map = self.build_teacher_availability_map()
        self.external_conflicts_map = self.build_external_conflicts_map()

    def build_teacher_availability_map(self):
        """Build teacher availability map by day and time slot"""
        slot_map = {}
        for teacher in self.teachers:
            slot_map[teacher.id] = {}
            for day in self.days:
                valid_slots = []
                availabilities = self.session.query(TeacherAvailability).filter_by(
                    teacher_id=teacher.id,
                    day_of_week=day,
                    is_available=True
                ).all()
                for slot_start, slot_end in self.time_slots:
                    for avail in availabilities:
                        if avail.start_time <= slot_start and avail.end_time >= slot_end:
                            valid_slots.append((slot_start, slot_end))
                            break
                slot_map[teacher.id][day] = valid_slots
        return slot_map

    def build_external_conflicts_map(self):
        """Build external conflicts map for teachers from existing schedules in the same academic year"""
        conflicts_map = {}
        
        existing_schedules = self.session.query(ScheduleSlot).join(Schedule).all()


        for slot in existing_schedules:
            teacher_id = slot.teacher_id
            day = slot.day_of_week
            time_slot = (slot.start_time, slot.end_time)
            if teacher_id not in conflicts_map:
                conflicts_map[teacher_id] = {}
            if day not in conflicts_map[teacher_id]:
                conflicts_map[teacher_id][day] = set()
            conflicts_map[teacher_id][day].add(time_slot)
        return conflicts_map
