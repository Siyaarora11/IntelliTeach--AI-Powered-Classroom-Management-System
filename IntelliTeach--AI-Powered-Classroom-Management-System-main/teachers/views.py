from django.forms import ValidationError
from django.http import HttpResponseForbidden, HttpResponseServerError, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from Home.models import Student_Marks, Student_Notice
from Admin.models import AuthUser, Faculty, Student
from teachers.models import AssignMents, Assignment_Questions, Important_Topics
from student.models import Student_Queries_Answers, Student_Query
import datetime
import os
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

title = 'Teachers Dashboard'

@login_required(login_url='/')
def facultyDashboard(request):
    if not request.user.is_faculty:
        return redirect('/')
    notices = Student_Notice.objects.all().order_by('-created_at')
    teacher = request.user.faculty # type: ignore
    students = Student.objects.all()
    student_data = []
    for student in students:
        student_marks_count = student.student_marks.filter(teacher__user__id=request.user.id).count()
        student_data.append({'student': student, 'student_marks_count': student_marks_count})

    queries = Student_Query.objects.all()
    context = {'title': f'Teachers Dahboard - {settings.APP_NAME}', 'notices': notices, 'queries': queries,'student_data': student_data}
    return render(request, 'faculty_dashboard.html',context=context) # type: ignore


def faculty_Profile(request):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    context = {'title': title, }
    return render(request, 'settings/profile.html', context=context)

def add_student(request):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    context = {'title': f'Add Students - {settings.APP_NAME}', }
    return render(request, 'faculty/add_students.html', context=context)

