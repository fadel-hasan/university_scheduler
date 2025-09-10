import streamlit as st
import pandas as pd
from db.models import AcademicYear, Schedule
from db.database import get_engine, get_session
from app.export import export_schedule_to_pdf

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
TIME_SLOTS = ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"]

def render():
    session = get_session(get_engine())
    st.title("📅 View Timetables")

    years = session.query(AcademicYear).all()
    year_options = {y.id: y.name for y in years}
    year_options[-1] = "All Academic Years"

    selected_year = st.selectbox("Select Academic Year", options=year_options.keys(), format_func=lambda x: year_options[x])

    if selected_year == -1:
        schedules = session.query(Schedule).order_by(Schedule.id.desc()).all()
    else:
        schedules = session.query(Schedule).filter_by(academic_year_id=selected_year).order_by(Schedule.id.desc()).all()

    if not schedules:
        st.info("No timetables available.")
        return

    selected_id = None
    if "selected_schedule" in st.session_state:
        selected_id = st.session_state.selected_schedule
        del st.session_state["selected_schedule"]
    else:
        options = {s.id: f"{s.name} ({s.academic_year.name})" for s in schedules}
        selected_id = st.selectbox("Select Timetable", options=options.keys(), format_func=lambda x: options[x])

    schedule = session.query(Schedule).get(selected_id)

    st.subheader(schedule.name)
    st.markdown(f"**Academic Year:** {schedule.academic_year.name}")
    st.markdown(f"**Fitness Score:** {schedule.fitness_score}%")

        
    st.markdown("""
        <style>
        .schedule-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }
        .schedule-table th, .schedule-table td {
            border: 1px solid #ccc;
            padding: 8px;
            text-align: center;
            vertical-align: top;
            min-width: 120px;
        }
        .schedule-table th {
            background-color: #f0f0f0;
        }
        .slot {
            font-weight: 500;
            color: #333;
        }
        .slot span {
            display: block;
            margin-top: 4px;
            color: #666;
            font-size: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

    html = "<table class='schedule-table'>"
    html += "<tr><th>Day / Time</th>" + "".join(f"<th>{t}</th>" for t in TIME_SLOTS) + "</tr>"

    for day_index, day in enumerate(DAYS):
        html += f"<tr><th>{day}</th>"
        for time_slot in TIME_SLOTS:
            slot_content = ""
            for slot in schedule.slots:
                slot_time = f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}"
                if slot.day_of_week == day_index and slot_time == time_slot:
                    slot_content = f"""
                        <div class='slot'>
                            {slot.course.name}
                            <span>{slot.teacher.name}</span>
                            <span>{slot.classroom.name}</span>
                        </div>
                    """
                    break
            html += f"<td>{slot_content}</td>"
        html += "</tr>"

    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

    pdf = export_schedule_to_pdf(schedule.id)
    if pdf:
        st.download_button("📄 Download PDF", data=pdf, file_name=f"{schedule.name}.pdf", mime="application/pdf")

    if st.button("🗑 Delete Timetable", type="primary"):
        session.delete(schedule)
        session.commit()
        st.success("Timetable deleted successfully.")
        st.rerun()
