import os
import sys

# Fix path to find the Django project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StudentAttendance.settings")

import django
django.setup()

from attendance.models import Student
from datetime import datetime

data = {
    "321654": {
        "name": "Murtaza Hassan",
        "major": "Robotics",
        "starting_year": 2017,
        "total_attendance": 7,
        "standing": "G",
        "year": 4,
        "last_attendance_time": "2022-12-11 00:54:34"
    },
    "852741": {
        "name": "Emly Blunt",
        "major": "Economics",
        "starting_year": 2021,
        "total_attendance": 12,
        "standing": "B",
        "year": 1,
        "last_attendance_time": "2022-12-11 00:54:34"
    },
    "963852": {
        "name": "Elon Musk",
        "major": "Physics",
        "starting_year": 2020,
        "total_attendance": 7,
        "standing": "G",
        "year": 2,
        "last_attendance_time": "2022-12-11 00:54:34"
    }
}

for student_id, details in data.items():
    student, created = Student.objects.update_or_create(
        student_id=student_id,
        defaults={
            "name": details["name"],
            "major": details["major"],
            "starting_year": details["starting_year"],
            "total_attendance": details["total_attendance"],
            "standing": details["standing"],
            "year": details["year"],
            "last_attendance_time": datetime.strptime(details["last_attendance_time"], "%Y-%m-%d %H:%M:%S")
        }
    )
    print(f"{'✅ Created' if created else '🔄 Updated'} student: {student.name}")
