from django.urls import path
from . import views

urlpatterns = [
    path('',views.teacher_dashboard ,name ="teachers_dashboard"),
    path('mark',views.mark_attendance ,name ="mark_attendance"),
    path('download_report',views.download_report ,name ="download_report"),
]