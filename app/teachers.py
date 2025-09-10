import streamlit as st
from datetime import time
from db.models import Teacher, Course, TeacherAvailability
from db.database import get_engine, get_session

def render():
    session = get_session(get_engine())
    st.title("👨‍🏫 Professors Management")

    with st.expander("➕ Add New Professor"):
        with st.form("add_teacher_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            courses = session.query(Course).all()
            selected_courses = st.multiselect("Select Courses", [c.id for c in courses], format_func=lambda id: session.query(Course).get(id).name)

            submit = st.form_submit_button("Add")
            if submit and name:
                teacher = Teacher(name=name, email=email, phone=phone)
                for cid in selected_courses:
                    course = session.query(Course).get(cid)
                    if course:
                        teacher.courses.append(course)
                session.add(teacher)
                session.commit()
                st.success("Professor added successfully!")

    
    teachers = session.query(Teacher).all()
    if not teachers:
        st.info("No professors found.")
        return

    for teacher in teachers:
        with st.expander(f"👨‍🏫 {teacher.name}"):
            st.markdown(f"**Email:** {teacher.email or 'Not provided'}")
            st.markdown(f"**Phone:** {teacher.phone or 'Not provided'}")

            if teacher.courses:
                st.markdown("**Courses:**")
                for c in teacher.courses:
                    st.markdown(f"- {c.name}")

            col_del1, col_del2 = st.columns([1,3])
            with col_del1:
                if st.button("🗑️ Delete Professor", key=f"delete_teacher_{teacher.id}"):
                    if teacher.courses:
                        st.warning("you can't delete the teacher because he has courses")
                    else:
                        availabilities = session.query(TeacherAvailability).filter_by(teacher_id=teacher.id).all()
                        for a in availabilities:
                            session.delete(a)
                        session.delete(teacher)
                        session.commit()
                        st.success("the teacher deleted successfully")
                        st.rerun()

            st.markdown("**Availability:**")
            availabilities = session.query(TeacherAvailability).filter_by(teacher_id=teacher.id).all()
            if availabilities:
                day_map = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
                grouped = {}
                for a in availabilities:
                    day_name = day_map[a.day_of_week]
                    if day_name not in grouped:
                        grouped[day_name] = []
                    grouped[day_name].append(a)

                for day_name, slots in grouped.items():
                    slot_texts = []
                    for a in slots:
                        status = "Available" if a.is_available else "Unavailable"
                        slot_texts.append(f"{a.start_time.strftime('%H:%M')} - {a.end_time.strftime('%H:%M')} ({status})")
                    st.markdown(f"**{day_name}:** " + ", ".join(slot_texts))

                    for a in slots:
                        col1, col2 = st.columns([1,1])
                        with col1:
                            edit_key = f"edit_{a.id}"
                            btn_key = f"edit_btn_{a.id}"
                            if edit_key not in st.session_state:
                                st.session_state[edit_key] = False
                            if st.button(f"Edit {day_name} {a.start_time.strftime('%H:%M')}-{a.end_time.strftime('%H:%M')}", key=btn_key):
                                st.session_state[edit_key] = True
                            if st.session_state[edit_key]:
                                with st.form(f"edit_avail_form_{a.id}"):
                                    day = st.selectbox("Day of Week", options=list(range(5)), index=a.day_of_week, format_func=lambda i: day_map[i])
                                    start_hour = st.slider("Start Hour", 8, 17, a.start_time.hour)
                                    end_hour = st.slider("End Hour", start_hour+1, 18, a.end_time.hour)
                                    is_available = st.checkbox("Available", value=a.is_available)
                                    submit_edit = st.form_submit_button("Update Availability")
                                    cancel_edit = st.form_submit_button("Cancel")
                                    if submit_edit:
                                        a.day_of_week = day
                                        a.start_time = time(start_hour, 0)
                                        a.end_time = time(end_hour, 0)
                                        a.is_available = is_available
                                        session.commit()
                                        st.success("Availability updated successfully.")
                                        st.session_state[edit_key] = False
                                        st.rerun()
                                    if cancel_edit:
                                        st.session_state[edit_key] = False
                                        st.rerun()
                        with col2:
                            if st.button(f"Delete {day_name} {a.start_time.strftime('%H:%M')}-{a.end_time.strftime('%H:%M')}", key=f"delete_{a.id}"):
                                session.delete(a)
                                session.commit()
                                st.success("Availability deleted successfully.")
                                st.rerun()
            else:
                st.write("No availability records.")

            with st.form(f"add_avail_{teacher.id}"):
                day = st.selectbox("Day of Week", options=list(range(5)), format_func=lambda i: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"][i])
                start_hour = st.slider("Start Hour", 8, 17, 8)
                end_hour = st.slider("End Hour", start_hour+1, 18, start_hour+2)
                is_available = st.checkbox("Available", value=True)
                submit_time = st.form_submit_button("Add Availability")
                if submit_time:
                    session.add(TeacherAvailability(
                        teacher_id=teacher.id,
                        day_of_week=day,
                        start_time=time(start_hour, 0),
                        end_time=time(end_hour, 0),
                        is_available=is_available
                    ))
                    session.commit()
                    st.success("Availability added successfully.")
                    st.rerun()
        
            with st.form(f"edit_teacher_{teacher.id}"):
                new_name = st.text_input("Full Name", value=teacher.name)
                new_email = st.text_input("Email", value=teacher.email or "")
                new_phone = st.text_input("Phone", value=teacher.phone or "")
                all_courses = session.query(Course).all()
                selected = [c.id for c in teacher.courses]
                course_ids = st.multiselect("Courses", [c.id for c in all_courses], default=selected, format_func=lambda id: session.query(Course).get(id).name)
                update_btn = st.form_submit_button("Update")

                if update_btn and new_name:
                    teacher.name = new_name
                    teacher.email = new_email
                    teacher.phone = new_phone
                    teacher.courses = [session.query(Course).get(cid) for cid in course_ids]
                    session.commit()
                    st.success("Professor updated successfully!")
                    st.rerun()
