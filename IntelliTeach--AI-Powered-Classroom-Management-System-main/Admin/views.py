from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import AuthUser, Faculty
from Home.models import Student_Notice, Time_Table, Attendance
import json
from django.conf import settings
import pandas as pd
import datetime
from urllib.parse import quote, unquote

def hod_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None and user.is_hod: # type: ignore
            login(request, user)
            return redirect('hod_dashboard')  # Replace with actual HOD dashboard URL
        else:
            # Handle invalid login for HOD
            pass

    return render(request, 'index.html')

def faculty_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None and user.is_faculty: # type: ignore
            login(request, user)
            return redirect('faculty_dashboard')
        elif user is not None  and user.is_hod: # type: ignore
            login(request, user)
            return redirect('admin_dashboard')
    return render(request, 'index.html')

def student_login(request):
    if request.method == 'POST':
        roll_number = request.POST['roll_number']
        password = request.POST['password']
        user = authenticate(request, username=roll_number, password=password)

        if user is not None and user.is_student: # type: ignore
            login(request, user)
            return redirect('student_dashboard')
        else:
            pass
    return render(request, 'index.html')


def admin_dashboard(request):
    notices = Student_Notice.objects.all().order_by('-created_at')
    context = {'title': f"Admin - {settings.APP_NAME}", 'notices': notices}
    return render(request, 'admin.html', context=context)


