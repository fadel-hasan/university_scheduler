import streamlit as st
from db.models import Course, AcademicYear, Teacher
from db.database import get_engine, get_session

def render():
    session = get_session(get_engine())
    st.title("📚 Courses Management")

    
    with st.expander("➕ Add New Course"):
        with st.form("add_course_form"):
            name = st.text_input("Course Name")
            code = st.text_input("Course Code")
            credit = st.number_input("Credit Hours", min_value=1, value=3)

            years = session.query(AcademicYear).all()
            year_ids = st.multiselect("Select Academic Years", [y.id for y in years], format_func=lambda id: session.query(AcademicYear).get(id).name)

            teachers = session.query(Teacher).all()
            teacher_ids = st.multiselect("Select Professors", [t.id for t in teachers], format_func=lambda id: session.query(Teacher).get(id).name)

            submit = st.form_submit_button("Add")
            if submit and name:
                course = Course(name=name, code=code, credit_hours=credit)
                for yid in year_ids:
                    y = session.query(AcademicYear).get(yid)
                    if y:
                        course.academic_years.append(y)
                for tid in teacher_ids:
                    t = session.query(Teacher).get(tid)
                    if t:
                        course.teachers.append(t)
                session.add(course)
                session.commit()
                st.success("Course added successfully!")

    courses = session.query(Course).all()
    if not courses:
        st.info("No courses found.")
        return

    for course in courses:
        with st.expander(f"📘 {course.name} ({course.code})"):
            st.markdown(f"**Academic Years:** {', '.join([y.name for y in course.academic_years])}")
            st.markdown(f"**Credit Hours:** {course.credit_hours}")
            st.markdown("**Professors:**")
            for t in course.teachers:
                st.markdown(f"- {t.name}")

            with st.form(f"edit_course_{course.id}"):
                name = st.text_input("Course Name", value=course.name)
                code = st.text_input("Course Code", value=course.code or "")
                credit = st.number_input("Credit Hours", min_value=1, value=course.credit_hours)

                selected_years = st.multiselect(
                    "Academic Years",
                    [y.id for y in years],
                    default=[y.id for y in course.academic_years],
                    format_func=lambda id: session.query(AcademicYear).get(id).name
                )

                selected_teachers = st.multiselect(
                    "Professors",
                    [t.id for t in teachers],
                    default=[t.id for t in course.teachers],
                    format_func=lambda id: session.query(Teacher).get(id).name
                )

                update = st.form_submit_button("Update")
                if update and name:
                    course.name = name
                    course.code = code
                    course.credit_hours = credit
                    course.academic_years = [session.query(AcademicYear).get(yid) for yid in selected_years]
                    course.teachers = [session.query(Teacher).get(tid) for tid in selected_teachers]
                    session.commit()
                    st.success("Course updated successfully!")
                    st.rerun()
