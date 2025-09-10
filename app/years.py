
import streamlit as st
from db.models import AcademicYear
from db.database import get_engine, get_session

def render():
    session = get_session(get_engine())
    st.title("📅 Academic Years Management")

    st.markdown("""
    <style>
    .expander-header {
        font-weight: bold;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

    
    with st.expander("➕ Add New Academic Year"):
        with st.form("add_year_form"):
            year_name = st.text_input("Academic Year Name")
            year_description = st.text_area("Description")
            submit_button = st.form_submit_button("Add")
            if submit_button and year_name:
                new_year = AcademicYear(name=year_name, description=year_description)
                session.add(new_year)
                session.commit()
                st.success(f"Academic year '{year_name}' added successfully!")

    years = session.query(AcademicYear).all()
    if years:
        for year in years:
            with st.expander(f"📘 {year.name}"):
                st.markdown(f"**Description:** {year.description or 'No description'}")
                st.markdown(f"**Courses Count:** {len(year.courses)}")
                st.markdown(f"**Linked Classrooms:** {len(year.classrooms)}")

                with st.form(f"edit_year_{year.id}"):
                    edit_name = st.text_input("Academic Year Name", value=year.name)
                    edit_description = st.text_area("Description", value=year.description or "")

                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button("Update")
                    with col2:
                        delete_button = st.form_submit_button("Delete", type="primary")

                    if update_button and edit_name:
                        year.name = edit_name
                        year.description = edit_description
                        session.commit()
                        st.success("Academic year updated successfully!")
                        st.rerun()

                    if delete_button:
                        # Delete all schedules linked to the year (cascade deletes slots)
                        for schedule in year.schedules:
                            session.delete(schedule)
                        # Delete all courses linked to the year
                        for course in year.courses:
                            session.delete(course)
                        # Clear classrooms association
                        year.classrooms.clear()
                        # Delete the year itself
                        session.delete(year)
                        session.commit()
                        st.success("Academic year and all related data deleted successfully!")
                        st.rerun()
    else:
        st.info("No academic years found. Use the form above to add one.")
