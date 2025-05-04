import os
import re
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from Admin.models import Student, Faculty
from Admin.views import get_html_time_table
from student.models import Student_Query
from Home.models import Student_Notice, Attendance, Student_Marks, Teacher_Messages, Time_Table

def home_login(request):
    if request.user.is_authenticated: # type: ignore
        if request.user.is_faculty: # type: ignore
            return redirect('teacher_dashboard')
        elif request.user.is_student:
            student = request.user.student
            marks = Student_Marks.objects.filter(student_id=student.id,)
            notices = Student_Notice.objects.filter().order_by('-created_at') # type: ignore
            queries = Student_Query.objects.filter(student_id=request.user.student.id).order_by('-created_at') # type: ignore
            html_table = get_html_time_table()
            att = Attendance.objects.filter(student=student)
            att_error = False
            att_percentage = 0
            if att:
                att = att[0]
                att_percentage = att.calculate_student_attendance_percentage()
                att_error = True if att_percentage < 75 else False

            from collections import defaultdict # import defaultdict

            title = 'Student Dashboard'
            return render(request, 'student/dashboard.html', {'title': title, 'queries': queries, 'notices': notices,'marks':marks, 'html_table': html_table, 'att_error': att_error, 'att_percentage': att_percentage})
        elif request.user.is_hod:
            return redirect('admin_dashboard')
        else:
            return HttpResponseServerError('Invalid User Type')
        
    title = f'Login to {settings.APP_NAME}'
    if request.method == 'POST': # type: ignore
        password = request.POST['password'] # type: ignore
        selected = request.POST.get('selected', None)  # type: ignore
        if selected == 'faculty':
            email = request.POST['email'] # type: ignore
            user = authenticate(request, username=email, password=password)
            try:
                faculty = Faculty.objects.get(user_id=user.id) if user else None # type: ignore
            except Exception as e:
                faculty = None
                print(e)
            if user is not None and user.is_faculty and faculty: # type: ignore
                login(request, user) # type: ignore
                return redirect('teacher_dashboard')
            elif user is not None and user.is_hod:
                login(request, user) # type: ignore
                return redirect('admin_dashboard')
            else:
                return render(request=request, template_name='index.html', context={'title':title, 'messages': [{'text': 'Invalid Email or Password', 'type': 'error'}], 'selected': 'faculty'}) # type: ignore
        elif selected == 'student':
            roll_number = request.POST.get('roll_number', None) # type: ignore
            try:
                student = Student.objects.get(roll_number=roll_number)
                if student and student.user.email: # type: ignore
                    user = authenticate(request, username=student.user.email, password=password) # type: ignore
                    if user is not None and user.is_student: # type: ignore
                        login(request, user) # type: ignore
                        return redirect('/')   
                    else:
                        messages = [{'text': 'Invalid Roll Number or Password', 'type': 'error'}]
                        return render(request=request, template_name='index.html', context={'title':title, 'messages': messages, 'selected': selected}) # type: ignore    
                else: 
                    messages = [{'text': 'Invalid Roll Number or Password', 'type': 'error'}]
                    return render(request=request, template_name='index.html', context={'title':title, 'messages': messages, 'selected': selected}) # type: ignore
            except Exception as e:
                print(e, f'Got error while logging Student {roll_number} ...')
                messages = [{'text': 'Invalid Roll Number or Password', 'type': 'error'}]
                return render(request=request, template_name='index.html', context={'title': title, 'messages': messages, 'selected': selected}) # type: ignore
        else:
            messages = [{'text': 'Something went wrong', 'type': 'error'}]
            return render(request=request, template_name='index.html', context={'title': title, 'messages': messages, 'selected': selected}) # type: ignore
    return render(request=request, template_name='index.html', context={'title':title}) # type: ignore

@login_required(login_url='/')
def studentDashboard(request):
    '''
        Used, but not usefull, because we have used home_login() instead of this...
    '''
    if not request.user.is_student:
        return redirect('/')
    notices = Student_Notice.objects.filter().order_by('-created_at') # type: ignore
    queries = Student_Query.objects.filter(student_id=request.user.student.id, ).order_by('-created_at') # type: ignore
    title = 'Student Dashboard'
    return render(request, 'student/dashboard.html', {'title': title, 'queries': queries, 'notices': notices})

def Images(request, path: str):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="image/jpeg")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

 
def marks_list(request):
    if not request.user.is_faculty:
        return redirect('/')

    if request.method == 'POST':
        try:
            student_id = request.POST.getlist('id', None)
            mst1 = request.POST.getlist('mst1', None)
            mst2 = request.POST.getlist('mst2', None)
            assignment = request.POST.getlist('assignment', None)
            print(request.POST, student_id, mst1, mst2, assignment)

            teacher = request.user.faculty
            if student_id and mst1 and mst2 and assignment:
                for id, m1, m2, a in zip(student_id, mst1, mst2, assignment):
                    student = Student.objects.get(id=id)
                    if not student:
                        return HttpResponseServerError('Invalid Student')
                    
                    student_marks = Student_Marks.objects.filter(student_id=student.id, teacher_id=teacher.id)
                    if student_marks:
                        student_marks.delete()
                    marks = Student_Marks(student=student, teacher=teacher, mst1=m1 if m1 else None, mst2=m2 if m2 else None, assignment=a if a else None)
                    marks.save()
                    mess = f'Hello {student.user.first_name},\n\nYour marks have been updated by {teacher.user.first_name} {teacher.user.last_name}.\n\nMST1: {m1}\nMST2: {m2}\nAssignment: {a}\n\n\n\nThis is an auto-generated email by the system and does not support incoming mails. If you have any queries, please reach out to us through your dashboard.'
                    student.send_marks_email(mess)
                return redirect('marks')
            else:
                return HttpResponseServerError('Invalid Data')
        except Exception as e: 
            print(e, 'Got error while saving marks ...')
            return HttpResponseServerError('Something went wrong')       

    teacher = request.user.faculty # type: ignore
    students = Student.objects.all()
    marks = Student_Marks.objects.filter(teacher_id=teacher.id)
    student_data = []

    for student in students:
        student_marks_count = student.student_marks.filter(teacher__user__id=request.user.id).count()
        student_data.append({'student': student, 'student_marks_count': student_marks_count})

    context = {'title': 'Marks List', 'marks': marks, 'students': students, 'student_data': student_data,}
    return render(request, 'student/marks-list.html', context=context)

