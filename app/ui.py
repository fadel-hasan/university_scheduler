import streamlit as st
from app import home, years, teachers, courses, classrooms, generate, view_schedules

def main():
    st.set_page_config(page_title="University Timetable System", page_icon="📚", layout="wide")

    PAGES = {
        "Home": home,
        "Academic years": years,
        "Professors": teachers,
        "Subjects": courses,
        "Rooms": classrooms,
        "Generate Tables": generate,
        "View Tables": view_schedules
    }

    st.sidebar.title("📚 Navigation")
    for page_name in PAGES:
        if st.sidebar.button(page_name,use_container_width=True):
            st.session_state.page = page_name

    selected = st.session_state.get("page", "Home")
    PAGES[selected].render()
