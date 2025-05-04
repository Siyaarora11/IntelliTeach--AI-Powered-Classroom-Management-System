from django.shortcuts import redirect, render
from django.http import HttpResponseServerError, JsonResponse
from Admin.models import Student, AuthUser
from django.core.exceptions import ValidationError
import datetime
from django.contrib.auth.decorators import login_required
from student.models import Student_Query
from teachers.models import AssignMents, Important_Topics
from django.conf import settings


def student(request, context={}):
    if request.method == 'POST':
        if not request.user.is_faculty and not request.user.is_hod:
            return redirect('home')
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        father_name = request.POST.get('father_name', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        mobile = request.POST.get('mobile', None)
        roll_number = request.POST.get('roll_number', None)
        image = request.FILES.get('image', None)
        dob = request.POST.get('dob', None)
        dob_date = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        dob_formatted = dob_date.strftime("%Y-%m-%d")
        try:
            user = AuthUser.objects.create(email=email, first_name=first_name, last_name=last_name, is_student=True, picture=image)
            user.set_password(password)
            student = Student.objects.create(user=user, roll_number=roll_number, dob=dob_formatted, father_name=father_name, mobile=mobile)
            student.send_welcome_email(password)
        except ValidationError as e:
            try:
                user.delete() if user else None
            except UnboundLocalError as e:
                pass
            return HttpResponseServerError("Something went wrong, try again.")
        except Exception as e:
            try:
                user.delete() if user else None
            except UnboundLocalError as e:
                pass
            students = Student.objects.all()
            context = {'title': f'Students - {settings.APP_NAME}', 'students': students, 'messages': [{'message': 'An error occurred!', 'tag': 'danger'}]}
            return render(request, 'student/index.html', context=context)
        students = Student.objects.all()
        context = {'title': f'Students - {settings.APP_NAME}', 'students': students, **context}
        return render(request, 'student/index.html', context=context)

    students = Student.objects.all()
    context = {'title': f'Students - {settings.APP_NAME}', 'students': students}
    return render(request, 'student/index.html', context=context)


def update_student(request):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    if request.method == 'POST':
        student_id = request.POST.get('id', None)
        first_name = request.POST.get('first_name', None)
        father_name = request.POST.get('father_name', None)
        last_name = request.POST.get('last_name', None)
        mobile = request.POST.get('mobile', None)
        email = request.POST.get('email', None)
        roll_number = request.POST.get('roll_number', None)
        image = request.FILES.get('image', None)
        dob = request.POST.get('dob', None)
        try:
            student = Student.objects.get(id=student_id)
            # student.roll_number = roll_number if roll_number else student.roll_number
            student.dob = dob if dob else student.dob
            # student.user.email = email if email else student.user.email
            student.user.first_name = first_name if first_name else student.user.first_name
            student.user.last_name = last_name if last_name else student.user.last_name
            student.user.picture = image if image else student.user.picture # type: ignore
            student.father_name = father_name if father_name else student.father_name
            student.mobile = mobile if mobile else student.mobile
            student.user.save()
            student.save()
            student.user.email_user(subject='Account Update', message='Your account has been updated successfully.', from_email=settings.DEFAULT_FROM_EMAIL)
        except ValidationError as e:
            return HttpResponseServerError("Something went wrong, try again.")
        except Exception as e:
            print(e)
            students = Student.objects.all()
            context = {'title': f'Students - {settings.APP_NAME}', 'students': students, 'messages': [{'message': 'An error occurred!', 'tag': 'danger'}]}
            return render(request, 'student/index.html', context=context)
        students = Student.objects.all()
        context = {'title': f'Students - {settings.APP_NAME}', 'students': students, 'messages': [{'message': 'Student updated successfully!', 'tag': 'success'}]}
        return render(request, 'student/index.html', context=context)
    students = Student.objects.all()
    context = {'title': f'Students - {settings.APP_NAME}', 'students': students}
    return render(request, 'student/index.html', context=context)

def delete_student(request):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    if request.method == 'POST':
        student_id = request.POST.get('id', None)
        try:
            student = Student.objects.get(id=student_id)
            student.user.delete_account_email()
            student.user.delete()
        except ValidationError as e:
            return HttpResponseServerError("Something went wrong, try again.")
        except Exception as e:
            students = Student.objects.all()
            context = {'title': f'Students - {settings.APP_NAME}', 'students': students, 'messages': [{'message': 'An error occurred!', 'tag': 'danger'}]}
            return render(request, 'student/index.html', context=context)
        students = Student.objects.all()
        context = {'title': f'Students - {settings.APP_NAME}', 'students': students, 'messages': [{'message': 'Student deleted successfully!', 'tag': 'success'}]}
        return render(request, 'student/index.html', context=context)
    students = Student.objects.all()
    context = {'title': f'Students - {settings.APP_NAME}', 'students': students}
    return render(request, 'student/index.html', context=context)


def student_info(request, id):
    try:
        student = Student.objects.get(roll_number=id)
        context = {'title': f'Students - {settings.APP_NAME}', 'student': student}
        return render(request, 'student/single.html', context=context)
    except Exception as e:
        students = Student.objects.all()
        context = {'title': f'Student - {settings.APP_NAME}', 'students': students, 'messages': [{'message': 'Student not found!', 'tag': 'danger'}]}
        return render(request, 'student/index.html', context=context)

@login_required(login_url='/')
def student_assignments(request):
    if request.user.is_student and request.user.student:
        assignments = AssignMents.objects.all()
        context = {'title': f'Assignments - {settings.APP_NAME}', 'assignments': assignments}
        return render(request, 'assignments.html', context=context)
    return redirect('/')

@login_required(login_url='/')
def student_assignments_view(request, id):
    if request.user.is_student and request.user.student:
        try:
            assignment = AssignMents.objects.get(id=int(id))
            context = {'title': f'Assignment - {settings.APP_NAME}', 'assignment': assignment}
            return render(request, 'single-assignment.html', context=context)
        except Exception as e:
            return redirect('/assignments/')
    return redirect('/')

@login_required
def student_topics(request):
    if request.user.is_student and request.user.student:
        topics = Important_Topics.objects.all()
        context = {'title': f'Important Topics - {settings.APP_NAME}', 'topics': topics}
        return render(request, 'topics.html', context=context)
    return redirect('/')

@login_required
def student_enquiry(request):
    if request.method == 'POST':
        title = request.POST.get('title', None)
        description = request.POST.get('description', None)
        try:
            student = request.user.student
            student_query = Student_Query.objects.create(student=student, title=title, description=description)
            student_query.send_succes_mail()
        except ValidationError as e:
            return render(request, 'settings/status.html', context={'messages': [{'message': 'An error occurred!', 'tag': 'danger'}]})
        except Exception as e:
            return render(request, 'settings/status.html', context={'messages': [{'message': 'An error occurred!', 'tag': 'danger'}]})
        return render(request, 'settings/status.html', context={'messages': [{'message': 'Query submitted successfully!', 'tag': 'success'}]})
    return render(request, 'settings/status.html', context={'messages': [{'message': 'Request not Allowed!', 'tag': 'danger'}]})