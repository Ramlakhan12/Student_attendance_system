from django.shortcuts import render
import os
import subprocess
from django.http import HttpResponse
import csv
from .models import Student
from django.http import FileResponse, Http404
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.

def teacher_dashboard(request):
    return render(request, 'teacher_dashboard.html')


def mark_attendance(request):
    try:
        manage_py_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'manage.py')
        main_script_path = os.path.join(os.path.dirname(__file__), 'main1.py')
        result = subprocess.run(
            ['python', manage_py_path, 'runscript', 'main1'],
            capture_output=True,
            text=True,
            check=True
        )
        messages.success(request, "✅ Attendance marked successfully.")
    except subprocess.CalledProcessError as e:
        return HttpResponse(f"Error while marking attendance:<br><br>{e}<br><br>{e.stdout}<br>{e.stderr}")
    return redirect('teachers_dashboard')


def download_report(request):
    logs_dir = os.path.join(settings.BASE_DIR,'attendance', 'AttendanceLogs')
    
    try:
        
        csv_files = [f for f in os.listdir(logs_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise Http404("No CSV reports found.")

     
        csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)
        latest_csv = csv_files[0]
        csv_path = os.path.join(logs_dir, latest_csv)

        return FileResponse(open(csv_path, 'rb'), as_attachment=True, filename=latest_csv)

    except Exception as e:
        raise Http404("Error fetching report file.")