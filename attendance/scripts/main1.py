
def run():

    import os
    import pickle
    import numpy as np
    import cv2
    import face_recognition
    import cvzone
    from datetime import datetime,date
    import django
    import sys
    from attendance.models import Student  
    from django.utils.timezone import now
    import csv

    # Setup Django
    sys.path.append(r'C:\Users\ramla\Downloads\Files\StudentAttendance')  
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StudentAttendance.settings")  
    django.setup()



    # Webcam setup
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    # Load background
    imgBackground = cv2.imread(r'C:\Users\ramla\Downloads\Files\StudentAttendance\Resources\background.png')

    # Load modes
    folderModePath = r'C:\Users\ramla\Downloads\Files\StudentAttendance\Resources\Modes'
    modePathList = os.listdir(folderModePath)
    imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]




    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # this points to attendance/scripts/
    file_path = os.path.join(BASE_DIR, '..', 'EncodeFile.p')  # go one level up

    # with open(os.path.normpath(file_path), 'rb') as file:


    # Load encoded data
    print("Loading Encode File ...")
    with open(os.path.normpath(file_path),'rb') as file:
        encodeListKnownWithIds = pickle.load(file)
    encodeListKnown, studentIds = encodeListKnownWithIds
    print("Encode File Loaded")

    modeType = 0
    counter = 0
    id = -1
    imgStudent = []

    while True:
        success, img = cap.read()

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS,model='cnn')
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        imgBackground[162:162 + 480, 55:55 + 640] = img
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = [val * 4 for val in (y1, x2, y2, x1)]
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    id = studentIds[matchIndex]
                    if counter == 0:
                        cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                        cv2.imshow("Face Attendance", imgBackground)
                        cv2.waitKey(1)
                        counter = 1
                        modeType = 1

            if counter != 0:
                if counter == 1:
                    try:
                        student = Student.objects.get(student_id=id)
                    except Student.DoesNotExist:
                        print(f"Student with ID {id} not found.")
                        counter = 0
                        modeType = 0
                        continue

                    studentInfo = {
                        'name': student.name,
                        'major': student.major,
                        'standing': student.standing,
                        'year': student.year,
                        'starting_year': student.starting_year,
                        'total_attendance': student.total_attendance,
                        'last_attendance_time': student.last_attendance_time.strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    img_path = student.image.path
                    imgStudent = cv2.imread(img_path)

                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    # print(secondsElapsed)

                    # from datetime import date

                    last_attendance_date = student.last_attendance_time.date()
                    current_date = datetime.now().date()

                    # if last_attendance_date != current_date :
                    #     student.total_attendance += 1
                    #     student.last_attendance_time = now()
                    #     student.save()
                    # else:
                    #     modeType = 3
                    #     counter = 0
                    #     cv2.waitKey(10)
                    #     imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]


                    if secondsElapsed > 30 and (last_attendance_date != current_date) :
                        student.total_attendance += 1
                        student.last_attendance_time = now()
                        student.save()
                        # import csv

                        # Define CSV file name based on month and year
                        csv_filename = f"Attendance_{datetime.now().strftime('%B_%Y')}.csv"
                        csv_path = os.path.join(BASE_DIR, '..', 'AttendanceLogs', csv_filename)

                        # Ensure the directory exists
                        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

                        # Get today's date as string
                        today_str = datetime.now().strftime('%Y-%m-%d')

                        # Try to open the CSV and update it
                        try:
                            # Load existing CSV
                            updated = False
                            rows = []
                            with open(csv_path, 'r', newline='') as file:
                                reader = csv.reader(file)
                                headers = next(reader)
                                
                                if today_str not in headers:
                                    headers.append(today_str)

                                for row in reader:
                                    if row[0] == str(id):
                                        # Mark present
                                        while len(row) < len(headers):
                                            row.append('')  # Fill any missing columns
                                        row[headers.index(today_str)] = 'P'
                                        updated = True
                                    rows.append(row)

                            # If student not found, add new row
                            if not updated:
                                new_row = [''] * len(headers)
                                new_row[0] = str(id)
                                new_row[headers.index(today_str)] = 'P'
                                rows.append(new_row)

                            # Write updated CSV
                            with open(csv_path, 'w', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow(headers)
                                writer.writerows(rows)

                        except FileNotFoundError:
                            # If file doesn't exist, create it
                            with open(csv_path, 'w', newline='') as file:
                                writer = csv.writer(file)
                                headers = ['ID', today_str]
                                writer.writerow(headers)
                                writer.writerow([id, 'P'])

                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if modeType != 3:
                    if 10 < counter < 20:
                        modeType = 2

                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if counter <= 10:
                        cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(id), (1006, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w, _), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, studentInfo['name'], (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                        imgStudent = cv2.resize(imgStudent, (216, 216)) 
                        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                    counter += 1
                    print(counter)
                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        else:
            modeType = 0
            counter = 0

        cv2.imshow("Face Attendance", imgBackground)
        if cv2.waitKey(1) == ord('q'):
            break
