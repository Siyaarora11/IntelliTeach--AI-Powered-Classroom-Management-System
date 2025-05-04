import cv2
import face_recognition
import os
from .models import Student
from Home.models import Attendance, Time_Table
from django.conf import settings
from datetime import datetime
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def generate_embedding(path):
    try:
        if os.path.exists(path):
            face_image = face_recognition.load_image_file(path)
            face_encodings = face_recognition.face_encodings(face_image)
            if face_encodings:
                return face_encodings[0] # Assuming only one face in the image
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
    return None

def recognize_faces(stop=False, time=None):
    try:
        if stop: 
            cv2.destroyAllWindows()
            return 'Attendance Stopped!!'

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("Unable to open camera.")
            return []

        res = []
        students = Student.objects.all()

        embeddings = []
        for student in students:
            if student.user.picture:
                path = student.user.picture.path
                embed = generate_embedding(path)
                name = student.user.get_full_name()
                embeddings.append((student.roll_number, embed, name))
            else:
                embeddings.append((student.roll_number, None, "Unknown"))

        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < time if time else (settings.FACE_RECOGNITION_TIMEOUT or 120):
            logger.debug(res)
            ret, frame = cap.read()
            if not ret:
                logger.error("Unable to capture frame.")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for roll_number, embed, name in embeddings:
                if embed is None:
                    for x in res:
                        if x['roll_no'] == roll_number:
                            x['status'] = False
                            break
                    else:
                        res.append({'roll_no': roll_number, 'name': name, 'status': False})
                    continue
                
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces([embed], face_encoding)
                    if any(matches):
                        for x in res:
                            if x['roll_no'] == roll_number:
                                x['status'] = True
                                break
                        else:
                            res.append({'roll_no': roll_number, 'name': name, 'status': True})
                        break
                else:
                    for x in res:
                        if x['roll_no'] == roll_number:
                            x['status'] = False
                            break
                    else:
                        res.append({'roll_no': roll_number, 'name': name, 'status': False})
                        
            cv2.imshow("IntelliTeach Face Recognition", frame)
            if cv2.waitKey(1) == ord('q'):
                break
        cap.release()
        return res
    except Exception as e:
        logger.error(f"Error recognizing faces: {e}")
        return []

    finally:
        cv2.destroyAllWindows()

def set_attendance(force=False, stop=False, time=None):
    try:
        if stop:
            return recognize_faces(stop=True)

        day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_day_index = timezone.now().weekday()
        current_day = day[current_day_index] if settings.FACE_RECOGNITION_DAY == 'Auto' else settings.FACE_RECOGNITION_DAY

        tm = Time_Table.objects.filter(day=current_day)
        current_time = timezone.localtime().time()
        print(tm, current_time)
        for t in tm:
            print(t.time_from, t.time_to)
            if t.time_from <= current_time <= t.time_to:
                attendance_date = datetime.now().date()
                attendance_entries = Attendance.objects.filter(time=t, created_at__date=attendance_date)

                if attendance_entries.exists() and not force:
                    data = recognize_faces(time=time)
                    print(data, 'existing')
                    for d in data:
                        student = Student.objects.get(roll_number=d['roll_no'])
                        attendance_entry = attendance_entries.filter(student=student).first()
                        if attendance_entry and attendance_entry.status is False:
                            attendance_entry.status = d['status']
                            attendance_entry.save()
                else:
                    data = recognize_faces(time=time)
                    print(data, 'new')
                    for d in data:
                        student = Student.objects.get(roll_number=d['roll_no'])
                        Attendance.objects.create(
                            teacher=None,
                            student=student,
                            time=t,
                            status=d['status']
                        )
                return  'Attendance Added Successfuly!!'
            continue
        else:
            logger.info("No classes scheduled for today.")
            return 'No classes scheduled for today'
    except Exception as e:
        logger.error(f"Error setting attendance: {e}")
        return 'Error setting attendance'