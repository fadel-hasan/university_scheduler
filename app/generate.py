
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
from db.models import AcademicYear, Course, Schedule
from db.database import get_engine, get_session
from core.genetic_scheduler import GeneticScheduler
from app.export import export_schedule_to_pdf


DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
TIME_SLOTS = ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"]

def render():
    session = get_session(get_engine())
    st.title("🧬 Generate New Timetable")

    years = session.query(AcademicYear).all()
    if not years:
        st.error("You must add at least one academic year first!")
        return

    year_options = {y.id: y.name for y in years}
    year_id = st.selectbox("Select Academic Year", options=list(year_options), format_func=lambda x: year_options[x])
    year = session.query(AcademicYear).get(year_id)

    if not year.courses:
        st.warning("No courses linked to this academic year.")
        return

    if not year.classrooms:
        st.warning("No classrooms linked to this academic year.")
        return

    no_teachers = [c.name for c in year.courses if not c.teachers]
    if no_teachers:
        st.warning("Some courses have no assigned professors: " + ", ".join(no_teachers))
        return

    st.subheader("Genetic Algorithm Settings")
    col1, col2, col3 = st.columns(3)
    pop_size = col1.slider("Population Size", 10, 200, 50, 10)
    generations = col2.slider("Number of Generations", 10, 500, 100, 10)
    mutation = col3.slider("Mutation Rate", 0.01, 0.5, 0.1, 0.01)

    name = st.text_input("Schedule Name", f"Schedule {year.name} - {datetime.now().strftime('%Y-%m-%d')}")

    if st.button("Generate Timetable"):
        progress = st.progress(0)
        status = st.empty()

        # بدء قياس الوقت
        start_time = time.time()

        scheduler = GeneticScheduler(
            session=session,
            academic_year_id=year_id,
            population_size=pop_size,
            generations=generations,
            mutation_rate=mutation
        )

        def update_progress(info):
            progress.progress(min(100, int((info['generation']+1)/generations * 100)))
            status.text(f"Generation {info['generation']+1} - Best Fitness: {int(info['best_fitness']*100)}%")

        best_schedule, fitness = scheduler.run(progress_callback=update_progress)
        saved = scheduler.save_schedule(best_schedule, name=name)

        # حساب الوقت المستغرق
        end_time = time.time()
        elapsed_time = end_time - start_time

        st.info(f"⏱️ Time taken to create the table: {elapsed_time:.2f} seconds")

        st.success(f"Timetable generated successfully with fitness score: {int(fitness*100)}%")
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
                for slot in saved.slots:
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


        pdf = export_schedule_to_pdf(saved.id)
        if pdf:
            st.download_button("📄 Download Timetable PDF", data=pdf, file_name=f"{name}.pdf", mime="application/pdf")
