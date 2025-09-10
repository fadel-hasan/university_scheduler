# University Timetable Scheduler

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red.svg)](https://streamlit.io/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.23-green.svg)](https://www.sqlalchemy.org/)

A comprehensive university timetable scheduling system that uses genetic algorithms to generate optimal schedules while considering various constraints such as teacher availability, classroom capacity, and course requirements.

## Features

- **Academic Year Management**: Create and manage academic years
- **Professor Management**: Add professors and set their availability
- **Course Management**: Create courses and assign them to professors and academic years
- **Classroom Management**: Add classrooms and assign them to academic years
- **Genetic Algorithm Scheduling**: Generate optimal timetables using genetic algorithms
- **Schedule Viewing**: View generated schedules in an interactive interface
- **PDF Export**: Export schedules to PDF format

## Technology Stack

- **Frontend**: Streamlit
- **Database**: SQLite with SQLAlchemy ORM
- **PDF Generation**: ReportLab
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib
- **Database Migration**: Alembic

## Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/university_scheduler.git
cd university_scheduler
```

2. Create and activate a virtual environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Initialize the database

```bash
alembic upgrade head
```

## Usage

1. Start the application

```bash
python main.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Use the navigation sidebar to access different sections of the application:
   - **Home**: Dashboard and overview
   - **Academic Years**: Manage academic years
   - **Professors**: Add and manage professors and their availability
   - **Subjects**: Create and manage courses
   - **Rooms**: Add and manage classrooms
   - **Generate Tables**: Generate new timetables using the genetic algorithm
   - **View Tables**: View and export generated timetables

## Genetic Algorithm

The system uses a genetic algorithm approach to generate optimal timetables:

1. **Initial Population**: Random valid schedules are generated
2. **Fitness Evaluation**: Schedules are evaluated based on constraints and preferences
3. **Selection**: Better schedules have higher chances of being selected for the next generation
4. **Crossover**: Selected schedules are combined to create new schedules
5. **Mutation**: Random changes are applied to maintain diversity
6. **Elitism**: The best schedules are preserved across generations

The algorithm considers various constraints:
- Teacher availability
- Classroom capacity
- Course requirements
- Avoiding scheduling conflicts

## Project Structure

```
university_scheduler/
├── app/                    # Application modules
│   ├── __init__.py
│   ├── classrooms.py       # Classroom management UI
│   ├── courses.py          # Course management UI
│   ├── export.py           # PDF export functionality
│   ├── generate.py         # Schedule generation UI
│   ├── home.py             # Home page UI
│   ├── teachers.py         # Teacher management UI
│   ├── ui.py               # Main UI components
│   ├── view_schedules.py   # Schedule viewing UI
│   └── years.py            # Academic year management UI
├── core/                   # Core algorithm components
│   ├── __init__.py
│   ├── conflict_checker.py # Checks for scheduling conflicts
│   ├── data_collector.py   # Collects data for the algorithm
│   ├── fitness_calculator.py # Calculates fitness of schedules
│   ├── genetic_algorithm.py # Main genetic algorithm logic
│   ├── genetic_operations.py # Genetic operations (crossover, mutation)
│   ├── genetic_scheduler.py # Coordinates the scheduling process
│   ├── individual_generator.py # Generates individual schedules
│   └── schedule_presenter.py # Presents schedules in various formats
├── db/                     # Database components
│   ├── __init__.py
│   ├── database.py         # Database connection and session management
│   └── models.py           # SQLAlchemy models
├── migrations/             # Alembic migrations
├── Amiri-Regular.ttf       # Font for Arabic text in PDFs
├── alembic.ini             # Alembic configuration
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
└── university_scheduler.db # SQLite database
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- The genetic algorithm implementation is based on research in timetable optimization
- Streamlit for providing an excellent framework for building data applications
- ReportLab for PDF generation capabilities