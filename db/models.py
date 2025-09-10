from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, Time, Date, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

teacher_course = Table(
    'teacher_course',
    Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

classroom_year = Table(
    'classroom_year',
    Base.metadata,
    Column('classroom_id', Integer, ForeignKey('classrooms.id'), primary_key=True),
    Column('year_id', Integer, ForeignKey('academic_years.id'), primary_key=True)
)

course_year = Table(
    'course_year',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('year_id', Integer, ForeignKey('academic_years.id'), primary_key=True)
)

class AcademicYear(Base):
    __tablename__ = 'academic_years'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    courses = relationship('Course', secondary=course_year, back_populates='academic_years')
    classrooms = relationship('Classroom', secondary=classroom_year, back_populates='academic_years')
    schedules = relationship('Schedule', back_populates='academic_year')
    
    def __repr__(self):
        return f"<AcademicYear(name='{self.name}')>"

class Teacher(Base):
    __tablename__ = 'teachers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    courses = relationship('Course', secondary=teacher_course, back_populates='teachers')
    availabilities = relationship('TeacherAvailability', back_populates='teacher')
    schedules = relationship('ScheduleSlot', back_populates='teacher')
    
    def __repr__(self):
        return f"<Teacher(name='{self.name}')>"

class TeacherAvailability(Base):
    __tablename__ = 'teacher_availabilities'
    
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    day_of_week = Column(Integer, nullable=False)  
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    
    teacher = relationship('Teacher', back_populates='availabilities')
    
    def __repr__(self):
        return f"<TeacherAvailability(teacher='{self.teacher.name}', day='{self.day_of_week}')>"

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)
    credit_hours = Column(Integer, default=3)
    
    academic_years = relationship('AcademicYear', secondary=course_year, back_populates='courses')
    teachers = relationship('Teacher', secondary=teacher_course, back_populates='courses')
    schedule_slots = relationship('ScheduleSlot', back_populates='course')
    
    def __repr__(self):
        return f"<Course(name='{self.name}', code='{self.code}')>"

class Classroom(Base):
    __tablename__ = 'classrooms'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, nullable=True)
    building = Column(String(100), nullable=True)
    
    academic_years = relationship('AcademicYear', secondary=classroom_year, back_populates='classrooms')
    schedule_slots = relationship('ScheduleSlot', back_populates='classroom')
    
    def __repr__(self):
        return f"<Classroom(name='{self.name}')>"


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    academic_year_id = Column(Integer, ForeignKey('academic_years.id'), nullable=False)
    created_at = Column(Date, nullable=True)
    fitness_score = Column(Integer, nullable=True)  

    
    academic_year = relationship('AcademicYear', back_populates='schedules')
    
    slots = relationship('ScheduleSlot', back_populates='schedule', cascade="all, delete-orphan") 

    def __repr__(self):
        return f"<Schedule(name='{self.name}')>"


class ScheduleSlot(Base):
    __tablename__ = 'schedule_slots'
    
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('schedules.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=False)
    day_of_week = Column(Integer, nullable=False)  
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    schedule = relationship('Schedule', back_populates='slots')
    course = relationship('Course', back_populates='schedule_slots')
    teacher = relationship('Teacher', back_populates='schedules')
    classroom = relationship('Classroom', back_populates='schedule_slots')
    
    def __repr__(self):
        return f"<ScheduleSlot(course='{self.course.name}', day='{self.day_of_week}')>"

def get_engine(db_path="sqlite:///university_scheduler.db"):
    return create_engine(db_path)


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

def create_tables(engine):
    Base.metadata.create_all(engine)