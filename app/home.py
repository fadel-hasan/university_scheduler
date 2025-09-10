import streamlit as st
import streamlit.components.v1 as components
from db.models import AcademicYear, Teacher, Course, Classroom, Schedule
from db.database import get_engine, get_session

def render():
    session = get_session(get_engine())

    st.title("📘 University Timetable System")
    st.markdown("""
    <style>
    .card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .card h4 { margin: 0; font-size: 1.2rem; color: #333; }
    .card p { margin: 0.2rem 0 0; color: #555; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## 👋 Welcome to the University Timetable System")
    st.write("Use the sidebar to manage data and generate optimized schedules for your academic years.")

    # Quick stats
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📆 Academic Years", session.query(AcademicYear).count())
        col2.metric("👨‍🏫 Professors", session.query(Teacher).count())
        col3.metric("📚 Courses", session.query(Course).count())
        col4.metric("🏫 Classrooms", session.query(Classroom).count())

    st.markdown("---")
    st.subheader("🗂 Latest Created Schedules")
    latest_schedules = session.query(Schedule).order_by(Schedule.id.desc()).limit(5).all()

    if latest_schedules:
        for schedule in latest_schedules:
            with st.container():
                st.markdown(f"""
                    <div class="card">
                        <h4>{schedule.name}</h4>
                        <p><strong>Academic Year:</strong> {schedule.academic_year.name}</p>
                        <p><strong>Created:</strong> {schedule.created_at.strftime('%Y-%m-%d')}</p>
                        <p><strong>Fitness:</strong> {schedule.fitness_score}%</p>
                    </div>
                """, unsafe_allow_html=True)

                if st.button(f"🔍 View Schedule #{schedule.id}", key=f"view_{schedule.id}"):
                    st.session_state.selected_schedule = schedule.id
                    st.session_state.page = "View Tables"
                    st.rerun()
    else:
        st.info("No schedules have been created yet. Go to 'Generate Tables' to create your first schedule.")

def _view_schedule(schedule_id):
    st.session_state.selected_schedule = schedule_id
    st.session_state.menu = "View table"
    st.rerun()
