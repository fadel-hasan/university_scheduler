import streamlit as st
from db.models import Classroom, AcademicYear
from db.database import get_engine, get_session

def render():
    session = get_session(get_engine())
    st.title("🏫 Classrooms Management")

    with st.expander("➕ Add New Classroom"):
        with st.form("add_classroom_form"):
            name = st.text_input("Classroom Name")
            capacity = st.number_input("Capacity", min_value=1, value=30)
            building = st.text_input("Building")

            years = session.query(AcademicYear).all()
            selected_years = st.multiselect(
                "Academic Years",
                [y.id for y in years],
                format_func=lambda id: session.query(AcademicYear).get(id).name
            )

            submit = st.form_submit_button("Add")
            if submit and name:
                classroom = Classroom(name=name, capacity=capacity, building=building)
                for yid in selected_years:
                    year = session.query(AcademicYear).get(yid)
                    classroom.academic_years.append(year)
                session.add(classroom)
                session.commit()
                st.success("Classroom added successfully!")

    classrooms = session.query(Classroom).all()
    if not classrooms:
        st.info("No classrooms found.")
        return

    for room in classrooms:
        with st.expander(f"🏫 {room.name}"):
            st.markdown(f"**Capacity:** {room.capacity}")
            st.markdown(f"**Building:** {room.building}")
            st.markdown("**Academic Years:**")
            for year in room.academic_years:
                st.markdown(f"- {year.name}")

            with st.form(f"edit_classroom_{room.id}"):
                name = st.text_input("Classroom Name", value=room.name)
                capacity = st.number_input("Capacity", min_value=1, value=room.capacity)
                building = st.text_input("Building", value=room.building or "")
                selected_years = st.multiselect(
                    "Academic Years",
                    [y.id for y in years],
                    default=[y.id for y in room.academic_years],
                    format_func=lambda id: session.query(AcademicYear).get(id).name
                )

                update = st.form_submit_button("Update")
                if update and name:
                    room.name = name
                    room.capacity = capacity
                    room.building = building
                    room.academic_years = [session.query(AcademicYear).get(yid) for yid in selected_years]
                    session.commit()
                    st.success("Classroom updated successfully!")
                    st.rerun()