def marks_mst1(request):
    if not request.user.is_faculty:
        return redirect('/')

    if request.method == 'POST':
        try:
            student_id = request.POST.getlist('id', None)
            mst1 = request.POST.getlist('mst1', None)

            teacher = request.user.faculty
            if student_id and mst1:
                for id, m1 in zip(student_id, mst1):
                    student = Student.objects.get(id=id)
                    if not student:
                        return HttpResponseServerError('Invalid Student')
                    student_marks = Student_Marks.objects.filter(student_id=student.id, teacher_id=teacher.id)
                    if student_marks:
                        student_marks[0].mst1 = m1
                        student_marks[0].save()
                    else:
                        marks = Student_Marks(student=student, teacher=teacher, mst1=m1)
                        marks.save()
                    student.send_marks_email(f'Hello {student.user.first_name},\n\nYour MST1 marks have been updated by {teacher.user.first_name} {teacher.user.last_name}.\n\nMST1: {m1}\n\n\n\nThis is an auto-generated email by the system and does not support incoming mails. If you have any queries, please reach out to us through your dashboard.')
                return redirect('marks')
            else:
                return HttpResponseServerError('Invalid Data')
        except Exception as e: 
            print(e, 'Got error while saving marks ...')
            return HttpResponseServerError('Something went wrong')       
    return HttpResponseBadRequest('Invalid Request')

def marks_mst2(request):
    if not request.user.is_faculty:
        return redirect('/')

    if request.method == 'POST':
        try:
            student_id = request.POST.getlist('id', None)
            mst2 = request.POST.getlist('mst2', None)

            teacher = request.user.faculty
            if student_id and mst2:
                for id, m2 in zip(student_id, mst2):
                    student = Student.objects.get(id=id)
                    if not student:
                        return HttpResponseServerError('Invalid Student')
                    student_marks = Student_Marks.objects.filter(student_id=student.id, teacher_id=teacher.id)
                    if student_marks:
                        student_marks[0].mst2 = m2
                        student_marks[0].save()
                    else:
                        marks = Student_Marks(student=student, teacher=teacher, mst2=m2)
                        marks.save()
                    student.send_marks_email(f'Hello {student.user.first_name},\n\nYour MST2 marks have been updated by {teacher.user.first_name} {teacher.user.last_name}.\n\nMST2: {m2}\n\n\n\nThis is an auto-generated email by the system and does not support incoming mails. If you have any queries, please reach out to us through your dashboard.')
                return redirect('marks')
            else:
                return HttpResponseServerError('Invalid Data')
        except Exception as e: 
            print(e, 'Got error while saving marks ...')
            return HttpResponseServerError('Something went wrong')       
    return HttpResponseBadRequest('Invalid Request')

def marks_assign(request):
    if not request.user.is_faculty:
        return redirect('/')

    if request.method == 'POST':
        try:
            student_id = request.POST.getlist('id', None)
            assignment = request.POST.getlist('assignment', None)

            teacher = request.user.faculty
            if student_id and assignment:
                for id, a in zip(student_id, assignment):
                    student = Student.objects.get(id=id)
                    if not student:
                        return HttpResponseServerError('Invalid Student')
                    student_marks = Student_Marks.objects.filter(student_id=student.id, teacher_id=teacher.id)
                    if student_marks:
                        student_marks[0].assignment = a
                        student_marks[0].save()
                    else:
                        marks = Student_Marks(student=student, teacher=teacher, assignment=a)
                        marks.save()
                    student.send_marks_email(f'Hello {student.user.first_name},\n\nYour Assignment marks have been updated by {teacher.user.first_name} {teacher.user.last_name}.\n\nAssignment: {a}\n\n\n\nThis is an auto-generated email by the system and does not support incoming mails. If you have any queries, please reach out to us through your dashboard.')
                return redirect('marks')
            else:
                return HttpResponseServerError('Invalid Data')
        except Exception as e: 
            print(e, 'Got error while saving marks ...')
            return HttpResponseServerError('Something went wrong')       
    return HttpResponseBadRequest('Invalid Request')

def teacher_messages(request):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    messages = Teacher_Messages.objects.all()
    context = {'title': 'Teacher Messages', 'messages': messages,}
    return render(request, 'settings/teachmess.html', context=context)


from Admin.utils import set_attendance
def hellj(request):
    value = set_attendance()

    print(value)
    return HttpResponse(f'Face Detection Completed, {value}')

from django.http import JsonResponse
def attendance_runner(request):
    if not request.user.is_hod:
        return JsonResponse({'error': "Sorry, you can request on this endpoint!!"})
    try:
        value = set_attendance()
        if value:
            response_data = {'result': value, 'success': True}
        else: 
            response_data = {'result': 'Something Went Wrong!', 'success': False}       
        return JsonResponse(response_data)
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)})