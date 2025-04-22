from django.db import models

# Create your models here.


class Student(models.Model):
    student_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    standing = models.CharField(max_length=50)
    year = models.IntegerField()
    starting_year = models.IntegerField()
    total_attendance = models.IntegerField(default=0)
    last_attendance_time = models.DateTimeField()
    image = models.ImageField(upload_to='student_images/')  # Assumes images are stored here
