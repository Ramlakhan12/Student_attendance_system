import os
import sys
import cv2
import face_recognition
import pickle
from datetime import datetime

# Django Setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StudentAttendance.settings")
import django
django.setup()

from attendance.models import Student  

# Load Images from Local Directory
folderPath = r'C:\Users\ramla\Downloads\Files\StudentAttendance\Images'
pathList = os.listdir(folderPath)
print("📂 Found Images:", pathList)

imgList = []
studentIds = []

for path in pathList:
    student_id = os.path.splitext(path)[0]
    filePath = os.path.join(folderPath, path)

    img = cv2.imread(filePath)
    if img is None:
        print(f" Could not read image: {filePath}. Skipping...")
        continue

    imgList.append(img)
    studentIds.append(student_id)

    
    student, created = Student.objects.update_or_create(
        student_id=student_id,
        defaults={
            "image": f"{folderPath}/{path}",  # If using ImageField with MEDIA_URL
            "last_attendance_time": datetime.now()
        }
    )
    print(f"{'✅ Created' if created else '🔄 Updated'} Student: {student_id}")

print("🧑‍🎓 Processed Student IDs:", studentIds)

# Face Encoding Function
def findEncodings(imagesList):
    encodeList = []
    for i, img in enumerate(imagesList):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img,model='cnn')
        if encodings:
            encodeList.append(encodings[0])
        else:
            print(f"⚠️ No face found in image for ID: {studentIds[i]}")
    return encodeList

# Encode and Save
print("🔍 Encoding Faces...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("✅ Encoding Complete.")

script_dir = os.path.dirname(os.path.abspath(__file__))
encode_file_path = os.path.join(script_dir, "EncodeFile.p")
# Save Encoded Data to Pickle File
with open(encode_file_path, 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)
print("💾 'EncodeFile.p' saved successfully.")