def teachers_list(request):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    title = f'Teachers - {settings.APP_NAME}'
    if request.method == 'POST':
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        subject = request.POST.get('subject', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        mobile = request.POST.get('mobile', None)
        image = request.FILES.get('image', None) 
        try:
            user = AuthUser.objects.create(email=email, first_name=first_name, last_name=last_name, is_faculty=True, picture=image)
            user.set_password(password)
            user.save()
            teacher = Faculty.objects.create(user=user, subject=subject, mobile=mobile)
            teacher.send_welcome_email(password)
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
            teachers = Faculty.objects.all()
            context = {'title': title, 'teachers': teachers, 'messages': [{'message': 'An error occurred!', 'tag': 'danger'}]}
            return render(request, 'teachers.html', context=context)
        teachers = Faculty.objects.all()
        context = {'title': f'Teachers - {settings.APP_NAME}', 'teachers': teachers}
        return render(request, 'teachers.html', context=context)
    data = Faculty.objects.all()
    context = {'title': title,'teachers': data}
    return render(request, 'teachers.html', context=context)


def update_teacher(request):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    if request.method == 'POST':
        _id = request.POST.get('id', None)
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        password = request.POST.get('password', None)
        subject = request.POST.get('subject', None)
        mobile = request.POST.get('mobile', None)
        email = request.POST.get('email', None)
        image = request.FILES.get('image', None)
        try:
            teacher = Faculty.objects.get(id=_id)
            # teacher.user.email = email if email else teacher.user.email
            teacher.user.first_name = first_name if first_name else teacher.user.first_name
            teacher.user.last_name = last_name if last_name else teacher.user.last_name
            teacher.subject = subject if subject else teacher.subject
            teacher.user.picture = image if image else teacher.user.picture # type: ignore
            teacher.mobile = mobile if mobile else teacher.mobile
            if password:
                teacher.user.set_password(password)
                try:
                    teacher.user.update_password_email(password)
                except Exception as e:
                    print(e)
                    pass
            teacher.user.save()
            teacher.save()
        except ValidationError as e:
            return HttpResponseServerError("Something went wrong, try again.")
        except Exception as e:
            print(e)
            teachers = Faculty.objects.all()
            context = {'title': f'Update Teacher - {settings.APP_NAME}', 'teachers': teachers, 'messages': [{'message': 'An error occurred!', 'tag': 'danger'}]}
            return render(request, 'teachers.html', context=context)
        teachers = Faculty.objects.all()
        context = {'title': f'Update Teacher - {settings.APP_NAME}', 'teachers': teachers, 'messages': [{'message': 'Teacher updated successfully!', 'tag': 'success'}]}
        return render(request, 'teachers.html', context=context)
    teachers = Faculty.objects.all()
    context = {'title': f'Update Teacher - {settings.APP_NAME}', 'teachers': teachers,}
    return render(request, 'teachers.html', context=context)

def delete_teacher(request):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    if request.method == 'POST':
        _id = request.POST.get('id', None)
        print(_id, 'teacher data', request.POST)
        try:
            teacher = Faculty.objects.get(id=_id)
            teacher.user.delete_account_email()
            teacher.user.delete()
        except ValidationError as e:
            return HttpResponseServerError("Something went wrong, try again.")
        except Exception as e:
            teachers = Faculty.objects.all()
            context = {'title': f'Delete Teacher - {settings.APP_NAME}', 'teachers': teachers, 'messages': [{'message': 'An error occurred!', 'tag': 'danger'}]}
            return render(request, 'teachers.html', context=context)
        teachers = Faculty.objects.all()
        context = {'title': f'Delete Teacher - {settings.APP_NAME}', 'teachers': teachers, 'messages': [{'message': 'Teacher deleted successfully!', 'tag': 'success'}]}
        return render(request, 'teachers.html', context=context)
    teachers = Faculty.objects.all()
    context = {'title': f'Delete Teacher - {settings.APP_NAME}', 'teachers': teachers}
    return render(request, 'teachers.html', context=context)


@login_required(login_url='/')
def assignment_list(request):
    if request.method == 'POST':
        if not request.user.is_faculty or not request.user.faculty:
            return JsonResponse({'message': 'You are not authorized to perform this action', 'success': False}, status=403)
        try:
            print(request.POST, 'request.POST', request.FILES)

            title = request.POST.get('title')
            description = request.POST.get('description')
            due_date = request.POST.get('dueDate')
            attachments = request.FILES.get('attachments')
            due_date = timezone.make_aware(datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M'))

            if not title:
                raise Exception('Title is required')
            teacher = request.user.faculty
            assignment = AssignMents.objects.create(
                title=title,
                description=description,
                due_date=due_date,
                attachments=attachments,
                teacher=teacher,
            )

            question_titles = request.POST.getlist('questionTitles')
            question_descriptions = request.POST.getlist('questionDescriptions')
            question_attachments = request.FILES.getlist('questionAttachments')
            print(question_titles, question_descriptions, question_attachments, 'question data')
            for title, description, attachment in zip(question_titles, question_descriptions, question_attachments):
                if attachment != 'undefined':
                    question = Assignment_Questions.objects.create(
                        question=title,
                        description=description,
                        attachments=attachment,
                    )
                    assignment.questions.add(question)
            assignment.save()
            assignment.send_assignment_email()

            return JsonResponse({'message': 'Assignment added successfully', 'success': True})
        except Exception as e:
            if assignment and assignment.questions:
                assignment.questions.all().delete()
            assignment.delete() if assignment else None
            print(e, 'error')
            return JsonResponse({'message': 'An error occurred', 'success': False}, status=500)

    data = AssignMents.objects.filter(teacher=request.user.faculty)
    context = {'title': f"Assignments - {settings.APP_NAME}",'assignments': data}
    return render(request, 'settings/assignment.html', context=context)

@login_required(login_url='/')
def delete_assignment(request):
    if request.method == 'POST':
        if not request.user.is_faculty or not request.user.faculty:
            return JsonResponse({'message': 'You are not authorized to perform this action', 'success': False}, status=403)
        _id = request.POST.get('id', None)
        try:
            assignment = AssignMents.objects.get(id=_id)
            if assignment and assignment.teacher == request.user.faculty:
                os.remove(assignment.attachments.path) if assignment.attachments else None
                assignment.delete()
            raise Exception('Assignment not found')
        except ValidationError as e:
            return HttpResponseServerError("Something went wrong, try again.")
        except Exception as e:
            assignments = AssignMents.objects.all()
            context = {'title': 'Assignments', 'assignments': assignments, 'messages': [{'message': 'An error occurred!', 'tag': 'danger'}]}
            return render(request, 'assignments.html', context=context)
        assignments = AssignMents.objects.all()
        context = {'title': 'Assignments', 'assignments': assignments, 'messages': [{'message': 'Assignment deleted successfully!', 'tag': 'success'}]}
        return render(request, 'assignments.html', context=context)
    assignments = AssignMents.objects.all()
    context = {'title': 'Assignments', 'assignments': assignments}
    return render(request, 'assignments.html', context=context)

@login_required(login_url='/')
def delete_assignment_r(request, id):
    if not request.user.is_faculty or not request.user.faculty:
        return HttpResponseForbidden()
    try:
        assignment = AssignMents.objects.get(id=int(id))
        assignment.delete() if assignment else None
        return redirect('assignments')
    except Exception as e:
        return HttpResponseServerError("Something Went Wrong")

@login_required(login_url='/')
def single_assignment(request, id):
    assignment = AssignMents.objects.get(id=id)
    context = {'title': f'Assignment- {settings.APP_NAME}', 'assignment': assignment}
    return render(request, 'settings/assign-single.html', context=context)


@csrf_exempt
def update_assignment(request, assignment_id):
    assignment = get_object_or_404(AssignMents, id=assignment_id)
    if assignment and request.user.faculty != assignment.teacher:
        return JsonResponse({'message': 'You are not Authorized to do this.', 'success': False})
    if request.method == 'POST':
        if not request.user.is_faculty or not request.user.faculty:
            return JsonResponse({'message': 'You are not authorized to perform this action', 'success': False}, status=403)
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            due_date = request.POST.get('dueDate')
            attachments = request.FILES.get('attachments')
            due_date = timezone.make_aware(datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M'))

            if not title:
                raise Exception('Title is required')            
            assignment.title = title if title else assignment.title
            assignment.description= description if description else assignment.description
            assignment.due_date= due_date if due_date else assignment.due_date
            if attachments:
                assignment.attachments= attachments
            try:
                question_ids = request.POST.getlist('questionIds')
                question_titles = request.POST.getlist('questionTitles')
                question_descriptions = request.POST.getlist('questionDescriptions')
                question_attachments = request.FILES.getlist('questionAttachments')
                print(question_ids, question_titles, question_descriptions, question_attachments, 'question data')
            except Exception as e:
                print(e, 'error')
                raise Exception('An error occurred')
            assignment.questions.all().delete()
            # Add new questions
            try:
                for id, title, description, attachment in zip(question_ids, question_titles, question_descriptions, question_attachments):
                    print(id, title, description, attachment, '--- question data')
                    if id:
                        question = Assignment_Questions.objects.get(pk=int(id))
                        question.question = title
                        question.description = description
                        if attachment and attachment != question.attachments:
                            question.attachments = attachment 
                        question.save()
                    else:
                        question = Assignment_Questions.objects.create(
                            question=title,
                            description=description,
                            attachments=attachment,
                        )
                    assignment.questions.add(question)
            except Exception as e:
                print(e, 'error')
                raise Exception('An error occurred')
            assignment.save()
            return JsonResponse({'message': 'Assignment updated successfully', 'success': True})
        except Exception as e:
            print(e, 'error')
            if assignment and assignment.questions:
                assignment.questions.all().delete()
            assignment.delete() if assignment else None
            return JsonResponse({'message': 'An error occurred', 'success': False}, status=500)
    else:
        context = {'title': f'Assignment- {settings.APP_NAME}', 'assignment': assignment}
        return render(request, 'settings/update_assignment.html', context=context)


@login_required(login_url='/')
def important_topics(request):
    if request.method == 'POST':
        if not request.user.is_faculty or not request.user.faculty:
            return JsonResponse({'message': 'You are not authorized to perform this action', 'success': False}, status=403)
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            attachments = request.FILES.get('attachments')
            if not title:
                raise Exception('Title is required')
            teacher = request.user.faculty
            imp = Important_Topics.objects.create(
                title=title,
                description=description,
                attachments=attachments,
                teacher=teacher,
            )
            imp.send_important_topics_email()
            data = Important_Topics.objects.filter(teacher=request.user.faculty)
            context = {'title': f"Important Topics - {settings.APP_NAME}",'topics': data, 'messages': [{'message': 'Topic added successfully', 'tag': 'success'}]}
            return render(request, 'settings/topics.html', context=context)
        except Exception as e:
            print(e, 'error')
            data = Important_Topics.objects.filter(teacher=request.user.faculty)
            context = {'title': f"Important Topics - {settings.APP_NAME}",'topics': data, 'messages': [{'message': 'An error occurred', 'tag': 'danger'}]}
            return render(request, 'settings/topics.html', context=context)

    data = Important_Topics.objects.filter(teacher=request.user.faculty)
    context = {'title': f"Important Topics - {settings.APP_NAME}",'topics': data}
    return render(request, 'settings/topics.html', context=context)

@login_required(login_url='/')
def delete_topic(request, id):
    if request.user.is_faculty:
        try:
            topic = Important_Topics.objects.get(pk=int(id))
            if topic and topic.teacher == request.user.faculty:
                os.remove(topic.attachments.path) if topic.attachments else None
                topic.delete()
                return redirect('topics')
            raise Exception('Topic not found')
        except Exception as e:
            print(e, 'error')
            return HttpResponseServerError("Something went wrong, try again.")
    return JsonResponse({'message': 'You are not authorized to perform this action', 'success': False}, status=403)

def view_query(request, id):
    template = 'student_dashboard.html' if request.user.is_student else 'admin-layout.html'
    data = Student_Query.objects.get(pk=int(id)) if request.user.is_faculty else Student_Query.objects.get(pk=int(id), student=request.user.student)
    context = {'title': f"Student Enquiries - {settings.APP_NAME}",'query': data, 'template':template}
    return render(request, 'settings/query.html', context=context)

def queries(request):
    template = 'student_dashboard.html' if request.user.is_student else 'admin-layout.html'
    if request.method == 'POST':
        if not request.user.is_faculty or not request.user.faculty:
            return JsonResponse({'message': 'You are not authorized to perform this action', 'success': False}, status=403)
        try:
            id = request.POST.get('query_id')
            description = request.POST.get('answer')

            teacher = request.user.faculty
            query = Student_Query.objects.get(pk=int(id))
            sq = Student_Queries_Answers.objects.create(
                student_query=query,
                teacher=teacher,
                answer=description,
            )
            sq.send_succes_mail()
            data = Student_Query.objects.all()
            context = {'template': template, 'title': f"Student Enquiries - {settings.APP_NAME}",'queries': data, 'messages': [{'message': 'Reply added successfully', 'tag': 'success'}]}
            return render(request, 'settings/queries.html', context=context)
        except Exception as e:
            print(e, 'error')
            data = Student_Query.objects.all()
            context = {'template': template,'title': f"Student Enquiries - {settings.APP_NAME}",'queries': data, 'messages': [{'message': 'An error occurred', 'tag': 'danger'}]}
            return render(request, 'settings/queries.html', context=context)
        
    data = Student_Query.objects.all() if request.user.is_faculty else Student_Query.objects.filter(student=request.user.student)
    context = {'template': template, 'title': f"Student Enquiries - {settings.APP_NAME}",'queries': data}
    return render(request, 'settings/queries.html', context=context)