def update_password(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            if request.user.is_faculty or request.user.is_hod : # type: ignore
                    try:
                        data = request.body.decode('utf-8')
                        data = json.loads(data)
                        _id = data.get('_id', None)
                        user = AuthUser.objects.get(id=int(_id))
                        password = data.get('password', None)
                        confirm_password = data.get('confirm_password', None)
                        if password:
                            if password == confirm_password:
                                user.set_password(password)
                                user.save()
                                user.update_password_email(password)
                                return JsonResponse({'success': True, 'message': 'Password updated successfully'})
                            else:
                                return JsonResponse({'success': False, 'message': 'New password and confirm password do not match'})
                        else:
                            return JsonResponse({'success': False, 'message': 'Please enter a valid password'})
                    except Exception as e:
                        print(e)
                        return JsonResponse({'success': False, 'message': 'An error occurred while updating password'})
            else:
                return JsonResponse({'success': False, 'message': 'You are not authorized to perform this action'})
        else:
            return JsonResponse({'success': False, 'message': 'You are not logged in'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required(login_url='home')
def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')

@login_required(login_url='home')
def add_notice(request):
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.is_hod or request.user.is_faculty: # type: ignore
            title = request.POST.get('title', None)
            description = request.POST.get('description', None)
            attachment = request.FILES.get('attachment', None)
            try:
                notice = Student_Notice.objects.create(title=title, message=description, attachment=attachment, admin=request.user)
                try:
                    notice.send_to_email()
                except Exception as e:
                    print(e)
                    return JsonResponse({'success': True, 'message': f'Notice added successfully, but an error occurred while sending email to students. \n-----> {e}'})
                return JsonResponse({'success': True, 'message': 'Notice added successfully'})
            except Exception as e:
                print(e)
                return JsonResponse({'success': False, 'message': 'An error occurred while adding notice'})
        else:
            return JsonResponse({'success': False, 'message': 'You are not authorized to perform this action'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

from django.core.mail import send_mail
@login_required(login_url='home')
def delete_notice(request, id):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    try:
        notice = Student_Notice.objects.get(id=int(id))
        notice.delete()
        return redirect('home')
    except Exception as e:
        print(e)
        return redirect('home')
    

def get_html_time_table():
    time_table_objects = Time_Table.objects.all() or []

    if not time_table_objects:
        return None
    # Create a DataFrame from the queryset
    df = pd.DataFrame(list(time_table_objects.values('day', 'time_from', 'time_to', 'subject')))

    # Convert time_from and time_to to strings
    df['time_from'] = df['time_from'].apply(lambda x: x.strftime('%I:%M %p') if x else None)
    df['time_to'] = df['time_to'].apply(lambda x: x.strftime('%I:%M %p') if x else None)

    df['time_range'] = df['time_from'] + ' - ' + df['time_to']

    # Define the desired order of time ranges
    time_range_order = settings.TIME_RANGE_ORDER

    day_order = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday'
    ]

    if settings.TIME_TABLE_WEEKEND_CLASSES:
        day_order.extend(['Saturday', 'Sunday'])

    # Pivot the DataFrame to rearrange the data
    df_pivot = df.pivot(index='day', columns='time_range', values='subject')

    # Reorder columns according to the defined order
    try:
        df_pivot = df_pivot[time_range_order] if time_range_order else df_pivot
    except KeyError:
        df_pivot = df_pivot

    # Sort days
    df_pivot = df_pivot.reindex(day_order)

    # Generate HTML table
    return df_pivot.to_html(classes='table table-bordered', na_rep='', index_names=False, justify='center')
    
@login_required(login_url='home')
def time_table(request):
    if request.method == 'POST':
        if not request.user.is_faculty and not request.user.is_hod:
            return redirect('home')
        day = request.POST.get('day', None)
        time_from = request.POST.get('from', None)
        time_to = request.POST.get('to', None)
        subject = request.POST.get('subject', None)
        try:
            Time_Table.objects.create(day=day, time_from=time_from, time_to=time_to, subject=subject)
            return redirect('time_table')
        except Exception as e:
            print(e)
            return redirect('time_table')
    
    html_table = get_html_time_table()

    if not html_table:
        return render(request=request, template_name='table.html', context={'title': f'Time table - {settings.APP_NAME}', 'emp': True})

    context = {'html_table': html_table, 'title': f'Time table - {settings.APP_NAME}', 'weekends': settings.TIME_TABLE_WEEKEND_CLASSES}
    return render(request=request, template_name='table.html', context=context)


def update_time_table(request):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    if request.method == 'POST':
        data = request.body
        data = json.loads(data) if data else {}
        for obj in data:
            _id = obj.get('pk', None)
            day = obj.get('day', None)
            time_from = datetime.datetime.strptime(obj.get('from', None), '%H:%M').time() if obj.get('from', None) else None
            time_to = datetime.datetime.strptime(obj.get('to', None), '%H:%M').time() if obj.get('to', None) else None
            subject = obj.get('subject', None)
            if _id:
                if day and time_from and time_to and subject and not subject == 'None':
                    try:
                        time_table = Time_Table.objects.get(id=_id)
                        time_table.day = day
                        time_table.time_from = time_from
                        time_table.time_to = time_to
                        time_table.subject = subject
                        time_table.save()
                    except Exception as e:
                        print(e)
                        return JsonResponse({'success': False, 'message': 'An error occurred while updating time table'})
                elif subject == 'None':
                    Time_Table.objects.get(id=_id).delete()
            else:
                return JsonResponse({'success': False, 'message': 'Invalid request'})
        return JsonResponse({'success': True, 'message': 'Time table updated successfully'})
    
    time_table_objects = Time_Table.objects.all()

    arr = []

    for obj in time_table_objects:
        arr.append({
            'id': obj.id,
            'day': obj.day,
            'time_from': obj.time_from.strftime('%H:%M') if obj.time_from else '',
            'time_to': obj.time_to.strftime('%H:%M') if obj.time_to else '',
            'subject': obj.subject
        })

    return render(request, 'update_table.html', {'time_table': arr, 'title': f'Time Table - {settings.APP_NAME}', 'weekends': settings.TIME_TABLE_WEEKEND_CLASSES})



def attendance_view(request):
    if not request.user.is_hod:
        return redirect('home')
    
     # Get all attendance records
    # attendance_records = Attendance.objects.all()

    tm = Time_Table.objects.all()
    
    # Create a dictionary to store unique combinations of date and subject
    attendance_dict = {}

    # Populate the dictionary with attendance data
    # for attendance in attendance_records:
    #     key = (attendance.created_at.date(), attendance.time.subject, attendance.time.id)
    #     if key not in attendance_dict:
    #         attendance_dict[key] = {
    #             'Day': attendance.time.day,
    #             'Date': attendance.created_at.date(),
    #             'Subject': attendance.time.subject,
    #             'Time Range': f"{attendance.time.time_from.strftime('%I:%M %p') if attendance.time.time_from else ''} - {attendance.time.time_to.strftime('%I:%M %p') if attendance.time.time_to else ''}",
    #             'View': f'<a href="/attendance/{attendance.time.id}" target="_blank">  <button class="btn btn-info btn-sm"> View </button> </a>'
    #         }

    for t in tm:
        if not t.subject:
            continue
        key = (t.subject, t.id)
        if key not in attendance_dict:
            attendance_dict[key] = {
                'Day': t.day,
                'Subject': t.subject,
                'Time Range': f"{t.time_from.strftime('%I:%M %p') if t.time_from else ''} - {t.time_to.strftime('%I:%M %p') if t.time_to else ''}",
                'View': f'<a href="/attendance/{t.id}" target="_blank">  <button class="btn btn-info btn-sm"> View </button> </a>'
            }
    
    # Convert dictionary values to a list of dictionaries
    attendance_data = list(attendance_dict.values())

    # Create DataFrame from the list of dictionaries
    attendance_df = pd.DataFrame(attendance_data)

    # Convert DataFrame to HTML
    attendance_table = attendance_df.to_html(classes='table rb_table table-bordered', na_rep='', index_names=False, justify='center', escape=False, index=False)
    context = {
        'attendance': attendance_table,
        'title': f'Attendance - {settings.APP_NAME}'
    }

    return render(request=request, template_name='settings/attendance-list.html', context=context)

def one_attendance_view(request, id):
    if not request.user.is_faculty and not request.user.is_hod:
        return redirect('home')
    try:
        # tm = Time_Table.objects.get(subject=unquote(id))
        _id = int(id)
        att = Attendance.objects.filter(time_id=_id).order_by('created_at')

        # Create a DataFrame to hold the attendance data
        data = []
        students = set()
        dates = set()
        for attendance in att:
            students.add(attendance.student.user.get_full_name())
            data.append({
                'Name / Date': attendance.created_at.date(),
                'Student Name': attendance.student.user.get_full_name(),
                'Status': 'P' if attendance.status else 'A'
            })
            dates.add(attendance.created_at.date())

        df = pd.DataFrame(data)

        # Pivot the DataFrame to have dates as columns and students as rows
        pivot_df = df.pivot(index='Student Name', columns='Name / Date', values='Status')

        # Reorder columns by date
        pivot_df = pivot_df[sorted(dates)]
        html_table = pivot_df.to_html(classes='table rb_table table-bordered', na_rep='', escape=False, justify='center', index_names=True, notebook=True, render_links=True)

        context = {'html_table': html_table, 'subject': f'Attendance for {att[0].time.subject} ({att[0].time.time_from.strftime("%I:%M %p")} - {att[0].time.time_to.strftime("%I:%M %p")})', 'title': f'Attendance - {settings.APP_NAME}'}
        return render(request=request, template_name='settings/one-attendance.html', context=context)
    except Exception as e:
        print(e)
        return render(request=request, template_name='settings/one-attendance.html', context={'emp':True, 'title': f'Attendance - {settings.APP_NAME}', 'subject': 'Attendance not available'})

def attendance_view_faculty(request):
    if not request.user.is_faculty:
        return redirect('home')

    tm = Time_Table.objects.filter(subject=request.user.faculty.subject)

    if not tm and not request.user.faculty.subject:
        return render(request=request, template_name='settings/attendance-list.html', context={'emp': True, 'title': f'Attendance - {settings.APP_NAME}'})
    
    attendance_dict = {}

    for t in tm:
        key = (t.subject, t.id)
        if key not in attendance_dict:
            attendance_dict[key] = {
                'Day': t.day,
                'Subject': t.subject,
                'Time Range': f"{t.time_from.strftime('%I:%M %p') if t.time_from else ''} - {t.time_to.strftime('%I:%M %p') if t.time_to else ''}",
                'View': f'<a href="/attendance/{t.id}" target="_blank">  <button class="btn btn-info btn-sm"> View </button> </a>'
            }
    
    # Convert dictionary values to a list of dictionaries
    attendance_data = list(attendance_dict.values())

    # Create DataFrame from the list of dictionaries
    attendance_df = pd.DataFrame(attendance_data)

    # Convert DataFrame to HTML
    attendance_table = attendance_df.to_html(classes='table rb_table table-bordered', na_rep='', index_names=False, justify='center', escape=False, index=False)
    context = {
        'attendance': attendance_table,
        'title': f'Attendance - {settings.APP_NAME}'
    }

    return render(request=request, template_name='settings/attendance-list.html', context=context)
