from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from db.models import Schedule
from db.database import get_engine, get_session
import arabic_reshaper
from bidi.algorithm import get_display

TIME_SLOTS = ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"]
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

def export_schedule_to_pdf(schedule_id):
    session = get_session(get_engine())
    schedule = session.query(Schedule).get(schedule_id)
    if not schedule:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Heading1'], fontName='Amiri', fontSize=18, alignment=TA_CENTER)
    normal_style = ParagraphStyle('normal', parent=styles['Normal'], fontName='Amiri', fontSize=12, alignment=TA_RIGHT)
    cell_style = ParagraphStyle('cell', parent=styles['Normal'], fontName='Amiri', fontSize=11, alignment=TA_RIGHT, leading=16)

    grid = {day: {slot: "" for slot in TIME_SLOTS} for day in DAYS}
    for slot in schedule.slots:
        day = DAYS[slot.day_of_week]
        time_key = f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}"
        if time_key in TIME_SLOTS:
            course_name = get_display(arabic_reshaper.reshape(slot.course.name))
            teacher_name = get_display(arabic_reshaper.reshape(slot.teacher.name))
            classroom_name = get_display(arabic_reshaper.reshape(slot.classroom.name))
            content = f"<b>{course_name}</b><br/><font size=10>{teacher_name}</font><br/><font size=10>{classroom_name}</font>"
            grid[day][time_key] = Paragraph(content, cell_style)

    data = [["Day / Time"] + TIME_SLOTS]
    for day_index, day in enumerate(DAYS):
        row = [day] + [grid[day][slot] for slot in TIME_SLOTS]
        data.append(row)

    table = Table(data, repeatRows=1, hAlign='CENTER')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,-1), 'Amiri'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('ROWBACKGROUNDS', (1,1), (-1,-1), [colors.whitesmoke, colors.lightcyan]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))

    elements = [
        Paragraph(get_display(arabic_reshaper.reshape(schedule.name)), title_style),
        Spacer(1,12),
        Paragraph(f"Academic Year: {get_display(arabic_reshaper.reshape(schedule.academic_year.name))}", normal_style),
        Paragraph(f"Fitness Score: {schedule.fitness_score}%", normal_style),
        Spacer(1,12),
        table
    ]

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
